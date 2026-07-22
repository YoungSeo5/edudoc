"""Unit tests for failure-record schema, safe writes, and aggregation."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.failure_log import (
    FailureRecord,
    failure_fingerprint,
    record_failure,
    summarize_failures,
)


def test_record_failure_writes_one_json_file_with_expected_schema(tmp_path: Path) -> None:
    failures_dir = tmp_path / "failures"
    record = FailureRecord(
        entry_point="pipeline",
        stage="convert",
        error_code="converter_not_found",
        source="samples/report.hwpx",
        error="지원하지 않는 확장자: .xyz",
        meta={"converter": "HwpSkillConverter"},
    )

    out_path = record_failure(failures_dir, record)

    assert out_path.parent == failures_dir
    assert out_path.suffix == ".json"
    data = json.loads(out_path.read_text(encoding="utf-8"))
    assert data["entry_point"] == "pipeline"
    assert data["stage"] == "convert"
    assert data["error_code"] == "converter_not_found"
    assert data["fingerprint"] == failure_fingerprint(
        "pipeline", "convert", "converter_not_found"
    )
    assert data["source"] == "samples/report.hwpx"
    assert data["error"] == "지원하지 않는 확장자: .xyz"
    assert data["meta"] == {"converter": "HwpSkillConverter"}
    assert "timestamp" in data and data["timestamp"]


def test_record_failure_filename_starts_with_sortable_timestamp_and_stage(
    tmp_path: Path,
) -> None:
    failures_dir = tmp_path / "failures"
    out_path = record_failure(
        failures_dir,
        FailureRecord(
            entry_point="compose_cli",
            stage="render",
            error_code="render_failed",
            source="exports/report.docx",
            error="boom",
        ),
    )

    name = out_path.name
    assert "-render-" in name
    assert name.endswith("report_docx.json")
    timestamp_prefix = name.split("-", 1)[0]
    assert len(timestamp_prefix) == 21  # YYYYMMDDTHHMMSSffffff
    assert timestamp_prefix[8] == "T"


def test_record_failure_creates_missing_directory(tmp_path: Path) -> None:
    failures_dir = tmp_path / "nested" / "failures"
    assert not failures_dir.exists()

    record_failure(
        failures_dir,
        FailureRecord(
            entry_point="pipeline",
            stage="convert",
            error_code="conversion_failed",
            source="x",
            error="y",
        ),
    )

    assert failures_dir.is_dir()
    assert len(list(failures_dir.glob("*.json"))) == 1


def test_record_failure_never_collides_within_same_run(tmp_path: Path) -> None:
    failures_dir = tmp_path / "failures"
    paths = [
        record_failure(
            failures_dir,
            FailureRecord(
                entry_point="pipeline",
                stage="convert",
                error_code="conversion_failed",
                source="same",
                error="e",
            ),
        )
        for _ in range(20)
    ]

    assert len(set(paths)) == 20
    assert len(list(failures_dir.glob("*.json"))) == 20


def test_fingerprint_excludes_variable_failure_details() -> None:
    first = FailureRecord(
        entry_point="compose_cli",
        stage="render",
        error_code="institution_template_not_found",
        source="C:/first/report.hwpx",
        error="template missing for first/report.hwpx",
        meta={"attempt": 1},
    )
    second = FailureRecord(
        entry_point="compose_cli",
        stage="render",
        error_code="institution_template_not_found",
        source="D:/second/other.hwpx",
        error="different human-readable details",
        meta={"attempt": 99},
    )

    assert first.fingerprint == second.fingerprint


def test_fingerprint_changes_with_stable_identity_fields() -> None:
    base = failure_fingerprint("compose_cli", "render", "render_failed")

    assert failure_fingerprint("pipeline", "render", "render_failed") != base
    assert failure_fingerprint("compose_cli", "export", "render_failed") != base
    assert failure_fingerprint("compose_cli", "render", "validation_failed") != base


def test_summarize_failures_groups_by_fingerprint(tmp_path: Path) -> None:
    failures_dir = tmp_path / "failures"
    for i in range(3):
        record_failure(
            failures_dir,
            FailureRecord(
                entry_point="pipeline",
                stage="convert",
                error_code="conversion_failed",
                source=f"doc-{i}",
                error=f"failure for doc-{i}",
            ),
        )
    record_failure(
        failures_dir,
        FailureRecord(
            entry_point="compose_cli",
            stage="render",
            error_code="render_failed",
            source="report.hwpx",
            error="render failed",
        ),
    )

    summaries = summarize_failures(failures_dir)

    assert len(summaries) == 2
    conversion = next(item for item in summaries if item.error_code == "conversion_failed")
    assert conversion.occurrence_count == 3
    assert conversion.entry_point == "pipeline"
    assert conversion.stage == "convert"
    assert conversion.first_seen <= conversion.last_seen


def test_slug_sanitizes_unsafe_filename_characters(tmp_path: Path) -> None:
    failures_dir = tmp_path / "failures"
    out_path = record_failure(
        failures_dir,
        FailureRecord(
            entry_point="pipeline",
            stage="export",
            error_code="export_failed",
            source="C:\\weird path/with:colons*and?stuff.docx",
            error="e",
        ),
    )

    assert all(ch not in out_path.name for ch in ":*?/\\")


def test_record_failure_returns_none_when_json_serialization_fails(tmp_path: Path) -> None:
    result = record_failure(
        tmp_path / "failures",
        FailureRecord(
            entry_point="pipeline",
            stage="export",
            error_code="export_failed",
            source="report.docx",
            error="export failed",
            meta={"not_json": {1, 2, 3}},
        ),
    )

    assert result is None


def test_record_failure_returns_none_when_file_write_fails(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fail_write(*args, **kwargs):
        raise OSError("simulated failure-log write error")

    monkeypatch.setattr(Path, "write_text", fail_write)

    result = record_failure(
        tmp_path / "failures",
        FailureRecord(
            entry_point="compose_cli",
            stage="render",
            error_code="render_failed",
            source="report.hwpx",
            error="original render error",
        ),
    )

    assert result is None


if __name__ == "__main__":
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        test_record_failure_writes_one_json_file_with_expected_schema(Path(tmp) / "a")
    with tempfile.TemporaryDirectory() as tmp:
        test_record_failure_filename_starts_with_sortable_timestamp_and_stage(Path(tmp) / "b")
    with tempfile.TemporaryDirectory() as tmp:
        test_record_failure_creates_missing_directory(Path(tmp) / "c")
    with tempfile.TemporaryDirectory() as tmp:
        test_record_failure_never_collides_within_same_run(Path(tmp) / "d")
    with tempfile.TemporaryDirectory() as tmp:
        test_summarize_failures_groups_by_fingerprint(Path(tmp) / "e")
    with tempfile.TemporaryDirectory() as tmp:
        test_slug_sanitizes_unsafe_filename_characters(Path(tmp) / "f")
    with tempfile.TemporaryDirectory() as tmp:
        test_record_failure_returns_none_when_json_serialization_fails(Path(tmp) / "g")
    print("PASS: failure_log")
