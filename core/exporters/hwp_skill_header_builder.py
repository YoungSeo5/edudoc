"""Build a custom HWPX header.xml from an ExtractedStyleProfile (method A).

Takes the hwp-skill ``report`` template header as a read-only base and patches
only the body entries with extracted values — the HANGUL body font, the body
char size, and the body line spacing. Everything else in the header is reused
unchanged. The skill template is never modified; the patched XML is returned as a
string for the caller to pass to ``md2hwpx --header``.

Body targets in the report template (verified from templates/report/header.xml):
- body font  = HANGUL fontface font id=1 (referenced by charPr 0 fontRef hangul=1)
- body size  = charPr id=0 height (1/100 pt)
- body spacing = paraPr id=0 lineSpacing PERCENT value
"""
from __future__ import annotations

import re
from pathlib import Path

from core.templates.models import ExtractedStyleProfile

_REPORT_HEADER = (
    Path(__file__).resolve().parents[2]
    / "skills" / "hwp-skill" / "templates" / "report" / "header.xml"
)
_BODY_FONT_ID = 1
_BODY_CHARPR_ID = 0
_BODY_PARAPR_ID = 0


def build_custom_header(
    extracted: ExtractedStyleProfile,
    base_header: Path | str = _REPORT_HEADER,
) -> tuple[str, list[str]]:
    """Return (custom_header_xml, fallback_fields).

    Fields the extracted profile lacks keep the base template value and are listed
    in ``fallback_fields`` (fallback_used honesty). Page margins are not settable
    via the header (they live in section0.xml), so they are out of scope here.
    """
    xml = Path(base_header).read_text(encoding="utf-8")
    fallback: list[str] = []

    if extracted.font_family:
        xml = _set_hangul_font_face(xml, _BODY_FONT_ID, extracted.font_family)
    else:
        fallback.append("font_family")

    if extracted.body_font_size_pt:
        xml = _set_charpr_height(xml, _BODY_CHARPR_ID, round(extracted.body_font_size_pt * 100))
    else:
        fallback.append("body_font_size_pt")

    pct = _percent(extracted.line_spacing)
    if pct is not None:
        xml = _set_parapr_linespacing(xml, _BODY_PARAPR_ID, pct)
    else:
        fallback.append("line_spacing")

    return xml, fallback


def _set_hangul_font_face(xml: str, font_id: int, face: str) -> str:
    block = re.search(r'<hh:fontface lang="HANGUL"[^>]*>.*?</hh:fontface>', xml, re.S)
    if not block:
        return xml
    patched = re.sub(
        rf'(<hh:font id="{font_id}"[^>]*\bface=")[^"]*(")',
        lambda m: m.group(1) + face + m.group(2),
        block.group(0),
        count=1,
    )
    return xml[: block.start()] + patched + xml[block.end():]


def _set_charpr_height(xml: str, charpr_id: int, height: int) -> str:
    return re.sub(
        rf'(<hh:charPr id="{charpr_id}"[^>]*\bheight=")\d+(")',
        lambda m: m.group(1) + str(height) + m.group(2),
        xml,
        count=1,
    )


def _set_parapr_linespacing(xml: str, parapr_id: int, percent: int) -> str:
    block = re.search(rf'<hh:paraPr id="{parapr_id}"\b.*?</hh:paraPr>', xml, re.S)
    if not block:
        return xml
    patched = re.sub(
        r'(<hh:lineSpacing[^>]*\btype="PERCENT"[^>]*\bvalue=")\d+(")',
        lambda m: m.group(1) + str(percent) + m.group(2),
        block.group(0),
        count=1,
    )
    return xml[: block.start()] + patched + xml[block.end():]


def _percent(value: str | None) -> int | None:
    if not value or not value.strip().endswith("%"):
        return None
    try:
        return int(value.strip().rstrip("%"))
    except ValueError:
        return None
