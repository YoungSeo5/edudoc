"""Render an agent-authored ComposedReport to HWPX / PPTX via edudoc exporters."""
from __future__ import annotations

import json
from pathlib import Path

from core.exporters.docx_exporter import DocxExporter
from core.exporters.hwpx_via_hwpskill import HwpxViaHwpSkillExporter
from core.exporters.pptx_exporter import PptxExporter

from .report import ComposedReport, validate_report


def load_plan(path: Path | str) -> ComposedReport:
    return ComposedReport.from_dict(json.loads(Path(path).read_text(encoding="utf-8")))


def render_report_to_hwpx(
    report: ComposedReport,
    markdown_path: Path | str,
    hwpx_path: Path | str,
    *,
    template: str = "report",
):
    """Validate -> clean Markdown -> HWPX. Returns (problems, export_result)."""
    problems = validate_report(report)
    markdown_path = Path(markdown_path)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.write_text(report.to_markdown(), encoding="utf-8")
    export_result = HwpxViaHwpSkillExporter(
        template=template, title=report.title
    ).export(markdown_path, hwpx_path)
    return problems, export_result


def render_report_to_pptx(
    report: ComposedReport,
    markdown_path: Path | str,
    pptx_path: Path | str,
    *,
    include_charts: bool = False,
):
    """Validate -> clean Markdown -> PPTX (pip-native). Returns (problems, export_result).

    Charts are opt-in: by default numeric tables render as table slides (written deck).
    Pass ``include_charts=True`` to turn numeric tables into chart slides.
    """
    problems = validate_report(report)
    markdown_path = Path(markdown_path)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.write_text(report.to_markdown(), encoding="utf-8")
    export_result = PptxExporter(include_charts=include_charts).export(markdown_path, pptx_path)
    return problems, export_result


def render_report_to_docx(
    report: ComposedReport,
    markdown_path: Path | str,
    docx_path: Path | str,
):
    """Validate -> clean Markdown -> DOCX (pip-native). Returns (problems, export_result)."""
    problems = validate_report(report)
    markdown_path = Path(markdown_path)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.write_text(report.to_markdown(), encoding="utf-8")
    export_result = DocxExporter().export(markdown_path, docx_path)
    return problems, export_result
