"""Loop 8.99: PDF export must be reported as fallback/experimental, not stable.

Locks in that pipeline `.pdf` export does NOT use the pip-native DocxExporter, is
flagged `stabilized: False` + `experimental: True`, and fails in a structured way if
the fallback engine is missing. Does NOT assert visual PDF correctness (the point is
to prevent false confidence, independent of whether Pandoc/Typst is installed).
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.pipeline import Pipeline, PipelineConfig

FIXTURE = (
    Path(__file__).resolve().parent
    / "fixtures" / "export" / "wide_table_activity_report.md"
)


def _entry(exports: list[dict], fmt: str) -> dict | None:
    for e in exports:
        if e["format"] == fmt:
            return e
    return None


def test_pdf_export_is_fallback_not_stable() -> None:
    assert FIXTURE.exists(), f"fixture missing: {FIXTURE}"

    with tempfile.TemporaryDirectory() as tmp:
        pipe = Pipeline(config=PipelineConfig(
            output_dir=Path(tmp) / "exports",
            export_formats=("docx", "pdf"),
        ))
        result = pipe.process_file(FIXTURE)
        assert result.ok, result.error

        exports = result.meta.get("exports", [])

        docx = _entry(exports, ".docx")
        assert docx is not None, "no .docx export entry"
        assert docx["exporter"] == "DocxExporter"
        assert docx["stabilized"] is True

        pdf = _entry(exports, ".pdf")
        assert pdf is not None, "no .pdf export entry"
        # PDF must never be presented as stable, and must not use the DOCX exporter.
        assert pdf["exporter"] != "DocxExporter"
        assert pdf["exporter"] == "OfficeExporter"
        assert pdf.get("stabilized") is False
        assert pdf.get("experimental") is True
        # if the fallback engine is missing, the failure is structured (no crash)
        if not pdf["ok"]:
            assert isinstance(pdf.get("error"), str) and pdf["error"].strip()


if __name__ == "__main__":
    test_pdf_export_is_fallback_not_stable()
    print("PASS: PDF export is fallback/experimental, not stable")
