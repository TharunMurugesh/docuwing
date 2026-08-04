from __future__ import annotations

from typing import Any

from docuwing_engine.llm.openai_provider.plugin import Transport
from docuwing_engine.interfaces.llm import LLMProvider
from docuwing_engine.plugins.registry import PluginCategory, PluginManifest


class OllamaProvider(LLMProvider):
    provider_name = "ollama"
    MANIFEST = PluginManifest(name="ollama_llm", category=PluginCategory.LLM_PROVIDER, capabilities={"structured_output": True, "embeddings": True})
    def __init__(self, transport: Transport) -> None: self._transport = transport
    async def generate(self, prompt: str, *, model: str, system: str = "", **kwargs: Any) -> str:
        return str((await self._transport("api/generate", {"model": model, "prompt": prompt, "system": system, "stream": False}))["response"])
    async def generate_structured(self, prompt: str, schema: dict[str, Any], *, model: str, system: str = "", **kwargs: Any) -> dict[str, Any]:
        result = await self._transport("api/generate", {"model": model, "prompt": prompt, "system": system, "format": schema, "stream": False})
        value = result["response"]
        return value if isinstance(value, dict) else __import__("json").loads(value)
    async def embed(self, texts: list[str], *, model: str, **kwargs: Any) -> list[list[float]]:
        return (await self._transport("api/embed", {"model": model, "input": texts}))["embeddings"]
