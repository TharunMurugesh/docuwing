"""Filesystem-backed repository adapters (JSON)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import TypeVar

import aiofiles

from docuwing_engine.adapters.memory.repositories import (
    InMemoryExtractionRepository,
    InMemoryKnowledgeGraphRepository,
    InMemoryPromptRepository,
    InMemorySchemaRepository,
    InMemoryWorkflowRepository,
)
from docuwing_engine.domain.entities import Document
from docuwing_engine.interfaces.repositories import (
    DocumentRepository,
    RepositoryBundle,
    StorageProvider,
)

T = TypeVar("T")


class FilesystemDocumentRepository(DocumentRepository):
    """A minimal JSON-file-backed document repository for CLI standalone use."""

    def __init__(self, root_dir: str = "/tmp/docuwing-db/documents") -> None:
        self.root = Path(root_dir)
        self.root.mkdir(parents=True, exist_ok=True)

    async def _read(self, path: Path) -> Document | None:
        if not path.exists():
            return None
        async with aiofiles.open(path, encoding="utf-8") as f:
            data = json.loads(await f.read())
            return Document(**data)

    async def _write(self, document: Document) -> Document:
        path = self.root / f"{document.id}.json"
        async with aiofiles.open(path, "w", encoding="utf-8") as f:
            await f.write(document.model_dump_json(indent=2))
        return document

    async def save(self, document: Document) -> Document:
        return await self._write(document)

    async def get(self, document_id: str) -> Document | None:
        return await self._read(self.root / f"{document_id}.json")

    async def get_by_workspace(
        self, workspace: str, limit: int = 100, offset: int = 0
    ) -> list[Document]:
        docs = []
        for path in self.root.glob("*.json"):
            doc = await self._read(path)
            if doc and doc.workspace == workspace:
                docs.append(doc)
        return docs[offset : offset + limit]

    async def delete(self, document_id: str) -> bool:
        path = self.root / f"{document_id}.json"
        if path.exists():
            path.unlink()
            return True
        return False

    async def update_status(self, document_id: str, status: str) -> Document | None:
        doc = await self.get(document_id)
        if doc:
            doc.status = status  # type: ignore
            await self._write(doc)
        return doc


def FilesystemRepositoryBundle(
    storage: StorageProvider, root_dir: str = "/tmp/docuwing-db"
) -> RepositoryBundle:
    """Create a JSON-backed repository bundle.
    For Phase 1 MVP, mostly falls back to in-memory for non-document types.
    """
    return RepositoryBundle(
        documents=FilesystemDocumentRepository(f"{root_dir}/documents"),
        schemas=InMemorySchemaRepository(),
        extractions=InMemoryExtractionRepository(),
        knowledge_graphs=InMemoryKnowledgeGraphRepository(),
        workflows=InMemoryWorkflowRepository(),
        prompts=InMemoryPromptRepository(),
        storage=storage,
    )
