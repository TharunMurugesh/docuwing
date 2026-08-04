from __future__ import annotations

import uuid
from typing import Any

from pydantic import BaseModel, Field

from docuwing_engine.domain.entities import ConfidenceScore, Provenance, ValidationState


class Entity(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: str
    name: str
    attributes: dict[str, Any] = Field(default_factory=dict)
    confidence: ConfidenceScore | None = None
    provenance: Provenance | None = None
    validation_state: ValidationState = ValidationState.PENDING


class Relationship(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: str
    source_entity_id: str
    target_entity_id: str
    confidence: ConfidenceScore | None = None
    provenance: Provenance | None = None


class Fact(BaseModel):
    name: str
    value: Any
    confidence: ConfidenceScore | None = None
    provenance: Provenance | None = None
    validation_state: ValidationState = ValidationState.PENDING


class SemanticTable(BaseModel):
    name: str
    rows: list[dict[str, Any]] = Field(default_factory=list)


class KnowledgeGraph(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    workspace: str
    document_id: str
    entities: list[Entity] = Field(default_factory=list)
    relationships: list[Relationship] = Field(default_factory=list)
    facts: list[Fact] = Field(default_factory=list)
    tables: list[SemanticTable] = Field(default_factory=list)
