"""DOCX exporter should expose table quality metadata."""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.exporters.docx_exporter import DocxExporter
from core.pipeline import Pipeline, PipelineConfig


FIXTURE = Path(__file__).resolve().parent / "fixtures" / "export" / "wide_activity_report.md"


def test_docx_exporter_reports_wide_table_metadata() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "wide.docx"
        result = DocxExporter().export(FIXTURE, out)

        assert result.ok, result.error
        assert result.meta["format"] == ".docx"
        assert result.meta["table_count"] == 3
        assert result.meta["max_table_column_count"] == 10
        assert result.meta["wide_table_detected"] is True
        assert result.meta["wide_table_strategy"] == "landscape_compact_table"
        assert result.meta["warnings"]


def test_pipeline_export_entry_includes_table_quality_metadata() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        pipe = Pipeline(config=PipelineConfig(
            output_dir=Path(tmp) / "exports",
            export_formats=("docx", "pdf", "hwpx"),
        ))
        result = pipe.process_file(FIXTURE)
        assert result.ok, result.error

        exports = {entry["format"]: entry for entry in result.meta["exports"]}

        docx = exports[".docx"]
        assert docx["status"] == "partially_stabilized"
        assert docx["table_count"] == 3
        assert docx["max_table_column_count"] == 10
        assert docx["wide_table_detected"] is True
        assert docx["wide_table_strategy"] == "landscape_compact_table"
        assert docx["warnings"]

        assert exports[".pdf"]["experimental"] is True
        assert exports[".pdf"]["stabilized"] is False
        assert exports[".hwpx"]["experimental"] is True
        assert exports[".hwpx"]["stabilized"] is False


if __name__ == "__main__":
    test_docx_exporter_reports_wide_table_metadata()
    test_pipeline_export_entry_includes_table_quality_metadata()
    print("PASS: DOCX wide table metadata")
