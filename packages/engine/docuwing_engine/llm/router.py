"""Provider selection, bounded retries, cost accounting, and rate limiting."""

from __future__ import annotations

import asyncio
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from typing import Any

from docuwing_engine.interfaces.llm import LLMProvider


@dataclass(frozen=True)
class ModelConfig:
    provider: str
    model: str
    family: str = ""
    requests_per_minute: int = 60
    input_cost_per_1k: float = 0.0
    output_cost_per_1k: float = 0.0


@dataclass(frozen=True)
class LLMCallLog:
    workspace: str
    provider: str
    model: str
    operation: str
    latency_ms: float
    input_tokens: int
    output_tokens: int
    cost: float


class LLMRouter:
    """The sole path from the engine to a model provider.

    Configuration is injected per workspace, so an on-prem workspace can
    select Ollama without any call site knowing which provider is in use.
    """

    def __init__(self, providers: dict[str, LLMProvider], default: ModelConfig, *, retries: int = 2) -> None:
        self._providers = providers
        self._default = default
        self._workspace_configs: dict[str, ModelConfig] = {}
        self._retries = retries
        self.logs: list[LLMCallLog] = []
        self._requests: dict[str, deque[float]] = defaultdict(deque)

    def set_workspace_config(self, workspace: str, config: ModelConfig) -> None:
        if config.provider not in self._providers:
            raise ValueError(f"Unknown LLM provider: {config.provider}")
        self._workspace_configs[workspace] = config

    def get_workspace_config(self, workspace: str) -> ModelConfig:
        return self._workspace_configs.get(workspace, self._default)

    async def generate(self, workspace: str, prompt: str, *, system: str = "") -> str:
        return await self._call(workspace, "generate", prompt, system=system)

    async def generate_structured(
        self, workspace: str, prompt: str, schema: dict[str, Any], *, system: str = ""
    ) -> dict[str, Any]:
        value = await self._call(workspace, "generate_structured", prompt, system=system, schema=schema)
        assert isinstance(value, dict)
        return value

    async def embed(self, workspace: str, texts: list[str]) -> list[list[float]]:
        value = await self._call(workspace, "embed", "\n".join(texts), texts=texts)
        assert isinstance(value, list)
        return value

    async def _limit(self, workspace: str, rpm: int) -> None:
        now = time.monotonic()
        bucket = self._requests[workspace]
        while bucket and now - bucket[0] >= 60:
            bucket.popleft()
        if len(bucket) >= rpm:
            await asyncio.sleep(max(0.0, 60 - (now - bucket[0])))
            return await self._limit(workspace, rpm)
        bucket.append(time.monotonic())

    async def _call(self, workspace: str, operation: str, prompt: str, **kwargs: Any) -> Any:
        config = self.get_workspace_config(workspace)
        provider = self._providers[config.provider]
        await self._limit(workspace, config.requests_per_minute)
        start = time.perf_counter()
        last_error: Exception | None = None
        for attempt in range(self._retries + 1):
            try:
                if operation == "embed":
                    value = await provider.embed(kwargs["texts"], model=config.model)
                elif operation == "generate_structured":
                    value = await provider.generate_structured(prompt, kwargs["schema"], model=config.model, system=kwargs.get("system", ""))
                else:
                    value = await provider.generate(prompt, model=config.model, system=kwargs.get("system", ""))
                self._record(workspace, config, operation, prompt, value, start)
                return value
            except Exception as exc:
                last_error = exc
                if attempt < self._retries:
                    await asyncio.sleep(0.1 * (2**attempt))
        assert last_error is not None
        raise last_error

    def _record(self, workspace: str, config: ModelConfig, operation: str, prompt: str, value: Any, start: float) -> None:
        input_tokens = max(1, len(prompt) // 4)
        output_tokens = max(1, len(str(value)) // 4)
        cost = (input_tokens * config.input_cost_per_1k + output_tokens * config.output_cost_per_1k) / 1000
        self.logs.append(LLMCallLog(workspace, config.provider, config.model, operation, (time.perf_counter() - start) * 1000, input_tokens, output_tokens, cost))
