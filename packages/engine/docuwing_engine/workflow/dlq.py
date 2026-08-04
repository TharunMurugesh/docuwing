from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime


@dataclass(frozen=True)
class DeadLetterEntry:
    run_id: str
    step_id: str
    error: str
    retries: int
    created_at: datetime


class DeadLetterQueue:
    def __init__(self) -> None: self._entries: list[DeadLetterEntry] = []
    def add(self, run_id: str, step_id: str, error: str, retries: int) -> None: self._entries.append(DeadLetterEntry(run_id, step_id, error, retries, datetime.now(UTC)))
    def list(self) -> list[DeadLetterEntry]: return list(self._entries)
