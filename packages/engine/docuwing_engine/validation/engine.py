from __future__ import annotations

import re

from docuwing_engine.domain.entities import ConfidenceScore, ExtractionResult, FieldDefinition, Schema, ValidationState
from docuwing_engine.llm.router import LLMRouter


class ValidationEngine:
    def __init__(self, router: LLMRouter | None = None, *, semantic_threshold: float = 0.7, review_threshold: float = 0.65) -> None:
        self._router, self._semantic_threshold, self._review_threshold = router, semantic_threshold, review_threshold

    async def validate(self, workspace: str, result: ExtractionResult, schema: Schema) -> ExtractionResult:
        definitions = {field.name: field for field in schema.fields}
        values = {field.field_name: field.value for field in result.fields}
        for field in result.fields:
            valid = self._rule_valid(field.value, definitions[field.field_name], values)
            validation = 1.0 if valid else 0.0
            field.confidence = ConfidenceScore(extraction=field.confidence.extraction, validation=validation, span_quality=field.confidence.span_quality)
            field.validation_state = ValidationState.VALID if valid else ValidationState.INVALID
            if valid and self._router and field.confidence.extraction < self._semantic_threshold:
                answer = await self._router.generate_structured(workspace, f"Is this value plausible? {field.value}", {"type": "object", "properties": {"valid": {"type": "boolean"}}, "required": ["valid"]})
                if not answer["valid"]:
                    field.validation_state = ValidationState.INVALID
            if field.validation_state == ValidationState.VALID and field.confidence.composite < self._review_threshold:
                field.validation_state = ValidationState.NEEDS_REVIEW
        result.review_status = "in_review" if any(f.validation_state == ValidationState.NEEDS_REVIEW for f in result.fields) else "approved"
        return result

    @staticmethod
    def _rule_valid(value: object, definition: FieldDefinition, values: dict[str, object]) -> bool:
        rules = definition.validation_rules
        if definition.required and value in (None, "", []): return False
        if value in (None, "", []): return True
        if "regex" in rules and not re.fullmatch(str(rules["regex"]), str(value)): return False
        if "min" in rules and float(value) < float(rules["min"]): return False
        if "max" in rules and float(value) > float(rules["max"]): return False
        if "equals_field" in rules and value != values.get(rules["equals_field"]): return False
        return True
