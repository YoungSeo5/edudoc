"""Public institution plan Markdown generator.

This generator turns a DocumentPlan into a conservative Markdown draft. It does
not call an LLM, parse HWPX/PDF files, or export DOCX/PDF/HWPX.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from core.document_plan import DocumentPlan, UNKNOWN, create_document_plan
from core.source_profile import SourceProfile


PUBLIC_PLAN_PROFILE_ID = "public_institution_plan"


@dataclass(frozen=True)
class PublicPlanGenerationResult:
    markdown: str
    document_plan: DocumentPlan

    @property
    def missing_required_fields(self) -> list[str]:
        return list(self.document_plan.missing_required_fields)

    @property
    def is_complete(self) -> bool:
        return not self.document_plan.missing_required_fields


def generate_public_plan_markdown(plan: DocumentPlan) -> str:
    """Generate a public institution planning-document Markdown draft."""
    if plan.target_profile_id != PUBLIC_PLAN_PROFILE_ID:
        raise ValueError(
            f"public plan generator requires {PUBLIC_PLAN_PROFILE_ID}, "
            f"got {plan.target_profile_id}"
        )

    sections = {section.section_id: section for section in plan.sections}
    lines: list[str] = [
        f"# {plan.title}",
        "",
        "문서유형: 공공기관 계획서",
        "작성상태: 초안",
        "",
    ]

    cover = sections.get("cover_decision")
    if cover is not None:
        lines.extend([
            "## 작성 기준",
            "",
            *_as_bullets(_content_or_unknown(cover.content)),
            "",
        ])

    ordered_sections = [
        ("background", "1. 추진 배경"),
        ("current_status", "2. 현황 및 문제점"),
        ("objectives", "3. 추진 목표"),
        ("major_tasks", "4. 주요 추진 과제"),
        ("schedule", "5. 추진 일정"),
        ("budget", "6. 예산"),
        ("expected_effects", "7. 기대 효과"),
        ("future_plan", "8. 향후 계획"),
    ]
    for section_id, title in ordered_sections:
        section = sections.get(section_id)
        content = _content_or_unknown(section.content if section else [])
        lines.extend([f"## {title}", ""])
        lines.extend(_as_numbered_items(content))
        missing = section.missing_fields if section else [section_id]
        if missing:
            lines.append(f"- {UNKNOWN}: {', '.join(missing)}")
        lines.append("")

    if plan.reference_sample_paths:
        lines.extend(["## 기준 참고 문서", ""])
        for path in plan.reference_sample_paths:
            lines.append(f"- {path}")
        lines.append("")

    if plan.missing_required_fields:
        lines.extend(["## 확인 필요", ""])
        for field in plan.missing_required_fields:
            lines.append(f"- {field}")
        lines.append("")

    lines.extend([
        "## 작성 메모",
        "",
        "- 본 초안은 SourceProfile과 DocumentPlan을 기반으로 한 보수적 Markdown 초안입니다.",
        "- 기준 PDF는 경로만 추적하며 본문을 자동 파싱하지 않습니다.",
        "- 확인되지 않은 사실은 확인 필요로 남깁니다.",
    ])
    return "\n".join(lines).rstrip() + "\n"


def generate_public_plan_from_source_profile(
    source_profile: SourceProfile,
    *,
    repo_root: Path | str = ".",
    title: str | None = None,
) -> PublicPlanGenerationResult:
    """Create a public-plan DocumentPlan and render it to Markdown."""
    plan = create_document_plan(
        source_profile,
        PUBLIC_PLAN_PROFILE_ID,
        repo_root=repo_root,
        title=title,
    )
    return PublicPlanGenerationResult(
        markdown=generate_public_plan_markdown(plan),
        document_plan=plan,
    )


def write_public_plan_markdown(plan: DocumentPlan, output_path: Path | str) -> Path:
    """Write a generated public-plan Markdown draft as UTF-8."""
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(generate_public_plan_markdown(plan), encoding="utf-8")
    return output


def _content_or_unknown(content: list[str]) -> list[str]:
    cleaned = [item.strip() for item in content if item and item.strip()]
    return cleaned or [UNKNOWN]


def _as_bullets(items: list[str]) -> list[str]:
    return [f"- {item}" for item in items]


def _as_numbered_items(items: list[str]) -> list[str]:
    return [f"{index}. {item}" for index, item in enumerate(items, start=1)]
