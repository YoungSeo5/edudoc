from __future__ import annotations

import html
import json
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Final

from ..adapters.hwpx_template_renderer import snapshot_source_hwpx
from .hwpx_package_extractor import HwpxExtractionResult, extract_hwpx_template


_T_NODE_RE = re.compile(
    r"(<(?P<self_prefix>[A-Za-z_][\w.-]*:)?t\b(?P<self_attrs>[^>]*)/>)"
    r"|(<(?P<open_prefix>[A-Za-z_][\w.-]*:)?t\b(?P<attrs>[^>]*)>)"
    r"(?P<body>.*?)"
    r"(</(?P=open_prefix)?t>)",
    re.S,
)
_DATE_RE = re.compile(r"(?:20\d{2}|'\d{2})[.년]\s*\d{1,2}")
_PHONE_RE = re.compile(r"☎|0\d{1,2}-\d{3,4}-\d{4}|\d{3,4}-\d{4}")
_FIXED_TEXTS: Final = frozenset({"※ 1페이지 하단에 보고자 및 연락처 등 표시"})
_STABLE_TEXTS = {
    "현안(이슈)보고",
    "☑ 요약 또는 배경",
    "1. 추진 배경",
    "시    간",
    "내     용",
    "비   고",
    "끝.",
}


@dataclass(frozen=True)
class HwpxContentSeparationResult:
    output_dir: Path
    extraction: HwpxExtractionResult
    content_sample: Path
    placeholder_map: Path
    review: Path


