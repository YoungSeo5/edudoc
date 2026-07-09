"""Build a candidate TemplateProfile from a reference document.

Orchestration only: it combines the deterministic style + structure extractors
into one candidate profile and marks the parts that need skill curation as
"확인 필요". It never invents required sections, tone, or defaulted style.
"""
from __future__ import annotations

from pathlib import Path

from .extract_structure import extract_structure
from .extract_style import extract_style
from .profiles import RendererContract, TemplateProfile

UNKNOWN = "확인 필요"


def build_candidate(
    reference: Path | str,
    *,
    institution: str,
    document_type: str,
    route: str = "gyeonggi_gonmun",
    extends: str | None = None,
) -> TemplateProfile:
    """Return a candidate profile: verifiable facts filled, judgment left as 확인 필요."""
    reference = Path(reference)
    style = extract_style(reference)
    structure = extract_structure(reference)

    return TemplateProfile(
        institution=institution,
        document_type=document_type,
        extends=extends,
        structure={
            "required_sections": UNKNOWN,      # 스킬이 확정
            "required_fields": UNKNOWN,
            "repeat_sections": UNKNOWN,
            "numbering_style": structure["marker_system"],
            "tables": structure["tables"],
            "line_candidates": structure["line_candidates"],
            "paragraph_count": structure["paragraph_count"],
        },
        writing_rules={"tone": UNKNOWN, "unknown_policy": UNKNOWN},
        style_profile=style,
        renderer=RendererContract(
            preferred_format="hwpx",
            route=route,
            reference_hwpx=str(reference),
            fallback="md2hwpx",
        ),
    )
