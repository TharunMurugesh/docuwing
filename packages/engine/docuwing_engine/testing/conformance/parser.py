"""Conformance test suite for Parser plugins."""

from __future__ import annotations

import io

import pytest

from docuwing_engine.domain.entities import Document
from docuwing_engine.interfaces.parser import ParserPlugin
from docuwing_engine.plugins.registry import PluginCategory
from docuwing_engine.plugins.sdk import PluginConformanceTests


class ParserConformanceTests(PluginConformanceTests):
    """Conformance test suite for Parser plugins.

    Plugin authors subclass this to verify their parser complies with the Engine contract.
    """

    def get_test_document(self) -> tuple[Document, io.BytesIO]:
        """Override to provide a valid test document and stream for this parser."""
        raise NotImplementedError

    def test_parser_category(self) -> None:
        assert self.plugin.MANIFEST.category == PluginCategory.PARSER

    @pytest.mark.asyncio
    async def test_parse_returns_ir(self) -> None:
        doc, stream = self.get_test_document()
        p = self.create_plugin()
        assert isinstance(p, ParserPlugin), "Plugin must be a ParserPlugin"
        p.initialize()

        ir = await p.parse(doc, stream)

        assert ir is not None
        assert ir.document_id == doc.id
        assert ir.pages >= 0
        assert isinstance(ir.sections, list)
