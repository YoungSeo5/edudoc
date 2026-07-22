"""Gongmun brief-generation CLI writes failure records for crash + validation-failed paths."""
from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

import scripts.gongmun.generate_from_brief as generate_from_brief_module
from core.generators.gongmun_generator import GongmunGenerationResult
from scripts.gongmun.generate_from_brief import main
from validators.gongmun_rules import ValidationReport, Violation


def _read_records(failures_dir: Path) -> list[dict]:
    return [json.loads(p.read_text(encoding="utf-8")) for p in sorted(failures_dir.glob("*.json"))]


def test_gongmun_cli_crash_writes_a_gongmun_generate_failure_record(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def _boom(_path):
        raise RuntimeError("simulated brief-parsing crash")

    monkeypatch.setattr(generate_from_brief_module, "generate_and_validate", _boom)

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        brief = tmp_path / "brief.md"
        brief.write_text("내용: 연수 참가 신청\n", encoding="utf-8")
        failures_dir = tmp_path / "failures"

        exit_code = main(
            [str(brief), "--out", str(tmp_path / "out")], failures_dir=failures_dir
        )

        assert exit_code == 2
        records = _read_records(failures_dir)
        assert len(records) == 1
        assert records[0]["entry_point"] == "gongmun_cli"
        assert records[0]["stage"] == "gongmun_generate"
        assert "simulated brief-parsing crash" in records[0]["error"]


def test_gongmun_cli_failed_validation_writes_a_gongmun_validate_failure_record(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    failing_report = ValidationReport(
        violations=[
            Violation("end_mark", "본문 종결에 '끝.' 표시가 없음"),
            Violation("attachment_count", "붙임 수량 불일치"),
        ]
    )

    def _fake_generate_and_validate(_path):
        return GongmunGenerationResult(markdown="# 제목\n\n본문\n", validation_report=failing_report)

    monkeypatch.setattr(
        generate_from_brief_module, "generate_and_validate", _fake_generate_and_validate
    )

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        brief = tmp_path / "brief.md"
        brief.write_text("내용: 연수 참가 신청\n", encoding="utf-8")
        failures_dir = tmp_path / "failures"

        exit_code = main(
            [str(brief), "--out", str(tmp_path / "out")], failures_dir=failures_dir
        )

        assert exit_code == 1
        records = _read_records(failures_dir)
        assert len(records) == 2
        assert {record["entry_point"] for record in records} == {"gongmun_cli"}
        assert {record["stage"] for record in records} == {"gongmun_validate"}
        assert {record["error_code"] for record in records} == {
            "gongmun_validation_attachment_count",
            "gongmun_validation_end_mark",
        }
        # the existing per-run validation report is unchanged/additional, not replaced
        assert (tmp_path / "out" / "brief.validation.txt").exists()


def test_gongmun_cli_passing_validation_writes_no_failure_record() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        brief = tmp_path / "brief.md"
        brief.write_text(
            "내용: 연수 참가 신청\n수신: 관내 학교장\n담당: 교육지원과\n"
            "관련 근거: 2026년 연수 운영 계획\n대상: 희망 교원\n기한: 2026. 7. 15.\n"
            "제출 방법: 이메일 제출\n붙임: 참가 신청서 1부\n",
            encoding="utf-8",
        )
        failures_dir = tmp_path / "failures"

        exit_code = main(
            [str(brief), "--out", str(tmp_path / "out")], failures_dir=failures_dir
        )

        assert exit_code == 0
        assert not failures_dir.exists()


if __name__ == "__main__":
    test_gongmun_cli_passing_validation_writes_no_failure_record()
    print("PASS: gongmun CLI failure log (monkeypatch tests run via pytest only)")
