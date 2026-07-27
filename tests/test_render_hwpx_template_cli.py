from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.templates import render_hwpx_template

ROOT = Path(__file__).resolve().parent.parent
FSS_VIRTUAL_ASSET = (
    ROOT
    / "templates"
    / "institutions"
    / "금융감독원"
    / "금감원 원장보고 가상자산"
)


def test_cli_renders_only_hwpx_from_template_content(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    output = tmp_path / "금감원_가상자산_테스트.hwpx"

    exit_code = render_hwpx_template.main(
        [
            "--institution",
            "금융감독원",
            "--document-type",
            "금감원 원장보고 가상자산",
            "--content",
            str(FSS_VIRTUAL_ASSET / "content.sample.json"),
            "--output",
            str(output),
        ]
    )

    summary = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert summary["ok"] is True
    assert summary["template_id"] == "fss_virtual_asset_report"
    assert summary["missing_fields"] == []
    assert summary["leftover_placeholders"] == []
    assert output.is_file()
    assert list(tmp_path.glob("*.md")) == []


def test_cli_rejects_content_for_a_different_template(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    content = json.loads(
        (FSS_VIRTUAL_ASSET / "content.sample.json").read_text(encoding="utf-8")
    )
    content["template_id"] = "different_template"
    content_path = tmp_path / "content.json"
    content_path.write_text(json.dumps(content, ensure_ascii=False), encoding="utf-8")

    exit_code = render_hwpx_template.main(
        [
            "--institution",
            "금융감독원",
            "--document-type",
            "금감원 원장보고 가상자산",
            "--content",
            str(content_path),
            "--output",
            str(tmp_path / "should-not-exist.hwpx"),
        ]
    )

    summary = json.loads(capsys.readouterr().out)
    assert exit_code == 1
    assert summary["ok"] is False
    assert "template_id mismatch" in summary["error"]
    assert not (tmp_path / "should-not-exist.hwpx").exists()
