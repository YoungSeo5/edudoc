"""Shared Pipeline writes one failure record per convert/export failure.

Proves core/failure_log.py is actually wired into core/pipeline.py, not just
implemented in isolation.
"""
from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

import core.pipeline as pipeline_module
from core.converter_base import BaseConverter, ConvertResult
from core.exporters.export_base import ExportResult
from core.pipeline import Pipeline, PipelineConfig
from core.registry import ConverterRegistry


class _AlwaysFailingConverter(BaseConverter):
    supported_ext = (".broken",)

    def convert(self, path: Path) -> ConvertResult:
        return ConvertResult(
            source=path,
            markdown="",
            ok=False,
            error="simulated conversion failure",
            meta={"converter": self.name},
        )


def _read_records(failures_dir: Path) -> list[dict]:
    return [json.loads(p.read_text(encoding="utf-8")) for p in sorted(failures_dir.glob("*.json"))]


def test_unsupported_extension_writes_a_convert_failure_record() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        source = tmp_path / "report.xyz"
        source.write_text("data", encoding="utf-8")
        failures_dir = tmp_path / "failures"
        pipe = Pipeline(
            registry=ConverterRegistry(),
            config=PipelineConfig(output_dir=tmp_path / "exports", failures_dir=failures_dir),
        )

        result = pipe.process_file(source)

        assert not result.ok
        records = _read_records(failures_dir)
        assert len(records) == 1
        assert records[0]["entry_point"] == "pipeline"
        assert records[0]["stage"] == "convert"
        assert records[0]["source"] == str(source)
        assert "지원하지 않는 확장자" in records[0]["error"]


def test_converter_failure_writes_a_convert_failure_record() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        source = tmp_path / "bad.broken"
        source.write_text("data", encoding="utf-8")
        failures_dir = tmp_path / "failures"
        registry = ConverterRegistry()
        registry.register(_AlwaysFailingConverter())
        pipe = Pipeline(
            registry=registry,
            config=PipelineConfig(output_dir=tmp_path / "exports", failures_dir=failures_dir),
        )

        result = pipe.process_file(source)

        assert not result.ok
        records = _read_records(failures_dir)
        assert len(records) == 1
        assert records[0]["stage"] == "convert"
        assert records[0]["error"] == "simulated conversion failure"
        assert records[0]["meta"]["converter"] == "_AlwaysFailingConverter"


def test_successful_conversion_writes_no_failure_record() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        source = tmp_path / "draft.md"
        source.write_text("# 제목\n\n본문\n", encoding="utf-8")
        failures_dir = tmp_path / "failures"
        pipe = Pipeline(
            config=PipelineConfig(output_dir=tmp_path / "exports", failures_dir=failures_dir)
        )

        result = pipe.process_file(source)

        assert result.ok
        assert not failures_dir.exists()


def test_export_failure_writes_an_export_failure_record(monkeypatch: pytest.MonkeyPatch) -> None:
    class _FailingDocxExporter:
        def __init__(self, *args, **kwargs) -> None:
            pass

        def export(self, markdown_path: Path, output_path: Path) -> ExportResult:
            return ExportResult(
                source=markdown_path,
                output=output_path,
                ok=False,
                error="simulated export failure",
                meta={"exporter": "DocxExporter"},
            )

    monkeypatch.setattr(pipeline_module, "DocxExporter", _FailingDocxExporter)

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        source = tmp_path / "draft.md"
        source.write_text("# 제목\n\n본문\n", encoding="utf-8")
        failures_dir = tmp_path / "failures"
        pipe = Pipeline(
            config=PipelineConfig(
                output_dir=tmp_path / "exports",
                failures_dir=failures_dir,
                export_formats=(".docx",),
            )
        )

        result = pipe.process_file(source)

        assert result.ok  # conversion itself succeeded
        records = _read_records(failures_dir)
        assert len(records) == 1
        assert records[0]["entry_point"] == "pipeline"
        assert records[0]["stage"] == "export"
        assert records[0]["error"] == "simulated export failure"
        assert records[0]["meta"]["format"] == ".docx"


if __name__ == "__main__":
    test_unsupported_extension_writes_a_convert_failure_record()
    test_converter_failure_writes_a_convert_failure_record()
    test_successful_conversion_writes_no_failure_record()
    print("PASS: pipeline failure log wiring (monkeypatch test run via pytest only)")
