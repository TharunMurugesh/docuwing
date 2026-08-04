from __future__ import annotations

from typing import Any

from docuwing_engine.interfaces.output_generator import OutputArtifact, OutputGenerator, UnsupportedOutputError
from docuwing_engine.knowledge.domain import KnowledgeGraph
from docuwing_engine.output.generators import BUILTIN_GENERATORS


class OutputEngineFacade:
    def __init__(self, generators: dict[str, type[OutputGenerator]] | None = None) -> None: self._generators = generators or BUILTIN_GENERATORS
    async def generate(self, graph: KnowledgeGraph, format: str, options: dict[str, Any] | None = None) -> OutputArtifact:
        generator = self._generators.get(format)
        if generator is None: raise UnsupportedOutputError(f"Unknown output format: {format}")
        instance = generator()
        if not instance.supports(graph): raise UnsupportedOutputError(f"{format} is unsupported by this document's knowledge graph")
        dependencies = {name: await self.generate(graph, name, options) for name in instance.composes}
        return await instance.generate(graph, options or {}, dependencies)
