"""Validated Gongmun Markdown -> DOCX export status and content test."""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from docx import Document

from core.exporters.style_profile import DEFAULT_GONGMUN_STYLE_PROFILE
from core.pipeline import Pipeline, PipelineConfig
from validators.gongmun_rules import validate


FIXTURE = Path(__file__).resolve().parent / "fixtures" / "gongmun" / "valid_gongmun.md"


def test_validated_gongmun_markdown_exports_to_docx_with_metadata() -> None:
    text = FIXTURE.read_text(encoding="utf-8")
    report = validate(text)
    assert report.passed, report.summary()

    with tempfile.TemporaryDirectory() as tmp:
        pipe = Pipeline(config=PipelineConfig(
            output_dir=Path(tmp) / "exports",
            export_formats=("docx",),
        ))
        result = pipe.process_file(FIXTURE)
        assert result.ok, result.error

        exports = result.meta.get("exports", [])
        assert len(exports) == 1
        entry = exports[0]

        assert entry["format"] == ".docx"
        assert entry["ok"] is True, entry.get("error")
        assert entry["exporter"] == "DocxExporter"
        assert entry["status"] == "partially_stabilized"
        assert entry["stabilized"] is True
        assert entry["experimental"] is False
        assert entry["requires_optional_tool"] is False
        assert entry["path"] == entry["output"]
        assert entry["note"]

        docx_path = Path(entry["path"])
        assert docx_path.exists()
        assert docx_path.stat().st_size > 0

        document = Document(str(docx_path))
        visible_text = "\n".join(p.text for p in document.paragraphs)
        assert "교육과정 수업 설계 연수 참가 신청 안내" in visible_text
        assert "수신:" in visible_text
        assert "관련" in visible_text
        assert "2026. 7. 15." in visible_text
        assert "붙임" in visible_text
        assert "끝." in visible_text
        assert abs(
            document.sections[0].top_margin.mm
            - DEFAULT_GONGMUN_STYLE_PROFILE.page_margin_top_mm
        ) < 0.5


if __name__ == "__main__":
    test_validated_gongmun_markdown_exports_to_docx_with_metadata()
    print("PASS: validated Gongmun Markdown -> DOCX metadata")
