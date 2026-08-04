from __future__ import annotations

from docuwing_engine.embedding.chunking import DocumentChunk
from docuwing_engine.llm.router import LLMRouter


class EmbeddingService:
    def __init__(self, router: LLMRouter) -> None: self._router = router
    async def embed(self, workspace: str, chunks: list[DocumentChunk]) -> dict[str, list[float]]:
        vectors = await self._router.embed(workspace, [chunk.text for chunk in chunks])
        return dict(zip((chunk.id for chunk in chunks), vectors, strict=True))
