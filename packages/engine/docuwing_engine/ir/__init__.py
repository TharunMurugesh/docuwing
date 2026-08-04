"""DocumentIR (Intermediate Representation) — EDS §4.2.

The standardized internal representation of all documents (PDF, Docx, Image)
after parsing and before semantic analysis.
"""

from docuwing_engine.ir.types import (
    Block,
    DocumentIR,
    ListBlock,
    Section,
    TableBlock,
    TableCell,
    TableRow,
    TextBlock,
)

__all__ = [
    "Block",
    "DocumentIR",
    "ListBlock",
    "Section",
    "TableBlock",
    "TableCell",
    "TableRow",
    "TextBlock",
]
