from __future__ import annotations

from docuwing_engine.knowledge.domain import Entity, KnowledgeGraph, Relationship, SemanticTable


class InMemoryKnowledgeStore:
    def __init__(self) -> None: self._graphs: dict[str, KnowledgeGraph] = {}
    def save(self, graph: KnowledgeGraph) -> KnowledgeGraph: self._graphs[graph.document_id] = graph; return graph
    def get(self, document_id: str) -> KnowledgeGraph | None: return self._graphs.get(document_id)
    def find_entities(self, document_id: str, entity_type: str | None = None) -> list[Entity]:
        graph = self.get(document_id); return [] if not graph else [e for e in graph.entities if entity_type is None or e.type == entity_type]
    def find_relationships(self, document_id: str) -> list[Relationship]: return (self.get(document_id) or KnowledgeGraph(workspace="", document_id=document_id)).relationships
    def get_table(self, document_id: str, name: str) -> SemanticTable | None: return next((t for t in (self.get(document_id) or KnowledgeGraph(workspace="", document_id=document_id)).tables if t.name == name), None)
    def search(self, document_id: str, query: str) -> list[Entity]: return [e for e in self.find_entities(document_id) if query.lower() in (e.name + " " + str(e.attributes)).lower()]
