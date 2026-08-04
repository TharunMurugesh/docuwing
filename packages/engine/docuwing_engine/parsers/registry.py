"""Parser registry."""

from __future__ import annotations

import mimetypes

from docuwing_engine.domain.entities import Document, SourceFormat
from docuwing_engine.interfaces.parser import ParserPlugin
from docuwing_engine.plugins.registry import PluginCategory, PluginRegistry


class ParserRegistry:
    """Wrapper around PluginRegistry specifically for resolving parsers."""

    def __init__(self, registry: PluginRegistry) -> None:
        self.registry = registry

    def resolve(self, document: Document) -> ParserPlugin | None:
        """Resolve the best parser for a document based on its declared format or filename."""
        mime_type = ""
        if document.source_format == SourceFormat.PDF_TEXT:
            mime_type = "application/pdf"
        elif document.source_format == SourceFormat.DOCX:
            mime_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        elif document.source_format == SourceFormat.XLSX:
            mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        elif document.source_format == SourceFormat.CSV:
            mime_type = "text/csv"
        else:
            guessed_mime, _ = mimetypes.guess_type(document.filename)
            mime_type = guessed_mime or ""

        if not mime_type:
            return None

        plugin_reg = self.registry.get_by_mime_type(mime_type, category=PluginCategory.PARSER)
        if plugin_reg:
            instance = plugin_reg.get_instance()
            if isinstance(instance, ParserPlugin):
                return instance

        return None
