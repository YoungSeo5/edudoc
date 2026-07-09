"""Honest template-candidate extraction + composition proof for one-page reports.

Builds a deterministic template *candidate* from a reference document and proves
the candidate can steer a draft's structure from unrelated source facts.

Honesty rules enforced here:
- style_profile holds ONLY parsed style (extract_style, HWPX-only). For a legacy
  .hwp / PDF / DOCX it stays unknown/low/null — never invented.
- Any font/size wording found in the reference *text* is kept separately as
  ``style_text_mentions`` (evidence), clearly not a parsed style value.
- Missing facts in a draft are written as "확인 필요", never invented.
"""
from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from zipfile import is_zipfile

from .extract_structure import extract_structure, extract_structure_from_text
from .extract_style import extract_style
from .hwp_text import hwp_to_text, style_mentions_in_text

UNKNOWN = "확인 필요"


def build_candidate_from_reference(
    reference: Path | str,
    *,
    institution: str,
    document_type: str,
) -> dict:
    """Return a deterministic, honest template candidate dict."""
    reference = Path(reference)
    ext = reference.suffix.lower()
    style = extract_style(reference)  # HWPX -> real values; else unknown/low
    style_dict = asdict(style)

    text: str | None = None
    style_text_mentions: list[str] = []
    evidence: list[str] = [f"reference_path: {reference.as_posix()}"]

    if is_zipfile(reference):
        reference_format = "hwpx"
        structure = extract_structure(reference)
        style_supported = style.source == "extracted_from_hwpx"
        evidence.append("format=hwpx: extract_style/extract_structure ran on Contents/*.xml")
    elif ext == ".hwp":
        reference_format = "hwp"
        style_supported = False
        text = hwp_to_text(reference)
        if text:
            structure = extract_structure_from_text(text)
            style_text_mentions = style_mentions_in_text(text)
            evidence.append("format=hwp: text via pyhwp (deterministic); structure from text")
        else:
            structure = extract_structure(reference)  # empty candidate
            evidence.append("format=hwp: pyhwp text extraction failed; structure empty")
        evidence.append(
            "extract_style() supports HWPX zip only -> style_profile stays unknown/low for .hwp"
        )
        if style_text_mentions:
            evidence.append(
                "style_text_mentions are the reference's OWN text descriptions, "
                "NOT parsed style records — human-review hints only, not promoted to style_profile"
            )
    else:
        reference_format = ext.lstrip(".") or "unknown"
        style_supported = False
        structure = extract_structure(reference)  # empty candidate
        evidence.append(
            f"format={reference_format}: no supported deterministic extractor -> style + structure unknown"
        )

    style_dict["reason"] = (
        "extracted from HWPX XML" if style_supported
        else f"extract_style() unsupported for {reference_format}; values left null"
    )

    unknown_fields = [
        f"style_profile.{k}"
        for k in ("font_family", "body_font_size_pt", "page_margins_mm", "line_spacing")
        if style_dict.get(k) is None
    ]
    unknown_fields += ["structure.required_sections", "structure.required_fields", "renderer.route"]

    return {
        "institution": institution,
        "document_type": document_type,
        "reference_path": reference.as_posix(),
        "reference_format": reference_format,
        "style_extraction_supported": style_supported,
        "structure": {
            **structure,
            "required_sections": UNKNOWN,
            "required_fields": UNKNOWN,
        },
        "style_profile": style_dict,
        "style_text_mentions": style_text_mentions,
        "renderer": {
            "preferred_format": "docx",
            "route": None,
            "note": f"{UNKNOWN} — 공식 렌더 경로 미정 (기존 DOCX 경로만 안전)",
        },
        "evidence": evidence,
        "confidence": "high" if style_supported else "low",
        "unknown_fields": unknown_fields,
    }


def build_skeleton(candidate: dict) -> str:
    """A structure-only one-page report skeleton (all slots 확인 필요)."""
    markers = candidate["structure"].get("marker_system") or ["1.", "□", "○", "-"]
    lines = [
        f"# {candidate['document_type']} 스켈레톤 (구조 전용)",
        f"> 참조: {candidate['reference_path']}  |  "
        f"스타일: {candidate['style_profile']['source']}/{candidate['style_profile']['confidence']}",
        "",
        f"제목: {UNKNOWN}",
        "",
    ]
    for level, marker in enumerate(markers):
        lines.append(f"{'  ' * level}{marker} {UNKNOWN}")
    return "\n".join(lines) + "\n"


def build_draft(candidate: dict, source_facts: dict) -> str:
    """Fill the candidate's structure with unrelated source facts.

    ``source_facts`` = {"title": str?, "headlines": [{"text": str, "details": [str, ...]}]}
    Missing values -> 확인 필요. Never invents facts not present in source_facts.
    """
    markers = candidate["structure"].get("marker_system") or ["1.", "□", "○"]
    head_marker = next((m for m in markers if m[0].isdigit()), "1.")
    sub_marker = next((m for m in markers if m in ("□", "○", "-")), "□")

    title = source_facts.get("title") or UNKNOWN
    out = [f"# {title}", f"> ({candidate['document_type']} 방향 초안 · 최종본 아님)", ""]

    numbered = head_marker[:1].isdigit()
    headlines = source_facts.get("headlines") or []
    if not headlines:
        out.append(f"{head_marker} {UNKNOWN}")
    for i, h in enumerate(headlines, 1):
        lead = f"{i}." if numbered else head_marker
        out.append(f"{lead} {h.get('text') or UNKNOWN}")
        details = h.get("details") or []
        if not details:
            out.append(f"  {sub_marker} {UNKNOWN}")
        for d in details:
            out.append(f"  {sub_marker} {d}")
        out.append("")

    out.append(f"※ {UNKNOWN}")
    return "\n".join(out).rstrip() + "\n"
