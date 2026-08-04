"""Plugin SDK — base classes, protocols, and testing stubs (EDS §7.4).

This is the public contract third-party plugin authors program against.
Published as part of docuwing_engine_sdk (internal for now).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from docuwing_engine.plugins.registry import PluginCategory, PluginManifest


class PluginBase(ABC):
    """Base class for all Docuwing Engine plugins.

    Every plugin must declare a MANIFEST class attribute and implement
    the category-specific protocol methods.
    """

    MANIFEST: PluginManifest

    @abstractmethod
    def initialize(self, config: dict[str, Any] | None = None) -> None:
        """Initialize the plugin with optional configuration."""
        ...

    def cleanup(self) -> None:
        """Clean up plugin resources. Override if needed."""
        pass

    @property
    def name(self) -> str:
        return self.MANIFEST.name

    @property
    def category(self) -> PluginCategory:
        return self.MANIFEST.category


class PluginConformanceTests(ABC):
    """Base class for plugin conformance test suites (EDS §7.4).

    Subclass this and implement the abstract methods to create a
    conformance test suite for a specific plugin category.

    Usage in tests:
        class TestMyParserConformance(PluginConformanceTests):
            def create_plugin(self):
                return MyParser()

            def test_manifest_valid(self):
                assert self.plugin.MANIFEST.name != ""
    """

    @abstractmethod
    def create_plugin(self) -> PluginBase:
        """Create a fresh instance of the plugin under test."""
        ...

    @property
    def plugin(self) -> PluginBase:
        return self.create_plugin()

    def test_has_manifest(self) -> None:
        """Plugin must declare a valid manifest."""
        p = self.create_plugin()
        assert hasattr(p, "MANIFEST"), "Plugin must have a MANIFEST class attribute"
        assert isinstance(p.MANIFEST, PluginManifest)

    def test_manifest_has_name(self) -> None:
        """Manifest must have a non-empty name."""
        assert self.plugin.MANIFEST.name != ""

    def test_manifest_has_category(self) -> None:
        """Manifest must declare a category."""
        assert isinstance(self.plugin.MANIFEST.category, PluginCategory)

    def test_initialize_does_not_crash(self) -> None:
        """Initialization must not raise."""
        p = self.create_plugin()
        p.initialize()

    def test_cleanup_does_not_crash(self) -> None:
        """Cleanup must not raise."""
        p = self.create_plugin()
        p.initialize()
        p.cleanup()
