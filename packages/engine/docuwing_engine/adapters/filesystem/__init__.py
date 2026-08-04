"""Filesystem adapters for standalone Engine execution."""

from docuwing_engine.adapters.filesystem.repositories import FilesystemRepositoryBundle
from docuwing_engine.adapters.filesystem.storage import FilesystemStorageProvider

__all__ = ["FilesystemRepositoryBundle", "FilesystemStorageProvider"]
