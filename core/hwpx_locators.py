"""Read source coordinates (paragraph order, table cell addresses) from an HWPX.

Additive provenance only. The pipeline's text still comes from
``HwpxDocument.export_markdown()``; this module never produces content, it only
records where content sits in the source package so a fact can be cited.

The Markdown round-trip cannot be cited: it merges and drops paragraphs, so its
indices do not line up with the source. These locators are the ones that do.
"""
from __future__ import annotations

import logging
from pathlib import Path

from .document_model import NativeParagraph, NativeTableCell


def read_native_locators(
    hwpx_path: Path | str,
) -> tuple[list[NativeParagraph], list[NativeTableCell]]:
    """Return (paragraphs, table cells) addressed by their source coordinates."""
    logging.getLogger("hwpx").setLevel(logging.ERROR)

    from hwpx import HwpxDocument

    doc = HwpxDocument.open(str(hwpx_path))
    try:
        paragraphs = [
            NativeParagraph(index=index, text=paragraph.text or "", section=section)
            for section, part in enumerate(doc.sections)
            for index, paragraph in enumerate(part.paragraphs)
        ]
        cells = [
            NativeTableCell(
                table=table.get("table_index", 0),
                row=cell.get("row", 0),
                column=cell.get("col", 0),
                text=cell.get("text", "") or "",
            )
            for table in doc.get_table_map().get("tables", [])
            for cell in table.get("cells", [])
        ]
        return paragraphs, cells
    finally:
        doc.close()
