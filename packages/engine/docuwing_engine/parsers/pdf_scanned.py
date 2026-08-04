"""Scanned PDF Parser using OCR."""

from __future__ import annotations

import io
from typing import Any

import fitz

from docuwing_engine.domain.entities import BoundingBox, Document
from docuwing_engine.interfaces.ocr import OCRProviderPlugin
from docuwing_engine.interfaces.parser import ParserPlugin
from docuwing_engine.ir.types import Block, DocumentIR, Section, TextBlock
from docuwing_engine.ocr.tesseract import TesseractOCRPlugin
from docuwing_engine.plugins.registry import PluginCategory, PluginManifest


class PdfScannedParserPlugin(ParserPlugin):
    """Parses scanned PDFs by rendering pages to images and running OCR."""

    MANIFEST = PluginManifest(
        name="pdf_scanned_parser",
        category=PluginCategory.PARSER,
        description="OCR-based parser for scanned PDFs",
        mime_types=["application/pdf"],
    )

    def __init__(self, ocr_provider: OCRProviderPlugin | None = None) -> None:
        self.ocr_provider = ocr_provider or TesseractOCRPlugin()

    def initialize(self, config: dict[str, Any] | None = None) -> None:
        pass

    async def parse(self, document: Document, stream: io.BytesIO) -> DocumentIR:
        pdf_doc = fitz.open("pdf", stream.read())
        pages = len(pdf_doc)

        blocks: list[Block] = []
        for page_num, page in enumerate(pdf_doc):
            pix = page.get_pixmap(dpi=150)
            img_bytes = pix.tobytes("png")

            ocr_res = await self.ocr_provider.recognize(img_bytes)
            for ocr_b in ocr_res.blocks:
                bbox = ocr_b.bbox
                if bbox:
                    bbox = BoundingBox(
                        x0=bbox.x0,
                        y0=bbox.y0,
                        x1=bbox.x1,
                        y1=bbox.y1,
                        page=page_num,
                    )
                blocks.append(
                    TextBlock(
                        text=ocr_b.text,
                        bbox=bbox,
                        source_ocr=True,
                        ocr_confidence=ocr_b.confidence,
                    )
                )

        root_section = Section(blocks=blocks)
        return DocumentIR(
            document_id=document.id,
            pages=pages,
            sections=[root_section],
        )
