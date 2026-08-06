from collections.abc import AsyncIterator
from typing import Protocol


class InferenceProvider(Protocol):
    async def complete(self, messages: list[dict], *, stream: bool = False, schema: dict | None = None) -> str | AsyncIterator[str]: ...
    async def embed(self, texts: list[str]) -> list[list[float]]: ...
