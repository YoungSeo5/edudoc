"""Target document profiles derived from protected reference skills.

These profiles are edudoc-owned metadata. They summarize document-type
knowledge from protected skills without copying their implementation or making
their scripts part of the default runtime.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


PROTECTED_HWPX_SKILL_DIR = Path("skills") / "hwp-skill"


@dataclass(frozen=True)
class SkillReference:
    path: str
    purpose: str
    protected: bool = True

    def to_dict(self) -> dict:
        return {
            "path": self.path,
            "purpose": self.purpose,
            "protected": self.protected,
        }


@dataclass(frozen=True)
class OptionalRenderer:
    name: str
    script_path: str
    input_contract: str
    output_formats: tuple[str, ...]
    policy: str
    required_decisions: tuple[str, ...] = ()

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "script_path": self.script_path,
            "input_contract": self.input_contract,
            "output_formats": list(self.output_formats),
            "policy": self.policy,
            "required_decisions": list(self.required_decisions),
        }


@dataclass(frozen=True)
class TargetDocumentProfile:
    profile_id: str
    name: str
    family: str
    purpose: str
    canonical_output: str
    required_fields: tuple[str, ...]
    optional_fields: tuple[str, ...]
    source_profile_fields: tuple[str, ...]
    required_sections: tuple[str, ...]
    generation_rules: tuple[str, ...]
    unknown_field_policy: str
    validation_target: str
    skill_references: tuple[SkillReference, ...]
    reference_sample_dir: str | None = None
    optional_renderer: OptionalRenderer | None = None

    def to_dict(self) -> dict:
        return {
            "profile_id": self.profile_id,
            "name": self.name,
            "family": self.family,
            "purpose": self.purpose,
            "canonical_output": self.canonical_output,
            "required_fields": list(self.required_fields),
            "optional_fields": list(self.optional_fields),
            "source_profile_fields": list(self.source_profile_fields),
            "required_sections": list(self.required_sections),
            "generation_rules": list(self.generation_rules),
            "unknown_field_policy": self.unknown_field_policy,
            "validation_target": self.validation_target,
            "skill_references": [
                reference.to_dict() for reference in self.skill_references
            ],
            "reference_sample_dir": self.reference_sample_dir,
            "optional_renderer": (
                self.optional_renderer.to_dict()
                if self.optional_renderer is not None
                else None
            ),
        }

    def referenced_paths(self, repo_root: Path | str = ".") -> list[Path]:
        root = Path(repo_root)
        paths = [root / reference.path for reference in self.skill_references]
        if self.optional_renderer is not None:
            paths.append(root / self.optional_renderer.script_path)
        return paths

    def reference_sample_paths(self, repo_root: Path | str = ".") -> list[Path]:
        if self.reference_sample_dir is None:
            return []
        sample_dir = Path(repo_root) / self.reference_sample_dir
        if not sample_dir.exists():
            return []
        return sorted(path for path in sample_dir.iterdir() if path.is_file())


def _skill_path(relative: str) -> str:
    return str(PROTECTED_HWPX_SKILL_DIR / relative)


STANDARD_GONGMUN = TargetDocumentProfile(
    profile_id="standard_gongmun",
    name="행안부 표준 기안문",
    family="gongmun",
    purpose=(
        "Generate a conservative public-office draft with header/body/closing "
        "structure and Gongmun writing-rule validation."
    ),
    canonical_output="markdown_or_document_model",
    required_fields=(
        "institution_name",
        "recipient",
        "title",
        "related_basis",
        "body_items",
        "sender_name",
        "ending_marker",
    ),
    optional_fields=(
        "cc",
        "attachments",
        "contact",
        "approval_line",
        "disclosure_type",
    ),
    source_profile_fields=(
        "source_titles",
        "institutions",
        "dates",
        "document_numbers",
        "legal_or_policy_basis",
        "attachments",
        "key_actions",
    ),
    required_sections=(
        "header",
        "related_basis",
        "numbered_body",
        "attachments",
        "closing",
    ),
    generation_rules=(
        "Do not invent recipients, dates, legal bases, attachments, or sender names.",
        "Mark missing required values as 확인 필요.",
        "Use conservative Gongmun numbering such as 1., 가., 1), 가) only when needed.",
        "Use numeric public-office date notation when dates are known.",
        "End the draft with 끝.",
        "Keep generation separate from final HWPX/DOCX/PDF rendering.",
    ),
    unknown_field_policy="Unknown required facts must be written as 확인 필요.",
    validation_target="validators.gongmun_rules.py",
    reference_sample_dir="references/document-types/gongmun/samples",
    skill_references=(
        SkillReference(
            _skill_path("scripts/gonmun.py"),
            "Optional HWPX renderer for a standard official draft.",
        ),
        SkillReference(
            _skill_path("scripts/gonmun_lint.py"),
            "Reference lint behavior for Gongmun writing rules.",
        ),
        SkillReference(
            _skill_path("references/official-doc-style.md"),
            "Official-document structure and field guidance.",
        ),
        SkillReference(
            _skill_path("references/gonmunseo-2025-writing-rules.md"),
            "Public-office writing rules reference.",
        ),
        SkillReference(
            _skill_path("templates/gonmun2025/header.xml"),
            "Reference HWPX header template.",
        ),
        SkillReference(
            _skill_path("templates/gonmun2025/section0.xml"),
            "Reference HWPX section template.",
        ),
    ),
    optional_renderer=OptionalRenderer(
        name="hwpx_skill_gonmun_renderer",
        script_path=_skill_path("scripts/gonmun.py"),
        input_contract="Gongmun JSON metadata/body lines",
        output_formats=("hwpx",),
        policy=(
            "Optional final HWPX rendering adapter only; do not auto-install, "
            "clone, or modify protected skill files."
        ),
    ),
)


GOVERNMENT_PRESS_RELEASE = TargetDocumentProfile(
    profile_id="government_press_release",
    name="정부 표준 보도자료",
    family="press_release",
    purpose=(
        "Generate a fact-preserving government-style press release draft from "
        "source material and render HWPX only through an optional adapter."
    ),
    canonical_output="markdown_or_document_model",
    required_fields=(
        "release_timing",
        "distribution_date",
        "title",
        "department",
        "contact",
        "body_items",
    ),
    optional_fields=(
        "subtitle",
        "embargo_note",
        "lead_summary",
        "attachments",
        "logo_or_image_policy",
    ),
    source_profile_fields=(
        "source_titles",
        "institutions",
        "dates",
        "people_or_departments",
        "statistics",
        "quoted_claims",
        "key_actions",
    ),
    required_sections=(
        "release_header",
        "title_and_subtitle",
        "lead",
        "body",
        "department_contact",
    ),
    generation_rules=(
        "Do not invent statistics, quotes, departments, contacts, or release dates.",
        "Use 확인 필요 for missing release timing, distribution date, and contact fields.",
        "Preserve source-backed facts and separate uncertain interpretation.",
        "Keep images/logos as renderer/template concerns, not Markdown-generation facts.",
        "Keep generation separate from final HWPX/DOCX/PDF rendering.",
    ),
    unknown_field_policy="Unknown required facts must be written as 확인 필요.",
    validation_target="planned: validators.press_release_rules.py",
    reference_sample_dir="references/document-types/press-release/samples",
    skill_references=(
        SkillReference(
            _skill_path("scripts/bodojaryo.py"),
            "Optional HWPX renderer using a government press-release reference package.",
        ),
        SkillReference(
            _skill_path("assets/bodojaryo-reference.hwpx"),
            "Reference HWPX package for government press-release layout.",
        ),
    ),
    optional_renderer=OptionalRenderer(
        name="hwpx_skill_bodojaryo_renderer",
        script_path=_skill_path("scripts/bodojaryo.py"),
        input_contract="Press-release JSON metadata/body items",
        output_formats=("hwpx",),
        policy=(
            "Optional final HWPX rendering adapter only; do not auto-install, "
            "clone, or modify protected skill files."
        ),
    ),
)


PUBLIC_INSTITUTION_PLAN = TargetDocumentProfile(
    profile_id="public_institution_plan",
    name="공공기관 계획서",
    family="public_plan",
    purpose=(
        "Generate a public-institution planning document draft from source "
        "material with explicit title/table-of-contents decisions."
    ),
    canonical_output="markdown_or_document_model",
    required_fields=(
        "title",
        "date",
        "include_title_page",
        "include_table_of_contents",
        "background",
        "objectives",
        "major_tasks",
        "schedule",
        "expected_effects",
    ),
    optional_fields=(
        "institution_name",
        "author",
        "current_status",
        "budget",
        "risk_factors",
        "attachments",
    ),
    source_profile_fields=(
        "source_titles",
        "institutions",
        "dates",
        "tables",
        "statistics",
        "budgets",
        "schedules",
        "key_actions",
        "risks",
    ),
    required_sections=(
        "cover_decision",
        "table_of_contents_decision",
        "background",
        "current_status",
        "objectives",
        "major_tasks",
        "schedule",
        "expected_effects",
        "future_plan",
    ),
    generation_rules=(
        "Ask or require explicit title-page and table-of-contents decisions.",
        "Do not invent budgets, schedules, statistics, departments, or expected effects.",
        "Use 확인 필요 for missing planning facts.",
        "Use source-backed tables and numbers conservatively.",
        "Keep generation separate from final HWPX/DOCX/PDF rendering.",
    ),
    unknown_field_policy="Unknown required facts must be written as 확인 필요.",
    validation_target="planned: validators.public_plan_rules.py",
    reference_sample_dir="references/document-types/public-plan/samples",
    skill_references=(
        SkillReference(
            _skill_path("scripts/gyehoek.py"),
            "Optional HWPX renderer for public-institution planning documents.",
        ),
        SkillReference(
            _skill_path("scripts/gyehoek_hook.py"),
            "Reference decision guard for title and table-of-contents choices.",
        ),
        SkillReference(
            _skill_path("assets/gyehoek-reference.hwpx"),
            "Reference HWPX package for public-institution plan layout.",
        ),
        SkillReference(
            _skill_path("references/report-style.md"),
            "Reference report/planning-document structure and style guidance.",
        ),
    ),
    optional_renderer=OptionalRenderer(
        name="hwpx_skill_gyehoek_renderer",
        script_path=_skill_path("scripts/gyehoek.py"),
        input_contract="Plan title/date plus title-page and table-of-contents decisions",
        output_formats=("hwpx",),
        policy=(
            "Optional final HWPX rendering adapter only; do not auto-install, "
            "clone, or modify protected skill files."
        ),
        required_decisions=("include_title_page", "include_table_of_contents"),
    ),
)


TARGET_DOCUMENT_PROFILES: dict[str, TargetDocumentProfile] = {
    profile.profile_id: profile
    for profile in (
        STANDARD_GONGMUN,
        GOVERNMENT_PRESS_RELEASE,
        PUBLIC_INSTITUTION_PLAN,
    )
}


def list_target_document_profiles() -> list[TargetDocumentProfile]:
    return list(TARGET_DOCUMENT_PROFILES.values())


def get_target_document_profile(profile_id: str) -> TargetDocumentProfile:
    try:
        return TARGET_DOCUMENT_PROFILES[profile_id]
    except KeyError as exc:
        known = ", ".join(sorted(TARGET_DOCUMENT_PROFILES))
        raise KeyError(f"unknown target document profile: {profile_id} ({known})") from exc


def target_document_profile_ids() -> tuple[str, ...]:
    return tuple(TARGET_DOCUMENT_PROFILES)
