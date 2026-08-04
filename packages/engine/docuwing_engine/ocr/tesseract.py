"""Tesseract OCR Provider Plugin (CPU fallback)."""

from __future__ import annotations

import io
from typing import Any

import pytesseract
from PIL import Image

from docuwing_engine.domain.entities import BoundingBox
from docuwing_engine.interfaces.ocr import OCRBlock, OCRProviderPlugin, OCRResult
from docuwing_engine.plugins.registry import PluginCategory, PluginManifest


class TesseractOCRPlugin(OCRProviderPlugin):
    """CPU-only OCR provider using Tesseract."""

    MANIFEST = PluginManifest(
        name="tesseract_ocr",
        category=PluginCategory.OCR_PROVIDER,
        description="Tesseract OCR engine plugin (CPU fallback)",
        mime_types=["image/png", "image/jpeg", "image/tiff"],
    )

    def initialize(self, config: dict[str, Any] | None = None) -> None:
        pass

    async def recognize(self, image_bytes: io.BytesIO | bytes) -> OCRResult:
        if isinstance(image_bytes, bytes):
            image_bytes = io.BytesIO(image_bytes)

        image = Image.open(image_bytes)
        width, height = image.size

        # Fetch detailed data with bounding boxes and confidence
        try:
            data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
            blocks = []
            full_text_parts = []

            n_boxes = len(data["text"])
            for i in range(n_boxes):
                text = data["text"][i].strip()
                conf_val = float(data["conf"][i])
                if text and conf_val >= 0:
                    x, y, w, h = (
                        data["left"][i],
                        data["top"][i],
                        data["width"][i],
                        data["height"][i],
                    )
                    bbox = BoundingBox(
                        x0=x / width if width else 0.0,
                        y0=y / height if height else 0.0,
                        x1=(x + w) / width if width else 0.0,
                        y1=(y + h) / height if height else 0.0,
                        page=0,
                    )
                    conf = max(0.0, min(1.0, conf_val / 100.0))
                    blocks.append(OCRBlock(text=text, confidence=conf, bbox=bbox))
                    full_text_parts.append(text)

            return OCRResult(
                blocks=blocks,
                full_text=" ".join(full_text_parts),
                language="en",
            )
        except Exception:
            # Fallback if tesseract binary is unavailable in environment
            text = pytesseract.image_to_string(image).strip()
            block = OCRBlock(text=text, confidence=0.8)
            return OCRResult(blocks=[block], full_text=text, language="en")
