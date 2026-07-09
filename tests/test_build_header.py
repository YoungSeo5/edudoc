"""core.templates.build_header + HWPX round-trip.

Proves (1) an ExtractedStyleProfile patches the body font/size/spacing into a copy
of the report header (skill template untouched), with honest fallback tracking,
and (2) a HWPX rendered with a style_reference actually carries the extracted body
font/size — not the template default.
"""
from __future__ import annotations

import re
import sys
import tempfile
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.compose.render import render_report_to_hwpx
from core.compose.report import Block, ComposedReport, Section
from core.templates.build_header import build_custom_header
from core.templates.profiles import ExtractedStyleProfile

ROOT = Path(__file__).resolve().parent.parent
SAMPLE_HWPX = ROOT / "samples" / "참가신청서 및 사업계획서 양식_기창 (1).hwpx"


def _hangul_font1(header: str) -> str:
    block = re.search(r'<hh:fontface lang="HANGUL"[^>]*>(.*?)</hh:fontface>', header, re.S).group(1)
    return re.search(r'<hh:font id="1"[^>]*face="([^"]+)"', block).group(1)


def _charpr0_height(header: str) -> int:
    attrs = re.search(r'<hh:charPr id="0"([^>]*)>', header).group(1)
    return int(re.search(r'height="(\d+)"', attrs).group(1))


def test_build_header_patches_body_and_tracks_fallback() -> None:
    extracted = ExtractedStyleProfile(
        source="extracted_from_hwpx", font_family="휴먼명조",
        body_font_size_pt=12.0, line_spacing="160%", confidence="high",
    )
    xml, fallback = build_custom_header(extracted)

    assert _hangul_font1(xml) == "휴먼명조"          # body font patched
    assert _charpr0_height(xml) == 1200              # 12pt -> height 1200
    assert fallback == []

    # empty profile keeps the template's own values and reports the fallback
    xml2, fallback2 = build_custom_header(ExtractedStyleProfile())
    assert _hangul_font1(xml2) == "함초롬바탕"        # unchanged base body font
    assert "font_family" in fallback2 and "body_font_size_pt" in fallback2


def test_hwpx_round_trip_uses_extracted_font() -> None:
    report = ComposedReport(
        title="스타일 왕복 HWPX",
        sections=[Section(no="Ⅰ", title="개요", blocks=[Block("□", "본문")])],
    )
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        _, result = render_report_to_hwpx(
            report, tmp / "r.md", tmp / "r.hwpx", style_reference=SAMPLE_HWPX
        )
        assert result.ok, result.error
        assert result.meta["style_source"] == "extracted"
        assert result.meta["style_fallback_used"] is False

        header = zipfile.ZipFile(tmp / "r.hwpx").read("Contents/header.xml").decode("utf-8")
        assert _hangul_font1(header) == "휴먼명조"     # extracted, not 함초롬바탕
        assert _charpr0_height(header) == 1200         # extracted 12pt, not 10pt


if __name__ == "__main__":
    test_build_header_patches_body_and_tracks_fallback()
    test_hwpx_round_trip_uses_extracted_font()
    print("PASS: build_header patch + HWPX round-trip uses extracted font")
