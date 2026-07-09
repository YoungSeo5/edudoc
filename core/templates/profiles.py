"""Data contracts for institution template profiles."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ExtractedStyleProfile:
    """Style values pulled from a reference document — extracted, never defaulted.

    A field stays ``None`` when the reference does not provide it. A renderer must
    fall back explicitly (and record that it did) rather than treat ``None`` as a
    real institution value. ``confidence`` and ``evidence`` let downstream steps
    tell extracted truth apart from a guess.
    """

    source: str = "unknown"                    # extracted_from_hwpx | unknown
    font_family: str | None = None
    body_font_size_pt: float | None = None
    page_margins_mm: dict | None = None        # {top, bottom, left, right}
    line_spacing: str | None = None            # e.g. "160%"
    heading_styles: list[dict] = field(default_factory=list)
    table_style: dict | None = None
    confidence: str = "low"                    # high | medium | low
    evidence: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class RendererContract:
    """How this template is rendered — maps to existing edudoc/hwp-skill routes."""

    preferred_format: str = "hwpx"
    route: str = "md2hwpx"                      # gonmun | gyeonggi_gonmun | md2hwpx | ...
    reference_hwpx: str | None = None          # style reference document, if any
    fallback: str = "md2hwpx"


@dataclass
class TemplateProfile:
    """An institution/document template: content structure + writing rules + style.

    ``structure`` and ``writing_rules`` start as a machine candidate and are meant
    to be curated by the template-extractor skill (required/optional, tone). The
    code fills what is verifiable; unresolved judgment stays as "확인 필요".
    """

    institution: str
    document_type: str
    extends: str | None = None
    structure: dict = field(default_factory=dict)
    writing_rules: dict = field(default_factory=dict)
    style_profile: ExtractedStyleProfile = field(default_factory=ExtractedStyleProfile)
    renderer: RendererContract = field(default_factory=RendererContract)
