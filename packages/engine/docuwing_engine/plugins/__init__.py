"""Plugin system — registry, discovery, and conformance (EDS §7).

The PluginRegistry discovers plugins via Python entry_points (PEP 621),
validates their manifests against compatibility constraints, and provides
typed lookup by category.
"""

from docuwing_engine.plugins.registry import PluginCategory, PluginManifest, PluginRegistry
from docuwing_engine.plugins.sdk import PluginBase

__all__ = [
    "PluginBase",
    "PluginCategory",
    "PluginManifest",
    "PluginRegistry",
]
