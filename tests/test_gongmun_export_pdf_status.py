"""Validated Gongmun Markdown -> PDF status honesty test."""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.pipeline import Pipeline, PipelineConfig
from validators.gongmun_rules import validate


FIXTURE = Path(__file__).resolve().parent / "fixtures" / "gongmun" / "valid_gongmun.md"


def test_validated_gongmun_pdf_export_remains_fallback_or_failed() -> None:
    text = FIXTURE.read_text(encoding="utf-8")
    report = validate(text)
    assert report.passed, report.summary()

    with tempfile.TemporaryDirectory() as tmp:
        pipe = Pipeline(config=PipelineConfig(
            output_dir=Path(tmp) / "exports",
            export_formats=("pdf",),
        ))
        result = pipe.process_file(FIXTURE)
        assert result.ok, result.error

        exports = result.meta.get("exports", [])
        assert len(exports) == 1
        entry = exports[0]

        assert entry["format"] == ".pdf"
        assert entry["exporter"] == "OfficeExporter"
        assert entry["stabilized"] is False
        assert entry["experimental"] is True
        assert entry["requires_optional_tool"] is True
        assert entry["status"] in {"fallback", "failed"}
        assert entry["path"] == entry["output"]
        assert entry["note"]

        if entry["ok"]:
            assert Path(entry["path"]).exists()
            assert Path(entry["path"]).stat().st_size > 0
        else:
            assert isinstance(entry["error"], str) and entry["error"].strip()


if __name__ == "__main__":
    test_validated_gongmun_pdf_export_remains_fallback_or_failed()
    print("PASS: validated Gongmun Markdown -> PDF status honesty")
