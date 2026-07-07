"""Render an agent-authored ComposedReport to HWPX via the hwp-skill adapter."""
from __future__ import annotations

import json
from pathlib import Path

from core.exporters.hwpx_via_hwpskill import HwpxViaHwpSkillExporter

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
