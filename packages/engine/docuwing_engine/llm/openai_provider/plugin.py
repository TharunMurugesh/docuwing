"""OpenAI-compatible provider adapter with an injectable transport for tests."""

from __future__ import annotations

from typing import Any, Awaitable, Callable

from docuwing_engine.interfaces.llm import LLMProvider
from docuwing_engine.plugins.registry import PluginCategory, PluginManifest


Transport = Callable[[str, dict[str, Any]], Awaitable[dict[str, Any]]]


class OpenAIProvider(LLMProvider):
    provider_name = "openai"
    MANIFEST = PluginManifest(name="openai_llm", category=PluginCategory.LLM_PROVIDER, capabilities={"structured_output": True, "embeddings": True})
    def __init__(self, transport: Transport) -> None: self._transport = transport
    async def generate(self, prompt: str, *, model: str, system: str = "", **kwargs: Any) -> str:
        response = await self._transport("chat/completions", {"model": model, "messages": [{"role": "system", "content": system}, {"role": "user", "content": prompt}]})
        return str(response["choices"][0]["message"]["content"])
    async def generate_structured(self, prompt: str, schema: dict[str, Any], *, model: str, system: str = "", **kwargs: Any) -> dict[str, Any]:
        response = await self._transport("chat/completions", {"model": model, "messages": [{"role": "system", "content": system}, {"role": "user", "content": prompt}], "response_format": {"type": "json_schema", "json_schema": {"name": "result", "schema": schema}}})
        value = response["choices"][0]["message"]["content"]
        return value if isinstance(value, dict) else __import__("json").loads(value)
    async def embed(self, texts: list[str], *, model: str, **kwargs: Any) -> list[list[float]]:
        response = await self._transport("embeddings", {"model": model, "input": texts})
        return [item["embedding"] for item in response["data"]]
