"""Core domain entities and value objects (EDS §2.1).

All types are either frozen Pydantic models (for validation) or frozen
dataclasses (for lightweight value objects). The domain layer has zero
infrastructure dependencies.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

# ── Enumerations ──────────────────────────────────────────────────────────────


class DocumentStatus(str, Enum):
    """Document processing lifecycle states."""

    PENDING = "pending"
    PARSING = "parsing"
    PARSED = "parsed"
    ANALYZING = "analyzing"
    ANALYZED = "analyzed"
    EXTRACTING = "extracting"
    EXTRACTED = "extracted"
    VALIDATING = "validating"
    VALIDATED = "validated"
    READY = "ready"
    FAILED = "failed"


class SourceFormat(str, Enum):
    """Supported document source formats."""

    PDF_TEXT = "pdf_text"
    PDF_SCANNED = "pdf_scanned"
    DOCX = "docx"
    XLSX = "xlsx"
    CSV = "csv"
    IMAGE = "image"


class ValidationState(str, Enum):
    """Validation state for extracted fields."""

    PENDING = "pending"
    VALID = "valid"
    INVALID = "invalid"
    NEEDS_REVIEW = "needs_review"
    HUMAN_CONFIRMED = "human_confirmed"


class FieldType(str, Enum):
    """Types for schema field definitions."""

    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    DATE = "date"
    DATETIME = "datetime"
    CURRENCY = "currency"
    ENUM = "enum"
    LIST = "list"
    TABLE = "table"
    RELATIONSHIP = "relationship"


class ProjectionHint(str, Enum):
    """Knowledge Layer projection hints (EDS §4.6)."""

    ENTITY = "entity"
    ATTRIBUTE_OF = "attribute_of"
    TABLE = "table"
    FACT = "fact"


class ProvenanceSource(str, Enum):
    """Origin of a piece of data."""

    PARSER = "parser"
    OCR = "ocr"
    LAYOUT_ANALYSIS = "layout_analysis"

    HUMAN_REVIEW = "human_review"
    RULE_VALIDATION = "rule_validation"


# ── Value Objects ──────────────────────────────────────────────────────────────


class BoundingBox(BaseModel, frozen=True):
    """A rectangular region on a document page.

    Coordinates are normalized to [0.0, 1.0] relative to page dimensions.
    """

    x0: float = Field(ge=0.0, le=1.0, description="Left edge (normalized)")
    y0: float = Field(ge=0.0, le=1.0, description="Top edge (normalized)")
    x1: float = Field(ge=0.0, le=1.0, description="Right edge (normalized)")
    y1: float = Field(ge=0.0, le=1.0, description="Bottom edge (normalized)")
    page: int = Field(ge=0, description="Zero-indexed page number")


class Span(BaseModel, frozen=True):
    """A reference to a specific region of source text in the DocumentIR.

    Used for extraction grounding — every extracted value traces back to
    one or more source spans.
    """

    text: str = Field(description="The source text content")
    start_offset: int = Field(ge=0, description="Character start offset in the block")
    end_offset: int = Field(ge=0, description="Character end offset in the block")
    block_id: str = Field(description="ID of the source Block in the DocumentIR")
    bbox: BoundingBox | None = Field(
        default=None, description="Bounding box in the source document"
    )


class ConfidenceScore(BaseModel, frozen=True):
    """Composite confidence score for an extracted value.

    Combines extraction confidence, validation pass/fail, and programmatic
    span-match quality into a single comparable score.
    """

    extraction: float = Field(ge=0.0, le=1.0, description="Raw extraction confidence")
    validation: float = Field(
        ge=0.0, le=1.0, default=1.0, description="Validation-adjusted confidence"
    )
    span_quality: float = Field(
        ge=0.0, le=1.0, default=1.0, description="Source span match quality"
    )

    @property
    def composite(self) -> float:
        """Weighted composite confidence score."""
        return round(
            self.extraction * 0.5 + self.validation * 0.3 + self.span_quality * 0.2,
            4,
        )


class Provenance(BaseModel, frozen=True):
    """Tracks the origin and audit trail of a piece of data."""

    source: ProvenanceSource
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    model_id: str | None = Field(default=None, description="Model identifier if applicable")
    prompt_version: str | None = Field(default=None, description="Prompt version")
    details: dict[str, Any] = Field(default_factory=dict)


# ── Entities ──────────────────────────────────────────────────────────────────


class Workspace(BaseModel, frozen=True):
    """Workspace identifier — the Engine's unit of tenant isolation.

    The Engine sees workspaces as opaque string IDs. The App layer maps
    these to its own Project/Organization hierarchy (Finding #1 boundary).
    """

    id: str = Field(description="Opaque workspace identifier")
    name: str = Field(default="", description="Human-readable workspace name")


class Document(BaseModel):
    """Document aggregate root.

    Represents a document being processed through the Engine pipeline.
    """

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    workspace: str = Field(description="Workspace this document belongs to")
    filename: str = Field(description="Original filename")
    source_format: SourceFormat = Field(description="Detected/declared source format")
    content_hash: str = Field(default="", description="SHA-256 hash of file content")
    status: DocumentStatus = Field(default=DocumentStatus.PENDING)
    uploaded_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    metadata: dict[str, Any] = Field(default_factory=dict)


class FieldDefinition(BaseModel, frozen=True):
    """Schema field definition — specifies what to extract.

    Includes projection_hint for Knowledge Layer mapping (EDS §4.6),
    set from Phase 6 onward but structurally present from Phase 1.
    """

    name: str = Field(description="Field name (unique within schema)")
    field_type: FieldType = Field(description="Expected value type")
    description: str = Field(default="", description="Human-readable description")
    required: bool = Field(default=False)
    validation_rules: dict[str, Any] = Field(
        default_factory=dict,
        description="Validation rules: regex, min, max, enum_values, etc.",
    )
    projection_hint: ProjectionHint = Field(
        default=ProjectionHint.FACT,
        description="Knowledge Layer projection hint (EDS §4.6)",
    )
    attribute_of: str | None = Field(
        default=None,
        description="Parent entity field name (when projection_hint=attribute_of)",
    )


class Schema(BaseModel):
    """Extraction schema — defines what fields to extract from documents."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    workspace: str = Field(description="Workspace this schema belongs to")
    name: str = Field(description="Human-readable schema name")
    version: int = Field(default=1, ge=1)
    fields: list[FieldDefinition] = Field(default_factory=list)
    description: str = Field(default="")
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class ExtractedField(BaseModel):
    """A single extracted field value with grounding and confidence."""

    field_name: str
    value: Any = None
    confidence: ConfidenceScore = Field(default_factory=lambda: ConfidenceScore(extraction=0.0))
    spans: list[Span] = Field(default_factory=list, description="Source spans for grounding")
    provenance: Provenance | None = None
    validation_state: ValidationState = Field(default=ValidationState.PENDING)
    human_confirmed: bool = Field(default=False)
    review_notes: str = Field(default="")


class ExtractionResult(BaseModel):
    """Result of applying a schema to a document."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    document_id: str
    schema_id: str
    workspace: str
    fields: list[ExtractedField] = Field(default_factory=list)
    review_status: str = Field(default="pending")  # pending | in_review | approved | rejected
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    provenance: Provenance | None = None
