"""scripts/compose/render_plan.py: one command renders a plan to multiple formats.

Proves the compose CLI takes an agent-authored plan.json and produces validated
docx/pptx (and hwpx when the skill is present) deliverables in one call.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

from core.exporters.export_base import ExportResult
from scripts.compose import render_plan

ROOT = Path(__file__).resolve().parent.parent
CLI = ROOT / "scripts" / "compose" / "render_plan.py"

PLAN = {
    "title": "테스트 결과보고서",
    "doc_type": "activity_report",
    "sections": [
        {"no": "Ⅰ", "title": "개요", "blocks": [
            {"marker": "□", "text": "요약"}, {"marker": "○", "text": "세부"},
        ]},
    ],
    "attachments": ["첨부 1부."],
}


def _write_plan(directory: Path) -> Path:
    plan = directory / "report.plan.json"
    plan.write_text(json.dumps(PLAN, ensure_ascii=False), encoding="utf-8")
    return plan


def test_render_plan_cli_passes_institution_options_to_hwpx_renderer(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    plan = _write_plan(tmp_path)
    content_path = tmp_path / "content.json"
    content_path.write_text(
        json.dumps({"template_id": "example", "fields": {"report_title": "기관 보고서"}}),
        encoding="utf-8",
    )
    received_kwargs = []
    received_docx_kwargs = []

    def fake_hwpx_renderer(report, markdown_path, output_path, **kwargs):
        received_kwargs.append(kwargs)
        return [], ExportResult(source=Path(markdown_path), output=Path(output_path))

    def fake_docx_renderer(report, markdown_path, output_path, **kwargs):
        received_docx_kwargs.append(kwargs)
        return [], ExportResult(source=Path(markdown_path), output=Path(output_path))

    monkeypatch.setitem(render_plan._RENDERERS, "hwpx", fake_hwpx_renderer)
    monkeypatch.setitem(render_plan._RENDERERS, "docx", fake_docx_renderer)

    exit_code = render_plan.main(
        [
            "--plan",
            str(plan),
            "--to",
            "docx,hwpx",
            "--out",
            str(tmp_path),
            "--institution",
            "금융감독원",
            "--document-type",
            "금감원 원장보고 가상자산",
            "--template-content",
            str(content_path),
        ]
    )

    assert exit_code == 0
    assert received_docx_kwargs == [{}]
    assert received_kwargs == [
        {
            "institution": "금융감독원",
            "document_type": "금감원 원장보고 가상자산",
            "template_content": {"report_title": "기관 보고서"},
        }
    ]


def test_render_plan_cli_keeps_generic_hwpx_call_without_institution_options(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    plan = _write_plan(tmp_path)
    received_kwargs = []

    def fake_hwpx_renderer(report, markdown_path, output_path, **kwargs):
        received_kwargs.append(kwargs)
        return [], ExportResult(source=Path(markdown_path), output=Path(output_path))

    monkeypatch.setitem(render_plan._RENDERERS, "hwpx", fake_hwpx_renderer)

    exit_code = render_plan.main(
        ["--plan", str(plan), "--to", "hwpx", "--out", str(tmp_path)]
    )

    assert exit_code == 0
    assert received_kwargs == [{}]


@pytest.mark.parametrize(
    "institution_args",
    [
        ["--institution", "금융감독원"],
        [
            "--institution",
            "금융감독원",
            "--document-type",
            "금감원 원장보고 가상자산",
        ],
    ],
)
def test_render_plan_cli_rejects_partial_institution_options(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    institution_args: list[str],
) -> None:
    plan = _write_plan(tmp_path)

    with pytest.raises(SystemExit) as exc_info:
        render_plan.main(["--plan", str(plan), "--to", "hwpx", *institution_args])

    assert exc_info.value.code == 2
    error = capsys.readouterr().err
    assert "usage:" in error
    assert "institution template options must be provided together" in error


def test_render_plan_cli_rejects_institution_options_without_hwpx(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    plan = _write_plan(tmp_path)
    content_path = tmp_path / "content.json"
    content_path.write_text("{}", encoding="utf-8")

    with pytest.raises(SystemExit) as exc_info:
        render_plan.main(
            [
                "--plan",
                str(plan),
                "--to",
                "docx",
                "--institution",
                "금융감독원",
                "--document-type",
                "금감원 원장보고 가상자산",
                "--template-content",
                str(content_path),
            ]
        )

    assert exc_info.value.code == 2
    error = capsys.readouterr().err
    assert "institution template options require hwpx in --to" in error


@pytest.mark.parametrize(
    ("filename", "contents"),
    [
        ("missing-content.json", None),
        ("invalid-content.json", "{not json"),
    ],
)
def test_render_plan_cli_rejects_unreadable_template_content_file(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    filename: str,
    contents: str | None,
) -> None:
    plan = _write_plan(tmp_path)
    content_path = tmp_path / filename
    if contents is not None:
        content_path.write_text(contents, encoding="utf-8")

    with pytest.raises(SystemExit) as exc_info:
        render_plan.main(
            [
                "--plan",
                str(plan),
                "--to",
                "hwpx",
                "--institution",
                "금융감독원",
                "--document-type",
                "금감원 원장보고 가상자산",
                "--template-content",
                str(content_path),
            ]
        )

    assert exc_info.value.code == 2
    error = capsys.readouterr().err
    assert "cannot read --template-content" in error
    assert str(content_path) in error


def test_render_plan_cli_docx_pptx() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        plan = tmp / "report.plan.json"
        plan.write_text(json.dumps(PLAN, ensure_ascii=False), encoding="utf-8")

        proc = subprocess.run(
            [sys.executable, str(CLI), "--plan", str(plan), "--to", "docx,pptx", "--out", str(tmp)],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        )
        assert proc.returncode == 0, proc.stderr or proc.stdout
        summary = json.loads(proc.stdout)

        assert summary["validation_problems"] == []
        by_fmt = {o["format"]: o for o in summary["outputs"]}
        assert by_fmt["docx"]["ok"] is True
        assert by_fmt["pptx"]["ok"] is True
        assert (tmp / "report.docx").exists()
        assert (tmp / "report.pptx").exists()
        assert (tmp / "report.md").exists()


def test_render_plan_cli_rejects_unknown_format() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        plan = tmp / "r.plan.json"
        plan.write_text(json.dumps(PLAN, ensure_ascii=False), encoding="utf-8")
        proc = subprocess.run(
            [sys.executable, str(CLI), "--plan", str(plan), "--to", "xlsx"],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        )
        assert proc.returncode != 0
        assert "unknown format" in (proc.stderr + proc.stdout)


if __name__ == "__main__":
    test_render_plan_cli_docx_pptx()
    test_render_plan_cli_rejects_unknown_format()
    print("PASS: compose render CLI (multi-format)")
