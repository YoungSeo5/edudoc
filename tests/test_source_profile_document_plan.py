"""SourceProfile and DocumentPlan planning scaffold."""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.document_plan import create_document_plan  # noqa: E402
from core.source_profile import build_source_profile_from_markdown_documents  # noqa: E402
from core.target_document_profiles import get_target_document_profile  # noqa: E402


SAMPLE_MARKDOWN = """# AI 교육 운영 계획

경기도교육청 미래교육과는 2026. 7. 15. AI 교육 운영 계획을 추진한다.

1. 추진 배경: 학교 현장의 AI 활용 수업 지원 필요
2. 주요 내용: 교원 연수 3회, 학생 캠프 120명 운영
3. 추진일정: 2026. 7. 15.부터 2026. 9. 30.까지
4. 예산: 12,000,000원
5. 개선 필요: 신청 절차 보완

| 구분 | 내용 | 인원 |
| --- | --- | --- |
| 연수 | 교원 대상 | 80명 |
| 캠프 | 학생 대상 | 120명 |

붙임  세부 추진 일정 1부.
"""


def test_source_profile_extracts_reusable_public_plan_facts() -> None:
    profile = build_source_profile_from_markdown_documents(
        [(Path("samples") / "ai_plan.md", SAMPLE_MARKDOWN)]
    )

    assert profile.documents[0].name == "ai_plan.md"
    assert profile.documents[0].title == "AI 교육 운영 계획"
    assert "AI 교육 운영 계획" in profile.source_titles
    assert any("경기도교육청" in item for item in profile.institutions)
    assert "2026. 7. 15." in profile.dates
    assert any("120명" in item for item in profile.statistics)
    assert any("12,000,000원" in item for item in profile.budgets)
    assert any("추진일정" in item for item in profile.schedules)
    assert any("추진 배경" in item for item in profile.key_actions)
    assert any("개선 필요" in item for item in profile.risks)
    assert any("붙임" in item for item in profile.attachments)
    assert profile.tables
    assert "PDF reference samples are not parsed by this layer." in profile.extraction_notes


def test_public_plan_document_plan_uses_source_profile_and_reference_samples() -> None:
    source_profile = build_source_profile_from_markdown_documents(
        [(Path("samples") / "ai_plan.md", SAMPLE_MARKDOWN)]
    )

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        reference_dir = root / "references" / "document-types" / "public-plan" / "samples"
        reference_dir.mkdir(parents=True)
        (reference_dir / "public_plan_reference.pdf").write_bytes(b"%PDF-1.7\n")

        plan = create_document_plan(
            source_profile,
            "public_institution_plan",
            repo_root=root,
        )

    assert plan.target_profile_id == "public_institution_plan"
    assert plan.target_name == "공공기관 계획서"
    assert plan.title == "AI 교육 운영 계획"
    assert plan.source_document_count == 1
    assert any(path.endswith("public_plan_reference.pdf") for path in plan.reference_sample_paths)

    sections = {section.section_id: section for section in plan.sections}
    assert "background" in sections
    assert "schedule" in sections
    assert "budget" in sections
    assert any("추진 배경" in item for item in sections["background"].content)
    assert any("2026. 7. 15." in item for item in sections["schedule"].content)
    assert any("12,000,000원" in item for item in sections["budget"].content)

    assert "include_title_page" in plan.missing_required_fields
    assert "include_table_of_contents" in plan.missing_required_fields
    assert "objectives" in plan.missing_required_fields
    assert any("Reference PDF samples are tracked" in item for item in plan.assumptions)


def test_public_plan_document_plan_markdown_scaffold_is_serializable() -> None:
    source_profile = build_source_profile_from_markdown_documents(
        [(Path("samples") / "ai_plan.md", SAMPLE_MARKDOWN)]
    )
    plan = create_document_plan(source_profile, "public_institution_plan")

    encoded = json.dumps(plan.to_dict(), ensure_ascii=False, indent=2)
    markdown = plan.to_markdown()

    assert "공공기관 계획서" in encoded
    assert "확인 필요" in encoded
    assert "# AI 교육 운영 계획" in markdown
    assert "## 추진 배경" in markdown
    assert "## 추진 일정" in markdown
    assert "## 기대 효과" in markdown
    assert "확인 필요" in markdown


def test_public_plan_profile_points_to_reference_sample_directory() -> None:
    profile = get_target_document_profile("public_institution_plan")

    assert profile.reference_sample_dir == "references/document-types/public-plan/samples"


if __name__ == "__main__":
    test_source_profile_extracts_reusable_public_plan_facts()
    test_public_plan_document_plan_uses_source_profile_and_reference_samples()
    test_public_plan_document_plan_markdown_scaffold_is_serializable()
    test_public_plan_profile_points_to_reference_sample_directory()
    print("PASS: source profile + document plan")
