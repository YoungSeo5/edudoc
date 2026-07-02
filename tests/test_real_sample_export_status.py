"""Loop 8.97: export status honesty for wide-table content.

DOCX is the only stabilized pip-native export target. PDF goes through the
Pandoc/Typst fallback and must NOT be reported as a stabilized default export.

Uses a plain Markdown fixture with a wide table so the test targets the export
stage itself and does not depend on HWP/HWPX parsing or on Pandoc/Typst being
installed. (The real HWP/HWPX -> unusable-PDF problem is a fallback-layout issue;
this test locks in that PDF is flagged fallback/experimental, not stabilized.)
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.pipeline import Pipeline, PipelineConfig

WIDE_TABLE_MD = """# 넓은 표 문서

| A | B | C | D | E | F | G | H |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
| 가 | 나 | 다 | 라 | 마 | 바 | 사 | 아 |

본문 문장입니다.
"""


def _entry(exports: list[dict], fmt: str) -> dict | None:
    for e in exports:
        if e["format"] == fmt:
            return e
    return None


def test_docx_stabilized_pdf_flagged_fallback() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        src = tmp_path / "wide.md"
        src.write_text(WIDE_TABLE_MD, encoding="utf-8")

        pipe = Pipeline(config=PipelineConfig(
            output_dir=tmp_path / "exports",
            export_formats=("docx", "pdf"),
        ))
        result = pipe.process_file(src)
        assert result.ok, result.error

        exports = result.meta.get("exports", [])

        docx = _entry(exports, ".docx")
        assert docx is not None, "no .docx export entry"
        assert docx["ok"] is True, docx.get("error")
        assert docx["stabilized"] is True, "DOCX should be the stabilized pip-native target"
        assert Path(docx["output"]).stat().st_size > 0, "DOCX output is empty"

        pdf = _entry(exports, ".pdf")
        assert pdf is not None, "no .pdf export entry"
        # PDF must never be presented as a stabilized default export,
        # regardless of whether the fallback engine is installed.
        assert pdf.get("stabilized") is False, "PDF must not be marked stabilized"
        assert pdf.get("experimental") is True, "PDF must be flagged experimental/fallback"


if __name__ == "__main__":
    test_docx_stabilized_pdf_flagged_fallback()
    print("PASS: DOCX stabilized, PDF flagged fallback/experimental")
