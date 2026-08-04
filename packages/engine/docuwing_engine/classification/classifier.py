from __future__ import annotations

from dataclasses import dataclass

from docuwing_engine.ir.types import DocumentIR
from docuwing_engine.llm.router import LLMRouter
from docuwing_engine.prompts.registry import PromptRegistry


@dataclass(frozen=True)
class Classification:
    label: str
    confidence: float
    tier: int


class DocumentClassifier:
    def __init__(self, router: LLMRouter, prompts: PromptRegistry, *, threshold: float = 0.8) -> None:
        self._router, self._prompts, self._threshold = router, prompts, threshold

    async def classify(self, workspace: str, ir: DocumentIR, filename: str, mime_type: str) -> Classification:
        first = self._heuristic(ir, filename, mime_type)
        if first.confidence >= self._threshold:
            return first
        config = self._router.get_workspace_config(workspace)
        artifact = await self._prompts.resolve("classification.document_type", config.model, config.family)
        result = await self._router.generate_structured(workspace, artifact.template.user + "\n" + ir.to_markdown(), {"type": "object", "properties": {"label": {"type": "string"}, "confidence": {"type": "number"}}, "required": ["label", "confidence"]}, system=artifact.template.system)
        return Classification(str(result["label"]), float(result["confidence"]), 2)

    def _heuristic(self, ir: DocumentIR, filename: str, mime_type: str) -> Classification:
        text = ir.to_markdown().lower()
        if "invoice" in filename.lower() or "invoice" in text or ("total" in text and "bill" in text):
            return Classification("invoice", 0.92, 1)
        if mime_type == "text/csv" or filename.lower().endswith(".csv"):
            return Classification("spreadsheet", 0.95, 1)
        if "agreement" in text or "contract" in text:
            return Classification("contract", 0.88, 1)
        return Classification("unknown", 0.2, 1)
