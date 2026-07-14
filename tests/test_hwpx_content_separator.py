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


def _write_hwpx(path: Path) -> None:
    with zipfile.ZipFile(path, "w") as package:
        package.writestr("mimetype", "application/hwp+zip", compress_type=zipfile.ZIP_STORED)
        package.writestr("Contents/header.xml", HEADER)
        package.writestr("Contents/content.hpf", CONTENT)
        package.writestr("Contents/section0.xml", SECTION)
        package.writestr("settings.xml", "<settings/>")


def test_separator_preserves_footer_instruction_as_fixed_text() -> None:
    # Given: a report with the exact fixed footer and a different ※ report text.
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        source = root / "source.hwpx"
        output = root / "template"
        _write_hwpx(source)

        # When: the source is separated into content and fixed template XML.
        result = separate_hwpx_template_content(
            source,
            output,
            template_id="demo_template",
            template_name="demo",
            institution="demo",
        )

        content = json.loads(result.content_sample.read_text(encoding="utf-8"))
        mapping = json.loads(result.placeholder_map.read_text(encoding="utf-8"))
        section_template = (output / "template" / "section0.template.xml").read_text(
            encoding="utf-8"
        )

        # Then: only the exact footer stays fixed; the other text remains replaceable.
        assert content["fields"]["document_title_01"] == "가상자산 관련 이상거래 현황파악 진행현황"
        assert content["fields"]["document_title_02"] == "※ 보고 일정은 별도 안내"
        assert content["fields"]["body_paragraph_01"] == "□ 최근 이상매매 정황이 포착됨"
        assert "footer_instruction_01" not in content["fields"]
        assert "{{document_title_01}}" in section_template
        assert "{{document_title_02}}" in section_template
        assert "{{body_paragraph_01}}" in section_template
        assert "※ 1페이지 하단에 보고자 및 연락처 등 표시" in section_template
        assert "{{footer_instruction_01}}" not in section_template
        assert "현안(이슈)보고" in section_template
        assert "끝." in section_template
        assert mapping["fields"][0]["table"] == 0
        assert mapping["fields"][0]["row"] == 0
        assert mapping["fields"][0]["col"] == 1
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


if __name__ == "__main__":
    test_separator_preserves_footer_instruction_as_fixed_text()
    print("PASS: HWPX content separator")
