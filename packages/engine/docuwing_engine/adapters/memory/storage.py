"""In-memory storage provider."""

from __future__ import annotations

from docuwing_engine.interfaces.repositories import StorageProvider


class InMemoryStorageProvider(StorageProvider):
    def __init__(self) -> None:
        self.blobs: dict[str, bytes] = {}
        self.content_types: dict[str, str] = {}

    async def upload(self, key: str, data: bytes, content_type: str = "") -> str:
        self.blobs[key] = data
        self.content_types[key] = content_type
        return key

    async def download(self, key: str) -> bytes:
        if key not in self.blobs:
            raise FileNotFoundError(f"Blob not found: {key}")
        return self.blobs[key]

    async def delete(self, key: str) -> bool:
        if key in self.blobs:
            del self.blobs[key]
            del self.content_types[key]
            return True
        return False

    async def exists(self, key: str) -> bool:
        return key in self.blobs
