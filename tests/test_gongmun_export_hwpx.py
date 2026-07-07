"""Validated Gongmun Markdown -> minimal HWPX package export test."""
from __future__ import annotations

import sys
import tempfile
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.exporters.hwpx_exporter import HwpxExporter
from core.pipeline import Pipeline, PipelineConfig
from validators.gongmun_rules import validate as validate_gongmun
from validators.hwpx_package_rules import validate as validate_hwpx_package


FIXTURE = Path(__file__).resolve().parent / "fixtures" / "gongmun" / "valid_gongmun.md"
REQUIRED = {
    "mimetype",
    "META-INF/manifest.xml",
    "Contents/content.hpf",
    "Contents/header.xml",
    "Contents/section0.xml",
    "Preview/PrvText.txt",
}


def test_validated_gongmun_markdown_exports_to_minimal_hwpx() -> None:
    text = FIXTURE.read_text(encoding="utf-8")
    gongmun_report = validate_gongmun(text)
    assert gongmun_report.passed, gongmun_report.summary()

    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "gongmun.hwpx"
        result = HwpxExporter().export(FIXTURE, out)

        assert result.ok, result.error
        assert result.meta["exporter"] == "HwpxExporter"
        assert result.meta["requires_optional_tool"] is False
        assert result.meta["validation_passed"] is True

        report = validate_hwpx_package(out)
        assert report.passed, report.summary()

        with zipfile.ZipFile(out) as zf:
            names = set(zf.namelist())
            assert REQUIRED.issubset(names)
            assert zf.namelist()[0] == "mimetype"
            assert zf.read("mimetype").decode("utf-8") == "application/hwp+zip"
            preview = zf.read("Preview/PrvText.txt").decode("utf-8")
            section = zf.read("Contents/section0.xml").decode("utf-8")

        assert "교육과정 수업 설계 연수 참가 신청 안내" in preview
        assert "관련" in preview
        assert "2026. 7. 15." in preview
        assert "붙임" in preview
        assert "끝." in preview
        assert "<hp:t>" in section


def test_pipeline_hwpx_export_reports_experimental_metadata() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        pipe = Pipeline(config=PipelineConfig(
            output_dir=Path(tmp) / "exports",
            export_formats=("hwpx",),
        ))
        result = pipe.process_file(FIXTURE)
        assert result.ok, result.error

        exports = result.meta.get("exports", [])
        assert len(exports) == 1
        entry = exports[0]

        assert entry["format"] == ".hwpx"
        assert entry["ok"] is True, entry.get("error")
        assert entry["exporter"] == "HwpxExporter"
        assert entry["status"] == "experimental"
        assert entry["stabilized"] is False
        assert entry["experimental"] is True
        assert entry["requires_optional_tool"] is False
        assert entry["path"] == entry["output"]
        assert entry["note"]
        assert Path(entry["path"]).exists()


if __name__ == "__main__":
    test_validated_gongmun_markdown_exports_to_minimal_hwpx()
    test_pipeline_hwpx_export_reports_experimental_metadata()
    print("PASS: validated Gongmun Markdown -> HWPX")
