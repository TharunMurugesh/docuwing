"""Minimal field-level exact-match eval harness (Phase 7)."""

from __future__ import annotations

import json
from pathlib import Path


def score(expected: dict[str, object], actual: dict[str, object]) -> dict[str, float]:
    keys = set(expected) | set(actual)
    matches = sum(expected.get(key) == actual.get(key) for key in keys)
    precision = matches / len(actual) if actual else 0.0
    recall = matches / len(expected) if expected else 0.0
    return {"precision": precision, "recall": recall, "exact_match": matches / len(keys) if keys else 1.0}


def test_golden_dataset_is_versioned_and_scoreable() -> None:
    dataset = json.loads((Path(__file__).parent / "golden_invoice.json").read_text())
    assert dataset[0]["expected"]["vendor"] == "Acme"
    assert score(dataset[0]["expected"], {"vendor": "Acme", "total": 25})["exact_match"] == 1.0
