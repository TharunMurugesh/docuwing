"""PaddleOCR Provider Plugin (GPU-preferred)."""

from __future__ import annotations

import io
from typing import Any

from PIL import Image

from docuwing_engine.interfaces.ocr import OCRBlock, OCRProviderPlugin, OCRResult
from docuwing_engine.plugins.registry import PluginCategory, PluginManifest


class PaddleOCRPlugin(OCRProviderPlugin):
    """GPU-preferred OCR provider using PaddleOCR with graceful fallback."""

    MANIFEST = PluginManifest(
        name="paddle_ocr",
        category=PluginCategory.OCR_PROVIDER,
        description="PaddleOCR engine plugin (GPU preferred, multilingual)",
        mime_types=["image/png", "image/jpeg", "image/tiff"],
    )

    def initialize(self, config: dict[str, Any] | None = None) -> None:
        self._paddle: Any = None

    async def recognize(self, image_bytes: io.BytesIO | bytes) -> OCRResult:
        if isinstance(image_bytes, bytes):
            image_bytes = io.BytesIO(image_bytes)

        # Fallback to Tesseract if paddleocr is not installed
        try:
            from paddleocr import PaddleOCR

            if self._paddle is None:
                self._paddle = PaddleOCR(use_angle_cls=True, lang="en", show_log=False)

            Image.open(image_bytes)
            # Run paddle OCR logic if available
            result = self._paddle.ocr(image_bytes.getvalue(), cls=True)
            blocks = []
            full_text_parts = []
            if result and result[0]:
                for line in result[0]:
                    text = line[1][0]
                    conf = float(line[1][1])
                    blocks.append(OCRBlock(text=text, confidence=conf))
                    full_text_parts.append(text)

            return OCRResult(blocks=blocks, full_text=" ".join(full_text_parts), language="en")
        except (ImportError, Exception):
            from docuwing_engine.ocr.tesseract import TesseractOCRPlugin

            fallback = TesseractOCRPlugin()
            return await fallback.recognize(image_bytes)
