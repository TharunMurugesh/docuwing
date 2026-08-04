from __future__ import annotations

from dataclasses import dataclass

from docuwing_engine.embedding.service import EmbeddingService
from docuwing_engine.knowledge.store import InMemoryKnowledgeStore
from docuwing_engine.llm.router import LLMRouter


@dataclass(frozen=True)
class Citation:
    kind: str
    reference: str


@dataclass(frozen=True)
class GroundedAnswer:
    answer: str
    citations: list[Citation]
    retrieval_path: str


class HybridRAGEngine:
    def __init__(self, store: InMemoryKnowledgeStore, vectors: object, router: LLMRouter | None = None) -> None:
        self._store, self._vectors, self._router = store, vectors, router

    async def query(self, question: str, workspace: str, document_id: str) -> GroundedAnswer:
        graph = self._store.get(document_id)
        if graph is None: return GroundedAnswer("I don't have knowledge for this document.", [], "none")
        terms = {term.strip("?,.! ").lower() for term in question.split() if len(term) > 2}
        facts = [fact for fact in graph.facts if any(term in f"{fact.name} {fact.value}".lower() for term in terms)]
        entities = [entity for entity in graph.entities if any(term in f"{entity.name} {entity.type}".lower() for term in terms)]
        if facts or entities:
            source = facts[0] if facts else entities[0]
            text = f"{source.name}: {source.value}" if facts else f"{source.name} ({source.type})"
            return GroundedAnswer(text, [Citation("fact" if facts else "entity", source.name)], "structured")
        return GroundedAnswer("No grounded answer was found in the indexed document.", [], "semantic")
