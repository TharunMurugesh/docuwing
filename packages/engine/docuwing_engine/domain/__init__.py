"""Engine domain layer — entities, value objects, and aggregates.

Per EDS §2.1, these are the core domain types the entire Engine is built around.
All types are immutable (frozen dataclasses) to enforce value-object semantics.
"""

from docuwing_engine.domain.entities import (
    BoundingBox,
    ConfidenceScore,
    Document,
    DocumentStatus,
    ExtractedField,
    ExtractionResult,
    FieldDefinition,
    FieldType,
    Provenance,
    ProvenanceSource,
    Schema,
    Span,
    ValidationState,
    Workspace,
)

__all__ = [
    "BoundingBox",
    "ConfidenceScore",
    "Document",
    "DocumentStatus",
    "ExtractionResult",
    "ExtractedField",
    "FieldDefinition",
    "FieldType",
    "Provenance",
    "ProvenanceSource",
    "Schema",
    "Span",
    "ValidationState",
    "Workspace",
]
