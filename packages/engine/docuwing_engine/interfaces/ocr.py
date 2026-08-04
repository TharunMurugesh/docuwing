"""OCR Provider interface and data types."""

from __future__ import annotations

import io
from abc import abstractmethod

from pydantic import BaseModel, Field

from docuwing_engine.domain.entities import BoundingBox
from docuwing_engine.plugins.sdk import PluginBase


class OCRBlock(BaseModel):
    """A single recognized line or block of text from OCR."""

    text: str
    confidence: float = Field(ge=0.0, le=1.0)
    bbox: BoundingBox | None = None


class OCRResult(BaseModel):
    """Complete result from OCR processing of an image."""

    blocks: list[OCRBlock] = Field(default_factory=list)
    full_text: str = ""
    language: str = "en"


class OCRProviderPlugin(PluginBase):
    """Abstract protocol for OCR engine plugins."""

    @abstractmethod
    async def recognize(self, image_bytes: io.BytesIO | bytes) -> OCRResult:
        """Recognize text in an image stream or raw bytes."""
        raise NotImplementedError
