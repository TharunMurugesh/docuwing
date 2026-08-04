"""Tests for Layout Analyzer."""

from __future__ import annotations

import pytest

from docuwing_engine.domain.entities import BoundingBox
from docuwing_engine.ir.types import DocumentIR, Section, TextBlock
from docuwing_engine.layout.analyzer import StandardLayoutAnalyzer


@pytest.mark.asyncio
async def test_layout_analyzer_multi_column_sorting():
    # Right column block (x0=0.6, y0=0.1)
    b_right = TextBlock(
        text="Right Column Text",
        bbox=BoundingBox(x0=0.6, y0=0.1, x1=0.9, y1=0.2, page=0),
    )
    # Left column block (x0=0.1, y0=0.5)
    b_left = TextBlock(
        text="Left Column Text",
        bbox=BoundingBox(x0=0.1, y0=0.5, x1=0.4, y1=0.6, page=0),
    )

    # Naive reading order (Right block appears first in list)
    ir = DocumentIR(
        document_id="doc-123",
        pages=1,
        sections=[Section(blocks=[b_right, b_left])],
    )

    analyzer = StandardLayoutAnalyzer()
    refined_ir = await analyzer.analyze(ir)

    # After layout analysis, left column block must come before right column block
    sorted_blocks = refined_ir.sections[0].blocks
    assert sorted_blocks[0].text == "Left Column Text"
    assert sorted_blocks[1].text == "Right Column Text"


@pytest.mark.asyncio
async def test_layout_analyzer_section_hierarchy():
    h1 = TextBlock(text="1. Introduction", role="heading")
    p1 = TextBlock(text="Intro paragraph content.", role="paragraph")
    h2 = TextBlock(text="2. Methodology", role="heading")
    p2 = TextBlock(text="Methodology paragraph content.", role="paragraph")

    ir = DocumentIR(
        document_id="doc-456",
        pages=1,
        sections=[Section(blocks=[h1, p1, h2, p2])],
    )

    analyzer = StandardLayoutAnalyzer()
    refined_ir = await analyzer.analyze(ir)

    assert len(refined_ir.sections) == 2
    assert refined_ir.sections[0].title == "1. Introduction"
    assert refined_ir.sections[0].blocks[0].text == "Intro paragraph content."
    assert refined_ir.sections[1].title == "2. Methodology"
    assert refined_ir.sections[1].blocks[0].text == "Methodology paragraph content."


@pytest.mark.asyncio
async def test_layout_analyzer_ocr_fragment_merging():
    b1 = TextBlock(
        text="This is line one",
        source_ocr=True,
        ocr_confidence=0.9,
        bbox=BoundingBox(x0=0.1, y0=0.1, x1=0.5, y1=0.15, page=0),
    )
    b2 = TextBlock(
        text="of the same paragraph.",
        source_ocr=True,
        ocr_confidence=0.85,
        bbox=BoundingBox(x0=0.1, y0=0.16, x1=0.6, y1=0.20, page=0),
    )

    ir = DocumentIR(
        document_id="doc-789",
        pages=1,
        sections=[Section(blocks=[b1, b2])],
    )

    analyzer = StandardLayoutAnalyzer()
    refined_ir = await analyzer.analyze(ir)

    merged_blocks = refined_ir.sections[0].blocks
    assert len(merged_blocks) == 1
    assert merged_blocks[0].text == "This is line one of the same paragraph."
