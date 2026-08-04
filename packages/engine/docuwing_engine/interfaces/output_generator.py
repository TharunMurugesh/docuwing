from __future__ import annotations

from abc import abstractmethod
from typing import Any

from docuwing_engine.knowledge.domain import KnowledgeGraph
from docuwing_engine.plugins.sdk import PluginBase


class UnsupportedOutputError(ValueError): pass


class OutputGenerator(PluginBase):
    id: str
    version: str = "v1"
    output_format: str
    composes: list[str] = []
    @abstractmethod
    def supports(self, graph: KnowledgeGraph) -> bool: ...
    @abstractmethod
    async def generate(self, graph: KnowledgeGraph, options: dict[str, Any], dependencies: dict[str, "OutputArtifact"]) -> "OutputArtifact": ...


class OutputArtifact:
    def __init__(self, format: str, content: str | bytes, mime_type: str) -> None:
        self.format, self.content, self.mime_type = format, content, mime_type
