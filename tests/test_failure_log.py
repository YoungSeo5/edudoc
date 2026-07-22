"""Unit tests for core/failure_log.py: schema, filename, retention pruning."""
from __future__ import annotations

import json
from pathlib import Path

from core.failure_log import FailureRecord, record_failure


def test_record_failure_writes_one_json_file_with_expected_schema(tmp_path: Path) -> None:
    failures_dir = tmp_path / "failures"
    record = FailureRecord(
        entry_point="pipeline",
        stage="convert",
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
        FailureRecord(entry_point="pipeline", stage="convert", source="x", error="y"),
    )

    assert failures_dir.is_dir()
    assert len(list(failures_dir.glob("*.json"))) == 1


def test_record_failure_never_collides_within_same_run(tmp_path: Path) -> None:
    failures_dir = tmp_path / "failures"
    paths = [
        record_failure(
            failures_dir,
            FailureRecord(entry_point="pipeline", stage="convert", source="same", error="e"),
        )
        for _ in range(20)
    ]

    assert len(set(paths)) == 20
    assert len(list(failures_dir.glob("*.json"))) == 20


def test_record_failure_prunes_oldest_beyond_retention_limit(tmp_path: Path) -> None:
    failures_dir = tmp_path / "failures"
    written: list[Path] = []
    for i in range(8):
        written.append(
            record_failure(
                failures_dir,
                FailureRecord(
                    entry_point="pipeline", stage="convert", source=f"doc-{i}", error="e"
                ),
                retention_limit=5,
            )
        )

    remaining = sorted(p.name for p in failures_dir.glob("*.json"))
    assert len(remaining) == 5
    # the 5 newest (last-written) records survive; the 3 oldest are pruned
    expected_survivors = sorted(p.name for p in written[-5:])
    assert remaining == expected_survivors
    for pruned in written[:3]:
        assert not pruned.exists()


def test_record_failure_retention_limit_zero_disables_pruning(tmp_path: Path) -> None:
    failures_dir = tmp_path / "failures"
    for i in range(5):
        record_failure(
            failures_dir,
            FailureRecord(entry_point="pipeline", stage="convert", source=f"doc-{i}", error="e"),
            retention_limit=0,
        )

    assert len(list(failures_dir.glob("*.json"))) == 5


def test_slug_sanitizes_unsafe_filename_characters(tmp_path: Path) -> None:
    failures_dir = tmp_path / "failures"
    out_path = record_failure(
        failures_dir,
        FailureRecord(
            entry_point="pipeline",
            stage="export",
            source="C:\\weird path/with:colons*and?stuff.docx",
            error="e",
        ),
    )

    assert all(ch not in out_path.name for ch in ":*?/\\")


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
        test_record_failure_prunes_oldest_beyond_retention_limit(Path(tmp) / "e")
    with tempfile.TemporaryDirectory() as tmp:
        test_record_failure_retention_limit_zero_disables_pruning(Path(tmp) / "f")
    with tempfile.TemporaryDirectory() as tmp:
        test_slug_sanitizes_unsafe_filename_characters(Path(tmp) / "g")
    print("PASS: failure_log")
