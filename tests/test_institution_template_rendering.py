"""Institution-template HWPX rendering stays explicit and preserves fixed labels."""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.adapters.hwpx_template_renderer import load_content_fields
from core.compose.render import render_report_to_hwpx
from core.compose.report import Block, ComposedReport, Section

ROOT = Path(__file__).resolve().parent.parent
TEMPLATES = ROOT / "templates" / "institutions"
FSS_VIRTUAL_ASSET = TEMPLATES / "금융감독원" / "금감원 원장보고 가상자산"
FSS_ONE_PAGE = TEMPLATES / "금융감독원" / "금감원 원페이지"


def test_compose_uses_requested_institution_template_when_content_is_complete() -> None:
    report = ComposedReport(
        title="가상자산 이상거래 관련 현황 점검 진행상황",
        sections=[Section(no="1", title="현황", blocks=[Block(marker="□", text="점검 중")])],
    )
    content = load_content_fields(FSS_VIRTUAL_ASSET / "content.sample.json")

    with tempfile.TemporaryDirectory() as tmp:
        output = Path(tmp) / "report.hwpx"
        _, result = render_report_to_hwpx(
            report,
            Path(tmp) / "report.md",
            output,
            institution="금융감독원",
            document_type="금감원 원장보고 가상자산",
            template_content=content,
        )

    assert result.ok, result.error
    assert result.meta["engine"] == "institution_template"
    assert result.meta["template_id"] == "fss_virtual_asset_report"


@pytest.mark.parametrize(
    ("institution", "document_type"),
    [
        ("금융감독원", None),
        (None, "금감원 원장보고 가상자산"),
    ],
)
def test_compose_requires_complete_institution_template_identity(
    institution: str | None,
    document_type: str | None,
) -> None:
    report = ComposedReport(title="기관 템플릿 입력 검증")

    with tempfile.TemporaryDirectory() as tmp:
        with pytest.raises(ValueError):
            render_report_to_hwpx(
                report,
                Path(tmp) / "report.md",
                Path(tmp) / "report.hwpx",
                institution=institution,
                document_type=document_type,
                template_content={},
            )


def test_compose_requires_content_for_institution_template() -> None:
    report = ComposedReport(title="기관 템플릿 콘텐츠 검증")

    with tempfile.TemporaryDirectory() as tmp:
        with pytest.raises(ValueError):
            render_report_to_hwpx(
                report,
                Path(tmp) / "report.md",
                Path(tmp) / "report.hwpx",
                institution="금융감독원",
                document_type="금감원 원장보고 가상자산",
            )


def test_compose_returns_failure_when_institution_template_is_not_registered() -> None:
    report = ComposedReport(
        title="미등록 기관 템플릿",
        sections=[Section(no="1", title="현황", blocks=[Block(marker="□", text="점검 중")])],
    )

    with tempfile.TemporaryDirectory() as tmp:
        output = Path(tmp) / "report.hwpx"
        problems, result = render_report_to_hwpx(
            report,
            Path(tmp) / "report.md",
            output,
            institution="등록되지 않은 기관",
            document_type="등록되지 않은 문서",
            template_content={},
        )

    assert problems == []
    assert result.ok is False
    assert result.output == output
    assert result.error is not None
    assert result.meta["engine"] == "institution_template"
    assert result.meta["available"] is False


def test_one_page_keeps_structural_labels_out_of_the_placeholder_map() -> None:
    mapping = json.loads((FSS_ONE_PAGE / "placeholder_map.json").read_text(encoding="utf-8"))
    fields = {entry["field_id"] for entry in mapping["fields"]}
    template_xml = (FSS_ONE_PAGE / "template" / "section0.template.xml").read_text(
        encoding="utf-8"
    )

    assert {"content_03", "content_05", "content_06", "content_10", "content_11"}.isdisjoint(fields)
    assert "Ⅰ." in template_xml
    assert "가" in template_xml
    assert "개요" in template_xml
    assert "나" in template_xml
    assert "진행상황" in template_xml
