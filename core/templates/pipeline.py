"""Template extraction, review, refinement, and validation pipeline."""
from __future__ import annotations

from pathlib import Path
from zipfile import is_zipfile

from .extractors import (
    extract_structure,
    extract_structure_from_text,
    extract_style,
    hwp_to_text,
    style_mentions_in_text,
)
from .models import RendererContract, TemplateCandidate, TemplateIdentity
from .quality.false_positive import (
    FalsePositiveRule,
    apply_false_positive_rules,
)
from .quality.gate import GateResult, evaluate_gate
from .quality.lint import lint_candidate
from .quality.refine import refine_candidate
from .quality.success_rules import SuccessRules

UNKNOWN = "확인 필요"


def build_candidate(
    reference: Path | str,
    *,
    institution: str,
    document_type: str,
    route: str | None = None,
    extends: str | None = None,
) -> TemplateCandidate:
    """Build one candidate shape from deterministic reference observations."""
    reference = Path(reference)
    style = extract_style(reference)
    evidence = [f"reference_path: {reference.as_posix()}"]
    style_mentions: list[str] = []

    if is_zipfile(reference):
        reference_format = "hwpx"
        structure = extract_structure(reference)
        evidence.append("HWPX XML inspected: Contents/header.xml and Contents/section0.xml")
    elif reference.suffix.lower() == ".hwp":
        reference_format = "hwp"
        text = hwp_to_text(reference)
        if text:
            structure = extract_structure_from_text(text)
            style_mentions = style_mentions_in_text(text)
            evidence.append("legacy HWP text extracted through pyhwp")
        else:
            structure = extract_structure(reference)
            evidence.append("legacy HWP text extraction unavailable")
    else:
        reference_format = reference.suffix.lower().lstrip(".") or "unknown"
        structure = extract_structure(reference)
        evidence.append(f"no deterministic extractor for format={reference_format}")

    if style_mentions:
        evidence.extend(f"style_text_mention (not parsed style): {item}" for item in style_mentions)

    unknown_fields = ["structure.required_sections", "structure.required_fields"]
    for field_name in ("font_family", "body_font_size_pt", "page_margins_mm", "line_spacing"):
        if getattr(style, field_name) is None:
            unknown_fields.append(f"style_profile.{field_name}")
    if route is None:
        unknown_fields.append("renderer.route")

    structure = {
        **structure,
        "required_sections": UNKNOWN,
        "required_fields": UNKNOWN,
        "repeat_sections": UNKNOWN,
    }
    return TemplateCandidate(
        identity=TemplateIdentity(
            institution=institution,
            document_type=document_type,
            extends=extends,
        ),
        reference_path=reference.as_posix(),
        reference_format=reference_format,
        structure=structure,
        writing_rules={"tone": UNKNOWN, "unknown_policy": UNKNOWN},
        style_profile=style,
        renderer=RendererContract(
            preferred_format="docx",
            route=route,
            reference_hwpx=reference.as_posix() if reference_format == "hwpx" else None,
            fallback="md2hwpx",
        ),
        evidence=evidence,
        unknown_fields=unknown_fields,
    )


def run_template_pipeline(
    reference: Path | str,
    *,
    institution: str,
    document_type: str,
    route: str | None = None,
    extends: str | None = None,
    success_rules: SuccessRules | None = None,
    false_positive_rules: list[FalsePositiveRule] | None = None,
    max_refinement_passes: int = 3,
) -> tuple[TemplateCandidate, GateResult]:
    """Extract, lint, refine, and gate a template candidate."""
    rules = success_rules or SuccessRules()
    candidate = build_candidate(
        reference,
        institution=institution,
        document_type=document_type,
        route=route,
        extends=extends,
    )
    memory_diagnostics = apply_false_positive_rules(
        candidate,
        false_positive_rules or [],
    )

    passes = 0
    refinement_history = []
    for pass_number in range(1, max_refinement_passes + 1):
        diagnostics = lint_candidate(candidate, rules)
        if not refine_candidate(candidate, diagnostics):
            break
        refinement_history.extend(diagnostics)
        passes = pass_number

    candidate.refinement_passes = passes
    final_diagnostics = lint_candidate(candidate, rules)
    candidate.diagnostics = memory_diagnostics + refinement_history + final_diagnostics
    gate = evaluate_gate(candidate, final_diagnostics, rules)
    candidate.status = "validated" if gate.passed else "rejected"
    return candidate, gate
