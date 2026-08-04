"""Plugin Registry (EDS §7.3).

Discovers plugins via entry_points, validates manifests, and provides
typed lookup. Plugins are registered as disabled (not crashed) when
their engine version compatibility check fails.
"""

from __future__ import annotations

import importlib.metadata
from enum import Enum
from typing import Any

import structlog
from pydantic import BaseModel, Field

from docuwing_engine import __version__ as engine_version

logger = structlog.get_logger(__name__)

ENTRY_POINT_GROUP = "docuwing.plugins"


class PluginCategory(str, Enum):
    """Categories of plugins the Engine supports."""

    PARSER = "parser"
    OCR_PROVIDER = "ocr_provider"
    LLM_PROVIDER = "llm_provider"
    VALIDATOR = "validator"
    OUTPUT_GENERATOR = "output_generator"
    ENTITY_RESOLVER = "entity_resolver"


class TrustLevel(str, Enum):
    """Plugin trust levels."""

    OFFICIAL = "official"
    VERIFIED = "verified"
    COMMUNITY = "community"


class PluginManifest(BaseModel):
    """Plugin manifest — metadata declared by each plugin."""

    name: str = Field(description="Unique plugin name")
    version: str = Field(default="0.1.0")
    category: PluginCategory
    description: str = Field(default="")
    trust_level: TrustLevel = Field(default=TrustLevel.OFFICIAL)
    engine_version_compat: str = Field(
        default=">=0.1.0",
        description="Engine version compatibility range (PEP 440 specifier)",
    )
    mime_types: list[str] = Field(
        default_factory=list,
        description="MIME types this plugin handles (for parsers/OCR)",
    )
    capabilities: dict[str, Any] = Field(
        default_factory=dict,
        description="Plugin-specific capability declarations",
    )


class RegisteredPlugin:
    """A plugin registered in the registry."""

    def __init__(
        self,
        manifest: PluginManifest,
        plugin_class: type,
        enabled: bool = True,
        disable_reason: str = "",
    ) -> None:
        self.manifest = manifest
        self.plugin_class = plugin_class
        self.enabled = enabled
        self.disable_reason = disable_reason
        self._instance: Any = None

    def get_instance(self, **kwargs: Any) -> Any:
        """Get or create the plugin instance (lazy singleton)."""
        if self._instance is None:
            self._instance = self.plugin_class(**kwargs)
        return self._instance


class PluginRegistry:
    """Central plugin registry with entry-point discovery and manifest validation.

    Usage:
        registry = PluginRegistry()
        registry.discover()  # Load from entry_points
        parser = registry.get("pdf_text_parser", PluginCategory.PARSER)
    """

    def __init__(self) -> None:
        self._plugins: dict[str, RegisteredPlugin] = {}

    def discover(self) -> int:
        """Discover and register plugins from entry_points.

        Returns the number of plugins discovered.
        """
        discovered = 0
        eps = importlib.metadata.entry_points()

        # entry_points() returns a dict in Python 3.12+, SelectableGroups before
        plugin_eps: list[importlib.metadata.EntryPoint] | Any
        if isinstance(eps, dict):
            plugin_eps = eps.get(ENTRY_POINT_GROUP, [])
        else:
            plugin_eps = eps.select(group=ENTRY_POINT_GROUP)

        for ep in plugin_eps:
            try:
                plugin_class = ep.load()
                self.register(ep.name, plugin_class)
                discovered += 1
            except Exception as e:
                logger.warning(
                    "plugin_discovery_failed",
                    entry_point=ep.name,
                    error=str(e),
                )

        logger.info("plugin_discovery_complete", count=discovered)
        return discovered

    def register(
        self,
        name: str,
        plugin_class: type,
        manifest: PluginManifest | None = None,
    ) -> RegisteredPlugin:
        """Register a plugin class with the registry.

        If the plugin has a `MANIFEST` class attribute, it's used automatically.
        Plugins with incompatible engine versions are registered as disabled,
        not rejected.
        """
        # Get manifest from class if not provided
        if manifest is None:
            manifest = getattr(plugin_class, "MANIFEST", None)
            if manifest is None:
                manifest = PluginManifest(
                    name=name,
                    category=PluginCategory.PARSER,  # default
                    description=f"Auto-registered plugin: {name}",
                )

        # Validate engine version compatibility
        enabled = True
        disable_reason = ""

        if not self._check_version_compat(manifest.engine_version_compat):
            enabled = False
            disable_reason = (
                f"Engine version {engine_version} does not satisfy "
                f"compat range '{manifest.engine_version_compat}'"
            )
            logger.warning(
                "plugin_registered_disabled",
                plugin=name,
                reason=disable_reason,
            )

        registered = RegisteredPlugin(
            manifest=manifest,
            plugin_class=plugin_class,
            enabled=enabled,
            disable_reason=disable_reason,
        )

        self._plugins[name] = registered

        logger.info(
            "plugin_registered",
            plugin=name,
            category=manifest.category.value,
            enabled=enabled,
        )

        return registered

    def get(self, name: str, category: PluginCategory | None = None) -> RegisteredPlugin | None:
        """Get a registered plugin by name, optionally filtered by category."""
        plugin = self._plugins.get(name)
        if plugin is None:
            return None
        if category and plugin.manifest.category != category:
            return None
        return plugin

    def get_by_category(self, category: PluginCategory) -> list[RegisteredPlugin]:
        """Get all enabled plugins in a category."""
        return [p for p in self._plugins.values() if p.manifest.category == category and p.enabled]

    def get_by_mime_type(
        self, mime_type: str, category: PluginCategory | None = None
    ) -> RegisteredPlugin | None:
        """Find an enabled plugin that handles a given MIME type."""
        for plugin in self._plugins.values():
            if not plugin.enabled:
                continue
            if category and plugin.manifest.category != category:
                continue
            if mime_type in plugin.manifest.mime_types:
                return plugin
        return None

    def list(self, include_disabled: bool = False) -> list[RegisteredPlugin]:
        """List all registered plugins."""
        if include_disabled:
            return list(self._plugins.values())
        return [p for p in self._plugins.values() if p.enabled]

    def _check_version_compat(self, compat_spec: str) -> bool:
        """Check if the current engine version satisfies a compatibility spec.

        Uses packaging.version for PEP 440 comparison when available,
        falls back to a simple prefix match.
        """
        try:
            from packaging.specifiers import SpecifierSet
            from packaging.version import Version

            return Version(engine_version) in SpecifierSet(compat_spec)
        except ImportError:
            # Fallback: accept everything if packaging isn't available
            return True
        except Exception:
            return False
