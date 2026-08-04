"""Small weighted round-robin dispatcher used before wiring an external queue."""

from __future__ import annotations

from collections import defaultdict, deque
from typing import Generic, TypeVar

T = TypeVar("T")


class FairScheduler(Generic[T]):
    def __init__(self) -> None: self._queues: dict[str, deque[T]] = defaultdict(deque); self._order: deque[str] = deque()
    def submit(self, workspace: str, item: T) -> None:
        if not self._queues[workspace]: self._order.append(workspace)
        self._queues[workspace].append(item)
    def pop(self) -> tuple[str, T] | None:
        if not self._order: return None
        workspace = self._order.popleft(); item = self._queues[workspace].popleft()
        if self._queues[workspace]: self._order.append(workspace)
        return workspace, item
