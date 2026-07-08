"""Lock the PPTX wiring: pipeline `--export pptx` and compose render_report_to_pptx.

Ensures `.pptx` routes to the pip-native PptxExporter (not the Pandoc fallback)
and is reported as a stabilized export, and that compose can render a report to
PPTX in one call.
"""
from __future__ import annotations

import sys
import tempfile
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.compose.render import render_report_to_pptx
from core.compose.report import Block, ComposedReport, Section
from core.pipeline import Pipeline, PipelineConfig


def test_pipeline_routes_pptx_to_pptx_exporter() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        src = tmp / "r.md"
        src.write_text("# 보고서\n\n## 개요\n\n□ 항목\n", encoding="utf-8")
        pipe = Pipeline(config=PipelineConfig(output_dir=tmp / "out", export_formats=("pptx",)))
        result = pipe.process_file(src)

        entry = next(e for e in result.meta["exports"] if e["format"] == ".pptx")
        assert entry["exporter"] == "PptxExporter", entry
        assert entry["ok"] is True, entry.get("error")
        assert entry["stabilized"] is True  # pip-native, not Pandoc fallback
        assert Path(entry["output"]).read_bytes()[:2] == b"PK"


def test_compose_render_report_to_pptx() -> None:
    report = ComposedReport(
        title="테스트 보고서",
        sections=[
            Section(no="Ⅰ", title="개요", blocks=[Block("□", "요약"), Block("○", "세부")]),
        ],
    )
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        problems, result = render_report_to_pptx(report, tmp / "r.md", tmp / "r.pptx")
        assert problems == []
        assert result.ok, result.error
        with zipfile.ZipFile(tmp / "r.pptx") as z:
            slides = [n for n in z.namelist() if n.startswith("ppt/slides/slide")]
        assert len(slides) >= 2  # title + section slide


if __name__ == "__main__":
    test_pipeline_routes_pptx_to_pptx_exporter()
    test_compose_render_report_to_pptx()
    print("PASS: PPTX wiring (pipeline + compose)")
