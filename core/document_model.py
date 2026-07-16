"""Minimal structured document model for validation-oriented workflows."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class ParagraphNode:
    index: int
    text: str
    style: str | None = None


@dataclass
class TableNode:
    index: int
    rows: list[list[str]] = field(default_factory=list)


@dataclass
class AttachmentNode:
    index: int
    text: str


@dataclass
class NativeParagraph:
    """A paragraph as it exists in the source package, in document order.

    Parallel to ``DocumentModel.paragraphs``, never a replacement: the Markdown
    round-trip merges and drops paragraphs, so the two lists do not line up.
    This index is what a citation can point at.
    """
    index: int
    text: str
    section: int = 0


@dataclass
class NativeTableCell:
    """A table cell addressed by its source coordinates."""
    table: int
    row: int
    column: int
    text: str


@dataclass
class DocumentModel:
    source_path: str
    format: str
    title: str | None = None
    paragraphs: list[ParagraphNode] = field(default_factory=list)
    tables: list[TableNode] = field(default_factory=list)
    attachments: list[AttachmentNode] = field(default_factory=list)
    raw_meta: dict[str, Any] = field(default_factory=dict)
    # Optional provenance index. Empty for inputs whose source coordinates
    # cannot be recovered (Markdown, legacy pyhwp HWP fallback).
    native_paragraphs: list[NativeParagraph] = field(default_factory=list)
    native_table_cells: list[NativeTableCell] = field(default_factory=list)
    locator_source: str | None = None

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        # Keep the serialized shape identical for inputs that carry no locators.
        for key in ("native_paragraphs", "native_table_cells"):
            if not data[key]:
                data.pop(key)
        if data["locator_source"] is None:
            data.pop("locator_source")
        return data


def document_model_from_markdown(
    *,
    source_path: Path,
    file_format: str,
    markdown: str,
    raw_meta: dict[str, Any] | None = None,
) -> DocumentModel:
    """Build a small DocumentModel from available Markdown structure.

    This is intentionally conservative: it preserves basic paragraphs, heading
    labels, simple Markdown tables, and attachment-looking lines without
    claiming full HWPX XML fidelity.
    """
    from .exporters.markdown_blocks import (
        Heading,
        ListBlock,
        Paragraph,
        Table,
        parse_markdown,
    )

    paragraphs: list[ParagraphNode] = []
    tables: list[TableNode] = []
    attachments: list[AttachmentNode] = []
    title: str | None = None

    for block in parse_markdown(markdown):
        if isinstance(block, Heading):
            text = _runs_text(block.runs)
            if title is None and text:
                title = text
            paragraphs.append(ParagraphNode(
                index=len(paragraphs),
                text=text,
                style=f"heading_{block.level}",
            ))
        elif isinstance(block, Paragraph):
            text = _runs_text(block.runs)
            paragraphs.append(ParagraphNode(
                index=len(paragraphs),
                text=text,
                style=None,
            ))
            _maybe_add_attachment(attachments, text)
        elif isinstance(block, ListBlock):
            for item in block.items:
                text = _runs_text(item)
                paragraphs.append(ParagraphNode(
                    index=len(paragraphs),
                    text=text,
                    style="ordered_list_item" if block.ordered else "bullet_list_item",
                ))
                _maybe_add_attachment(attachments, text)
        elif isinstance(block, Table):
            rows: list[list[str]] = []
            if block.header:
                rows.append([_runs_text(cell) for cell in block.header])
            rows.extend([[_runs_text(cell) for cell in row] for row in block.rows])
            tables.append(TableNode(index=len(tables), rows=rows))

    meta = dict(raw_meta or {})
    meta.setdefault("structure_source", "markdown_fallback")
    meta.setdefault("paragraph_count", len(paragraphs))
    meta.setdefault("table_count", len(tables))
    meta.setdefault("attachment_count", len(attachments))

    return DocumentModel(
        source_path=str(source_path),
        format=file_format,
        title=title,
        paragraphs=paragraphs,
        tables=tables,
        attachments=attachments,
        raw_meta=meta,
    )


def _runs_text(runs) -> str:  # noqa: ANN001
    return "".join(run.text for run in runs).strip()


def _maybe_add_attachment(attachments: list[AttachmentNode], text: str) -> None:
    if "붙임" in text:
        attachments.append(AttachmentNode(index=len(attachments), text=text))
