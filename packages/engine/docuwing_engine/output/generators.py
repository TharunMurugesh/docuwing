from __future__ import annotations

import csv
import io
import json
from typing import Any

from docuwing_engine.interfaces.output_generator import OutputArtifact, OutputGenerator
from docuwing_engine.knowledge.domain import KnowledgeGraph


class _Generator(OutputGenerator):
    def supports(self, graph: KnowledgeGraph) -> bool: return True


class Summary(_Generator):
    id = output_format = "summary"
    async def generate(self, graph: KnowledgeGraph, options: dict[str, Any], dependencies: dict[str, OutputArtifact]) -> OutputArtifact:
        facts = "; ".join(f"{fact.name}: {fact.value}" for fact in graph.facts)
        entities = ", ".join(entity.name for entity in graph.entities)
        return OutputArtifact(self.id, f"Document summary\n\nEntities: {entities or 'none'}\nFacts: {facts or 'none'}", "text/markdown")


class Timeline(_Generator):
    id = output_format = "timeline"
    def supports(self, graph: KnowledgeGraph) -> bool: return any("date" in fact.name.lower() for fact in graph.facts)
    async def generate(self, graph: KnowledgeGraph, options: dict[str, Any], dependencies: dict[str, OutputArtifact]) -> OutputArtifact:
        items = [f"- {fact.name}: {fact.value}" for fact in graph.facts if "date" in fact.name.lower()]
        return OutputArtifact(self.id, "\n".join(items), "text/markdown")


class GraphView(_Generator):
    id = output_format = "knowledge_graph_view"
    async def generate(self, graph: KnowledgeGraph, options: dict[str, Any], dependencies: dict[str, OutputArtifact]) -> OutputArtifact:
        return OutputArtifact(self.id, json.dumps(graph.model_dump(), default=str, indent=2), "application/json")


class Mermaid(_Generator):
    id = output_format = "mermaid_diagram"
    async def generate(self, graph: KnowledgeGraph, options: dict[str, Any], dependencies: dict[str, OutputArtifact]) -> OutputArtifact:
        names = {entity.id: entity.name.replace('"', "'") for entity in graph.entities}
        lines = ["graph TD", *[f'  {entity.id.replace("-", "_")}["{entity.name}"]' for entity in graph.entities]]
        lines += [f"  {rel.source_entity_id.replace('-', '_')} -->|{rel.type}| {rel.target_entity_id.replace('-', '_')}" for rel in graph.relationships if rel.source_entity_id in names and rel.target_entity_id in names]
        return OutputArtifact(self.id, "\n".join(lines), "text/vnd.mermaid")


class Chart(_Generator):
    id = output_format = "chart"
    async def generate(self, graph: KnowledgeGraph, options: dict[str, Any], dependencies: dict[str, OutputArtifact]) -> OutputArtifact:
        series = [{"label": f.name, "value": f.value} for f in graph.facts if isinstance(f.value, (int, float))]
        return OutputArtifact(self.id, json.dumps({"type": "bar", "series": series}), "application/json")


class JsonExport(GraphView): id = output_format = "json_export"
class MarkdownExport(Summary): id = output_format = "markdown_export"


class CsvExport(_Generator):
    id = output_format = "csv_export"
    async def generate(self, graph: KnowledgeGraph, options: dict[str, Any], dependencies: dict[str, OutputArtifact]) -> OutputArtifact:
        stream = io.StringIO(); writer = csv.writer(stream); writer.writerow(["name", "value"])
        writer.writerows((fact.name, fact.value) for fact in graph.facts)
        return OutputArtifact(self.id, stream.getvalue(), "text/csv")


class PptxExport(_Generator):
    id = output_format = "pptx_export"; composes = ["summary", "chart", "knowledge_graph_view"]
    async def generate(self, graph: KnowledgeGraph, options: dict[str, Any], dependencies: dict[str, OutputArtifact]) -> OutputArtifact:
        # Portable JSON slide deck descriptor; host can render with python-pptx if desired.
        return OutputArtifact(self.id, json.dumps({"slides": [{"title": key, "content": str(value.content)} for key, value in dependencies.items()]}), "application/vnd.docuwing.pptx+json")


BUILTIN_GENERATORS: dict[str, type[OutputGenerator]] = {c.id: c for c in (Summary, Timeline, GraphView, Mermaid, Chart, JsonExport, MarkdownExport, CsvExport, PptxExport)}
