"""Layout Analyzer interface."""

from __future__ import annotations

from abc import abstractmethod

from docuwing_engine.ir.types import DocumentIR
from docuwing_engine.plugins.sdk import PluginBase


class LayoutAnalyzerPlugin(PluginBase):
    """Abstract protocol for layout analysis and IR refinement plugins."""

    @abstractmethod
    async def analyze(self, ir: DocumentIR) -> DocumentIR:
        """Refine reading order, section structure, and merge OCR fragments."""
        raise NotImplementedError
