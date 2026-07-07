"""Target document profiles extracted from protected hwpx skill references."""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.target_document_profiles import (  # noqa: E402
    get_target_document_profile,
    list_target_document_profiles,
    target_document_profile_ids,
)


REPO_ROOT = Path(__file__).resolve().parent.parent


def test_expected_target_document_profiles_exist() -> None:
    assert target_document_profile_ids() == (
        "standard_gongmun",
        "government_press_release",
        "public_institution_plan",
    )

    profiles = list_target_document_profiles()

    assert len(profiles) == 3
    assert {profile.family for profile in profiles} == {
        "gongmun",
        "press_release",
        "public_plan",
    }


def test_profiles_keep_markdown_document_model_as_canonical_output() -> None:
    for profile in list_target_document_profiles():
        assert profile.canonical_output == "markdown_or_document_model"
        assert "확인 필요" in profile.unknown_field_policy
        assert any(
            "Keep generation separate from final HWPX/DOCX/PDF rendering" in rule
            for rule in profile.generation_rules
        )
        assert profile.optional_renderer is not None
        assert profile.optional_renderer.output_formats == ("hwpx",)
        assert "do not auto-install" in profile.optional_renderer.policy
        assert "modify protected skill files" in profile.optional_renderer.policy


def test_profiles_reference_existing_protected_skill_files() -> None:
    for profile in list_target_document_profiles():
        for path in profile.referenced_paths(REPO_ROOT):
            assert path.exists(), f"missing reference path for {profile.profile_id}: {path}"
            assert "skills" in path.parts
            assert "hwp-skill" in path.parts


def test_standard_gongmun_profile_contract() -> None:
    profile = get_target_document_profile("standard_gongmun")

    assert profile.validation_target == "validators.gongmun_rules.py"
    assert "recipient" in profile.required_fields
    assert "related_basis" in profile.required_fields
    assert "ending_marker" in profile.required_fields
    assert "legal_or_policy_basis" in profile.source_profile_fields
    assert "numbered_body" in profile.required_sections
    assert "closing" in profile.required_sections
    assert profile.optional_renderer.script_path.endswith("scripts\\gonmun.py")


def test_press_release_profile_contract() -> None:
    profile = get_target_document_profile("government_press_release")

    assert profile.validation_target == "planned: validators.press_release_rules.py"
    assert "release_timing" in profile.required_fields
    assert "distribution_date" in profile.required_fields
    assert "statistics" in profile.source_profile_fields
    assert "department_contact" in profile.required_sections
    assert profile.optional_renderer.script_path.endswith("scripts\\bodojaryo.py")


def test_public_plan_profile_contract() -> None:
    profile = get_target_document_profile("public_institution_plan")

    assert profile.validation_target == "planned: validators.public_plan_rules.py"
    assert "include_title_page" in profile.required_fields
    assert "include_table_of_contents" in profile.required_fields
    assert "tables" in profile.source_profile_fields
    assert "schedule" in profile.required_sections
    assert profile.optional_renderer is not None
    assert profile.optional_renderer.required_decisions == (
        "include_title_page",
        "include_table_of_contents",
    )
    assert profile.optional_renderer.script_path.endswith("scripts\\gyehoek.py")


def test_profiles_are_json_serializable() -> None:
    encoded = json.dumps(
        [profile.to_dict() for profile in list_target_document_profiles()],
        ensure_ascii=False,
        indent=2,
    )

    assert "행안부 표준 기안문" in encoded
    assert "정부 표준 보도자료" in encoded
    assert "공공기관 계획서" in encoded
    assert "skills" in encoded


if __name__ == "__main__":
    test_expected_target_document_profiles_exist()
    test_profiles_keep_markdown_document_model_as_canonical_output()
    test_profiles_reference_existing_protected_skill_files()
    test_standard_gongmun_profile_contract()
    test_press_release_profile_contract()
    test_public_plan_profile_contract()
    test_profiles_are_json_serializable()
    print("PASS: target document profiles")
