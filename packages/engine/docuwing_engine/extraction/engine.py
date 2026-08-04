from __future__ import annotations

import json
from typing import Any

from docuwing_engine.caching import VersionedCache, cache_key
from docuwing_engine.domain.entities import ConfidenceScore, ExtractionResult, ExtractedField, Provenance, ProvenanceSource, Schema, Span
from docuwing_engine.ir.types import DocumentIR, TextBlock
from docuwing_engine.llm.router import LLMRouter
from docuwing_engine.prompts.registry import PromptRegistry


class ExtractionEngine:
    def __init__(self, router: LLMRouter, prompts: PromptRegistry, *, chunk_chars: int = 12000, cache: VersionedCache | None = None) -> None:
        self._router, self._prompts, self._chunk_chars = router, prompts, chunk_chars
        self._cache = cache

    @staticmethod
    def json_schema(schema: Schema) -> dict[str, Any]:
        types = {"string": "string", "integer": "integer", "float": "number", "boolean": "boolean", "list": "array", "table": "array"}
        props = {f.name: {"type": types.get(f.field_type.value, "string"), "description": f.description} for f in schema.fields}
        return {"type": "object", "properties": props, "required": [f.name for f in schema.fields if f.required]}

    async def extract(self, workspace: str, ir: DocumentIR, schema: Schema) -> ExtractionResult:
        config = self._router.get_workspace_config(workspace)
        artifact = await self._prompts.resolve(f"extraction.{schema.name}", config.model, config.family)
        chunks = self._chunks(ir)
        key = cache_key(ir.to_markdown(), schema_version=schema.version, prompt_version=artifact.version, model_identifier=config.model)
        cached = self._cache.get(key) if self._cache else None
        if cached is not None:
            return cached
        responses = [await self._router.generate_structured(workspace, artifact.template.user + "\n" + chunk, self.json_schema(schema), system=artifact.template.system) for chunk in chunks]
        values = self._merge(responses, schema)
        fields = [self._field(field.name, values.get(field.name), ir, config.model, artifact.version) for field in schema.fields]
        result = ExtractionResult(document_id=ir.document_id, schema_id=schema.id, workspace=workspace, fields=fields)
        if self._cache:
            self._cache.set(key, result)
        return result

    def _chunks(self, ir: DocumentIR) -> list[str]:
        text = ir.to_markdown()
        return [text[i : i + self._chunk_chars] for i in range(0, len(text), self._chunk_chars)] or [""]

    @staticmethod
    def _merge(responses: list[dict[str, Any]], schema: Schema) -> dict[str, Any]:
        merged: dict[str, Any] = {}
        for field in schema.fields:
            values = [r[field.name] for r in responses if r.get(field.name) not in (None, "", [])]
            if field.field_type.value in {"list", "table"}:
                merged[field.name] = [item for value in values for item in (value if isinstance(value, list) else [value])]
            elif values:
                merged[field.name] = values[0]
        return merged

    @staticmethod
    def _field(name: str, value: Any, ir: DocumentIR, model: str, prompt_version: str) -> ExtractedField:
        rendered = str(value) if value is not None else ""
        span: Span | None = None
        for section in ir.sections:
            for block in section.blocks:
                if isinstance(block, TextBlock) and rendered and rendered.lower() in block.text.lower():
                    offset = block.text.lower().index(rendered.lower())
                    span = Span(text=block.text[offset : offset + len(rendered)], start_offset=offset, end_offset=offset + len(rendered), block_id=block.id, bbox=block.bbox)
                    break
            if span:
                break
        confidence = 0.9 if span else (0.55 if value is not None else 0.0)
        return ExtractedField(field_name=name, value=value, confidence=ConfidenceScore(extraction=confidence, span_quality=1.0 if span else 0.4), spans=[span] if span else [], provenance=Provenance(source=ProvenanceSource.PARSER, model_id=model, prompt_version=prompt_version, details={"structured": True}))
