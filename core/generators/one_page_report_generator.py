"""Generate a one-page-report Markdown draft from a validated template shape."""
from __future__ import annotations

from typing import Any

from core.templates.models import TemplateCandidate

UNKNOWN = "확인 필요"


def build_skeleton(candidate: TemplateCandidate) -> str:
    """Return a structure-only skeleton with no invented facts."""
    markers = candidate.structure.get("marker_system") or ["1.", "□", "○", "-"]
    lines = [
        f"# {candidate.identity.document_type} 스켈레톤 (구조 전용)",
        f"> 참조: {candidate.reference_path} | "
        f"스타일: {candidate.style_profile.source}/{candidate.style_profile.confidence}",
        "",
        f"제목: {UNKNOWN}",
        "",
    ]
    for level, marker in enumerate(markers):
        lines.append(f"{'  ' * level}{marker} {UNKNOWN}")
    return "\n".join(lines) + "\n"


def build_draft(candidate: TemplateCandidate, source_facts: dict[str, Any]) -> str:
    """Fill a one-page-report marker hierarchy with source-backed facts."""
    markers = candidate.structure.get("marker_system") or ["1.", "□", "○"]
    head_marker = next((marker for marker in markers if marker[:1].isdigit()), "1.")
    sub_marker = next((marker for marker in markers if marker in ("□", "○", "-")), "□")

    title = source_facts.get("title") or UNKNOWN
    out = [
        f"# {title}",
        f"> ({candidate.identity.document_type} 방향 초안 · 최종본 아님)",
        "",
    ]
    numbered = head_marker[:1].isdigit()
    headlines = source_facts.get("headlines") or []
    if not headlines:
        out.append(f"{head_marker} {UNKNOWN}")
    for index, headline in enumerate(headlines, 1):
        lead = f"{index}." if numbered else head_marker
        out.append(f"{lead} {headline.get('text') or UNKNOWN}")
        details = headline.get("details") or []
        if not details:
            out.append(f"  {sub_marker} {UNKNOWN}")
        for detail in details:
            out.append(f"  {sub_marker} {detail}")
        out.append("")
    out.append(f"※ {UNKNOWN}")
    return "\n".join(out).rstrip() + "\n"