def separate_hwpx_template_content(
    source: Path | str,
    output_dir: Path | str,
    *,
    template_id: str,
    template_name: str | None = None,
    institution: str = "확인 필요",
) -> HwpxContentSeparationResult:
    extraction = extract_hwpx_template(
        source,
        output_dir,
        template_id=template_id,
        template_name=template_name,
        institution=institution,
    )
    root = Path(output_dir)
    # self-contain: keep a byte copy of the original so rendering needs no external file
    snapshot_source_hwpx(source, root)
    section_results = []
    fields: dict[str, Any] = {}
    placeholder_entries = []

    for raw_section in sorted((root / "raw").glob("section*.xml"), key=_section_sort_key):
        decisions = _section_decisions(raw_section)
        template_xml, applied = _apply_decisions(raw_section.read_text(encoding="utf-8"), decisions)
        template_section = root / "template" / raw_section.name.replace(".xml", ".template.xml")
        template_section.write_text(template_xml, encoding="utf-8")
        section_results.append(
            {
                "section": raw_section.name,
                "text_node_count": len(decisions),
                "placeholder_count": len(applied),
            }
        )
        for item in applied:
            fields[item["field_id"]] = item["sample_value"]
            placeholder_entries.append(item)

    content_sample = root / "content.sample.json"
    placeholder_map = root / "placeholder_map.json"
    review = root / "template.review.md"
    content_sample.write_text(
        json.dumps(
            {
                "template_id": template_id,
                "source_file": Path(source).name,
                "fields": fields,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    placeholder_map.write_text(
        json.dumps(
            {
                "template_id": template_id,
                "replacement_mode": "hp_t_text_only",
                "fields": placeholder_entries,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    review.write_text(
        _review_text(template_id, section_results, placeholder_entries),
        encoding="utf-8",
    )
    _update_template_json(root / "template.json", content_sample, placeholder_map, review)
    return HwpxContentSeparationResult(
        output_dir=root,
        extraction=extraction,
        content_sample=content_sample,
        placeholder_map=placeholder_map,
        review=review,
    )


def _section_decisions(path: Path) -> list[dict[str, Any]]:
    root = ET.fromstring(path.read_bytes())
    parent_map = {child: parent for parent in root.iter() for child in parent}
    table_indexes = {id(node): index for index, node in enumerate(_nodes(root, "tbl"))}
    decisions = []
    counters: dict[str, int] = {}
    for index, node in enumerate(_nodes(root, "t")):
        text = "".join(node.itertext())
        normalized = _normalize(text)
        category = _category(normalized)
        if normalized in _FIXED_TEXTS:
            category = "fixed_text"
        replace = bool(normalized) and category not in {"fixed_label", "fixed_text"}
        field_id = None
        if replace:
            counters[category] = counters.get(category, 0) + 1
            field_id = f"{category}_{counters[category]:02d}"
        decisions.append(
            {
                "text_node_index": index,
                "original_text": text,
                "normalized_text": normalized,
                "replace": replace,
                "category": category,
                "field_id": field_id,
                "placeholder": f"{{{{{field_id}}}}}" if field_id else None,
                "location": _location(node, parent_map, table_indexes, path.name),
            }
        )
    return decisions


def _apply_decisions(xml: str, decisions: list[dict[str, Any]]) -> tuple[str, list[dict[str, Any]]]:
    parts = []
    cursor = 0
    text_index = 0
    applied = []
    for match in _T_NODE_RE.finditer(xml):
        parts.append(xml[cursor:match.start()])
        decision = decisions[text_index] if text_index < len(decisions) else None
        if match.group(1):
            parts.append(match.group(1))
        elif decision and decision["replace"]:
            placeholder = html.escape(decision["placeholder"], quote=False)
            parts.append(match.group(4))
            parts.append(placeholder)
            parts.append(match.group(8))
            applied.append(
                {
                    "field_id": decision["field_id"],
                    "placeholder": decision["placeholder"],
                    "sample_value": decision["original_text"],
                    "category": decision["category"],
                    "section": decision["location"]["section"],
                    "text_node_index": decision["text_node_index"],
                    "table": decision["location"].get("table"),
                    "row": decision["location"].get("row"),
                    "col": decision["location"].get("col"),
                }
            )
        else:
            parts.append(match.group(0))
        cursor = match.end()
        text_index += 1
    parts.append(xml[cursor:])
    return "".join(parts), applied


def _category(text: str) -> str:
    if not text:
        return "empty"
    if text in _STABLE_TEXTS:
        return "fixed_label"
    if _DATE_RE.search(text):
        return "date"
    if _PHONE_RE.search(text):
        return "contact"
    if "☑" in text or text.count("□") >= 2:
        return "checkbox_line"
    if text.startswith("□"):
        return "body_paragraph"
    if text.startswith("◦"):
        return "body_bullet"
    if text.startswith("*"):
        return "stat_note"
    if text.startswith("†"):
        return "detail_note"
    if text.startswith("⇨"):
        return "conclusion"
    if ("보고" in text or "현황" in text or "계획" in text) and len(text) <= 80:
        return "document_title"
    if text.endswith("국") or text.endswith("팀") or text.endswith("과"):
        return "department"
    return "content"


def _location(
    node: ET.Element,
    parent_map: dict[ET.Element, ET.Element],
    table_indexes: dict[int, int],
    section_name: str,
) -> dict[str, Any]:
    table = None
    row = None
    col = None
    current = node
    while current in parent_map:
        current = parent_map[current]
        local = _local_name(current.tag)
        if local == "tbl" and table is None:
            table = table_indexes.get(id(current))
        elif local == "tc":
            for child in current:
                if _local_name(child.tag) == "cellAddr":
                    row = _int_attr(child, "rowAddr")
                    col = _int_attr(child, "colAddr")
                    break
    return {"section": section_name, "table": table, "row": row, "col": col}


def _nodes(root: ET.Element, local_name: str) -> list[ET.Element]:
    return [node for node in root.iter() if _local_name(node.tag) == local_name]


def _local_name(value: str) -> str:
    return value.rsplit("}", 1)[-1].split(":", 1)[-1]


def _int_attr(node: ET.Element, name: str) -> int | None:
    for key, value in node.attrib.items():
        if _local_name(key) == name:
            try:
                return int(value)
            except ValueError:
                return None
    return None


def _normalize(value: str) -> str:
    return " ".join(value.split())


def _section_sort_key(path: Path) -> int:
    match = re.search(r"section(\d+)", path.name)
    return int(match.group(1)) if match else 10**9


def _review_text(
    template_id: str,
    section_results: list[dict[str, Any]],
    entries: list[dict[str, Any]],
) -> str:
    lines = [
        "# Template Content Separation Review",
        "",
        f"- Template ID: `{template_id}`",
        "- Status: `candidate`",
        "- XML structure, style IDs, table shapes, and linesegarray are preserved.",
        "- Only selected `<hp:t>` text contents were replaced with placeholders.",
        "",
        "## Sections",
        "",
    ]
    for section in section_results:
        lines.append(
            f"- `{section['section']}`: text_nodes={section['text_node_count']}, "
            f"placeholders={section['placeholder_count']}"
        )
    lines.extend(["", "## Placeholder Fields", ""])
    for entry in entries:
        location = []
        if entry.get("table") is not None:
            location.append(f"table={entry['table']}")
        if entry.get("row") is not None:
            location.append(f"row={entry['row']}")
        if entry.get("col") is not None:
            location.append(f"col={entry['col']}")
        suffix = f" ({', '.join(location)})" if location else ""
        lines.append(
            f"- `{entry['field_id']}` -> `{entry['placeholder']}` "
            f"[{entry['category']}]{suffix}"
        )
    lines.append("")
    return "\n".join(lines)


def _update_template_json(
    path: Path,
    content_sample: Path,
    placeholder_map: Path,
    review: Path,
) -> None:
    data = json.loads(path.read_text(encoding="utf-8"))
    placeholder_data = json.loads(placeholder_map.read_text(encoding="utf-8"))
    template_sections = sorted(
        str(item.relative_to(path.parent)).replace("\\", "/")
        for item in (path.parent / "template").glob("section*.template.xml")
    )
    data["content_separation"] = {
        "status": "candidate",
        "content_sample": content_sample.name,
        "placeholder_map": placeholder_map.name,
        "review": review.name,
        "replacement_mode": "hp_t_text_only",
        "field_count": len(placeholder_data.get("fields", [])),
        "template_sections": template_sections,
    }
    data.setdefault("rendering_rules", {})
    data["rendering_rules"]["self_contained_base"] = "source.hwpx"
    data["rendering_rules"]["replace_only_hp_t_text"] = True
    data["rendering_rules"]["preserve_table_structure"] = True
    data["rendering_rules"]["preserve_linesegarray"] = True
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
