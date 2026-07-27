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

# 이 모듈의 경계:
# hwpx_package_extractor가 만든 candidate 폴더
# → 각 <hp:t>를 고정 구조 또는 교체 콘텐츠로 분류
# → template XML, content.sample.json, placeholder_map.json, 검토 보고서 생성
# 승인 여부는 바꾸지 않으며, 결과는 계속 candidate 상태다.

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
    # 흐름 1: 공통 분류 규칙과 기관별 추가 규칙을 먼저 읽는다.
    rules = load_separation_rules(rules_path)

    # 흐름 2: 원본 HWPX에서 raw/와 template/ 작업본 및 candidate
    # template.json을 만든다. 이 함수가 패키지 추출 단계를 내부 호출한다.
    extraction = extract_hwpx_template(
        source,
        output_dir,
        template_id=template_id,
        template_name=template_name,
        institution=institution,
    )
    root = Path(output_dir)

    # 흐름 3: raw/만으로는 완전한 HWPX 패키지를 재구성할 수 없으므로,
    # 렌더러가 사용할 원본 전체 패키지를 source.hwpx로 보존한다.
    # raw/에는 분석 대상으로 선택한 일부 자산만 들어있고, hwpx 패키지에 필요한 추출되지 않은 기타 자산은 source.hwpx에서 가져와야 한다.

    snapshot_source_hwpx(source, root)
    section_results = []
    fields: dict[str, Any] = {}
    placeholder_entries = []

    # 흐름 4: 모든 section의 <hp:t>를 문서 순서대로 분류한다.
    # counters를 section 밖에 두어 여러 section에서도 field_id가 중복되지 않는다.
    field_id_counters: dict[str, int] = {}
    for raw_section in sorted((root / "raw").glob("section*.xml"), key=_section_sort_key):
        decisions = _section_decisions(raw_section, rules, field_id_counters)

        # CONTENT로 판정한 텍스트만 {{field_id}}로 바꾸고, FIXED 텍스트와
        # XML 구조·스타일 ID는 원문 그대로 유지한다.
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

    # 흐름 5: 같은 분리 결과를 세 관점으로 저장한다.
    # content.sample.json은 원본 예시 값, placeholder_map.json은 위치 계약,
    # template.review.md는 사람이 승인 전에 읽는 검토 자료다.
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

    # 흐름 6: 생성한 산출물의 상대 경로와 분리 상태를 candidate
    # template.json에 연결한다. status 자체를 approved로 바꾸지는 않는다.
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


# 한 section을 읽어 각 텍스트 노드에 "유지/교체" 결정을 붙인다.
# 이 단계는 아직 XML을 변경하지 않고 결정 목록만 만든다.
def _section_decisions(
    path: Path, rules: SeparationRules, counters: dict[str, int]
) -> list[dict[str, Any]]:
    root = ET.fromstring(path.read_bytes())
    decisions = []
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


# 결정 목록을 원본 XML 문자열의 <hp:t> 순서와 맞춰 적용한다.
# XML 파서를 통한 재직렬화를 피하므로 템플릿의 나머지 바이트 구조는 유지된다.
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
