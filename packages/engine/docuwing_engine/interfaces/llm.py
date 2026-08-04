"""Provider-neutral LLM protocol used by all engine features."""

from __future__ import annotations

from abc import abstractmethod
from typing import Any

from docuwing_engine.plugins.sdk import PluginBase


class LLMProvider(PluginBase):
    """A provider capable of generation, structured generation, and embeddings."""

    provider_name: str

    @abstractmethod
    async def generate(self, prompt: str, *, model: str, system: str = "", **kwargs: Any) -> str: ...

    @abstractmethod
    async def generate_structured(
        self, prompt: str, schema: dict[str, Any], *, model: str, system: str = "", **kwargs: Any
    ) -> dict[str, Any]: ...

    @abstractmethod
    async def embed(self, texts: list[str], *, model: str, **kwargs: Any) -> list[list[float]]: ...
