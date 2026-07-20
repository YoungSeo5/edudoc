"""core.exporters.extracted_style_mapper + DOCX round-trip.

Proves (1) extracted style maps onto DocumentStyleProfile with honest fallback
tracking, and (2) a DOCX rendered with a style_reference actually carries the
extracted font/size/margins — not the fixed default.
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from docx import Document

from core.compose.render import render_report_to_docx
from core.compose.report import ComposedReport
from core.exporters.style_profile import DEFAULT_PUBLIC_DOCUMENT_STYLE_PROFILE
from core.exporters.extracted_style_mapper import to_document_style_profile
from core.templates.models import ExtractedStyleProfile

ROOT = Path(__file__).resolve().parent.parent
SAMPLE_HWPX = ROOT / "samples" / "참가신청서 및 사업계획서 양식_기창 (1).hwpx"


def test_mapping_extracted_wins_no_fallback() -> None:
    extracted = ExtractedStyleProfile(
        source="extracted_from_hwpx", font_family="휴먼명조", body_font_size_pt=12.0,
        page_margins_mm={"top": 15.0, "bottom": 15.0, "left": 15.0, "right": 15.0},
        line_spacing="160%", confidence="high",
    )
    profile, fallback = to_document_style_profile(extracted)

    assert profile.font_family == "휴먼명조"
    assert profile.font_size_pt == 12.0
    assert profile.page_margin_left_mm == 15.0
    assert profile.line_spacing == 1.6
    assert fallback == []  # everything came from the reference


def test_mapping_missing_values_fall_back_and_are_reported() -> None:
    profile, fallback = to_document_style_profile(ExtractedStyleProfile())

    # missing font falls back to the neutral default and is reported, not invented
    assert profile.font_family == DEFAULT_PUBLIC_DOCUMENT_STYLE_PROFILE.font_family
    assert "font_family" in fallback
    assert "font_size_pt" in fallback
    assert "line_spacing" in fallback


def test_docx_round_trip_uses_extracted_font() -> None:
    report = ComposedReport(
        title="스타일 왕복 테스트",
        sections=[__import__("core.compose.report", fromlist=["Section"]).Section(
            no="Ⅰ", title="개요",
            blocks=[__import__("core.compose.report", fromlist=["Block"]).Block("□", "본문")],
        )],
    )
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        md, docx = tmp / "r.md", tmp / "r.docx"
        problems, result = render_report_to_docx(report, md, docx, style_reference=SAMPLE_HWPX)

        assert result.ok, result.error
        assert result.meta["style_source"] == "extracted"
        assert result.meta["style_fallback_used"] is False  # sample yields full style

        doc = Document(str(docx))
        assert doc.styles["Normal"].font.name == "휴먼명조"      # extracted, not "Malgun Gothic"
        assert doc.styles["Normal"].font.size.pt == 12.0        # extracted, not 11.0
        assert round(doc.sections[0].left_margin.mm) == 15      # extracted, not 20


if __name__ == "__main__":
    test_mapping_extracted_wins_no_fallback()
    test_mapping_missing_values_fall_back_and_are_reported()
    test_docx_round_trip_uses_extracted_font()
    print("PASS: apply_style mapping + DOCX round-trip uses extracted font")
