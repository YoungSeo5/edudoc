"""``Contents/content.hpf`` 메타데이터 갱신 계약.

생성일·수정일은 렌더 시각으로 갱신하고, 문서 제목은
``alias_map.json``의 ``title_field``가 선언된 템플릿에서만 바꾼다.
선언이 없으면 제목을 원본 그대로 유지하고
``RenderResult.title_updated``로 미변경 사실을 보고한다.

일반 템플릿의 작성자·최종저장자와 매니페스트는 원본 그대로 유지한다.
금감원 원장보고의 전용 메타데이터 계약은 task-scoped 테스트에서 별도로 검증한다.
"""
from __future__ import annotations

import json
import re
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.adapters.hwpx_template_renderer import (
    HwpxTemplateRenderError,
    RenderExecutionContext,
    orchestrate_hwpx_render,
    snapshot_source_hwpx,
)

ROOT = Path(__file__).resolve().parent.parent
FSS_DIR = ROOT / "templates" / "institutions" / "금융감독원" / "금감원 원장보고"
CONTENT = (
    ROOT / "tests" / "fixtures" / "template-content" / "fss_director_report.input.json"
)
BROTHER_HWPX = (
    ROOT / "references" / "document-types" / "public-plan"
    / "브라더 공공기관 보고서 양식.hwpx"
)

_TITLE_RE = re.compile(r"<opf:title(?:\s*/>|>(.*?)</opf:title>)", re.DOTALL)
_MANIFEST_RE = re.compile(r"<opf:manifest>.*?</opf:manifest>", re.DOTALL)
REQUESTED_AT = datetime(2026, 8, 3, 5, 49, 12, tzinfo=timezone.utc)
EXECUTION_CONTEXT = RenderExecutionContext("오영서", REQUESTED_AT)


def _hpf(package: Path) -> str:
    with zipfile.ZipFile(package) as archive:
        return archive.read("Contents/content.hpf").decode("utf-8")


def _meta(xml: str, name: str) -> str | None:
    match = re.search(
        rf'<opf:meta name="{name}"[^>]*>(.*?)</opf:meta>', xml, re.DOTALL
    )
    return match.group(1) if match else None


def _render_fss(tmp_path: Path):
    content = json.loads(CONTENT.read_text(encoding="utf-8"))
    output = tmp_path / "금감원_원장보고.hwpx"
    return output, orchestrate_hwpx_render(
        FSS_DIR,
        content,
        output,
        execution_context=EXECUTION_CONTEXT,
    )


def _brother_template_dir(tmp_path: Path) -> Path:
    """alias_map.json이 없는 템플릿 디렉터리 (제목 필드 선언 없음)."""
    section0 = zipfile.ZipFile(BROTHER_HWPX).read("Contents/section0.xml").decode("utf-8")
    target = next(t for t in re.findall(r"<hp:t>([^<]+)</hp:t>", section0) if t.strip())
    (tmp_path / "template").mkdir(parents=True, exist_ok=True)
    (tmp_path / "template" / "section0.template.xml").write_text(
        section0.replace(f"<hp:t>{target}</hp:t>", "<hp:t>{{demo_field}}</hp:t>", 1),
        encoding="utf-8",
    )
    (tmp_path / "placeholder_map.json").write_text(
        json.dumps(
            {
                "fields": [
                    {
                        "field_id": "demo_field",
                        "placeholder": "{{demo_field}}",
                        "section": "section0.xml",
                    }
                ]
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    snapshot_source_hwpx(BROTHER_HWPX, tmp_path)
    return tmp_path


def test_content_hpf_title_matches_the_rendered_document_title(tmp_path: Path) -> None:
    output, result = _render_fss(tmp_path)

    content = json.loads(CONTENT.read_text(encoding="utf-8"))
    assert result.title_updated is True
    assert _TITLE_RE.search(_hpf(output)).group(1) == content["제목"]


def test_content_hpf_dates_use_the_execution_request_time(tmp_path: Path) -> None:
    output, _ = _render_fss(tmp_path)

    filled = _hpf(output)
    for name in ("CreatedDate", "ModifiedDate"):
        assert _meta(filled, name) == "2026-08-03T05:49:12Z"


def test_content_hpf_uses_requester_and_report_date(tmp_path: Path) -> None:
    output, _ = _render_fss(tmp_path)

    filled = _hpf(output)
    content = json.loads(CONTENT.read_text(encoding="utf-8"))
    assert _meta(filled, "creator") == "오영서"
    assert _meta(filled, "lastsaveby") == "오영서"
    assert _meta(filled, "date") == content["보고일"]


def test_content_hpf_manifest_is_not_reformatted(tmp_path: Path) -> None:
    output, _ = _render_fss(tmp_path)

    assert (
        _MANIFEST_RE.search(_hpf(output)).group(0)
        == _MANIFEST_RE.search(_hpf(FSS_DIR / "source.hwpx")).group(0)
    )


def test_template_without_alias_map_gets_fresh_dates_and_keeps_title(
    tmp_path: Path,
) -> None:
    template_dir = _brother_template_dir(tmp_path)
    output = tmp_path / "브라더.hwpx"

    result = orchestrate_hwpx_render(template_dir, {"demo_field": "OK"}, output)

    filled = _hpf(output)
    source = _hpf(BROTHER_HWPX)
    assert result.title_updated is False
    assert "<opf:title/>" in filled
    assert _meta(filled, "CreatedDate") != _meta(source, "CreatedDate")
    assert _meta(filled, "ModifiedDate") != _meta(source, "ModifiedDate")


def test_missing_created_date_meta_is_reported_not_ignored(tmp_path: Path) -> None:
    template_dir = _brother_template_dir(tmp_path)
    broken = tmp_path / "broken-base.hwpx"
    with zipfile.ZipFile(BROTHER_HWPX) as source, zipfile.ZipFile(
        broken, "w"
    ) as destination:
        for info in source.infolist():
            payload = source.read(info.filename)
            if info.filename == "Contents/content.hpf":
                payload = re.sub(
                    rb'<opf:meta name="CreatedDate".*?</opf:meta>',
                    b"",
                    payload,
                    flags=re.DOTALL,
                )
            destination.writestr(info, payload)

    with pytest.raises(HwpxTemplateRenderError, match="CreatedDate"):
        orchestrate_hwpx_render(
            template_dir,
            {"demo_field": "OK"},
            tmp_path / "출력.hwpx",
            base_hwpx=broken,
        )
