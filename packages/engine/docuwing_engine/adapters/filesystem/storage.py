"""Filesystem-backed object storage provider."""

from __future__ import annotations

import os
from pathlib import Path

import aiofiles

from docuwing_engine.interfaces.repositories import StorageProvider


class FilesystemStorageProvider(StorageProvider):
    def __init__(self, root_dir: str = "/tmp/docuwing-storage") -> None:
        self.root = Path(root_dir)
        self.root.mkdir(parents=True, exist_ok=True)

    def _get_path(self, key: str) -> Path:
        # Prevent directory traversal
        clean_key = os.path.normpath(key).lstrip("/")
        if clean_key.startswith(".."):
            raise ValueError("Invalid storage key")
        return self.root / clean_key

    async def upload(self, key: str, data: bytes, content_type: str = "") -> str:
        path = self._get_path(key)
        path.parent.mkdir(parents=True, exist_ok=True)
        async with aiofiles.open(path, "wb") as f:
            await f.write(data)
        return key

    async def download(self, key: str) -> bytes:
        path = self._get_path(key)
        if not path.exists():
            raise FileNotFoundError(f"Blob not found: {key}")
        async with aiofiles.open(path, "rb") as f:
            return bytes(await f.read())

    async def delete(self, key: str) -> bool:
        path = self._get_path(key)
        if path.exists():
            path.unlink()
            return True
        return False

    async def exists(self, key: str) -> bool:
        return self._get_path(key).exists()
