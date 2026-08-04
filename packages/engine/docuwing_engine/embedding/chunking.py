from __future__ import annotations

import hashlib
from dataclasses import dataclass

from docuwing_engine.ir.types import DocumentIR


@dataclass(frozen=True)
class DocumentChunk:
    id: str
    document_id: str
    text: str
    ordinal: int


class SemanticChunker:
    def __init__(self, max_chars: int = 1500) -> None: self.max_chars = max_chars
    def chunk(self, ir: DocumentIR) -> list[DocumentChunk]:
        sections = ["\n".join(ir._section_to_markdown(section)) for section in ir.sections] or [""]
        chunks: list[DocumentChunk] = []
        for section in sections:
            for start in range(0, len(section), self.max_chars):
                text = section[start : start + self.max_chars]
                chunks.append(DocumentChunk(hashlib.sha256(f"{ir.document_id}:{len(chunks)}:{text}".encode()).hexdigest(), ir.document_id, text, len(chunks)))
        return chunks
