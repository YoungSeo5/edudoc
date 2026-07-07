"""compose Phase 2: ComposedReport renders clean structure (fix for fake-table bug).

Locks the rules: sections -> Markdown headings (never tables); tables only from
explicit Table data; □/○/― body markers; validator catches placeholder leftovers.
"""
from __future__ import annotations

import re
import sys
import tempfile
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.compose.report import Block, ComposedReport, Section, Table, validate_report


def _sample() -> ComposedReport:
    return ComposedReport(
        title="테스트 결과보고서",
        meta=[("작성자", "홍길동")],
        summary_table=Table(caption="개요", header=["구분", "값"], rows=[["A", "1"], ["B", "2"]]),
        sections=[
            Section(no="Ⅰ", title="개요", blocks=[
                Block("□", "상위 항목"), Block("○", "하위 항목"), Block("―", "세부"),
            ]),
            Section(no="Ⅱ", title="현황", blocks=[Block("□", "현황 설명")]),
        ],
        attachments=["첨부 1부."],
    )


def test_sections_are_headings_not_tables() -> None:
    md = _sample().to_markdown()
    # sections render as headings
    assert "## Ⅰ. 개요" in md
    assert "## Ⅱ. 현황" in md
    # exactly one table (the summary_table), i.e. one GFM delimiter row
    assert len(re.findall(r"^\| --- ", md, flags=re.MULTILINE)) == 1, md
    # section titles are NOT inside a table row
    assert "| 개요 |" not in md and "| Ⅰ |" not in md
    # official markers present
    assert "□ 상위 항목" in md and "○ 하위 항목" in md and "― 세부" in md
    # attachment + end mark
    assert "[붙임] 1. 첨부 1부.  끝." in md


def test_validator_flags_placeholder_leftover() -> None:
    bad = ComposedReport(
        title="x",
        sections=[Section(no="Ⅰ", title="개요", blocks=[Block("□", "헤드라인M 폰트 16포인트")])],
    )
    problems = validate_report(bad)
    assert any("placeholder" in p for p in problems), problems


def test_clean_report_validates() -> None:
    assert validate_report(_sample()) == []


def test_optional_hwpx_render_has_one_real_table() -> int:
    from core.compose.render import render_report_to_hwpx

    with tempfile.TemporaryDirectory() as tmp:
        md = Path(tmp) / "r.md"
        out = Path(tmp) / "r.hwpx"
        problems, result = render_report_to_hwpx(_sample(), md, out)
        assert problems == []
        if result.meta.get("available") is False:
            print("SKIP: hwp-skill not present; HWPX render not exercised")
            return 0
        assert result.ok, result.error
        section = zipfile.ZipFile(out).read("Contents/section0.xml").decode("utf-8")
        assert len(re.findall(r"<hp:tbl", section)) == 1, "expected exactly one real table"
    return 0


if __name__ == "__main__":
    test_sections_are_headings_not_tables()
    test_validator_flags_placeholder_leftover()
    test_clean_report_validates()
    test_optional_hwpx_render_has_one_real_table()
    print("PASS: compose report clean structure")
