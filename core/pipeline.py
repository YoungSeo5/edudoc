"""
Phase 0 파이프라인.

흐름: 입력 파일 -> (레지스트리에서 변환기 선택) -> Markdown -> exports/ 저장

Phase 0 목표는 "변환 왕복이 되는가"의 첫 절반(입력 -> md)을 검증하는 것이다.
출력(md -> docx/hwpx)은 exports 모듈에서 이어받는다.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from .converter_base import ConvertResult
from .exporters import HwpxExporter, OfficeExporter
from .exporters.docx_exporter import DocxExporter
from .exporters.pptx_exporter import PptxExporter
from .input_filter import is_processable_input
from .registry import ConverterRegistry, default_registry
from validators.document_model_rules import validate as validate_document_model
from validators.gongmun_rules import validate as validate_gongmun


@dataclass
class PipelineConfig:
    output_dir: Path = Path("exports")
    write_files: bool = True
    validate_gongmun: bool = False
    write_validation_report: bool = False
    export_formats: tuple[str, ...] = ()


class Pipeline:
    def __init__(
        self,
        registry: ConverterRegistry | None = None,
        config: PipelineConfig | None = None,
    ) -> None:
        self.registry = registry or default_registry()
        self.config = config or PipelineConfig()

    def process_file(self, path: Path) -> ConvertResult:
        path = Path(path)
        converter = self.registry.find(path)
        if converter is None:
            return ConvertResult(
                source=path, markdown="", ok=False,
                error=f"지원하지 않는 확장자: {path.suffix} "
                      f"(지원: {sorted(self.registry.supported_ext)})",
            )

        result = converter.convert(path)

        if result.ok and self.config.write_files:
            out_path = self._write_markdown(path, result.markdown)
            result.meta["output"] = str(out_path)

            if result.document_model is not None:
                model_path = self._write_document_model(path, result.document_model)
                result.meta["document_model"] = str(model_path)

                # DocumentModel 무결성 검증(공문 문체 검증과 별개). 막지 않고 리포트만 한다.
                dm_report = validate_document_model(result.document_model)
                result.meta["document_model_validation"] = {
                    "available": True,
                    "passed": dm_report.passed,
                    "summary": dm_report.summary(),
                }
                if self.config.write_validation_report:
                    dm_report_path = self._write_document_model_report(
                        path, dm_report.summary()
                    )
                    result.meta["document_model_validation_report"] = str(dm_report_path)
            else:
                result.meta["document_model_validation"] = {
                    "available": False,
                    "reason": "converter did not provide document_model",
                }

            if self.config.validate_gongmun:
                report = validate_gongmun(result.markdown)
                result.meta["validation_passed"] = report.passed
                result.meta["validation_summary"] = report.summary()
                if self.config.write_validation_report:
                    report_path = self._write_validation_report(path, report.summary())
                    result.meta["validation_report"] = str(report_path)

            if self.config.export_formats:
                result.meta["exports"] = self._export_outputs(out_path)

        return result

    def process_dir(self, in_dir: Path) -> list[ConvertResult]:
        in_dir = Path(in_dir)
        results: list[ConvertResult] = []
        for path in sorted(in_dir.rglob("*")):
            if path.is_file() and is_processable_input(path) and self.registry.find(path):
                results.append(self.process_file(path))
        return results

    def _write_markdown(self, source: Path, markdown: str) -> Path:
        self.config.output_dir.mkdir(parents=True, exist_ok=True)
        out_path = self.config.output_dir / (source.stem + ".md")
        out_path.write_text(markdown, encoding="utf-8")
        return out_path

    def _write_validation_report(self, source: Path, summary: str) -> Path:
        self.config.output_dir.mkdir(parents=True, exist_ok=True)
        out_path = self.config.output_dir / (source.stem + ".validation.txt")
        out_path.write_text(summary, encoding="utf-8")
        return out_path

    def _write_document_model(self, source: Path, document_model) -> Path:  # noqa: ANN001
        self.config.output_dir.mkdir(parents=True, exist_ok=True)
        out_path = self.config.output_dir / (source.stem + ".document.json")
        out_path.write_text(
            json.dumps(document_model.to_dict(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return out_path

    def _write_document_model_report(self, source: Path, summary: str) -> Path:  # noqa: ANN001
        # 공문 문체 리포트(.validation.txt)와 별개 파일로 저장한다.
        self.config.output_dir.mkdir(parents=True, exist_ok=True)
        out_path = self.config.output_dir / (source.stem + ".document.validation.txt")
        out_path.write_text(summary, encoding="utf-8")
        return out_path

    def _export_outputs(self, markdown_path: Path) -> list[dict]:
        exports: list[dict] = []
        for ext in self.config.export_formats:
            ext = ext if ext.startswith(".") else f".{ext}"
            output_path = self.config.output_dir / (markdown_path.stem + ext)
            exporter = self._select_exporter(ext)
            export_result = exporter.export(markdown_path, output_path)
            exporter_name = export_result.meta.get("exporter")
            status = self._export_status(export_result, output_path)
            entry = {
                "format": ext,
                "path": str(output_path),
                "output": str(output_path),
                "ok": export_result.ok,
                "error": export_result.error,
                "exporter": exporter_name,
                "stabilized": status["stabilized"],
                "experimental": status["experimental"],
                "requires_optional_tool": status["requires_optional_tool"],
                "status": status["status"],
                "note": status["note"],
            }
            for key in (
                "table_count",
                "max_table_column_count",
                "wide_table_detected",
                "wide_table_strategy",
                "warnings",
            ):
                if key in export_result.meta:
                    entry[key] = export_result.meta[key]
            exports.append(entry)
        return exports

    def _export_status(self, export_result, output_path: Path) -> dict:  # noqa: ANN001
        exporter_name = export_result.meta.get("exporter")
        requires_optional_tool = bool(
            export_result.meta.get("requires_optional_tool", exporter_name == "OfficeExporter")
        )

        if exporter_name == "DocxExporter":
            return {
                "status": "partially_stabilized" if export_result.ok else "failed",
                "stabilized": export_result.ok,
                "experimental": False,
                "requires_optional_tool": False,
                "note": export_result.meta.get(
                    "note",
                    "pip-native DOCX export; content and structure are tested, "
                    "but layout-perfect output is not claimed",
                ),
            }

        if exporter_name == "PptxExporter":
            return {
                "status": "partially_stabilized" if export_result.ok else "failed",
                "stabilized": export_result.ok,
                "experimental": False,
                "requires_optional_tool": False,
                "note": export_result.meta.get(
                    "note",
                    "pip-native PPTX export; text/bullets/tables are tested, "
                    "but slide visual design is not claimed",
                ),
            }

        if exporter_name == "HwpxExporter":
            return {
                "status": "experimental" if export_result.ok else "failed",
                "stabilized": False,
                "experimental": True,
                "requires_optional_tool": False,
                "note": export_result.meta.get(
                    "note",
                    "minimal pip-native HWPX package; structural smoke-tested, "
                    "not a full official HWPX layout exporter",
                ),
            }

        if exporter_name == "OfficeExporter":
            return {
                "status": "fallback" if export_result.ok else "failed",
                "stabilized": False,
                "experimental": True,
                "requires_optional_tool": True,
                "note": (
                    "fallback via Pandoc/Typst; layout may not be preserved for "
                    f"{output_path.suffix.lower()} output and this is not a "
                    "stabilized pip-native exporter"
                ),
            }

        return {
            "status": "unsupported" if not export_result.ok else "experimental",
            "stabilized": False,
            "experimental": True,
            "requires_optional_tool": requires_optional_tool,
            "note": export_result.meta.get("note", "export status is not stabilized"),
        }

    def _select_exporter(self, ext: str):
        if ext.lower() == ".docx":
            return DocxExporter()
        if ext.lower() == ".pptx":
            return PptxExporter()
        if ext.lower() == ".hwpx":
            return HwpxExporter()
        return OfficeExporter()
