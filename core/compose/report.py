"""ComposedReport: the agent↔glue content contract, and a clean Markdown renderer.

Design rules (fix past mistakes):
- Sections render as Markdown headings, NOT tables.
- Body hierarchy uses official public-document markers □ / ○ / ― / ※ as paragraph text.
- Markdown tables are emitted ONLY from explicit `Table` objects (real tabular data).
- Unknown facts must be written as "확인 필요" by the agent; the validator flags leftovers.
"""
from __future__ import annotations

from dataclasses import dataclass, field

UNKNOWN = "확인 필요"
_MARKERS = ("□", "○", "―", "※")
# leading indent per marker level (visual hierarchy; md-it keeps it as paragraph text)
_INDENT = {"□": "", "○": "  ", "―": "   ", "※": "     "}
# placeholder strings that must never survive into a finished report
_PLACEHOLDER_HINTS = ("헤드라인M", "휴면명조", "포인트(문단", "세부내용")


@dataclass
class Block:
    """One body line. marker ∈ {□,○,―,※} or "" for a plain paragraph."""
    marker: str
    text: str


@dataclass
class Section:
    no: str            # "Ⅰ", "Ⅱ", ... or "1", "2"
    title: str
    blocks: list[Block] = field(default_factory=list)


@dataclass
class Table:
    """Real tabular data only (rendered as a GFM table)."""
    caption: str
    header: list[str]
    rows: list[list[str]]


@dataclass
class ComposedReport:
    title: str
    doc_type: str = "activity_report"
    meta: list[tuple[str, str]] = field(default_factory=list)   # (label, value) header lines
    summary_table: Table | None = None
    sections: list[Section] = field(default_factory=list)
    attachments: list[str] = field(default_factory=list)

    # --- construction ---------------------------------------------------

    @classmethod
    def from_dict(cls, data: dict) -> "ComposedReport":
        return cls(
            title=data["title"],
            doc_type=data.get("doc_type", "activity_report"),
            meta=[tuple(pair) for pair in data.get("meta", [])],
            summary_table=_table_from_dict(data.get("summary_table")),
            sections=[
                Section(
                    no=s["no"],
                    title=s["title"],
                    blocks=[Block(b.get("marker", ""), b["text"]) for b in s.get("blocks", [])],
                )
                for s in data.get("sections", [])
            ],
            attachments=list(data.get("attachments", [])),
        )

    # --- rendering ------------------------------------------------------

    def to_markdown(self) -> str:
        lines: list[str] = [f"# {self.title}", ""]

        for label, value in self.meta:
            lines.append(f"{label}: {value}")
        if self.meta:
            lines.append("")

        if self.summary_table is not None:
            lines.extend(_table_to_markdown(self.summary_table))
            lines.append("")

        for section in self.sections:
            heading = f"{section.no}. {section.title}".strip(". ")
            lines.append(f"## {heading}")
            lines.append("")
            for block in section.blocks:
                if block.marker in _MARKERS:
                    lines.append(f"{_INDENT[block.marker]}{block.marker} {block.text}")
                else:
                    lines.append(block.text)
                lines.append("")  # blank line -> separate paragraph per block

        if self.attachments:
            for i, att in enumerate(self.attachments, 1):
                tail = "  끝." if i == len(self.attachments) else ""
                lines.append(f"[붙임] {i}. {att}{tail}")
                lines.append("")

        return "\n".join(lines).rstrip() + "\n"


def _table_from_dict(data: dict | None) -> Table | None:
    if not data:
        return None
    return Table(
        caption=data.get("caption", ""),
        header=list(data["header"]),
        rows=[list(r) for r in data.get("rows", [])],
    )


def _table_to_markdown(table: Table) -> list[str]:
    out: list[str] = []
    if table.caption:
        out.extend([f"**{table.caption}**", ""])
    out.append("| " + " | ".join(table.header) + " |")
    out.append("| " + " | ".join("---" for _ in table.header) + " |")
    for row in table.rows:
        padded = list(row) + [""] * (len(table.header) - len(row))
        out.append("| " + " | ".join(padded[: len(table.header)]) + " |")
    return out


def validate_report(report: ComposedReport) -> list[str]:
    """Return a list of problems (empty = ok). Deterministic structural checks."""
    problems: list[str] = []
    if not report.title.strip():
        problems.append("title is empty")
    if not report.sections:
        problems.append("no sections")
    for section in report.sections:
        if not section.blocks:
            problems.append(f"section '{section.no} {section.title}' has no content")
        for block in section.blocks:
            for hint in _PLACEHOLDER_HINTS:
                if hint in block.text:
                    problems.append(
                        f"placeholder text leaked into section '{section.title}': {hint}"
                    )
    return problems
