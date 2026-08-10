"""메타데이터 필수화 이후 기존 호출 경로가 실행 문맥까지 연결되어 있는지 확인한다.

compose CLI → render_report_to_hwpx → orchestrate_hwpx_render 구간에서
requester 정보가 중간에 끊기면 최종 문서가 생성되지 않는다.
연결 전에는 compose 경로가 실행 문맥을 전달하지 못해 승인 템플릿도 거부됐다.
"""
from __future__ import annotations

import json
import re
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from core.compose.report import Block, ComposedReport, Section
from scripts.compose import render_plan

ROOT = Path(__file__).resolve().parents[2]
FSS_DIRECTOR_CONTENT = (
    ROOT / "tests" / "fixtures" / "template-content" / "fss_director_report.input.json"
)


def _write_plan(directory: Path) -> Path:
    report = ComposedReport(
        title="가상자산 이상거래 대응 진행현황",
        sections=[
            Section(no="1", title="현황", blocks=[Block(marker="□", text="점검 중")])
        ],
    )
    plan = directory / "report.plan.json"
    plan.write_text(
        json.dumps(
            {
                "title": report.title,
                "doc_type": "activity_report",
                "sections": [
                    {
                        "no": "1",
                        "title": "현황",
                        "blocks": [{"marker": "□", "text": "점검 중"}],
                    }
                ],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    return plan


def _write_content(directory: Path) -> Path:
    content_path = directory / "content.json"
    content_path.write_text(
        json.dumps(
            {
                "template_id": "fss_director_report",
                "fields": json.loads(
                    FSS_DIRECTOR_CONTENT.read_text(encoding="utf-8")
                ),
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    return content_path


def test_compose_cli_carries_the_requester_into_content_hpf(tmp_path: Path) -> None:
    plan = _write_plan(tmp_path)
    content_path = _write_content(tmp_path)

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

    output = tmp_path / "report.hwpx"
    assert exit_code == 0
    assert output.is_file()

    with zipfile.ZipFile(output) as package:
        hpf = package.read("Contents/content.hpf").decode("utf-8")

    # 요청자가 CLI에서 content.hpf까지 끊기지 않고 도착했는지 확인한다.
    assert re.search(r'<opf:meta name="creator"[^>]*>오영서</opf:meta>', hpf)
    assert re.search(r'<opf:meta name="lastsaveby"[^>]*>오영서</opf:meta>', hpf)
    assert "<opf:title>가상자산 이상거래 대응 진행현황</opf:title>" in hpf


def test_compose_cli_requires_the_requester_with_the_other_options(
    tmp_path: Path,
) -> None:
    plan = _write_plan(tmp_path)
    content_path = _write_content(tmp_path)

    try:
        render_plan.main(
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
            ],
            failures_dir=tmp_path / "failures",
        )
    except SystemExit as exit_error:
        assert exit_error.code == 2
    else:
        raise AssertionError("expected the CLI to reject a missing --requester-name")

    assert not (tmp_path / "report.hwpx").exists()
