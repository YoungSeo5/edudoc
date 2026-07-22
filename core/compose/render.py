"""Render an agent-authored ComposedReport to HWPX / PPTX via edudoc exporters."""
from __future__ import annotations

import json
from pathlib import Path

from core.adapters.hwpx_template_renderer import HwpxTemplateRenderError, render_hwpx_template
from core.exporters.docx_exporter import DocxExporter
from core.exporters.export_base import ExportResult
from core.exporters.hwpx_via_hwpskill import HwpxViaHwpSkillExporter
from core.exporters.pptx_exporter import PptxExporter
from core.exporters.style_profile import (
    DEFAULT_GONGMUN_STYLE_PROFILE,
    DEFAULT_PUBLIC_DOCUMENT_STYLE_PROFILE,
    DocumentStyleProfile,
)
from core.templates.registry import TemplateRegistry

from .report import ComposedReport, attachment_policy_for_family, validate_report

# target document profile family -> DOCX style profile (unknown family => neutral)
_FAMILY_STYLE_PROFILES = {"gongmun": DEFAULT_GONGMUN_STYLE_PROFILE}


def _style_profile_for_family(family: str | None) -> DocumentStyleProfile:
    return _FAMILY_STYLE_PROFILES.get(family or "", DEFAULT_PUBLIC_DOCUMENT_STYLE_PROFILE)


def load_plan(path: Path | str) -> ComposedReport:
    return ComposedReport.from_dict(json.loads(Path(path).read_text(encoding="utf-8")))


def render_report_to_hwpx(
    report: ComposedReport,
    markdown_path: Path | str,
    hwpx_path: Path | str,
    *,
    template: str = "report",
    style_reference: Path | str | None = None,
    profile_family: str | None = None,
    institution: str | None = None,
    document_type: str | None = None,
    template_content: dict[str, object] | None = None,
):
    """Validate -> clean Markdown -> HWPX. Returns (problems, export_result).

    When ``style_reference`` (an HWPX) is given, its body font/size/spacing are
    extracted and patched into a custom header.xml passed to md2hwpx; fields the
    reference lacks keep the template value and are recorded in
    ``export_result.meta['style_fallback_fields']`` (fallback_used honesty).
    Page margins are not header-settable, so they are left to the template.
    """
    if (institution is None) != (document_type is None):
        raise ValueError("institution and document_type must be provided together")
    if institution is not None and template_content is None:
        raise ValueError("template_content is required for institution template rendering")

    problems = validate_report(report)
    markdown_path = Path(markdown_path)
    hwpx_path = Path(hwpx_path)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.write_text(
        report.to_markdown(attachment_policy_for_family(profile_family)), encoding="utf-8"
    )

    if institution is not None and document_type is not None:
        registry = TemplateRegistry()
        candidate = registry.find(institution, document_type)
        meta = {
            "engine": "institution_template",
            "institution": institution,
            "document_type": document_type,
        }
        if candidate is None:
            return problems, ExportResult(
                source=markdown_path,
                output=hwpx_path,
                ok=False,
                error=(
                    "approved institution template not found: "
                    f"{institution} / {document_type}"
                ),
                meta={**meta, "available": False},
            )

        template_dir = registry.template_path(institution, document_type).parent
        template_meta = {
            **meta,
            "available": True,
            "template_id": candidate.identity.template_id,
        }
        try:
            render_result = render_hwpx_template(template_dir, template_content, hwpx_path)
        except HwpxTemplateRenderError as exc:
            return problems, ExportResult(
                source=markdown_path,
                output=hwpx_path,
                ok=False,
                error=str(exc),
                meta=template_meta,
            )

        return problems, ExportResult(
            source=markdown_path,
            output=render_result.output,
            meta={**render_result.to_meta(), **template_meta},
        )

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
    profile_family: str | None = None,
):
    """Validate -> clean Markdown -> PPTX (pip-native). Returns (problems, export_result).

    Charts are opt-in: by default numeric tables render as table slides (written deck).
    Pass ``include_charts=True`` to turn numeric tables into chart slides.
    """
    problems = validate_report(report)
    markdown_path = Path(markdown_path)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.write_text(
        report.to_markdown(attachment_policy_for_family(profile_family)), encoding="utf-8"
    )
    export_result = PptxExporter(include_charts=include_charts).export(markdown_path, pptx_path)
    return problems, export_result


def render_report_to_docx(
    report: ComposedReport,
    markdown_path: Path | str,
    docx_path: Path | str,
    *,
    style_reference: Path | str | None = None,
    profile_family: str | None = None,
):
    """Validate -> clean Markdown -> DOCX (pip-native). Returns (problems, export_result).

    When ``style_reference`` (an HWPX) is given, its real style is extracted and
    applied; fields the reference lacks fall back to the default and are recorded
    in ``export_result.meta['style_fallback_fields']`` (fallback_used honesty).
    Otherwise the style profile is selected by ``profile_family`` (Gongmun only
    on the "gongmun" family; every other family gets the neutral profile).
    """
    problems = validate_report(report)
    markdown_path = Path(markdown_path)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.write_text(
        report.to_markdown(attachment_policy_for_family(profile_family)), encoding="utf-8"
    )

    style_profile = _style_profile_for_family(profile_family)
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
