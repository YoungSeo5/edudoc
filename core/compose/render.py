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
    style_reference: Path | str | None = None,
):
    """Validate -> clean Markdown -> HWPX. Returns (problems, export_result).

    When ``style_reference`` (an HWPX) is given, its body font/size/spacing are
    extracted and patched into a custom header.xml passed to md2hwpx; fields the
    reference lacks keep the template value and are recorded in
    ``export_result.meta['style_fallback_fields']`` (fallback_used honesty).
    Page margins are not header-settable, so they are left to the template.
    """
    problems = validate_report(report)
    markdown_path = Path(markdown_path)
    hwpx_path = Path(hwpx_path)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.write_text(report.to_markdown(), encoding="utf-8")

    custom_header: Path | None = None
    fallback_fields: list[str] | None = None
    if style_reference is not None:
        from core.exporters.hwp_skill_header_builder import build_custom_header
        from core.templates.extractors.style import extract_style

        extracted = extract_style(style_reference)
        header_xml, fallback_fields = build_custom_header(extracted)
        custom_header = hwpx_path.parent / f"{hwpx_path.stem}.header.xml"
        custom_header.parent.mkdir(parents=True, exist_ok=True)
        custom_header.write_text(header_xml, encoding="utf-8")

    export_result = HwpxViaHwpSkillExporter(
        template=template, title=report.title, custom_header=custom_header
    ).export(markdown_path, hwpx_path)
    if fallback_fields is not None and export_result.ok:
        export_result.meta["style_source"] = "extracted"
        export_result.meta["style_fallback_fields"] = fallback_fields
        export_result.meta["style_fallback_used"] = bool(fallback_fields)
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
    *,
    style_reference: Path | str | None = None,
):
    """Validate -> clean Markdown -> DOCX (pip-native). Returns (problems, export_result).

    When ``style_reference`` (an HWPX) is given, its real style is extracted and
    applied; fields the reference lacks fall back to the default and are recorded
    in ``export_result.meta['style_fallback_fields']`` (fallback_used honesty).
    """
    problems = validate_report(report)
    markdown_path = Path(markdown_path)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.write_text(report.to_markdown(), encoding="utf-8")

    style_profile = None
    fallback_fields: list[str] | None = None
    if style_reference is not None:
        from core.exporters.extracted_style_mapper import to_document_style_profile
        from core.templates.extractors.style import extract_style

        extracted = extract_style(style_reference)
        style_profile, fallback_fields = to_document_style_profile(extracted)

    export_result = DocxExporter(style_profile=style_profile).export(markdown_path, docx_path)
    if fallback_fields is not None and export_result.ok:
        export_result.meta["style_source"] = "extracted"
        export_result.meta["style_fallback_fields"] = fallback_fields
        export_result.meta["style_fallback_used"] = bool(fallback_fields)
    return problems, export_result
