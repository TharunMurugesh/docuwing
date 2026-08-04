"""Layout Analyzer implementation for DocumentIR refinement."""

from __future__ import annotations

from typing import Any

from docuwing_engine.domain.entities import BoundingBox
from docuwing_engine.interfaces.layout import LayoutAnalyzerPlugin
from docuwing_engine.ir.types import Block, DocumentIR, Section, TextBlock
from docuwing_engine.plugins.registry import PluginCategory, PluginManifest


class StandardLayoutAnalyzer(LayoutAnalyzerPlugin):
    """Refines DocumentIR by sorting multi-column reading orders.

    Forms section hierarchies, and merges OCR line fragments.
    """

    MANIFEST = PluginManifest(
        name="standard_layout_analyzer",
        category=PluginCategory.PARSER,  # Layout sits in pipeline alongside parser tools
        description="Standard spatial reading-order and section hierarchy layout analyzer",
    )

    def initialize(self, config: dict[str, Any] | None = None) -> None:
        pass

    async def analyze(self, ir: DocumentIR) -> DocumentIR:
        refined_sections = []

        for section in ir.sections:
            # 1. Merge adjacent OCR text fragments
            merged_blocks = self._merge_ocr_fragments(section.blocks)

            # 2. Sort multi-column reading order per page
            sorted_blocks = self._sort_reading_order(merged_blocks)

            # 3. Form section hierarchy from headings
            sections = self._build_section_hierarchy(sorted_blocks, section.title)
            refined_sections.extend(sections)

        return DocumentIR(
            document_id=ir.document_id,
            pages=ir.pages,
            sections=refined_sections,
            metadata=ir.metadata,
        )

    def _merge_ocr_fragments(self, blocks: list[Block]) -> list[Block]:
        if not blocks:
            return []

        merged: list[Block] = []
        curr: TextBlock | None = None

        for b in blocks:
            if isinstance(b, TextBlock) and b.source_ocr:
                if (
                    curr is not None
                    and curr.bbox
                    and b.bbox
                    and curr.bbox.page == b.bbox.page
                    and abs(b.bbox.y0 - curr.bbox.y1) < 0.05
                    and abs(b.bbox.x0 - curr.bbox.x0) < 0.1
                ):
                    new_bbox = BoundingBox(
                        x0=curr.bbox.x0,
                        y0=curr.bbox.y0,
                        x1=max(curr.bbox.x1, b.bbox.x1),
                        y1=b.bbox.y1,
                        page=curr.bbox.page,
                    )
                    curr = TextBlock(
                        id=curr.id,
                        text=f"{curr.text} {b.text}",
                        role=curr.role,
                        bbox=new_bbox,
                        source_ocr=True,
                        ocr_confidence=min(curr.ocr_confidence or 1.0, b.ocr_confidence or 1.0),
                    )
                    continue
                if curr:
                    merged.append(curr)
                curr = TextBlock(
                    id=b.id,
                    text=b.text,
                    role=b.role,
                    bbox=b.bbox,
                    source_ocr=b.source_ocr,
                    ocr_confidence=b.ocr_confidence,
                )
            else:
                if curr:
                    merged.append(curr)
                    curr = None
                merged.append(b)

        if curr:
            merged.append(curr)

        return merged

    def _sort_reading_order(self, blocks: list[Block]) -> list[Block]:
        """Sort blocks by page, column (x0), then vertical position (y0)."""

        def block_key(b: Block) -> tuple[int, float, float]:
            if hasattr(b, "bbox") and b.bbox:
                # Group into 2 columns if x0 > 0.55
                col = 1 if b.bbox.x0 > 0.55 else 0
                return (b.bbox.page, col, b.bbox.y0)
            return (0, 0, 0)

        return sorted(blocks, key=block_key)

    def _build_section_hierarchy(
        self, blocks: list[Block], root_title: str | None
    ) -> list[Section]:
        """Group blocks into sections based on heading roles."""
        sections: list[Section] = []
        current_title = root_title
        current_blocks: list[Block] = []

        for b in blocks:
            if isinstance(b, TextBlock) and b.role == "heading":
                if current_blocks:
                    sections.append(Section(title=current_title, blocks=current_blocks))
                    current_blocks = []
                current_title = b.text
            else:
                current_blocks.append(b)

        if current_blocks or not sections:
            sections.append(Section(title=current_title, blocks=current_blocks))

        return sections
