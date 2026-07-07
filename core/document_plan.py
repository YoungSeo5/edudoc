"""Document planning from SourceProfile and TargetDocumentProfile."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path

from .source_profile import SourceProfile
from .target_document_profiles import (
    TargetDocumentProfile,
    get_target_document_profile,
)


UNKNOWN = "확인 필요"


@dataclass(frozen=True)
class DocumentPlanSection:
    section_id: str
    title: str
    content: list[str] = field(default_factory=list)
    source_fields: list[str] = field(default_factory=list)
    missing_fields: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class DocumentPlan:
    target_profile_id: str
    target_name: str
    title: str
    source_document_count: int
    sections: list[DocumentPlanSection] = field(default_factory=list)
    missing_required_fields: list[str] = field(default_factory=list)
    reference_sample_paths: list[str] = field(default_factory=list)
    assumptions: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "target_profile_id": self.target_profile_id,
            "target_name": self.target_name,
            "title": self.title,
            "source_document_count": self.source_document_count,
            "sections": [section.to_dict() for section in self.sections],
            "missing_required_fields": list(self.missing_required_fields),
            "reference_sample_paths": list(self.reference_sample_paths),
            "assumptions": list(self.assumptions),
        }

    def to_markdown(self) -> str:
        lines = [f"# {self.title}", ""]
        if self.reference_sample_paths:
            lines.extend(["## 기준 참고 문서", ""])
            lines.extend(f"- {path}" for path in self.reference_sample_paths)
            lines.append("")
        for section in self.sections:
            lines.extend([f"## {section.title}", ""])
            content = section.content or [UNKNOWN]
            lines.extend(f"- {item}" for item in content)
            if section.missing_fields:
                lines.append(f"- {UNKNOWN}: {', '.join(section.missing_fields)}")
            lines.append("")
        return "\n".join(lines).rstrip() + "\n"


def create_document_plan(
    source_profile: SourceProfile,
    target_profile_id: str,
    *,
    repo_root: Path | str = ".",
    title: str | None = None,
) -> DocumentPlan:
    target_profile = get_target_document_profile(target_profile_id)
    if target_profile.profile_id == "public_institution_plan":
        return _public_institution_plan(
            source_profile,
            target_profile,
            repo_root=repo_root,
            title=title,
        )
    return _generic_plan(
        source_profile,
        target_profile,
        repo_root=repo_root,
        title=title,
    )


def _public_institution_plan(
    source_profile: SourceProfile,
    target_profile: TargetDocumentProfile,
    *,
    repo_root: Path | str,
    title: str | None,
) -> DocumentPlan:
    plan_title = title or _first(source_profile.source_titles) or f"{UNKNOWN} 추진계획"
    reference_paths = _reference_paths(target_profile, repo_root)
    missing = _missing_public_plan_fields(source_profile, title=title)

    sections = [
        DocumentPlanSection(
            section_id="cover_decision",
            title="표지 및 목차 결정",
            content=[
                f"표지 포함 여부: {UNKNOWN}",
                f"목차 포함 여부: {UNKNOWN}",
                f"작성 기준일: {_first(source_profile.dates) or UNKNOWN}",
            ],
            source_fields=["dates"],
            missing_fields=["include_title_page", "include_table_of_contents"],
        ),
        DocumentPlanSection(
            section_id="background",
            title="추진 배경",
            content=_fallback_list(source_profile.key_actions, "background"),
            source_fields=["key_actions"],
            missing_fields=[] if source_profile.key_actions else ["background"],
        ),
        DocumentPlanSection(
            section_id="current_status",
            title="현황 및 문제점",
            content=_fallback_list(
                source_profile.statistics + source_profile.tables + source_profile.risks,
                "current_status",
            ),
            source_fields=["statistics", "tables", "risks"],
            missing_fields=(
                []
                if source_profile.statistics or source_profile.tables or source_profile.risks
                else ["current_status"]
            ),
        ),
        DocumentPlanSection(
            section_id="objectives",
            title="추진 목표",
            content=[UNKNOWN],
            source_fields=[],
            missing_fields=["objectives"],
        ),
        DocumentPlanSection(
            section_id="major_tasks",
            title="주요 추진 과제",
            content=_fallback_list(source_profile.key_actions, "major_tasks"),
            source_fields=["key_actions"],
            missing_fields=[] if source_profile.key_actions else ["major_tasks"],
        ),
        DocumentPlanSection(
            section_id="schedule",
            title="추진 일정",
            content=_fallback_list(source_profile.schedules + source_profile.dates, "schedule"),
            source_fields=["schedules", "dates"],
            missing_fields=[] if source_profile.schedules or source_profile.dates else ["schedule"],
        ),
        DocumentPlanSection(
            section_id="budget",
            title="예산",
            content=_fallback_list(source_profile.budgets, "budget"),
            source_fields=["budgets"],
            missing_fields=[] if source_profile.budgets else ["budget"],
        ),
        DocumentPlanSection(
            section_id="expected_effects",
            title="기대 효과",
            content=[UNKNOWN],
            source_fields=[],
            missing_fields=["expected_effects"],
        ),
        DocumentPlanSection(
            section_id="future_plan",
            title="향후 계획",
            content=[UNKNOWN],
            source_fields=[],
            missing_fields=["future_plan"],
        ),
    ]

    return DocumentPlan(
        target_profile_id=target_profile.profile_id,
        target_name=target_profile.name,
        title=plan_title,
        source_document_count=len(source_profile.documents),
        sections=sections,
        missing_required_fields=missing,
        reference_sample_paths=reference_paths,
        assumptions=[
            "This is a planning scaffold, not a final generated report.",
            "Reference PDF samples are tracked but not parsed by this deterministic layer.",
            "Missing or unsupported facts remain 확인 필요.",
        ],
    )


def _generic_plan(
    source_profile: SourceProfile,
    target_profile: TargetDocumentProfile,
    *,
    repo_root: Path | str,
    title: str | None,
) -> DocumentPlan:
    plan_title = title or _first(source_profile.source_titles) or f"{UNKNOWN} {target_profile.name}"
    sections = [
        DocumentPlanSection(
            section_id=section_id,
            title=section_id.replace("_", " "),
            content=[UNKNOWN],
            missing_fields=[section_id],
        )
        for section_id in target_profile.required_sections
    ]
    return DocumentPlan(
        target_profile_id=target_profile.profile_id,
        target_name=target_profile.name,
        title=plan_title,
        source_document_count=len(source_profile.documents),
        sections=sections,
        missing_required_fields=list(target_profile.required_fields),
        reference_sample_paths=_reference_paths(target_profile, repo_root),
        assumptions=[
            "Generic document planning is a scaffold only.",
            "Use a target-specific planner for production generation.",
        ],
    )


def _missing_public_plan_fields(
    source_profile: SourceProfile,
    *,
    title: str | None,
) -> list[str]:
    missing: list[str] = []
    if not title and not source_profile.source_titles:
        missing.append("title")
    if not source_profile.dates:
        missing.append("date")
    missing.extend(["include_title_page", "include_table_of_contents"])
    if not source_profile.key_actions:
        missing.extend(["background", "major_tasks"])
    missing.append("objectives")
    if not source_profile.schedules and not source_profile.dates:
        missing.append("schedule")
    missing.append("expected_effects")
    return _unique(missing)


def _reference_paths(target_profile: TargetDocumentProfile, repo_root: Path | str) -> list[str]:
    return [str(path) for path in target_profile.reference_sample_paths(repo_root)]


def _fallback_list(values: list[str], field_name: str) -> list[str]:
    if values:
        return values[:5]
    return [f"{field_name}: {UNKNOWN}"]


def _first(values: list[str]) -> str | None:
    return values[0] if values else None


def _unique(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        result.append(value)
    return result
