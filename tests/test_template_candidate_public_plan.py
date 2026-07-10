"""One-page-report template extraction and composition proof."""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.generators.one_page_report_generator import build_draft, build_skeleton
from core.templates.pipeline import run_template_pipeline

ROOT = Path(__file__).resolve().parent.parent
REFERENCE = (
    ROOT
    / "references"
    / "document-types"
    / "public-plan"
    / "대통령비서실 보고서의 표준서식_한장보고서의 표준.hwp"
)


def _candidate():
    candidate, gate = run_template_pipeline(
        REFERENCE,
        institution="대통령비서실",
        document_type="한장보고서",
    )
    assert gate.passed
    return candidate


def test_reference_file_is_found() -> None:
    assert REFERENCE.is_file(), f"reference not found: {REFERENCE}"


def test_candidate_uses_unified_shape_without_fake_values() -> None:
    candidate = _candidate()
    blob = json.dumps(candidate.to_dict(), ensure_ascii=False)
    assert candidate.identity.institution == "대통령비서실"
    assert candidate.identity.document_type == "한장보고서"
    assert candidate.status == "validated"
    assert "..." not in blob


def test_unsupported_style_stays_unknown_and_evidenced() -> None:
    candidate = _candidate()
    style = candidate.style_profile
    assert candidate.reference_format == "hwp"
    assert style.source == "unknown"
    assert style.font_family is None
    assert style.body_font_size_pt is None
    assert style.line_spacing is None
    assert any("휴먼명조" in item for item in candidate.evidence)


def test_structure_and_draft_follow_report_direction() -> None:
    candidate = _candidate()
    assert "1." in candidate.structure["marker_system"]
    assert "□" in candidate.structure["marker_system"]
    assert candidate.structure["paragraph_count"] > 0

    draft = build_draft(
        candidate,
        {
            "title": "CI 빌드 파이프라인 개선",
            "headlines": [
                {"text": "빌드 캐시 도입", "details": ["의존성 캐시로 재빌드 단축"]},
                {"text": "테스트 병렬화", "details": []},
            ],
        },
    )
    assert "1. 빌드 캐시 도입" in draft
    assert "□ 의존성 캐시로 재빌드 단축" in draft
    assert "확인 필요" in draft
    assert "비서관" not in draft and "안건" not in draft
    assert build_skeleton(candidate).count("확인 필요") >= 3


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
    print("PASS: unified one-page-report template pipeline")
