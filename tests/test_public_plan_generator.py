"""Public institution plan Markdown generator."""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.document_plan import create_document_plan  # noqa: E402
from core.generators.public_plan_generator import (  # noqa: E402
    generate_public_plan_from_source_profile,
    generate_public_plan_markdown,
    write_public_plan_markdown,
)
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


def _source_profile():
    return build_source_profile_from_markdown_documents(
        [(Path("samples") / "ai_plan.md", SAMPLE_MARKDOWN)]
    )


def test_public_plan_generator_renders_markdown_from_document_plan() -> None:
    source_profile = _source_profile()
    plan = create_document_plan(source_profile, "public_institution_plan")

    markdown = generate_public_plan_markdown(plan)

    assert markdown.startswith("# AI 교육 운영 계획")
    assert "문서유형: 공공기관 계획서" in markdown
    assert "작성상태: 초안" in markdown
    assert "## 작성 기준" in markdown
    assert "## 1. 추진 배경" in markdown
    assert "## 2. 현황 및 문제점" in markdown
    assert "## 4. 주요 추진 과제" in markdown
    assert "## 5. 추진 일정" in markdown
    assert "## 6. 예산" in markdown
    assert "## 8. 향후 계획" in markdown
    assert "추진 배경" in markdown
    assert "2026. 7. 15." in markdown
    assert "12,000,000원" in markdown
    assert "확인 필요" in markdown


def test_public_plan_generator_tracks_reference_samples_without_parsing_pdf() -> None:
    source_profile = _source_profile()

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        reference_dir = root / "references" / "document-types" / "public-plan" / "samples"
        reference_dir.mkdir(parents=True)
        (reference_dir / "public_plan_reference.pdf").write_bytes(b"%PDF-1.7\n")

        result = generate_public_plan_from_source_profile(
            source_profile,
            repo_root=root,
        )

    assert any(
        path.endswith("public_plan_reference.pdf")
        for path in result.document_plan.reference_sample_paths
    )
    assert "## 기준 참고 문서" in result.markdown
    assert "public_plan_reference.pdf" in result.markdown
    assert "기준 PDF는 경로만 추적" in result.markdown
    assert not result.is_complete
    assert "objectives" in result.missing_required_fields


def test_public_plan_generator_write_markdown_file() -> None:
    source_profile = _source_profile()
    plan = create_document_plan(source_profile, "public_institution_plan")

    with tempfile.TemporaryDirectory() as tmp:
        output = Path(tmp) / "public_plan.generated.md"
        written = write_public_plan_markdown(plan, output)

        assert written == output
        text = output.read_text(encoding="utf-8")

    assert "# AI 교육 운영 계획" in text
    assert "## 확인 필요" in text
    assert "expected_effects" in text


def test_public_plan_generator_rejects_other_profiles() -> None:
    source_profile = _source_profile()
    profile = get_target_document_profile("standard_gongmun")
    plan = create_document_plan(source_profile, profile.profile_id)

    try:
        generate_public_plan_markdown(plan)
    except ValueError as exc:
        assert "public_institution_plan" in str(exc)
        assert "standard_gongmun" in str(exc)
    else:
        raise AssertionError("public plan generator should reject other profiles")


if __name__ == "__main__":
    test_public_plan_generator_renders_markdown_from_document_plan()
    test_public_plan_generator_tracks_reference_samples_without_parsing_pdf()
    test_public_plan_generator_write_markdown_file()
    test_public_plan_generator_rejects_other_profiles()
    print("PASS: public plan generator")
