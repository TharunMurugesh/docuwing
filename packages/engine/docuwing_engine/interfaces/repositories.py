"""Repository port interfaces (EDS §2.2).

These are the abstract contracts the Engine depends on. Concrete implementations
(in-memory, file-based, Postgres-backed) live in the adapters package.

The Engine never depends on a specific adapter — it programs against these ports.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from docuwing_engine.domain.entities import (
    Document,
    ExtractionResult,
    Schema,
)


class DocumentRepository(ABC):
    """Port for Document persistence operations."""

    @abstractmethod
    async def save(self, document: Document) -> Document:
        """Persist a document (create or update)."""
        ...

    @abstractmethod
    async def get(self, document_id: str) -> Document | None:
        """Retrieve a document by ID."""
        ...

    @abstractmethod
    async def get_by_workspace(
        self, workspace: str, limit: int = 100, offset: int = 0
    ) -> list[Document]:
        """List documents for a workspace."""
        ...

    @abstractmethod
    async def delete(self, document_id: str) -> bool:
        """Delete a document by ID. Returns True if deleted."""
        ...

    @abstractmethod
    async def update_status(self, document_id: str, status: str) -> Document | None:
        """Update a document's processing status."""
        ...


class SchemaRepository(ABC):
    """Port for Schema persistence operations."""

    @abstractmethod
    async def save(self, schema: Schema) -> Schema:
        """Persist a schema (create or update)."""
        ...

    @abstractmethod
    async def get(self, schema_id: str) -> Schema | None:
        """Retrieve a schema by ID."""
        ...

    @abstractmethod
    async def get_by_workspace(
        self, workspace: str, limit: int = 100, offset: int = 0
    ) -> list[Schema]:
        """List schemas for a workspace."""
        ...

    @abstractmethod
    async def get_version(self, schema_id: str, version: int) -> Schema | None:
        """Retrieve a specific version of a schema."""
        ...

    @abstractmethod
    async def delete(self, schema_id: str) -> bool:
        """Delete a schema by ID."""
        ...


class ExtractionResultRepository(ABC):
    """Port for ExtractionResult persistence."""

    @abstractmethod
    async def save(self, result: ExtractionResult) -> ExtractionResult:
        """Persist an extraction result."""
        ...

    @abstractmethod
    async def get(self, result_id: str) -> ExtractionResult | None:
        """Retrieve an extraction result by ID."""
        ...

    @abstractmethod
    async def get_by_document(
        self, document_id: str, schema_id: str | None = None
    ) -> list[ExtractionResult]:
        """Get extraction results for a document, optionally filtered by schema."""
        ...


class KnowledgeGraphRepository(ABC):
    """Port for Knowledge Graph persistence (Phase 8).

    Defined now as an empty interface — methods added when KnowledgeGraph
    domain types are built.
    """

    pass


class WorkflowRepository(ABC):
    """Port for Workflow persistence operations."""

    @abstractmethod
    async def save_definition(self, definition: Any) -> Any:
        """Persist a workflow definition."""
        ...

    @abstractmethod
    async def get_definition(self, definition_id: str) -> Any | None:
        """Retrieve a workflow definition."""
        ...

    @abstractmethod
    async def save_run(self, run: Any) -> Any:
        """Persist a workflow run."""
        ...

    @abstractmethod
    async def get_run(self, run_id: str) -> Any | None:
        """Retrieve a workflow run by ID."""
        ...

    @abstractmethod
    async def update_run(self, run: Any) -> Any:
        """Update a workflow run."""
        ...

    @abstractmethod
    async def save_step_run(self, step_run: Any) -> Any:
        """Persist a workflow step run."""
        ...

    @abstractmethod
    async def get_step_runs(self, run_id: str) -> list[Any]:
        """Get all step runs for a workflow run."""
        ...

    @abstractmethod
    async def update_step_run(self, step_run: Any) -> Any:
        """Update a workflow step run."""
        ...

    @abstractmethod
    async def save_event(self, event: Any) -> Any:
        """Persist an engine event."""
        ...

    @abstractmethod
    async def get_events(self, run_id: str | None = None, limit: int = 100) -> list[Any]:
        """Get engine events, optionally filtered by run ID."""
        ...

    @abstractmethod
    async def count_active_runs(self, workspace: str) -> int:
        """Count currently active (non-terminal) workflow runs for a workspace."""
        ...


class PromptRepository(ABC):
    """Port for prompt artifact persistence."""

    @abstractmethod
    async def get_active_pointer(self, task_type: str, model_id: str) -> str | None:
        """Get the active prompt version for a task/model combination."""
        ...

    @abstractmethod
    async def set_active_pointer(self, task_type: str, model_id: str, version: str) -> None:
        """Set the active prompt version for a task/model combination."""
        ...


class StorageProvider(ABC):
    """Port for object storage (file blobs)."""

    @abstractmethod
    async def upload(self, key: str, data: bytes, content_type: str = "") -> str:
        """Upload a file blob. Returns the storage key/URL."""
        ...

    @abstractmethod
    async def download(self, key: str) -> bytes:
        """Download a file blob by key."""
        ...

    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Delete a file blob. Returns True if deleted."""
        ...

    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Check if a file exists."""
        ...


class RepositoryBundle:
    """Aggregate of all repository ports — passed to DocuwingEngine at construction.

    This is the single point of adapter injection. The Engine receives
    a RepositoryBundle and never constructs adapters itself.
    """

    def __init__(
        self,
        documents: DocumentRepository,
        schemas: SchemaRepository,
        extractions: ExtractionResultRepository,
        knowledge_graphs: KnowledgeGraphRepository,
        workflows: WorkflowRepository,
        prompts: PromptRepository,
        storage: StorageProvider,
    ) -> None:
        self.documents = documents
        self.schemas = schemas
        self.extractions = extractions
        self.knowledge_graphs = knowledge_graphs
        self.workflows = workflows
        self.prompts = prompts
        self.storage = storage
