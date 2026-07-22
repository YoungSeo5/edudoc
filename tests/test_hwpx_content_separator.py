from __future__ import annotations

import json
import sys
import tempfile
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.templates.hwpx_content_separator import separate_hwpx_template_content


HEADER = (
    '<?xml version="1.0" encoding="UTF-8"?>'
    '<hh:head xmlns:hh="http://www.hancom.co.kr/hwpml/2011/head">'
    "<hh:beginNum/>"
    "</hh:head>"
)
CONTENT = (
    '<?xml version="1.0" encoding="UTF-8"?>'
    '<opf:package xmlns:opf="http://www.idpf.org/2007/opf/">'
    "<opf:manifest>"
    '<opf:item id="header" href="Contents/header.xml" media-type="application/xml"/>'
    '<opf:item id="section0" href="Contents/section0.xml" media-type="application/xml"/>'
    "</opf:manifest>"
    "<opf:spine><opf:itemref idref=\"section0\"/></opf:spine>"
    "</opf:package>"
)
SECTION = (
    '<?xml version="1.0" encoding="UTF-8"?>'
    '<hs:sec xmlns:hs="http://www.hancom.co.kr/hwpml/2011/section" '
    'xmlns:hp="http://www.hancom.co.kr/hwpml/2011/paragraph">'
    '<hp:p><hp:run><hp:tbl rowCnt="1" colCnt="2">'
    '<hp:tr><hp:tc><hp:cellAddr rowAddr="0" colAddr="0"/>'
    '<hp:subList><hp:p><hp:run><hp:t>현안(이슈)보고</hp:t></hp:run></hp:p></hp:subList>'
    "</hp:tc><hp:tc><hp:cellAddr rowAddr=\"0\" colAddr=\"1\"/>"
    '<hp:subList><hp:p><hp:run><hp:t>가상자산 관련 이상거래 현황파악 진행현황</hp:t></hp:run></hp:p></hp:subList>'
    "</hp:tc></hp:tr></hp:tbl></hp:run></hp:p>"
    "<hp:p><hp:run><hp:t>□ 최근 이상매매 정황이 포착됨</hp:t></hp:run></hp:p>"
    "<hp:p><hp:run><hp:t>※ 보고 일정은 별도 안내</hp:t></hp:run></hp:p>"
    "<hp:p><hp:run><hp:t>※ 1페이지 하단에 보고자 및 연락처 등 표시</hp:t></hp:run></hp:p>"
    "<hp:p><hp:run><hp:t>끝.</hp:t></hp:run></hp:p>"
    "</hs:sec>"
)

STRUCTURED_SECTION = (
    '<?xml version="1.0" encoding="UTF-8"?>'
    '<hs:sec xmlns:hs="http://www.hancom.co.kr/hwpml/2011/section" '
    'xmlns:hp="http://www.hancom.co.kr/hwpml/2011/paragraph">'
    '<hp:p><hp:run><hp:tbl rowCnt="1" colCnt="1"><hp:tr><hp:tc>'
    '<hp:cellAddr rowAddr="0" colAddr="0"/><hp:subList>'
    '<hp:p><hp:run><hp:t>Ⅱ.</hp:t><hp:t>향후계획</hp:t></hp:run></hp:p>'
    '</hp:subList></hp:tc></hp:tr></hp:tbl></hp:run></hp:p>'
    '<hp:p><hp:run><hp:tbl rowCnt="1" colCnt="3"><hp:tr>'
    '<hp:tc><hp:cellAddr rowAddr="0" colAddr="0"/><hp:subList>'
    '<hp:p><hp:run><hp:t>다</hp:t></hp:run></hp:p></hp:subList></hp:tc>'
    '<hp:tc><hp:cellAddr rowAddr="0" colAddr="1"/><hp:subList>'
    '<hp:p><hp:run><hp:t/></hp:run></hp:p></hp:subList></hp:tc>'
    '<hp:tc><hp:cellAddr rowAddr="0" colAddr="2"/><hp:subList>'
    '<hp:p><hp:run><hp:t>검토사항</hp:t></hp:run></hp:p></hp:subList></hp:tc>'
    '</hp:tr></hp:tbl></hp:run></hp:p>'
    '<hp:p><hp:run><hp:tbl rowCnt="2" colCnt="2">'
    '<hp:tr><hp:tc><hp:cellAddr rowAddr="0" colAddr="0"/><hp:subList>'
    '<hp:p><hp:run><hp:t>구분</hp:t></hp:run></hp:p></hp:subList></hp:tc>'
    '<hp:tc><hp:cellAddr rowAddr="0" colAddr="1"/><hp:subList>'
    '<hp:p><hp:run><hp:t>검토 결과</hp:t></hp:run></hp:p></hp:subList></hp:tc></hp:tr>'
    '<hp:tr><hp:tc><hp:cellAddr rowAddr="1" colAddr="0"/><hp:subList>'
    '<hp:p><hp:run><hp:t>담당 부서</hp:t></hp:run></hp:p></hp:subList></hp:tc>'
    '<hp:tc><hp:cellAddr rowAddr="1" colAddr="1"/><hp:subList>'
    '<hp:p><hp:run><hp:t>디지털감독팀</hp:t></hp:run></hp:p></hp:subList></hp:tc></hp:tr>'
    '</hp:tbl></hp:run></hp:p>'
    '<hp:p><hp:run><hp:t>사용자가 문서마다 작성하는 실제 검토 내용</hp:t></hp:run></hp:p>'
    '</hs:sec>'
)


