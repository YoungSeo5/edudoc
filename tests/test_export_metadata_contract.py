"""Export metadata contract for Loop 8 outputs."""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.pipeline import Pipeline, PipelineConfig


FIXTURE = Path(__file__).resolve().parent / "fixtures" / "gongmun" / "valid_gongmun.md"
REQUIRED_KEYS = {
    "format",
    "ok",
    "path",
    "output",
    "exporter",
    "stabilized",
    "experimental",
    "requires_optional_tool",
    "status",
    "note",
    "error",
}


def _by_format(exports: list[dict], fmt: str) -> dict:
    for entry in exports:
        if entry["format"] == fmt:
            return entry
    raise AssertionError(f"missing export entry: {fmt}")


def test_export_metadata_contract_for_docx_pdf_hwpx() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        pipe = Pipeline(config=PipelineConfig(
            output_dir=Path(tmp) / "exports",
            export_formats=("docx", "pdf", "hwpx"),
        ))
        result = pipe.process_file(FIXTURE)
        assert result.ok, result.error

        exports = result.meta.get("exports", [])
        assert len(exports) == 3
        for entry in exports:
            assert REQUIRED_KEYS.issubset(entry.keys())
            assert entry["path"] == entry["output"]
            assert entry["status"] in {
                "stable",
                "partially_stabilized",
                "fallback",
                "experimental",
                "unsupported",
                "failed",
            }

        docx = _by_format(exports, ".docx")
        assert docx["exporter"] == "DocxExporter"
        assert docx["status"] == "partially_stabilized"
        assert docx["stabilized"] is True
        assert docx["experimental"] is False
        assert docx["requires_optional_tool"] is False

        pdf = _by_format(exports, ".pdf")
        assert pdf["exporter"] == "OfficeExporter"
        assert pdf["status"] in {"fallback", "failed"}
        assert pdf["stabilized"] is False
        assert pdf["experimental"] is True
        assert pdf["requires_optional_tool"] is True

        hwpx = _by_format(exports, ".hwpx")
        assert hwpx["exporter"] == "HwpxExporter"
        assert hwpx["status"] == "experimental"
        assert hwpx["stabilized"] is False
        assert hwpx["experimental"] is True
        assert hwpx["requires_optional_tool"] is False


if __name__ == "__main__":
    test_export_metadata_contract_for_docx_pdf_hwpx()
    print("PASS: export metadata contract")
