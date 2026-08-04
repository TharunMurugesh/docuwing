"""PDF Text Parser using PyMuPDF (fitz)."""

from __future__ import annotations

import io
from typing import Any

import fitz

from docuwing_engine.domain.entities import BoundingBox, Document
from docuwing_engine.interfaces.parser import ParserPlugin
from docuwing_engine.ir.types import Block, DocumentIR, Section, TextBlock
from docuwing_engine.plugins.registry import PluginCategory, PluginManifest


class PdfTextParser(ParserPlugin):
    """Parses digital PDFs extracting text blocks and simple layout using PyMuPDF."""

    MANIFEST = PluginManifest(
        name="pdf_text_parser",
        category=PluginCategory.PARSER,
        description="PyMuPDF-based parser for born-digital PDFs",
        mime_types=["application/pdf"],
    )

    def initialize(self, config: dict[str, Any] | None = None) -> None:
        pass

    async def parse(self, document: Document, stream: io.BytesIO) -> DocumentIR:
        pdf_doc = fitz.open("pdf", stream.read())
        pages = len(pdf_doc)

        blocks: list[Block] = []
        for page_num, page in enumerate(pdf_doc):
            page_dict = page.get_text("dict")
            width = page_dict["width"]
            height = page_dict["height"]

            for b in page_dict["blocks"]:
                if b["type"] == 0:  # text block
                    text = ""
                    for line in b["lines"]:
                        for span in line["spans"]:
                            text += span["text"] + " "
                    text = text.strip()

                    if not text:
                        continue

                    x0, y0, x1, y1 = b["bbox"]

                    # Normalize bbox
                    bbox = BoundingBox(
                        x0=x0 / width if width else 0,
                        y0=y0 / height if height else 0,
                        x1=x1 / width if width else 0,
                        y1=y1 / height if height else 0,
                        page=page_num,
                    )

                    blocks.append(TextBlock(text=text, bbox=bbox))

        # Dump everything into a root section for now
        root_section = Section(blocks=blocks)

        ir = DocumentIR(
            document_id=document.id,
            pages=pages,
            sections=[root_section],
        )

        return ir
