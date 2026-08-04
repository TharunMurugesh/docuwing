"""DOCX Parser using python-docx."""

from __future__ import annotations

import io
from typing import Any

import docx

from docuwing_engine.domain.entities import Document
from docuwing_engine.interfaces.parser import ParserPlugin
from docuwing_engine.ir.types import Block, DocumentIR, Section, TextBlock
from docuwing_engine.plugins.registry import PluginCategory, PluginManifest


class DocxParser(ParserPlugin):
    """Parses Word documents using python-docx."""

    MANIFEST = PluginManifest(
        name="docx_parser",
        category=PluginCategory.PARSER,
        description="Native parser for DOCX files",
        mime_types=["application/vnd.openxmlformats-officedocument.wordprocessingml.document"],
    )

    def initialize(self, config: dict[str, Any] | None = None) -> None:
        pass

    async def parse(self, document: Document, stream: io.BytesIO) -> DocumentIR:
        doc = docx.Document(stream)

        blocks: list[Block] = []
        for para in doc.paragraphs:
            text = para.text.strip()
            if text:
                role = (
                    "heading"
                    if (
                        para.style is not None
                        and para.style.name
                        and para.style.name.startswith("Heading")
                    )
                    else "paragraph"
                )
                blocks.append(TextBlock(text=text, role=role))

        root_section = Section(blocks=blocks)

        ir = DocumentIR(
            document_id=document.id,
            pages=0,  # DOCX doesn't have fixed pages
            sections=[root_section],
        )

        return ir
