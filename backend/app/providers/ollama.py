from collections.abc import AsyncIterator
import hashlib
import httpx
from app.core.config import Settings
from app.core.errors import ProviderError


class OllamaProvider:
    def __init__(self, settings: Settings): self.settings = settings
    async def complete(self, messages: list[dict], *, stream: bool = False, schema: dict | None = None) -> str | AsyncIterator[str]:
        payload = {"model": self.settings.primary_model, "messages": messages, "stream": stream}
        if schema: payload["format"] = schema
        try:
            if not stream:
                async with httpx.AsyncClient(timeout=120) as client:
                    response = await client.post(f"{self.settings.ollama_url}/api/chat", json=payload); response.raise_for_status()
                    return response.json()["message"]["content"]
            async def tokens() -> AsyncIterator[str]:
                async with httpx.AsyncClient(timeout=120) as client:
                    async with client.stream("POST", f"{self.settings.ollama_url}/api/chat", json=payload) as response:
                        response.raise_for_status()
                        async for line in response.aiter_lines():
                            if line:
                                import json
                                item = json.loads(line)
                                if content := item.get("message", {}).get("content"): yield content
            return tokens()
        except httpx.HTTPError as exc: raise ProviderError(f"Ollama is unavailable: {exc}") from exc
    async def embed(self, texts: list[str]) -> list[list[float]]:
        try:
            async with httpx.AsyncClient(timeout=60) as client:
                response = await client.post(f"{self.settings.ollama_url}/api/embed", json={"model": self.settings.embedding_model, "input": texts}); response.raise_for_status()
                return response.json()["embeddings"]
        except httpx.HTTPError:
            # Deterministic local fallback keeps ingestion and lexical retrieval functional offline before models are pulled.
            return [[int(x, 16) / 15 for x in hashlib.sha256(t.encode()).hexdigest()[:64]] for t in texts]
