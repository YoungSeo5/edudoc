from __future__ import annotations

import hashlib
import json
from pathlib import Path

import hwpx
import pytest

from scripts.templates import qa_hwpx_template

ROOT = Path(__file__).resolve().parent.parent
FSS_VIRTUAL_ASSET_SOURCE = (
    ROOT
    / "templates"
    / "institutions"
    / "금융감독원"
    / "금감원 원장보고 가상자산"
    / "source.hwpx"
)


def test_cli_creates_and_validates_an_unapproved_template_candidate(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    output_dir = tmp_path / "candidate"

    exit_code = qa_hwpx_template.main(
        [
            "--source",
            str(FSS_VIRTUAL_ASSET_SOURCE),
            "--output-dir",
            str(output_dir),
            "--institution",
            "금융감독원",
            "--document-type",
            "금감원 신규 보고서",
            "--template-id",
            "fss_new_report_v1",
        ]
    )

    summary = json.loads(capsys.readouterr().out)
    candidate = json.loads((output_dir / "template.json").read_text(encoding="utf-8"))
    sample = json.loads(
        (output_dir / "content.sample.json").read_text(encoding="utf-8")
    )
    test_content = json.loads(
        (output_dir / "content.test.json").read_text(encoding="utf-8")
    )
    qa_report = json.loads(
        (output_dir / "qa.report.json").read_text(encoding="utf-8")
    )
    test_values = list(test_content["fields"].values())

    assert exit_code == 0
    assert summary["ok"] is True
    assert qa_report == summary
    assert summary["status"] == "candidate"
    assert candidate["status"] == "candidate"
    assert candidate["identity"]["institution"] == "금융감독원"
    assert candidate["identity"]["document_type"] == "금감원 신규 보고서"
    assert candidate["identity"]["template_id"] == "fss_new_report_v1"
    assert sample["fields"]
    assert set(test_content["fields"]) == set(sample["fields"])
    assert len(test_values) == len(set(test_values))
    assert all(
        test_content["fields"][field_id] != sample["fields"][field_id]
        for field_id in sample["fields"]
    )
    assert summary["sample_render"]["missing_fields"] == []
    assert summary["sample_render"]["leftover_placeholders"] == []
    assert summary["test_render"]["missing_fields"] == []
    assert summary["test_render"]["leftover_placeholders"] == []
    assert hwpx.validate_package(output_dir / "roundtrip.sample.hwpx").ok
    assert hwpx.validate_package(output_dir / "roundtrip.test.hwpx").ok
    assert (output_dir / "template.review.md").is_file()
    assert (output_dir / "placeholder_map.json").is_file()
    assert (output_dir / "qa.report.json").is_file()


def test_cli_generates_template_id_when_omitted(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    output_dir = tmp_path / "candidate"
    institution = "초등학교"
    document_type = "개인위생 점검표"
    source_hash = hashlib.sha256(FSS_VIRTUAL_ASSET_SOURCE.read_bytes()).hexdigest()
    identity = "\0".join((institution, document_type, source_hash))
    expected_template_id = (
        f"tpl_{hashlib.sha256(identity.encode('utf-8')).hexdigest()[:24]}"
    )

    exit_code = qa_hwpx_template.main(
        [
            "--source",
            str(FSS_VIRTUAL_ASSET_SOURCE),
            "--output-dir",
            str(output_dir),
            "--institution",
            institution,
            "--document-type",
            document_type,
        ]
    )

    summary = json.loads(capsys.readouterr().out)
    candidate = json.loads((output_dir / "template.json").read_text(encoding="utf-8"))
    sample = json.loads(
        (output_dir / "content.sample.json").read_text(encoding="utf-8")
    )
    test_content = json.loads(
        (output_dir / "content.test.json").read_text(encoding="utf-8")
    )

    assert exit_code == 0
    assert summary["template_id"] == expected_template_id
    assert summary["template_id_source"] == "generated"
    assert candidate["identity"]["template_id"] == expected_template_id
    assert sample["template_id"] == expected_template_id
    assert test_content["template_id"] == expected_template_id
