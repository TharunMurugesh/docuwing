from __future__ import annotations

import pytest

from docuwing_engine.caching import cache_key
from docuwing_engine.classification import DocumentClassifier
from docuwing_engine.domain.entities import FieldDefinition, FieldType, ProjectionHint, Schema
from docuwing_engine.embedding import SemanticChunker
from docuwing_engine.extraction import ExtractionEngine
from docuwing_engine.ir.types import DocumentIR, Section, TextBlock
from docuwing_engine.knowledge import KnowledgeBuilder
from docuwing_engine.llm import LLMRouter, ModelConfig
from docuwing_engine.validation import ValidationEngine


class FakeLLM:
    async def generate(self, *args, **kwargs): return "ok"
    async def generate_structured(self, *args, **kwargs): return {"vendor": "Acme", "total": 25, "label": "form", "confidence": 0.8}
    async def embed(self, texts, **kwargs): return [[float(len(text))] for text in texts]


@pytest.fixture
def ir(): return DocumentIR(document_id="doc", pages=1, sections=[Section(blocks=[TextBlock(text="Invoice from Acme. Total 25")])])


@pytest.mark.asyncio
async def test_heuristic_classification_avoids_llm(ir):
    router = LLMRouter({"fake": FakeLLM()}, ModelConfig("fake", "fake"))
    classifier = DocumentClassifier(router, None)  # type: ignore[arg-type]
    result = await classifier.classify("ws", ir, "invoice.pdf", "application/pdf")
    assert result.tier == 1 and not router.logs


def test_cache_key_is_versioned():
    assert cache_key("same", schema_version=1, prompt_version="v1", model_identifier="m") != cache_key("same", schema_version=1, prompt_version="v2", model_identifier="m")


def test_chunking_observes_boundaries(ir):
    assert SemanticChunker(10).chunk(ir)[0].text == "Invoice fro"


@pytest.mark.asyncio
async def test_validation_and_knowledge_projection():
    schema = Schema(workspace="ws", name="invoice", fields=[FieldDefinition(name="vendor", field_type=FieldType.STRING, projection_hint=ProjectionHint.ENTITY), FieldDefinition(name="total", field_type=FieldType.FLOAT, validation_rules={"min": 1})])
    from docuwing_engine.domain.entities import ExtractionResult, ExtractedField, ConfidenceScore
    result = ExtractionResult(document_id="doc", schema_id=schema.id, workspace="ws", fields=[ExtractedField(field_name="vendor", value="Acme", confidence=ConfidenceScore(extraction=.9)), ExtractedField(field_name="total", value=25, confidence=ConfidenceScore(extraction=.9))])
    result = await ValidationEngine().validate("ws", result, schema)
    graph = KnowledgeBuilder().build(result, schema)
    assert graph.entities[0].name == "Acme" and graph.facts[0].value == 25
