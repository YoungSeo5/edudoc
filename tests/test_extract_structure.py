"""core.templates.extractors.structure: deterministic body-structure scan of HWPX.

Verifies the first-pass scan reports numbering markers, table shapes, and ordered
body lines from the document's own XML — and stays a candidate (no required/repeat
judgment baked in).
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.templates.extractors.structure import extract_structure

ROOT = Path(__file__).resolve().parent.parent
SAMPLE_HWPX = ROOT / "samples" / "참가신청서 및 사업계획서 양식_기창 (1).hwpx"


def test_extract_structure_reports_tables_and_lines() -> None:
    result = extract_structure(SAMPLE_HWPX)

    # the business-plan form is table-heavy -> real table shapes are reported
    assert result["tables"], "expected at least one table shape"
    first = result["tables"][0]
    assert set(first) == {"rows", "cols", "header"}
    assert first["rows"] >= 1 and first["cols"] >= 1

    assert isinstance(result["line_candidates"], list)
    assert result["paragraph_count"] >= 0
    assert "candidate" in result["note"]  # stays a candidate, not final


def test_extract_structure_detects_markers() -> None:
    # a synthetic section with mixed numbering markers
    section = (
        '<hp:p><hp:run><hp:t>1. 관련 근거</hp:t></hp:run></hp:p>'
        '<hp:p><hp:run><hp:t>  가. 세부 항목</hp:t></hp:run></hp:p>'
        '<hp:p><hp:run><hp:t>    1) 하위 항목</hp:t></hp:run></hp:p>'
    )
    xml = (
        '<?xml version="1.0"?><hs:sec xmlns:hp="x" xmlns:hs="y">'
        + section + "</hs:sec>"
    )
    with tempfile.TemporaryDirectory() as tmp:
        import zipfile
        path = Path(tmp) / "doc.hwpx"
        with zipfile.ZipFile(path, "w") as z:
            z.writestr("Contents/section0.xml", xml)
        result = extract_structure(path)

    assert result["marker_system"] == ["1.", "가.", "1)"]


if __name__ == "__main__":
    test_extract_structure_reports_tables_and_lines()
    test_extract_structure_detects_markers()
    print("PASS: extract_structure (markers + table shapes + candidate note)")
