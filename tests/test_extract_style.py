"""core.templates.extractors.style: deterministic style extraction from HWPX.

Proves the extractor pulls real font/size/margin/spacing values out of an HWPX's
own XML (with evidence), and stays honest — non-HWPX inputs yield no values, not
a guessed default.
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.templates.extractors.style import extract_style

ROOT = Path(__file__).resolve().parent.parent
SAMPLE_HWPX = ROOT / "samples" / "참가신청서 및 사업계획서 양식_기창 (1).hwpx"


def test_extract_style_from_hwpx() -> None:
    profile = extract_style(SAMPLE_HWPX)

    assert profile.source == "extracted_from_hwpx"
    assert profile.confidence == "high"
    # values come straight from the document XML, not a default
    assert profile.font_family == "휴먼명조"
    assert profile.body_font_size_pt == 12.0
    assert profile.page_margins_mm == {"top": 15.0, "bottom": 15.0, "left": 15.0, "right": 15.0}
    assert profile.line_spacing == "160%"
    assert profile.evidence == ["Contents/header.xml", "Contents/section0.xml"]


def test_extract_style_non_hwpx_is_honest() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        fake = Path(tmp) / "reference.pdf"
        fake.write_bytes(b"%PDF-1.7 not a real hwpx package")

        profile = extract_style(fake)

    assert profile.source == "unknown"
    assert profile.confidence == "low"
    # nothing is invented when the reference cannot be read
    assert profile.font_family is None
    assert profile.body_font_size_pt is None
    assert profile.page_margins_mm is None
    assert any("not an HWPX" in e for e in profile.evidence)


if __name__ == "__main__":
    test_extract_style_from_hwpx()
    test_extract_style_non_hwpx_is_honest()
    print("PASS: extract_style (HWPX style extraction + non-HWPX honesty)")
