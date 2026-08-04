"""Tests for OCR Providers and Upload Security Wrapper."""

from __future__ import annotations

import io
import zipfile

import pytest
from PIL import Image, ImageDraw

from docuwing_engine.domain.entities import Document, SourceFormat
from docuwing_engine.ingestion.security import (
    EICAR_SIGNATURE,
    SecurityValidationError,
    UploadSecurityWrapper,
)
from docuwing_engine.ocr.paddle import PaddleOCRPlugin
from docuwing_engine.ocr.tesseract import TesseractOCRPlugin
from docuwing_engine.parsers.image import ImageParserPlugin


@pytest.fixture
def sample_ocr_image_stream() -> io.BytesIO:
    image = Image.new("RGB", (300, 100), color=(255, 255, 255))
    draw = ImageDraw.Draw(image)
    draw.text((10, 10), "Docuwing OCR Test", fill=(0, 0, 0))
    stream = io.BytesIO()
    image.save(stream, format="PNG")
    stream.seek(0)
    return stream


@pytest.mark.asyncio
async def test_tesseract_ocr_provider(sample_ocr_image_stream):
    ocr = TesseractOCRPlugin()
    res = await ocr.recognize(sample_ocr_image_stream)
    assert res is not None
    assert isinstance(res.full_text, str)


@pytest.mark.asyncio
async def test_paddle_ocr_fallback(sample_ocr_image_stream):
    ocr = PaddleOCRPlugin()
    res = await ocr.recognize(sample_ocr_image_stream)
    assert res is not None


@pytest.mark.asyncio
async def test_image_parser_plugin(sample_ocr_image_stream):
    doc = Document(workspace="ws-test", filename="test.png", source_format=SourceFormat.IMAGE)
    parser = ImageParserPlugin()
    ir = await parser.parse(doc, sample_ocr_image_stream)
    assert ir is not None
    assert ir.pages == 1
    assert len(ir.sections) == 1


def test_upload_security_eicar_rejection():
    sec = UploadSecurityWrapper()
    bad_stream = io.BytesIO(EICAR_SIGNATURE)
    with pytest.raises(SecurityValidationError, match="Malware signature detected"):
        sec.validate_and_read(bad_stream, "test.txt")


def test_upload_security_size_limit():
    sec = UploadSecurityWrapper(max_bytes=100)
    oversized = io.BytesIO(b"A" * 150)
    with pytest.raises(SecurityValidationError, match="exceeds maximum allowed size"):
        sec.validate_and_read(oversized, "huge.txt")


def test_upload_security_zip_bomb_detection():
    sec = UploadSecurityWrapper(max_decompression_ratio=5.0)

    zip_bytes = io.BytesIO()
    with zipfile.ZipFile(zip_bytes, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("bomb.txt", b"0" * 100000)  # High compression ratio

    zip_bytes.seek(0)
    with pytest.raises(SecurityValidationError, match="Zip bomb detected"):
        sec.validate_and_read(zip_bytes, "suspicious.xlsx")
