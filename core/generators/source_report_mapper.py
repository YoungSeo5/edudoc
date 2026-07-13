"""Map a source report (Markdown) onto an institution template's fields.

Deterministic half of the source -> document flow. It fills ONLY the fields that
can be read unambiguously from the source (date, title, department, contact) and
leaves judgment fields (body paragraphs, conclusion, checkbox lines, notes) as
``확인 필요`` — never inventing content. It also returns the parsed
``source_facts`` (title/date/body lines/contacts) so the agent (skill) can assign
the judgment fields into the right blocks.

Output feeds ``core.adapters.hwpx_template_renderer``.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

UNKNOWN = "확인 필요"

# categories a deterministic reader can fill from the source text
_DETERMINISTIC_CATEGORIES = {"date", "document_title", "department", "contact"}

_DATE_RE = re.compile(
    r"20\d{2}\s*\.\s*\d{1,2}\s*\.\s*\d{1,2}\s*\.?|20\d{2}\s*년\s*\d{1,2}\s*월\s*\d{1,2}\s*일"
)
_PHONE = r"0\d{1,2}[-)]\s?\d{3,4}-\d{4}"
_DEPARTMENT_RE = re.compile(r"[가-힣A-Za-z0-9·]{2,20}(?:국|과|실|팀|원|센터|위원회)")
_CONTACT_RE = re.compile(
    r"(?:국장|팀장|과장|담당자?|반장)\s*[가-힣]{2,4}\s*\(?\s*☎?\s*" + _PHONE + r"\s*\)?"
)
_BODY_MARKERS = ("□", "○", "◦", "❍", "-", "※", "⇨", "*", "†")


@dataclass
class MappingResult:
    content: dict[str, str]                        # field_id -> value (or 확인 필요)
    filled_fields: list[str] = field(default_factory=list)
    unresolved_fields: list[str] = field(default_factory=list)
    source_facts: dict[str, Any] = field(default_factory=dict)

    def to_content_json(self, template_id: str, source_name: str) -> dict:
        return {"template_id": template_id, "source_file": source_name, "fields": self.content}


def map_source_to_template_fields(
    source_markdown: str,
    placeholder_map: dict | Path | str,
    *,
    unknown: str = UNKNOWN,
) -> MappingResult:
    """Map source Markdown onto placeholder-map fields (deterministic fields only)."""
    if not isinstance(placeholder_map, dict):
        placeholder_map = _load_placeholder_map(placeholder_map)

    facts = extract_source_facts(source_markdown)
    departments = list(facts["departments"])
    contacts = list(facts["contacts"])

    content: dict[str, str] = {}
    filled: list[str] = []
    unresolved: list[str] = []
    for entry in placeholder_map["fields"]:
        field_id = entry["field_id"]
        category = entry.get("category")
        value: str | None = None
        if category == "date":
            value = facts["date"]
        elif category == "document_title":
            value = facts["title"]
        elif category == "department":
            value = departments.pop(0) if departments else None
        elif category == "contact":
            value = contacts.pop(0) if contacts else None

        if category in _DETERMINISTIC_CATEGORIES and value:
            content[field_id] = value
            filled.append(field_id)
        else:
            content[field_id] = unknown  # judgment field or nothing extracted -> agent fills
            unresolved.append(field_id)

    return MappingResult(
        content=content,
        filled_fields=filled,
        unresolved_fields=unresolved,
        source_facts=facts,
    )


def extract_source_facts(markdown: str) -> dict[str, Any]:
    """Parse deterministic material from the source Markdown for downstream mapping."""
    lines = [line.rstrip() for line in markdown.splitlines()]
    date_match = _DATE_RE.search(markdown)
    # department is taken from the contact/문의 context (avoids the agency name in the header)
    contact_lines = [line for line in lines if re.search(_PHONE, line)]
    departments = _unique(
        match for line in contact_lines for match in _DEPARTMENT_RE.findall(line)
    )
    return {
        "title": _first_title(lines),
        "date": _normalize(date_match.group(0)) if date_match else None,
        "departments": departments,
        "all_departments": _unique(_DEPARTMENT_RE.findall(markdown)),
        "contacts": _unique(_CONTACT_RE.findall(markdown)),
        "body_lines": [
            _normalize(line) for line in lines
            if line.strip() and line.strip()[:1] in _BODY_MARKERS
        ],
    }


def _first_title(lines: list[str]) -> str | None:
    headings = [line.lstrip("#").strip() for line in lines if line.strip().startswith("#")]
    if headings:
        return headings[0]
    for line in lines:
        stripped = line.strip()
        if stripped and not _DATE_RE.search(stripped) and len(stripped) >= 4:
            return stripped
    return None


def _load_placeholder_map(path: Path | str) -> dict:
    path = Path(path)
    if path.is_dir():
        path = path / "placeholder_map.json"
    return json.loads(path.read_text(encoding="utf-8"))


def _unique(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        norm = _normalize(value)
        if norm and norm not in seen:
            seen.add(norm)
            result.append(norm)
    return result


def _normalize(value: str) -> str:
    return " ".join(value.split())