def _write_hwpx(path: Path, section: str = SECTION) -> None:
    with zipfile.ZipFile(path, "w") as package:
        package.writestr("mimetype", "application/hwp+zip", compress_type=zipfile.ZIP_STORED)
        package.writestr("Contents/header.xml", HEADER)
        package.writestr("Contents/content.hpf", CONTENT)
        package.writestr("Contents/section0.xml", section)
        package.writestr("settings.xml", "<settings/>")


def test_separator_preserves_footer_instruction_as_fixed_text() -> None:
    # Given: a report with the exact fixed footer and a different ※ report text.
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        source = root / "source.hwpx"
        output = root / "template"
        rules = root / "content-separation-rules.json"
        _write_hwpx(source)
        rules.write_text(
            json.dumps(
                {
                    "rules": [
                        {
                            "role": "fixed_text",
                            "section": "section0.xml",
                            "text_node_index": 4,
                        }
                    ]
                }
            ),
            encoding="utf-8",
        )

        # When: the source is separated into content and fixed template XML.
        result = separate_hwpx_template_content(
            source,
            output,
            template_id="demo_template",
            template_name="demo",
            institution="demo",
            rules_path=rules,
        )

        content = json.loads(result.content_sample.read_text(encoding="utf-8"))
        mapping = json.loads(result.placeholder_map.read_text(encoding="utf-8"))
        section_template = (output / "template" / "section0.template.xml").read_text(
            encoding="utf-8"
        )

        # Then: only the exact footer stays fixed; the other text remains replaceable.
        assert content["fields"]["document_title_02"] == "가상자산 관련 이상거래 현황파악 진행현황"
        assert content["fields"]["document_title_03"] == "※ 보고 일정은 별도 안내"
        assert content["fields"]["body_paragraph_01"] == "□ 최근 이상매매 정황이 포착됨"
        assert "footer_instruction_01" not in content["fields"]
        assert "{{document_title_02}}" in section_template
        assert "{{document_title_03}}" in section_template
        assert "{{body_paragraph_01}}" in section_template
        assert "※ 1페이지 하단에 보고자 및 연락처 등 표시" in section_template
        assert "{{footer_instruction_01}}" not in section_template
        assert "현안(이슈)보고" in section_template
        assert "끝." in section_template
        assert mapping["fields"][0]["table"] == 0
        assert mapping["fields"][0]["row"] == 0
        assert mapping["fields"][0]["col"] == 1
        assert mapping["classification_rule_set"] == "structural-v1"
        assert mapping["template_rule_count"] == 1
        updated_template = json.loads((output / "template.json").read_text(encoding="utf-8"))
        assert updated_template["content_separation"]["status"] == "candidate"
        assert updated_template["rendering_rules"]["preserve_linesegarray"] is False
        review = result.review.read_text(encoding="utf-8")
        assert "- XML structure, style IDs, and table shapes are preserved." in review
        assert (
            "- Rendering removes `linesegarray` caches from changed sections so "
            "Hancom can recalculate text layout."
        ) in review
        assert (
            "- Rendering retains `linesegarray` caches in unchanged sections."
        ) in review
        assert "linesegarray are preserved" not in review


def test_separator_uses_structure_roles_and_keeps_user_values_replaceable() -> None:
    # Given: section markers, table labels, and document-specific values share one HWPX.
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        source = root / "source.hwpx"
        output = root / "template"
        _write_hwpx(source, STRUCTURED_SECTION)

        # When: the source is separated using common structural rules only.
        result = separate_hwpx_template_content(
            source,
            output,
            template_id="structured_template",
            template_name="structured",
            institution="demo",
        )

        mapping = json.loads(result.placeholder_map.read_text(encoding="utf-8"))
        placeholders = {
            entry["sample_value"]: entry["placeholder"] for entry in mapping["fields"]
        }
        section_template = (output / "template" / "section0.template.xml").read_text(
            encoding="utf-8"
        )

        # Then: fixed structure stays literal, while per-document values stay replaceable.
        assert {
            "Ⅱ.",
            "다",
            "검토사항",
            "향후계획",
            "구분",
            "검토 결과",
            "담당 부서",
        }.isdisjoint(placeholders)
        assert "디지털감독팀" in placeholders
        assert "사용자가 문서마다 작성하는 실제 검토 내용" in placeholders
        assert "Ⅱ." in section_template
        assert "다" in section_template
        assert "검토사항" in section_template
        assert "향후계획" in section_template
        assert placeholders["디지털감독팀"] in section_template
        assert placeholders["사용자가 문서마다 작성하는 실제 검토 내용"] in section_template


def test_separator_is_deterministic_for_the_same_source() -> None:
    # Given: one HWPX source and two fresh output directories.
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        source = root / "source.hwpx"
        _write_hwpx(source, STRUCTURED_SECTION)

        # When: the same source is separated twice.
        first = separate_hwpx_template_content(
            source,
            root / "first",
            template_id="structured_template",
            institution="demo",
        )
        second = separate_hwpx_template_content(
            source,
            root / "second",
            template_id="structured_template",
            institution="demo",
        )

        # Then: every content-separation derivative is byte-identical.
        assert first.content_sample.read_bytes() == second.content_sample.read_bytes()
        assert first.placeholder_map.read_bytes() == second.placeholder_map.read_bytes()
        assert first.review.read_bytes() == second.review.read_bytes()
        assert (
            first.output_dir / "template" / "section0.template.xml"
        ).read_bytes() == (
            second.output_dir / "template" / "section0.template.xml"
        ).read_bytes()


if __name__ == "__main__":
    test_separator_preserves_footer_instruction_as_fixed_text()
    print("PASS: HWPX content separator")
