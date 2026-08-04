"""Image Document Parser using OCR."""

from __future__ import annotations

import io
from typing import Any

from docuwing_engine.domain.entities import Document
from docuwing_engine.interfaces.ocr import OCRProviderPlugin
from docuwing_engine.interfaces.parser import ParserPlugin
from docuwing_engine.ir.types import Block, DocumentIR, Section, TextBlock
from docuwing_engine.ocr.tesseract import TesseractOCRPlugin
from docuwing_engine.plugins.registry import PluginCategory, PluginManifest


class ImageParserPlugin(ParserPlugin):
    """Parses image files (PNG, JPEG, TIFF) via OCR."""

    MANIFEST = PluginManifest(
        name="image_parser",
        category=PluginCategory.PARSER,
        description="OCR-based parser for image files",
        mime_types=["image/png", "image/jpeg", "image/tiff"],
    )

    def __init__(self, ocr_provider: OCRProviderPlugin | None = None) -> None:
        self.ocr_provider = ocr_provider or TesseractOCRPlugin()

    def initialize(self, config: dict[str, Any] | None = None) -> None:
        pass

    async def parse(self, document: Document, stream: io.BytesIO) -> DocumentIR:
        img_bytes = stream.read()
        ocr_res = await self.ocr_provider.recognize(img_bytes)

        blocks: list[Block] = [
            TextBlock(
                text=ocr_b.text,
                bbox=ocr_b.bbox,
                source_ocr=True,
                ocr_confidence=ocr_b.confidence,
            )
            for ocr_b in ocr_res.blocks
        ]

        root_section = Section(blocks=blocks)
        return DocumentIR(
            document_id=document.id,
            pages=1,
            sections=[root_section],
        )
