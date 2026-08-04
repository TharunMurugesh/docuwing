"""CSV Parser."""

from __future__ import annotations

import csv
import io
from typing import Any

from docuwing_engine.domain.entities import Document
from docuwing_engine.interfaces.parser import ParserPlugin
from docuwing_engine.ir.types import DocumentIR, Section, TableBlock, TableCell, TableRow
from docuwing_engine.plugins.registry import PluginCategory, PluginManifest


class CsvParser(ParserPlugin):
    """Parses CSV files."""

    MANIFEST = PluginManifest(
        name="csv_parser",
        category=PluginCategory.PARSER,
        description="Native parser for CSV files",
        mime_types=["text/csv"],
    )

    def initialize(self, config: dict[str, Any] | None = None) -> None:
        pass

    async def parse(self, document: Document, stream: io.BytesIO) -> DocumentIR:
        text = stream.read().decode("utf-8")
        reader = csv.reader(io.StringIO(text))

        rows = []
        for i, row in enumerate(reader):
            cells = [TableCell(text=cell.strip(), is_header=(i == 0)) for cell in row]
            rows.append(TableRow(cells=cells))

        table_block = TableBlock(rows=rows)
        root_section = Section(blocks=[table_block])

        ir = DocumentIR(
            document_id=document.id,
            pages=1,
            sections=[root_section],
        )

        return ir
