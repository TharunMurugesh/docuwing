from collections.abc import AsyncIterator
import httpx
from app.core.errors import ProviderError


class OpenAICompatibleProvider:
    """Opt-in adapter for a user-configured OpenAI-compatible endpoint."""
    def __init__(self, endpoint: str, model: str, api_key: str | None = None):
        self.endpoint, self.model, self.api_key = endpoint.rstrip("/"), model, api_key
    def _headers(self) -> dict[str, str]: return {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}
    async def complete(self, messages: list[dict], *, stream: bool = False, schema: dict | None = None) -> str | AsyncIterator[str]:
        payload: dict = {"model": self.model, "messages": messages, "stream": stream}
        if schema: payload["response_format"] = {"type": "json_schema", "json_schema": {"name": "response", "schema": schema}}
        try:
            if not stream:
                async with httpx.AsyncClient(timeout=120) as client:
                    response = await client.post(f"{self.endpoint}/chat/completions", headers=self._headers(), json=payload); response.raise_for_status()
                    return response.json()["choices"][0]["message"]["content"]
            async def tokens() -> AsyncIterator[str]:
                async with httpx.AsyncClient(timeout=120) as client:
                    async with client.stream("POST", f"{self.endpoint}/chat/completions", headers=self._headers(), json=payload) as response:
                        response.raise_for_status()
                        async for line in response.aiter_lines():
                            if line.startswith("data: ") and line[6:] != "[DONE]":
                                import json
                                content = json.loads(line[6:])["choices"][0]["delta"].get("content")
                                if content: yield content
            return tokens()
        except httpx.HTTPError as exc: raise ProviderError(f"Configured inference provider is unavailable: {exc}") from exc
    async def embed(self, texts: list[str]) -> list[list[float]]:
        try:
            async with httpx.AsyncClient(timeout=60) as client:
                response = await client.post(f"{self.endpoint}/embeddings", headers=self._headers(), json={"model": self.model, "input": texts}); response.raise_for_status()
                return [item["embedding"] for item in response.json()["data"]]
        except httpx.HTTPError as exc: raise ProviderError(f"Configured embedding provider is unavailable: {exc}") from exc
