from __future__ import annotations

from docuwing_engine.domain.entities import ExtractionResult, ProjectionHint, Schema
from docuwing_engine.knowledge.domain import Entity, Fact, KnowledgeGraph, Relationship, SemanticTable
from docuwing_engine.knowledge.resolvers.default import DefaultEntityResolver


class KnowledgeBuilder:
    def __init__(self, resolver: DefaultEntityResolver | None = None) -> None:
        self._resolver = resolver or DefaultEntityResolver()

    def build(self, result: ExtractionResult, schema: Schema) -> KnowledgeGraph:
        graph = KnowledgeGraph(workspace=result.workspace, document_id=result.document_id)
        definitions = {field.name: field for field in schema.fields}
        entity_fields: dict[str, Entity] = {}
        for extracted in result.fields:
            definition = definitions[extracted.field_name]
            if extracted.value is None: continue
            if definition.projection_hint == ProjectionHint.ENTITY:
                entity = Entity(type=definition.name, name=str(extracted.value), confidence=extracted.confidence, provenance=extracted.provenance, validation_state=extracted.validation_state)
                entity = self._resolver.resolve(entity, graph.entities)
                if entity not in graph.entities:
                    graph.entities.append(entity)
                entity_fields[definition.name] = entity
            elif definition.projection_hint == ProjectionHint.TABLE:
                graph.tables.append(SemanticTable(name=definition.name, rows=extracted.value if isinstance(extracted.value, list) else [{"value": extracted.value}]))
            elif definition.projection_hint == ProjectionHint.FACT:
                graph.facts.append(Fact(name=definition.name, value=extracted.value, confidence=extracted.confidence, provenance=extracted.provenance, validation_state=extracted.validation_state))
        for extracted in result.fields:
            definition = definitions[extracted.field_name]
            if definition.projection_hint == ProjectionHint.ATTRIBUTE_OF and definition.attribute_of in entity_fields:
                entity_fields[definition.attribute_of].attributes[definition.name] = extracted.value
            if definition.field_type.value == "relationship" and isinstance(extracted.value, (list, tuple)) and len(extracted.value) == 2:
                left, right = (entity_fields.get(str(x)) for x in extracted.value)
                if left and right: graph.relationships.append(Relationship(type=definition.name, source_entity_id=left.id, target_entity_id=right.id, confidence=extracted.confidence, provenance=extracted.provenance))
        return graph
