"""공문 형식 오염 방지: 일반 보고서 공통 경로에 공문 고유 표현/프로필이 섞이지 않는다.

- 일반(activity_report) 경로: 첨부가 있어도 [붙임]/끝. 없음, DOCX는 중립 프로필.
- 공문(profile_family="gongmun") 경로: [붙임] ... 끝. 형식과 공문 프로필을 명시적으로 선택.
- HWPX/DOCX/PPTX 렌더러가 쓰는 Markdown 모두 동일 정책을 따른다.
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.compose.render import (
    render_report_to_docx,
    render_report_to_hwpx,
    render_report_to_pptx,
)
from core.compose.report import Block, ComposedReport, Section
from core.exporters.docx_exporter import DocxExporter


def _general_report() -> ComposedReport:
    return ComposedReport(
        title="일반 활동보고서",
        doc_type="activity_report",
        sections=[Section(no="Ⅰ", title="개요", blocks=[Block("□", "활동 내용")])],
        attachments=["활동 사진 1부.", "참가자 명단 1부."],
    )


def test_general_report_markdown_has_no_gongmun_tail_across_formats() -> None:
    report = _general_report()
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)

        # DOCX / PPTX / HWPX 세 렌더러 모두 공문 꼬리 없는 Markdown을 써야 한다.
        # (HWPX는 hwp-skill 미설치 시 export가 실패할 수 있으나 Markdown은 먼저 기록된다.)
        render_report_to_docx(report, tmp_path / "r_docx.md", tmp_path / "r.docx")
        render_report_to_pptx(report, tmp_path / "r_pptx.md", tmp_path / "r.pptx")
        render_report_to_hwpx(report, tmp_path / "r_hwpx.md", tmp_path / "r.hwpx")

        for stem in ("r_docx", "r_pptx", "r_hwpx"):
            md = (tmp_path / f"{stem}.md").read_text(encoding="utf-8")
            assert "끝." not in md, f"{stem}: 일반 보고서에 공문 종결 표시가 섞임"
            assert "[붙임]" not in md, f"{stem}: 일반 보고서에 공문 첨부 표기가 섞임"
            assert "[첨부] 1. 활동 사진 1부." in md
            assert "[첨부] 2. 참가자 명단 1부." in md


def test_general_report_docx_uses_neutral_style_profile() -> None:
    report = _general_report()
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        problems, result = render_report_to_docx(
            report, tmp_path / "r.md", tmp_path / "r.docx"
        )
        assert problems == []
        assert result.ok, result.error
        assert result.meta["style_profile"] == "default_public_document"
        assert result.meta["style_profile"] != "default_gongmun"


def test_docx_exporter_default_is_not_gongmun_profile() -> None:
    exporter = DocxExporter()
    assert exporter.style_profile.profile_id == "default_public_document"


def test_gongmun_family_selects_gongmun_tail_and_profile() -> None:
    report = _general_report()
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        problems, result = render_report_to_docx(
            report, tmp_path / "g.md", tmp_path / "g.docx", profile_family="gongmun"
        )
        assert problems == []
        assert result.ok, result.error
        assert result.meta["style_profile"] == "default_gongmun"

        md = (tmp_path / "g.md").read_text(encoding="utf-8")
        assert "[붙임] 1. 활동 사진 1부." in md
        assert "[붙임] 2. 참가자 명단 1부.  끝." in md


if __name__ == "__main__":
    test_general_report_markdown_has_no_gongmun_tail_across_formats()
    test_general_report_docx_uses_neutral_style_profile()
    test_docx_exporter_default_is_not_gongmun_profile()
    test_gongmun_family_selects_gongmun_tail_and_profile()
    print("PASS: compose profile separation (no Gongmun leakage on general paths)")
