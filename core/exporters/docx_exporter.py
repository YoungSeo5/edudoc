"""
Markdown -> DOCX exporter (pip-native 기본 엔진).

python-docx로 DOCX를 직접 만든다. 외부 바이너리(Pandoc 등) 없이
`pip install` 만으로 동작하는 것이 목적이다.
공통 파서(markdown_blocks)가 만든 블록 구조를 받아 Word 요소로 옮긴다.
"""
from __future__ import annotations

from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.shared import Mm, Pt

from .export_base import BaseExporter, ExportResult
from .markdown_blocks import (
    Heading,
    ListBlock,
    Paragraph,
    Run,
    Table,
    parse_markdown,
)
from .style_profile import DEFAULT_GONGMUN_STYLE_PROFILE, DocumentStyleProfile


class DocxExporter(BaseExporter):
    """Markdown 파일 -> DOCX (python-docx)."""

    supported_ext = (".docx",)

    def __init__(self, style_profile: DocumentStyleProfile | None = None) -> None:
        self.style_profile = style_profile or DEFAULT_GONGMUN_STYLE_PROFILE

    def export(self, markdown_path: Path, output_path: Path) -> ExportResult:
        markdown_path = Path(markdown_path)
        output_path = Path(output_path)

        if not self.can_export(output_path):
            return ExportResult(
                source=markdown_path, output=output_path, ok=False,
                error=f"Unsupported output extension: {output_path.suffix} "
                      f"(supported: {sorted(self.supported_ext)})",
                meta={"exporter": self.name},
            )
        if not markdown_path.exists():
            return ExportResult(
                source=markdown_path, output=output_path, ok=False,
                error=f"Markdown source does not exist: {markdown_path}",
                meta={"exporter": self.name},
            )

        try:
            blocks = parse_markdown(markdown_path.read_text(encoding="utf-8"))
            document = Document()
            self._apply_style_profile(document)
            for block in blocks:
                self._write_block(document, block)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            document.save(str(output_path))
            return ExportResult(
                source=markdown_path, output=output_path, ok=True,
                meta={"exporter": self.name, "blocks": len(blocks)},
            )
        except Exception as e:  # noqa: BLE001  (실패는 구조화해 돌려준다)
            return ExportResult(
                source=markdown_path, output=output_path, ok=False,
                error=repr(e), meta={"exporter": self.name},
            )

    # --- 블록별 변환 -----------------------------------------------------

    def _write_block(self, document, block) -> None:  # noqa: ANN001
        if isinstance(block, Heading):
            p = document.add_paragraph(style=f"Heading {min(block.level, 9)}")
            self._add_runs(p, block.runs)
        elif isinstance(block, Paragraph):
            p = document.add_paragraph()
            self._add_runs(p, block.runs)
        elif isinstance(block, ListBlock):
            style = "List Number" if block.ordered else "List Bullet"
            for item in block.items:
                p = document.add_paragraph(style=style)
                self._add_runs(p, item)
        elif isinstance(block, Table):
            self._write_table(document, block)

    def _write_table(self, document, block: Table) -> None:  # noqa: ANN001
        body_cols = max((len(r) for r in block.rows), default=0)
        ncols = max(len(block.header), body_cols)
        if ncols == 0:
            return
        rows = block.rows
        nrows = (1 if block.header else 0) + len(rows)
        if nrows == 0:
            return

        table = document.add_table(rows=nrows, cols=ncols)
        table.style = "Table Grid"

        r = 0
        if block.header:
            self._fill_row(table.rows[0].cells, block.header, ncols)
            r = 1
        for row in rows:
            self._fill_row(table.rows[r].cells, row, ncols)
            r += 1

    def _fill_row(self, cells, row_runs: list[list[Run]], ncols: int) -> None:  # noqa: ANN001
        for c in range(ncols):
            runs = row_runs[c] if c < len(row_runs) else []
            paragraph = cells[c].paragraphs[0]
            self._add_runs(paragraph, runs)

    def _add_runs(self, paragraph, runs: list[Run]) -> None:  # noqa: ANN001
        for run in runs:
            r = paragraph.add_run(run.text)
            r.bold = run.bold
            r.italic = run.italic

    # --- 스타일 프로파일 (Loop 8.5) --------------------------------------

    def _apply_style_profile(self, document) -> None:  # noqa: ANN001
        """공문 기본 스타일 프로파일을 DOCX에 적용한다(여백/폰트/줄간격/제목).

        보수적인 프로젝트 로컬 기본값이며, 공식 서식 준수를 보장하지 않는다.
        Markdown 파싱/블록 변환 동작은 건드리지 않는다.
        """
        profile = self.style_profile

        for section in document.sections:
            section.top_margin = Mm(profile.page_margin_top_mm)
            section.bottom_margin = Mm(profile.page_margin_bottom_mm)
            section.left_margin = Mm(profile.page_margin_left_mm)
            section.right_margin = Mm(profile.page_margin_right_mm)

        normal = document.styles["Normal"]
        normal.font.name = profile.font_family
        normal.font.size = Pt(profile.font_size_pt)
        self._set_eastasia_font(normal, profile.font_family)
        normal_format = normal.paragraph_format
        normal_format.line_spacing = profile.line_spacing
        normal_format.space_after = Pt(profile.paragraph_space_after_pt)

        heading = document.styles["Heading 1"]
        heading.font.name = profile.font_family
        heading.font.size = Pt(profile.heading_font_size_pt)
        self._set_eastasia_font(heading, profile.font_family)
        alignment = self._alignment(profile.heading_alignment)
        if alignment is not None:
            heading.paragraph_format.alignment = alignment

    def _set_eastasia_font(self, style, font_name: str) -> None:  # noqa: ANN001
        """스타일에 동아시아(한글) 폰트를 지정해 한글이 깨지지 않게 한다."""
        rpr = style.element.get_or_add_rPr()
        rpr.get_or_add_rFonts().set(qn("w:eastAsia"), font_name)

    @staticmethod
    def _alignment(name: str):
        return {
            "left": WD_ALIGN_PARAGRAPH.LEFT,
            "center": WD_ALIGN_PARAGRAPH.CENTER,
            "right": WD_ALIGN_PARAGRAPH.RIGHT,
            "justify": WD_ALIGN_PARAGRAPH.JUSTIFY,
        }.get(name.lower())
