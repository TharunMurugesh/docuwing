import asyncio
import json
from collections import defaultdict


class EventBus:
    def __init__(self) -> None: self._queues: dict[str, set[asyncio.Queue[str]]] = defaultdict(set)
    async def publish(self, project_id: str, event: str, data: dict) -> None:
        payload = f"event: {event}\ndata: {json.dumps(data, default=str)}\n\n"
        for queue in list(self._queues[project_id]): await queue.put(payload)
    async def subscribe(self, project_id: str):
        queue: asyncio.Queue[str] = asyncio.Queue()
        self._queues[project_id].add(queue)
        try:
            while True: yield await queue.get()
        finally: self._queues[project_id].discard(queue)


event_bus = EventBus()
