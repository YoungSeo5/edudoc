"""Validated Gongmun Markdown -> DOCX export smoke test."""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from docx import Document

from core.exporters.docx_exporter import DocxExporter
from core.exporters.style_profile import DEFAULT_GONGMUN_STYLE_PROFILE
from core.generators.gongmun_generator import generate_and_validate


def test_validated_gongmun_markdown_exports_to_docx() -> None:
    root = Path(__file__).resolve().parent.parent
    brief = root / "skills" / "gongmun_writer" / "examples" / "input_brief.md"

    generated = generate_and_validate(brief)
    assert generated.passed, generated.validation_report.summary()

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        markdown_path = tmp_path / "gongmun.generated.md"
        docx_path = tmp_path / "gongmun.generated.docx"
        markdown_path.write_text(generated.markdown, encoding="utf-8")

        result = DocxExporter(style_profile=DEFAULT_GONGMUN_STYLE_PROFILE).export(
            markdown_path, docx_path
        )

        assert result.ok, result.error
        assert docx_path.exists(), "DOCX output missing"
        assert docx_path.stat().st_size > 0, "DOCX output is empty"

        document = Document(str(docx_path))
        visible_text = "\n".join(p.text for p in document.paragraphs)

        assert "디지털 수업 설계 연수 참가 신청 안내" in visible_text
        assert "수신: 관내 초·중·고등학교장" in visible_text
        assert "관련: 2026년 교원 역량 강화 연수 운영 계획" in visible_text
        assert "붙임  참가 신청서 1부.  끝." in visible_text
        assert "끝." in visible_text


if __name__ == "__main__":
    test_validated_gongmun_markdown_exports_to_docx()
    print("PASS: Gongmun Markdown -> DOCX export")
