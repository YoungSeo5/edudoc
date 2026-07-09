"""Honest template-candidate extraction from the 대통령비서실 한장보고서 reference,
plus a composition proof that the candidate steers a draft from unrelated facts.

Honesty is the point: the reference is a legacy .hwp (no HWPX style records), so
parsed style must stay unknown/null — never invented — while structure is still
derived deterministically from the text, and a draft follows the report direction
with missing facts left as 확인 필요.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.templates.one_page_report import (
    build_candidate_from_reference,
    build_draft,
    build_skeleton,
)

ROOT = Path(__file__).resolve().parent.parent
REFERENCE = (
    ROOT / "references" / "document-types" / "public-plan"
    / "대통령비서실 보고서의 표준서식_한장보고서의 표준.hwp"
)


def _candidate() -> dict:
    return build_candidate_from_reference(
        REFERENCE, institution="대통령비서실", document_type="한장보고서"
    )


def test_reference_file_is_found() -> None:
    assert REFERENCE.is_file(), f"reference not found: {REFERENCE}"


def test_candidate_json_is_produced_without_placeholder_dots() -> None:
    candidate = _candidate()
    blob = json.dumps(candidate, ensure_ascii=False)
    assert candidate["institution"] == "대통령비서실"
    assert candidate["document_type"] == "한장보고서"
    assert '"..."' not in blob and "..." not in blob  # no fake extracted values


def test_unsupported_style_stays_unknown_and_null() -> None:
    candidate = _candidate()
    sp = candidate["style_profile"]
    assert candidate["reference_format"] == "hwp"
    assert candidate["style_extraction_supported"] is False
    assert candidate["confidence"] == "low"
    # style is NOT invented even though the reference text names fonts
    assert sp["source"] == "unknown"
    assert sp["font_family"] is None
    assert sp["body_font_size_pt"] is None
    assert sp["line_spacing"] is None
    # text-stated fonts are kept as evidence only, never promoted to style_profile
    assert any("휴먼명조" in m for m in candidate["style_text_mentions"])


def test_evidence_records_path_and_limitation() -> None:
    candidate = _candidate()
    evidence = " ".join(candidate["evidence"])
    assert "reference_path" in evidence
    assert "HWPX zip only" in evidence  # explains why style is unknown
    assert "structure.required_sections" in candidate["unknown_fields"]


def test_structure_is_derived_from_text() -> None:
    candidate = _candidate()
    markers = candidate["structure"]["marker_system"]
    # the one-page-report hierarchy is captured from the text
    for expected in ("1.", "□"):
        assert expected in markers
    assert candidate["structure"]["paragraph_count"] > 0


def test_draft_follows_report_direction_and_marks_missing() -> None:
    candidate = _candidate()
    facts = {
        "title": "CI 빌드 파이프라인 개선",  # unrelated to presidential content
        "headlines": [
            {"text": "빌드 캐시 도입", "details": ["의존성 캐시로 재빌드 단축"]},
            {"text": "테스트 병렬화", "details": []},  # no details -> 확인 필요
        ],
    }
    draft = build_draft(candidate, facts)

    assert "CI 빌드 파이프라인 개선" in draft          # provided title used
    assert "1. 빌드 캐시 도입" in draft                # report numbering direction
    assert "□ 의존성 캐시로 재빌드 단축" in draft       # template marker steers structure
    assert "확인 필요" in draft                        # missing details not invented
    assert "비서관" not in draft and "안건" not in draft  # no reference content leaked in

    # skeleton is structure-only, every slot unknown
    skeleton = build_skeleton(candidate)
    assert skeleton.count("확인 필요") >= 3


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
    print("PASS: presidential one-page-report template candidate + composition proof")
