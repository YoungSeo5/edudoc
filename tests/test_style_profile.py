"""Loop 8.95: style profile behavior + custom-profile injection.

Covers the previously untested style profile layer:
- DEFAULT_GONGMUN_STYLE_PROFILE has sane values
- load_from_toml() reads the committed TOML (stdlib tomllib, no external dependency)
- load_from_toml() falls back to defaults for missing keys
- a custom DocumentStyleProfile actually changes DOCX output (not hardcoded)

The profile is project-local/conservative and does NOT claim official layout compliance.
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH

from core.exporters.docx_exporter import DocxExporter
from core.exporters.style_profile import (
    DEFAULT_GONGMUN_STYLE_PROFILE,
    DocumentStyleProfile,
    load_from_toml,
)

_VALID_ALIGNMENTS = {"left", "center", "right", "justify"}


def test_default_profile_has_sane_values() -> None:
    p = DEFAULT_GONGMUN_STYLE_PROFILE
    assert p.page_margin_top_mm > 0
    assert p.page_margin_bottom_mm > 0
    assert p.page_margin_left_mm > 0
    assert p.page_margin_right_mm > 0
    assert p.font_family.strip() != ""
    assert p.font_size_pt > 0
    assert p.heading_font_size_pt >= p.font_size_pt
    assert p.line_spacing > 0
    assert p.paragraph_space_after_pt >= 0
    assert p.heading_alignment in _VALID_ALIGNMENTS


def test_load_from_toml_matches_default() -> None:
    toml_path = (
        Path(__file__).resolve().parent.parent
        / "templates" / "gongmun" / "gyeonggi_style_profile.toml"
    )
    assert toml_path.exists(), f"style profile TOML missing: {toml_path}"
    # stdlib tomllib only; no external dependency.
    assert load_from_toml(toml_path) == DEFAULT_GONGMUN_STYLE_PROFILE, (
        "gyeonggi_style_profile.toml drifted from DEFAULT_GONGMUN_STYLE_PROFILE"
    )


def test_load_from_toml_falls_back_for_missing_keys() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        partial = Path(tmp) / "partial.toml"
        partial.write_text("[style]\nfont_size_pt = 20.0\n", encoding="utf-8")
        loaded = load_from_toml(partial)
        # overridden key applied
        assert loaded.font_size_pt == 20.0
        # missing keys fall back to default values
        assert loaded.font_family == DEFAULT_GONGMUN_STYLE_PROFILE.font_family
        assert loaded.page_margin_top_mm == DEFAULT_GONGMUN_STYLE_PROFILE.page_margin_top_mm


def test_custom_style_profile_affects_docx_output() -> None:
    custom = DocumentStyleProfile(
        page_margin_top_mm=15.0,
        page_margin_bottom_mm=15.0,
        page_margin_left_mm=15.0,
        page_margin_right_mm=15.0,
        font_family="Malgun Gothic",
        font_size_pt=9.0,
        heading_font_size_pt=22.0,
        line_spacing=2.0,
        paragraph_space_after_pt=3.0,
        heading_alignment="left",
    )
    # values chosen to differ from DEFAULT so a hardcoded profile would fail.
    assert custom.font_size_pt != DEFAULT_GONGMUN_STYLE_PROFILE.font_size_pt

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        md_path = tmp_path / "doc.md"
        docx_path = tmp_path / "doc.docx"
        md_path.write_text("# 제목\n\n본문 문장입니다.\n", encoding="utf-8")

        result = DocxExporter(style_profile=custom).export(md_path, docx_path)
        assert result.ok, result.error

        document = Document(str(docx_path))
        assert abs(document.sections[0].top_margin.mm - custom.page_margin_top_mm) < 0.5
        assert abs(document.styles["Normal"].font.size.pt - custom.font_size_pt) < 0.1
        assert abs(document.styles["Heading 1"].font.size.pt - custom.heading_font_size_pt) < 0.1
        assert document.styles["Heading 1"].paragraph_format.alignment == WD_ALIGN_PARAGRAPH.LEFT


if __name__ == "__main__":
    test_default_profile_has_sane_values()
    test_load_from_toml_matches_default()
    test_load_from_toml_falls_back_for_missing_keys()
    test_custom_style_profile_affects_docx_output()
    print("PASS: style profile behavior + custom injection")
