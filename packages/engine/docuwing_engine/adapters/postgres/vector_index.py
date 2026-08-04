"""Vector-index port adapter.

SQL is deliberately kept behind this adapter; deployments using pgvector can
replace the JSON migration column with ``vector`` without changing callers.
"""

from __future__ import annotations

from math import sqrt


class InMemoryVectorIndex:
    """Deterministic reference adapter used by engine tests and local CLI."""

    def __init__(self) -> None: self._vectors: dict[str, list[float]] = {}
    def upsert(self, key: str, vector: list[float]) -> None: self._vectors[key] = vector
    def search(self, vector: list[float], limit: int = 10) -> list[tuple[str, float]]:
        def cosine(other: list[float]) -> float:
            magnitude = sqrt(sum(x * x for x in vector)) * sqrt(sum(x * x for x in other))
            return sum(a * b for a, b in zip(vector, other, strict=True)) / magnitude if magnitude else 0.0
        return sorted(((key, cosine(item)) for key, item in self._vectors.items()), key=lambda item: item[1], reverse=True)[:limit]
