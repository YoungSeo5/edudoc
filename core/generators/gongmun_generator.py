"""Tiny Gongmun Markdown generation harness.

This module turns a structured Markdown brief into a conservative 공문-style
Markdown draft. It does not call an LLM, parse HWPX, or export final files.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from validators.gongmun_rules import ValidationReport, validate


UNKNOWN = "확인 필요"

BRIEF_FIELDS = (
    "목적",
    "수신",
    "담당",
    "관련 근거",
    "대상",
    "내용",
    "기한",
    "제출 방법",
    "붙임",
)


@dataclass
class GongmunGenerationResult:
    markdown: str
    validation_report: ValidationReport

    @property
    def passed(self) -> bool:
        return self.validation_report.passed


def read_brief(path: Path) -> dict[str, str]:
    """Read a UTF-8 Markdown brief containing simple `key: value` lines."""
    return parse_brief(Path(path).read_text(encoding="utf-8"))


def parse_brief(text: str) -> dict[str, str]:
    """Parse known Gongmun Writer fields from Markdown text."""
    fields = {name: UNKNOWN for name in BRIEF_FIELDS}
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue

        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip() or UNKNOWN
        if key in fields:
            fields[key] = value
    return fields


def generate_gongmun_markdown(fields: dict[str, str]) -> str:
    """Generate a conservative validation-ready Gongmun Markdown draft."""
    value = _field_getter(fields)
    title = _title_from_fields(fields)
    content = value("내용")
    object_particle = _object_particle(content)

    lines = [
        f"# {title}",
        "",
        f"수신: {value('수신')}",
        f"담당: {value('담당')}",
        "",
        f"관련: {value('관련 근거')}",
        "",
        _body_intro(content, object_particle),
        "",
        f"1. 대상: {value('대상')}",
        f"2. 내용: {content}",
        f"3. 기한: {value('기한')}",
        f"4. 제출 방법: {value('제출 방법')}",
        "",
        f"붙임  {value('붙임')}.  끝.",
    ]
    return "\n".join(lines) + "\n"


def generate_gongmun_from_file(path: Path) -> str:
    """Read a brief file and return generated Gongmun Markdown."""
    return generate_gongmun_markdown(read_brief(path))


def write_gongmun_draft(brief_path: Path, output_path: Path) -> Path:
    """Generate a Gongmun Markdown draft and write it as UTF-8."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(generate_gongmun_from_file(brief_path), encoding="utf-8")
    return output_path


def generate_and_validate(brief_path: Path) -> GongmunGenerationResult:
    """Generate a draft and validate it with existing gongmun_rules."""
    markdown = generate_gongmun_from_file(brief_path)
    return GongmunGenerationResult(
        markdown=markdown,
        validation_report=validate(markdown),
    )


def _field_getter(fields: dict[str, str]):
    def get(name: str) -> str:
        value = fields.get(name, UNKNOWN).strip()
        return value or UNKNOWN

    return get


def _title_from_fields(fields: dict[str, str]) -> str:
    content = fields.get("내용", "").strip()
    purpose = fields.get("목적", "").strip()
    if content and content != UNKNOWN:
        return f"{content} 안내"
    if purpose and purpose != UNKNOWN:
        return f"{purpose.rstrip('.')} 안내"
    return "문서 제목"


def _body_intro(content: str, object_particle: str) -> str:
    if content == UNKNOWN:
        return "관련 근거에 따라 아래와 같이 안내합니다."
    return f"관련 근거에 따라 {content}{object_particle} 아래와 같이 안내합니다."


def _object_particle(text: str) -> str:
    if not text or text == UNKNOWN:
        return ""

    last = text[-1]
    if not ("가" <= last <= "힣"):
        return "을"

    has_final_consonant = (ord(last) - ord("가")) % 28 != 0
    return "을" if has_final_consonant else "를"
