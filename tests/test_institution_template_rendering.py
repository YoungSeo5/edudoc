"""Institution-template HWPX rendering stays explicit and preserves fixed labels."""
from __future__ import annotations

import json
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.adapters.hwpx_template_renderer import (
    RenderExecutionContext,
    TemplateContent,
    load_template_content,
)
from core.compose.render import render_report_to_hwpx
from core.compose.report import Block, ComposedReport, Section
from scripts.compose import render_plan

ROOT = Path(__file__).resolve().parent.parent
TEMPLATES = ROOT / "templates" / "institutions"
FSS_DIRECTOR = TEMPLATES / "금융감독원" / "금감원 원장보고"
FSS_VIRTUAL_ASSET = TEMPLATES / "금융감독원" / "금감원 원장보고 가상자산"
FSS_ONE_PAGE = TEMPLATES / "금융감독원" / "금감원 원페이지"
FSS_DIRECTOR_CONTENT = (
    ROOT / "tests" / "fixtures" / "template-content" / "fss_director_report.input.json"
)
EXECUTION_CONTEXT = RenderExecutionContext(
    "오영서",
    datetime(2026, 8, 5, tzinfo=timezone.utc),
)


def test_compose_renders_an_institution_template_with_a_metadata_contract() -> None:
    """계약과 실행 문맥이 모두 있으면 compose 경로로 최종 문서가 나온다."""
    report = ComposedReport(
        title="가상자산 이상거래 대응 진행현황",
        sections=[Section(no="1", title="현황", blocks=[Block(marker="□", text="점검 중")])],
    )
    content = TemplateContent(
        template_id="fss_director_report",
        fields=json.loads(FSS_DIRECTOR_CONTENT.read_text(encoding="utf-8")),
    )

    with tempfile.TemporaryDirectory() as tmp:
        output = Path(tmp) / "report.hwpx"
        _, result = render_report_to_hwpx(
            report,
            Path(tmp) / "report.md",
            output,
            institution="금융감독원",
            document_type="금감원 원장보고",
            template_content=content,
            execution_context=EXECUTION_CONTEXT,
        )
        rendered = output.is_file()

    assert result.ok, result.error
    assert rendered
    assert result.meta["engine"] == "institution_template"
    assert result.meta["template_id"] == "fss_director_report"
    assert result.meta["title_updated"] is True


def test_compose_requires_an_execution_context_for_institution_rendering() -> None:
    report = ComposedReport(title="실행 문맥 검증")
    content = TemplateContent(
        template_id="fss_director_report",
        fields=json.loads(FSS_DIRECTOR_CONTENT.read_text(encoding="utf-8")),
    )

    with tempfile.TemporaryDirectory() as tmp:
        with pytest.raises(ValueError, match="execution_context is required"):
            render_report_to_hwpx(
                report,
                Path(tmp) / "report.md",
                Path(tmp) / "report.hwpx",
                institution="금융감독원",
                document_type="금감원 원장보고",
                template_content=content,
            )


def test_compose_refuses_an_unapproved_institution_template() -> None:
    """최종 문서 생성은 승인된 템플릿만 사용한다.

    `금감원 원장보고 가상자산`은 반복·간격 계약이 없어 승인 상태에서 내려왔다.
    승인되지 않은 템플릿은 registry가 돌려주지 않으므로, 부분 결과를 쓰는 대신
    거부하고 그 사실을 오류로 보고한다.
    """
    report = ComposedReport(
        title="가상자산 이상거래 관련 현황 점검 진행상황",
        sections=[Section(no="1", title="현황", blocks=[Block(marker="□", text="점검 중")])],
    )
    content = load_template_content(FSS_VIRTUAL_ASSET / "content.sample.json")

    with tempfile.TemporaryDirectory() as tmp:
        output = Path(tmp) / "report.hwpx"
        _, result = render_report_to_hwpx(
            report,
            Path(tmp) / "report.md",
            output,
            institution="금융감독원",
            document_type="금감원 원장보고 가상자산",
            template_content=content,
            execution_context=EXECUTION_CONTEXT,
        )

    assert result.ok is False
    assert result.error_code == "institution_template_not_found"
    assert "approved institution template not found" in result.error
    assert result.meta["engine"] == "institution_template"
    assert result.meta["available"] is False
    assert not output.exists()


def test_compose_cli_rejects_content_for_a_different_template(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    plan = tmp_path / "report.plan.json"
    plan.write_text(
        json.dumps({"title": "기관 템플릿 식별 검증", "sections": []}, ensure_ascii=False),
        encoding="utf-8",
    )
    content = json.loads((FSS_DIRECTOR / "content.sample.json").read_text(encoding="utf-8"))
    content["template_id"] = "different_template"
    content_path = tmp_path / "content.json"
    content_path.write_text(json.dumps(content, ensure_ascii=False), encoding="utf-8")

    exit_code = render_plan.main(
        [
            "--plan",
            str(plan),
            "--to",
            "hwpx",
            "--out",
            str(tmp_path),
            "--institution",
            "금융감독원",
            "--document-type",
            "금감원 원장보고",
            "--template-content",
            str(content_path),
            "--requester-name",
            "오영서",
        ],
        failures_dir=tmp_path / "failures",
    )

    summary = json.loads(capsys.readouterr().out)
    assert exit_code == 1
    assert summary["outputs"][0]["ok"] is False
    assert "template_id mismatch" in summary["outputs"][0]["error"]
    assert not (tmp_path / "report.hwpx").exists()


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
                template_content=TemplateContent(template_id="fss_virtual_asset_report", fields={}),
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
            template_content=TemplateContent(template_id="unregistered_template", fields={}),
            execution_context=EXECUTION_CONTEXT,
        )

    assert problems == []
    assert result.ok is False
    assert result.output == output
    assert result.error is not None
    assert result.error_code == "institution_template_not_found"
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
