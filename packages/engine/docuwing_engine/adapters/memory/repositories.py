"""In-memory repository adapters."""

from __future__ import annotations

from typing import Any

from docuwing_engine.domain.entities import Document, ExtractionResult, Schema
from docuwing_engine.interfaces.repositories import (
    DocumentRepository,
    ExtractionResultRepository,
    KnowledgeGraphRepository,
    PromptRepository,
    RepositoryBundle,
    SchemaRepository,
    StorageProvider,
    WorkflowRepository,
)


class InMemoryDocumentRepository(DocumentRepository):
    def __init__(self) -> None:
        self.docs: dict[str, Document] = {}

    async def save(self, document: Document) -> Document:
        self.docs[document.id] = document
        return document

    async def get(self, document_id: str) -> Document | None:
        return self.docs.get(document_id)

    async def get_by_workspace(
        self, workspace: str, limit: int = 100, offset: int = 0
    ) -> list[Document]:
        matches = [d for d in self.docs.values() if d.workspace == workspace]
        return matches[offset : offset + limit]

    async def delete(self, document_id: str) -> bool:
        if document_id in self.docs:
            del self.docs[document_id]
            return True
        return False

    async def update_status(self, document_id: str, status: str) -> Document | None:
        if doc := self.docs.get(document_id):
            doc.status = status  # type: ignore
            return doc
        return None


class InMemorySchemaRepository(SchemaRepository):
    def __init__(self) -> None:
        self.schemas: dict[str, Schema] = {}

    async def save(self, schema: Schema) -> Schema:
        self.schemas[schema.id] = schema
        return schema

    async def get(self, schema_id: str) -> Schema | None:
        return self.schemas.get(schema_id)

    async def get_by_workspace(
        self, workspace: str, limit: int = 100, offset: int = 0
    ) -> list[Schema]:
        matches = [s for s in self.schemas.values() if s.workspace == workspace]
        return matches[offset : offset + limit]

    async def get_version(self, schema_id: str, version: int) -> Schema | None:
        # Simplistic versioning for memory adapter
        schema = self.schemas.get(schema_id)
        if schema and schema.version == version:
            return schema
        return None

    async def delete(self, schema_id: str) -> bool:
        if schema_id in self.schemas:
            del self.schemas[schema_id]
            return True
        return False


class InMemoryExtractionRepository(ExtractionResultRepository):
    def __init__(self) -> None:
        self.results: dict[str, ExtractionResult] = {}

    async def save(self, result: ExtractionResult) -> ExtractionResult:
        self.results[result.id] = result
        return result

    async def get(self, result_id: str) -> ExtractionResult | None:
        return self.results.get(result_id)

    async def get_by_document(
        self, document_id: str, schema_id: str | None = None
    ) -> list[ExtractionResult]:
        matches = [r for r in self.results.values() if r.document_id == document_id]
        if schema_id:
            matches = [r for r in matches if r.schema_id == schema_id]
        return matches


class InMemoryWorkflowRepository(WorkflowRepository):
    def __init__(self) -> None:
        self.defs: dict[str, Any] = {}
        self.runs: dict[str, Any] = {}
        self.step_runs: dict[str, Any] = {}
        self.events: list[Any] = []

    async def save_definition(self, definition: Any) -> Any:
        self.defs[definition.id] = definition
        return definition

    async def get_definition(self, definition_id: str) -> Any | None:
        return self.defs.get(definition_id)

    async def save_run(self, run: Any) -> Any:
        self.runs[run.id] = run
        return run

    async def get_run(self, run_id: str) -> Any | None:
        return self.runs.get(run_id)

    async def update_run(self, run: Any) -> Any:
        self.runs[run.id] = run
        return run

    async def save_step_run(self, step_run: Any) -> Any:
        self.step_runs[step_run.id] = step_run
        return step_run

    async def get_step_runs(self, run_id: str) -> list[Any]:
        return [sr for sr in self.step_runs.values() if sr.run_id == run_id]

    async def update_step_run(self, step_run: Any) -> Any:
        self.step_runs[step_run.id] = step_run
        return step_run

    async def save_event(self, event: Any) -> Any:
        self.events.append(event)
        return event

    async def get_events(self, run_id: str | None = None, limit: int = 100) -> list[Any]:
        # Basic filtering logic not implemented here
        return self.events[-limit:]

    async def count_active_runs(self, workspace: str) -> int:
        return len(
            [
                r
                for r in self.runs.values()
                if r.workspace == workspace and r.status in ("pending", "running")
            ]
        )


class InMemoryPromptRepository(PromptRepository):
    def __init__(self) -> None:
        self.pointers: dict[tuple[str, str], str] = {}

    async def get_active_pointer(self, task_type: str, model_id: str) -> str | None:
        return self.pointers.get((task_type, model_id))

    async def set_active_pointer(self, task_type: str, model_id: str, version: str) -> None:
        self.pointers[(task_type, model_id)] = version


class InMemoryKnowledgeGraphRepository(KnowledgeGraphRepository):
    pass


def InMemoryRepositoryBundle(storage: StorageProvider) -> RepositoryBundle:
    """Create a fully in-memory repository bundle."""
    return RepositoryBundle(
        documents=InMemoryDocumentRepository(),
        schemas=InMemorySchemaRepository(),
        extractions=InMemoryExtractionRepository(),
        knowledge_graphs=InMemoryKnowledgeGraphRepository(),
        workflows=InMemoryWorkflowRepository(),
        prompts=InMemoryPromptRepository(),
        storage=storage,
    )
