from __future__ import annotations

import html
import json
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ..adapters.hwpx_template_renderer import snapshot_source_hwpx
from .hwpx_content_artifacts import (
    render_separation_review,
    update_template_content_separation,
)
from .hwpx_content_classifier import (
    COMMON_RULE_DESCRIPTIONS,
    COMMON_RULE_SET,
    build_text_contexts,
    classify_text,
    content_category,
)
from .hwpx_package_extractor import HwpxExtractionResult, extract_hwpx_template
from .hwpx_separation_rules import (
    SeparationRules,
    TextRole,
    load_separation_rules,
)


_T_NODE_RE = re.compile(
    r"(<(?P<self_prefix>[A-Za-z_][\w.-]*:)?t\b(?P<self_attrs>[^>]*)/>)"
    r"|(<(?P<open_prefix>[A-Za-z_][\w.-]*:)?t\b(?P<attrs>[^>]*)>)"
    r"(?P<body>.*?)"
    r"(</(?P=open_prefix)?t>)",
    re.S,
)


@dataclass(frozen=True, slots=True)
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
    rules_path: Path | str | None = None,
) -> HwpxContentSeparationResult:
    rules = load_separation_rules(rules_path)
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
        decisions = _section_decisions(raw_section, rules)
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
                "classification_rule_set": COMMON_RULE_SET,
                "classification_rules": list(COMMON_RULE_DESCRIPTIONS),
                "template_rule_count": len(rules.rules),
                "fields": placeholder_entries,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    review.write_text(
        render_separation_review(template_id, section_results, placeholder_entries, rules),
        encoding="utf-8",
    )
    update_template_content_separation(
        root / "template.json", content_sample, placeholder_map, review
    )
    return HwpxContentSeparationResult(
        output_dir=root,
        extraction=extraction,
        content_sample=content_sample,
        placeholder_map=placeholder_map,
        review=review,
    )


def _section_decisions(path: Path, rules: SeparationRules) -> list[dict[str, Any]]:
    root = ET.fromstring(path.read_bytes())
    decisions = []
    counters: dict[str, int] = {}
    for context in build_text_contexts(root, path.name):
        category = content_category(context.normalized_text)
        role = classify_text(context, rules)
        candidate_field_id = None
        if context.normalized_text:
            counters[category] = counters.get(category, 0) + 1
            candidate_field_id = f"{category}_{counters[category]:02d}"
        replace = bool(context.normalized_text) and role is TextRole.CONTENT
        field_id = candidate_field_id if replace else None
        location = context.location
        decisions.append(
            {
                "text_node_index": location.text_node_index,
                "original_text": context.original_text,
                "normalized_text": context.normalized_text,
                "replace": replace,
                "category": category,
                "role": role.value,
                "field_id": field_id,
                "placeholder": f"{{{{{field_id}}}}}" if field_id else None,
                "location": {
                    "section": location.section,
                    "table": location.table,
                    "row": location.row,
                    "col": location.col,
                },
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


def _section_sort_key(path: Path) -> int:
    match = re.search(r"section(\d+)", path.name)
    return int(match.group(1)) if match else 10**9
