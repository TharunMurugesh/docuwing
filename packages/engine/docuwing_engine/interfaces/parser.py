"""Parser Plugin Interface (EDS §4.1)."""

from __future__ import annotations

import io
from abc import abstractmethod

from docuwing_engine.domain.entities import Document
from docuwing_engine.ir.types import DocumentIR
from docuwing_engine.plugins.registry import PluginManifest
from docuwing_engine.plugins.sdk import PluginBase


class ParserPlugin(PluginBase):
    """Base class for all document parsers.

    Parsers are responsible for taking a raw byte stream and converting it
    into a DocumentIR.
    """

    MANIFEST: PluginManifest

    @abstractmethod
    async def parse(self, document: Document, stream: io.BytesIO) -> DocumentIR:
        """Parse the document byte stream into a DocumentIR."""
        ...
