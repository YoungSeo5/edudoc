"""Apply an ExtractedStyleProfile to a renderer's style profile — honestly.

Maps extracted truth onto the DOCX ``DocumentStyleProfile``. Extracted values win;
fields the reference did not provide fall back to the render-side default and are
reported so the caller can record ``fallback_used`` instead of pretending the
fallback is the institution's real style.
"""
from __future__ import annotations

from dataclasses import replace

from core.exporters.style_profile import DEFAULT_GONGMUN_STYLE_PROFILE, DocumentStyleProfile

from .profiles import ExtractedStyleProfile


def to_document_style_profile(
    extracted: ExtractedStyleProfile,
    base: DocumentStyleProfile = DEFAULT_GONGMUN_STYLE_PROFILE,
) -> tuple[DocumentStyleProfile, list[str]]:
    """Return (profile, fallback_fields).

    ``fallback_fields`` lists the DocumentStyleProfile fields that came from
    ``base`` because the reference did not supply them (empty == fully extracted).
    """
    overrides: dict = {}
    fallback: list[str] = []

    def take(value, field_name: str) -> None:
        if value is not None:
            overrides[field_name] = value
        else:
            fallback.append(field_name)

    take(extracted.font_family, "font_family")
    take(extracted.body_font_size_pt, "font_size_pt")

    margins = extracted.page_margins_mm or {}
    for key, field_name in (
        ("top", "page_margin_top_mm"),
        ("bottom", "page_margin_bottom_mm"),
        ("left", "page_margin_left_mm"),
        ("right", "page_margin_right_mm"),
    ):
        take(margins.get(key), field_name)

    take(_percent_to_multiple(extracted.line_spacing), "line_spacing")

    return replace(base, **overrides), fallback


def _percent_to_multiple(value: str | None) -> float | None:
    """'160%' -> 1.6 (python-docx line-spacing multiple). Non-percent -> None."""
    if not value or not value.strip().endswith("%"):
        return None
    try:
        return round(int(value.strip().rstrip("%")) / 100, 3)
    except ValueError:
        return None
