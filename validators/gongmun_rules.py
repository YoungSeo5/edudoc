"""
공문서 규칙 검증기 (Phase 0 골격).

'생성-검증 루프'의 검증 단계. LLM이 만든 공문 본문(텍스트)을 받아
기계적으로 검사 가능한 규칙 위반을 찾아 목록으로 돌려준다.
위반 0건이면 통과, 아니면 위반 목록을 되먹여 재생성한다.

주의: 여기 규칙들은 '검사 가능한 것만'의 최소 예시다.
      대상 기관(교육청 등)의 최신 공문서 작성 지침으로 반드시 보정할 것.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field


@dataclass
class Violation:
    rule: str          # 규칙 식별자
    message: str       # 사람이 읽는 설명
    severity: str = "error"   # error | warning


@dataclass
class ValidationReport:
    violations: list[Violation] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return not any(v.severity == "error" for v in self.violations)

    def summary(self) -> str:
        if self.passed and not self.violations:
            return "검수 결과: 위반 0건 (통과)"
        errs = sum(1 for v in self.violations if v.severity == "error")
        warns = sum(1 for v in self.violations if v.severity == "warning")
        head = f"검수 결과: 오류 {errs}건, 경고 {warns}건"
        lines = [head] + [f"  - [{v.severity}] {v.rule}: {v.message}"
                          for v in self.violations]
        return "\n".join(lines)


def check_end_mark(text: str) -> list[Violation]:
    """본문이 '끝' 표시로 마무리되는지 (공문서 종결 규칙)."""
    if "끝." not in text and not text.rstrip().endswith("끝"):
        return [Violation("end_mark", "본문 종결에 '끝.' 표시가 없음")]
    return []


def check_attachment_count(text: str) -> list[Violation]:
    """'붙임'에 적힌 수량과 실제 나열된 붙임 개수가 맞는지."""
    v: list[Violation] = []
    m = re.search(r"붙임[^\d]*(\d+)\s*부", text)
    if not m:
        return v  # 붙임이 없으면 검사 생략
    declared = int(m.group(1))
    # '1. ... 2. ...' 형태로 나열된 붙임 항목 수 추정
    listed = len(re.findall(r"^\s*\d+\.\s", text[m.end():], flags=re.MULTILINE))
    if listed and declared != listed:
        v.append(Violation(
            "attachment_count",
            f"붙임 수량 불일치: 선언 {declared}부 vs 나열 {listed}건",
        ))
    return v


def check_honorific(text: str) -> list[Violation]:
    """경어체(합쇼체) 사용 여부의 최소 검사."""
    # 반말/평서 종결의 흔한 형태를 경고로만 표시 (오탐 가능 → warning)
    banmal = re.findall(r"(?:한다|이다|했다|된다)\.", text)
    if banmal:
        return [Violation(
            "honorific",
            f"경어체가 아닌 종결 표현 {len(banmal)}건 발견(예: '~한다.')",
            severity="warning",
        )]
    return []


def check_key_terms(text: str) -> list[Violation]:
    """공문서 핵심 구성요소(관련/붙임 등) 존재 여부의 최소 검사."""
    v: list[Violation] = []
    if "관련" not in text:
        v.append(Violation("key_term_related",
                           "'관련' 표기가 없음(근거 문서 인용 관행)",
                           severity="warning"))
    return v


# --- 경기도교육청 공문서작성예시 기반 규칙 ------------------------------
# 근거: references/gongmun/gyeonggi_office_format_example.pdf
# (행정업무규정/행안부 편람). 오탐 여지가 있어 우선 warning 으로 둔다.

_DATE_YMD_CHARS = re.compile(r"\d{4}\s*년\s*\d{1,2}\s*월\s*\d{1,2}\s*일")
_DATE_NO_SPACE = re.compile(r"\d{4}\.\d{1,2}\.\d{1,2}")
_DATE_LEADING_ZERO = re.compile(r"\.\s?0[1-9]\.")
_TIME_AMPM = re.compile(r"(오전|오후)\s*\d{1,2}\s*시")
_TIME_HANGUL = re.compile(r"\d{1,2}\s*시\s*\d{1,2}\s*분")


def check_date_format(text: str) -> list[Violation]:
    """날짜: 연·월·일 글자 생략, 온점+1타, 월·일 앞 '0' 제거 (예: 2024. 9. 6.)."""
    v: list[Violation] = []
    if _DATE_YMD_CHARS.search(text):
        v.append(Violation("date_format",
                           "날짜는 연·월·일 글자 대신 온점 표기 (예: 2024. 9. 6.)",
                           severity="warning"))
    if _DATE_NO_SPACE.search(text):
        v.append(Violation("date_format",
                           "날짜 온점 뒤 한 타 띄우기 (예: 2023.11.21 → 2023. 11. 21.)",
                           severity="warning"))
    if _DATE_LEADING_ZERO.search(text):
        v.append(Violation("date_format",
                           "날짜의 월·일 앞 '0'은 표기하지 않음 (예: 09. 06. → 9. 6.)",
                           severity="warning"))
    return v


def check_time_format(text: str) -> list[Violation]:
    """시각: 24시각제 쌍점 표기 (예: 오후 3시 20분 → 15:20)."""
    if _TIME_AMPM.search(text) or _TIME_HANGUL.search(text):
        return [Violation("time_format",
                          "시각은 24시각제 쌍점 표기 (예: 15:20)",
                          severity="warning")]
    return []


def check_amount_unit(text: str) -> list[Violation]:
    """금액: '천 원' 단위 지양, 일반 숫자 표기 (예: 345천원 → 345,000원)."""
    if re.search(r"\d+\s*천\s*원", text):
        return [Violation("amount_unit",
                          "금액은 '천 원' 단위 대신 일반 숫자 표기 (예: 345,000원)",
                          severity="warning")]
    return []


DEFAULT_RULES = [
    check_end_mark,
    check_attachment_count,
    check_honorific,
    check_key_terms,
    check_date_format,
    check_time_format,
    check_amount_unit,
]


def validate(text: str, rules=None) -> ValidationReport:
    """모든 규칙을 적용해 위반 리포트를 만든다."""
    rules = rules or DEFAULT_RULES
    report = ValidationReport()
    for rule in rules:
        report.violations.extend(rule(text))
    return report
