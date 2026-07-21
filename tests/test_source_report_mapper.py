"""core.generators.source_report_mapper: source Markdown -> template fields.

Proves the deterministic mapper fills only unambiguous fields (date, title,
department, contact), leaves judgment fields as 확인 필요 (never invented), picks
the reporting department from the contact context (not the agency header), and
produces a content mapping the renderer can consume with no leftover placeholders.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.adapters.hwpx_template_renderer import fill_template_sections
from core.generators.source_report_mapper import map_source_to_template_fields

ROOT = Path(__file__).resolve().parent.parent
FSS_DIR = ROOT / "templates" / "institutions" / "금융감독원" / "금감원 원장보고 가상자산"
PLACEHOLDER_MAP = FSS_DIR / "placeholder_map.json"

SOURCE = """# 가상자산 이상거래 관련 현황 점검 진행상황

(2026. 7. 9.) 금융감독원 보도자료

□ 최근 가상자산 시장에서 이상매매 정황이 다수 포착됨에 따라 대응방안을 마련하고자 함
 ◦ FDS 및 거래소 제보를 통해 특정 종목에서 단기간 거래량이 급증하는 사례가 확인됨
※ 세부 수치는 관계기관 확인 후 업데이트 예정

문의: 가상자산감독국 국장 김도윤(☎02-3145-5501), 팀장 박서연(☎02-3145-5502)
"""


def test_deterministic_fields_are_filled() -> None:
    result = map_source_to_template_fields(SOURCE, PLACEHOLDER_MAP)

    assert result.content["date_01"] == "2026. 7. 9."
    assert result.content["document_title_01"] == "가상자산 이상거래 관련 현황 점검 진행상황"
    assert result.content["department_01"] == "가상자산감독국"      # from 문의 context
    assert result.content["contact_01"] == "국장 김도윤(☎02-3145-5501)"
    assert result.content["contact_02"] == "팀장 박서연(☎02-3145-5502)"
    assert set(result.filled_fields) == {
        "date_01", "document_title_01", "department_01", "contact_01", "contact_02"
    }


def test_department_prefers_contact_context_over_agency_header() -> None:
    facts = map_source_to_template_fields(SOURCE, PLACEHOLDER_MAP).source_facts
    assert facts["departments"] == ["가상자산감독국"]        # not 금융감독원
    assert "금융감독원" in facts["all_departments"]           # still surfaced for the agent


def test_judgment_fields_stay_unknown_with_source_facts() -> None:
    result = map_source_to_template_fields(SOURCE, PLACEHOLDER_MAP)

    for field_id in ("body_paragraph_01", "conclusion_01", "checkbox_line_01", "stat_note_01"):
        assert result.content[field_id] == "확인 필요"
        assert field_id in result.unresolved_fields
    # raw material is handed to the agent, never auto-placed
    assert len(result.source_facts["body_lines"]) == 3


def test_mapper_output_renders_with_no_leftover_placeholders() -> None:
    result = map_source_to_template_fields(SOURCE, PLACEHOLDER_MAP)
    sections, render = fill_template_sections(FSS_DIR, result.content)

    section0 = sections["Contents/section0.xml"]
    assert "가상자산감독국" in section0            # deterministic field rendered
    assert "확인 필요" in section0                  # judgment field honestly shown
    assert render.leftover_placeholders == []       # every field got a value (real or 확인 필요)


if __name__ == "__main__":
    test_deterministic_fields_are_filled()
    test_department_prefers_contact_context_over_agency_header()
    test_judgment_fields_stay_unknown_with_source_facts()
    test_mapper_output_renders_with_no_leftover_placeholders()
    print("PASS: source_report_mapper (deterministic fields + honest 확인 필요 + renders)")
