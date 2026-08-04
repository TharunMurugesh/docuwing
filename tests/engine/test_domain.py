"""Tests for domain entities."""

import pytest

from docuwing_engine.domain.entities import (
    BoundingBox,
    ConfidenceScore,
    FieldDefinition,
    FieldType,
    ProjectionHint,
    Span,
)


def test_confidence_score_composite():
    score = ConfidenceScore(extraction=0.9, validation=0.5, span_quality=1.0)
    # 0.9 * 0.5 = 0.45, 0.5 * 0.3 = 0.15, 1.0 * 0.2 = 0.2
    # 0.45 + 0.15 + 0.20 = 0.80
    assert score.composite == 0.80


def test_field_definition_projection_hint():
    field = FieldDefinition(
        name="invoice_total",
        field_type=FieldType.CURRENCY,
        projection_hint=ProjectionHint.FACT,
    )
    assert field.projection_hint == ProjectionHint.FACT


def test_bounding_box_validation():
    # Invalid box (x0 > 1.0)
    with pytest.raises(ValueError):
        BoundingBox(x0=1.5, y0=0.0, x1=0.0, y1=0.0, page=1)


def test_span_creation():
    span = Span(text="1,000", start_offset=0, end_offset=5, block_id="b1")
    assert span.text == "1,000"
    assert span.bbox is None
