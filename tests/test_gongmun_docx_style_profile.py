"""Loop 8.5: Gongmun DOCX 출력에 스타일 프로파일이 적용되는지 확인.

정확한 Word 렌더링이 아니라, 텍스트 보존 + 선택된 스타일 속성의 존재/근사 일치만 확인한다.
외부 오피스 소프트웨어나 PDF 파싱은 사용하지 않는다.
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH

from core.exporters.docx_exporter import DocxExporter
from core.exporters.style_profile import DEFAULT_GONGMUN_STYLE_PROFILE
from core.generators.gongmun_generator import generate_and_validate


def test_gongmun_docx_applies_style_profile() -> None:
    profile = DEFAULT_GONGMUN_STYLE_PROFILE
    root = Path(__file__).resolve().parent.parent
    brief = root / "skills" / "gongmun_writer" / "examples" / "input_brief.md"

    generated = generate_and_validate(brief)
    assert generated.passed, generated.validation_report.summary()

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        md_path = tmp_path / "gongmun.md"
        docx_path = tmp_path / "gongmun.docx"
        md_path.write_text(generated.markdown, encoding="utf-8")

        result = DocxExporter(style_profile=profile).export(md_path, docx_path)
        assert result.ok, result.error
        assert docx_path.exists(), "DOCX output missing"
        assert docx_path.stat().st_size > 0, "DOCX output is empty"

        document = Document(str(docx_path))

        # 텍스트 보존
        visible_text = "\n".join(p.text for p in document.paragraphs)
        for token in ("디지털 수업 설계 연수 참가 신청 안내", "수신", "관련", "붙임", "끝."):
            assert token in visible_text, f"visible text missing: {token}"

        # 스타일 속성 적용 (근사 일치)
        section = document.sections[0]
        assert abs(section.top_margin.mm - profile.page_margin_top_mm) < 0.5
        assert abs(section.bottom_margin.mm - profile.page_margin_bottom_mm) < 0.5
        assert abs(section.left_margin.mm - profile.page_margin_left_mm) < 0.5
        assert abs(section.right_margin.mm - profile.page_margin_right_mm) < 0.5

        normal = document.styles["Normal"]
        assert normal.font.name == profile.font_family
        assert normal.font.size is not None
        assert abs(normal.font.size.pt - profile.font_size_pt) < 0.1
        assert normal.paragraph_format.line_spacing is not None
        assert abs(normal.paragraph_format.line_spacing - profile.line_spacing) < 0.01
        assert normal.paragraph_format.space_after is not None
        assert abs(normal.paragraph_format.space_after.pt - profile.paragraph_space_after_pt) < 0.1

        heading = document.styles["Heading 1"]
        assert heading.font.size is not None
        assert abs(heading.font.size.pt - profile.heading_font_size_pt) < 0.1
        assert heading.paragraph_format.alignment == WD_ALIGN_PARAGRAPH.CENTER


if __name__ == "__main__":
    test_gongmun_docx_applies_style_profile()
    print("PASS: Gongmun DOCX style profile")
