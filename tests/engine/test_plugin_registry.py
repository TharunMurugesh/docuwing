"""Tests for plugin registry."""

from typing import Any

from docuwing_engine.plugins.registry import (
    PluginCategory,
    PluginManifest,
    PluginRegistry,
)
from docuwing_engine.plugins.sdk import PluginBase


class ValidPlugin(PluginBase):
    MANIFEST = PluginManifest(
        name="valid_test_plugin",
        category=PluginCategory.PARSER,
    )

    def initialize(self, config: dict[str, Any] | None = None) -> None:
        pass


class IncompatiblePlugin(PluginBase):
    MANIFEST = PluginManifest(
        name="incompatible_plugin",
        category=PluginCategory.PARSER,
        engine_version_compat="<0.0.1",
    )

    def initialize(self, config: dict[str, Any] | None = None) -> None:
        pass


def test_plugin_registration():
    registry = PluginRegistry()
    registry.register("valid", ValidPlugin)

    plugin = registry.get("valid")
    assert plugin is not None
    assert plugin.enabled is True
    assert plugin.manifest.name == "valid_test_plugin"


def test_incompatible_plugin_registered_disabled():
    registry = PluginRegistry()
    registry.register("incompat", IncompatiblePlugin)

    plugin = registry.get("incompat")
    assert plugin is not None
    assert plugin.enabled is False
    assert "compat range" in plugin.disable_reason

    # Shouldn't show up in enabled lists
    assert len(registry.list()) == 0
    assert len(registry.list(include_disabled=True)) == 1
