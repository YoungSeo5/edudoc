"""Tests for the tiny Gongmun generation harness."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.generators.gongmun_generator import (
    generate_and_validate,
    generate_gongmun_markdown,
    parse_brief,
)


def test_gongmun_generator_creates_validation_ready_markdown() -> None:
    root = Path(__file__).resolve().parent.parent
    brief = root / "skills" / "gongmun_writer" / "examples" / "input_brief.md"

    result = generate_and_validate(brief)
    draft = result.markdown

    assert result.passed, result.validation_report.summary()
    assert draft.startswith("# "), "Generated draft should start with a Markdown title"
    assert "수신: 관내 초·중·고등학교장" in draft
    assert "담당: 교육지원과 홍길동" in draft
    assert "관련: 2026년 교원 역량 강화 연수 운영 계획" in draft
    assert "1. 대상: 희망 교원" in draft
    assert "2. 내용: 디지털 수업 설계 연수 참가 신청" in draft
    assert "3. 기한: 2026. 7. 15." in draft
    assert "4. 제출 방법: 업무관리시스템 공문 회신" in draft
    assert "붙임  참가 신청서 1부.  끝." in draft
    assert "끝." in draft


def test_gongmun_generator_fills_missing_fields_with_unknown_marker() -> None:
    fields = parse_brief("내용: 학교 안전 점검 결과 제출\n")

    draft = generate_gongmun_markdown(fields)

    assert "수신: 확인 필요" in draft
    assert "담당: 확인 필요" in draft
    assert "관련: 확인 필요" in draft
    assert "1. 대상: 확인 필요" in draft
    assert "3. 기한: 확인 필요" in draft
    assert "4. 제출 방법: 확인 필요" in draft
    assert "붙임  확인 필요.  끝." in draft


if __name__ == "__main__":
    test_gongmun_generator_creates_validation_ready_markdown()
    test_gongmun_generator_fills_missing_fields_with_unknown_marker()
    print("PASS: Gongmun generator")
