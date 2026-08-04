"""DocumentIR types (EDS §4.2).

These are frozen pydantic models representing the hierarchical structure
of a document. This is what the Engine operates on for analysis and extraction.
"""

from __future__ import annotations

import uuid
from typing import Literal

from pydantic import BaseModel, Field

from docuwing_engine.domain.entities import BoundingBox


class Block(BaseModel, frozen=True):
    """Base class for all document blocks."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    block_type: str = Field(description="Subclass discriminator")
    bbox: BoundingBox | None = Field(default=None)


class TextBlock(Block, frozen=True):
    """A block of continuous text (paragraph, heading, etc.)."""

    block_type: Literal["text"] = "text"
    text: str
    role: str = Field(
        default="paragraph",
        description="Role assigned by Layout Analysis: title, heading, paragraph, footer, etc.",
    )
    source_ocr: bool = Field(default=False, description="True if block text was derived from OCR")
    ocr_confidence: float | None = Field(
        default=None, description="OCR confidence score if source_ocr is True"
    )


class ListBlock(Block, frozen=True):
    """A bulleted or numbered list."""

    block_type: Literal["list"] = "list"
    items: list[str]


class TableCell(BaseModel, frozen=True):
    """A single cell in a table."""

    text: str
    row_span: int = 1
    col_span: int = 1
    is_header: bool = False
    bbox: BoundingBox | None = None


class TableRow(BaseModel, frozen=True):
    """A row in a table."""

    cells: list[TableCell]


class TableBlock(Block, frozen=True):
    """A tabular data structure."""

    block_type: Literal["table"] = "table"
    rows: list[TableRow]


class Section(BaseModel, frozen=True):
    """A hierarchical section of a document (e.g., Chapter 1)."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str | None = None
    level: int = Field(default=1, description="Nesting level (1=H1, 2=H2, etc.)")
    blocks: list[Block] = Field(default_factory=list)
    subsections: list[Section] = Field(default_factory=list)


class DocumentIR(BaseModel, frozen=True):
    """The root Intermediate Representation of a document."""

    document_id: str
    pages: int
    sections: list[Section] = Field(default_factory=list)
    metadata: dict[str, str] = Field(default_factory=dict)

    def to_markdown(self) -> str:
        """Convert the IR to Markdown for LLM consumption (EDS §4.2.2)."""
        lines = []
        for section in self.sections:
            lines.extend(self._section_to_markdown(section))
        return "\n\n".join(lines)

    def _section_to_markdown(self, section: Section) -> list[str]:
        lines = []
        if section.title:
            prefix = "#" * section.level
            lines.append(f"{prefix} {section.title}")

        for block in section.blocks:
            if isinstance(block, TextBlock):
                if block.role in ("title", "heading"):
                    lines.append(f"**{block.text}**")
                else:
                    lines.append(block.text)
            elif isinstance(block, ListBlock):
                for item in block.items:
                    lines.append(f"- {item}")
            elif isinstance(block, TableBlock):
                for r_idx, row in enumerate(block.rows):
                    row_str = "| " + " | ".join(cell.text for cell in row.cells) + " |"
                    lines.append(row_str)
                    # Add separator after header row
                    if r_idx == 0 and any(c.is_header for c in row.cells):
                        sep = "| " + " | ".join("---" for _ in row.cells) + " |"
                        lines.append(sep)

        for sub in section.subsections:
            lines.extend(self._section_to_markdown(sub))

        return lines
