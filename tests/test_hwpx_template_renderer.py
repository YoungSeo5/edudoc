"""core.adapters.hwpx_template_renderer: fill {{placeholder}}s -> filled HWPX.

Proves the renderer fills a template's placeholders from a content mapping
(honestly: missing fields stay {{placeholder}}, values are XML-escaped), and
repacks the filled sections into a byte-perfect copy of a base HWPX.
"""
from __future__ import annotations

import json
import re
import sys
import tempfile
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.adapters.hwpx_template_renderer import (
    HwpxTemplateRenderError,
    fill_template_sections,
    load_content_fields,
    render_hwpx_template,
    snapshot_source_hwpx,
    validate_hwpx_output,
)

ROOT = Path(__file__).resolve().parent.parent
FSS_DIR = ROOT / "skills" / "templates" / "fss_virtual_asset_report"
BROTHER_HWPX = ROOT / "references" / "document-types" / "public-plan" / "브라더 공공기관 보고서 양식.hwpx"


def test_fill_fss_full_content_has_no_leftover() -> None:
    content = load_content_fields(FSS_DIR / "content.sample.json")
    sections, result = fill_template_sections(FSS_DIR, content)

    assert len(result.filled_fields) == 11
    assert result.missing_fields == []
    assert result.leftover_placeholders == []
    section0 = sections["Contents/section0.xml"]
    assert "가상자산감독국" in section0 and "{{" not in section0


def test_fill_reports_missing_and_keeps_placeholder() -> None:
    # only two of the mapped fields provided
    content = {"date_01": "(2026. 1. 1.)", "document_title_01": "테스트 제목"}
    sections, result = fill_template_sections(FSS_DIR, content)

    section0 = sections["Contents/section0.xml"]
    assert "(2026. 1. 1.)" in section0 and "테스트 제목" in section0
    assert set(result.filled_fields) == {"date_01", "document_title_01"}
    assert "body_paragraph_01" in result.missing_fields
    assert "{{body_paragraph_01}}" in section0            # kept, never invented
    assert "body_paragraph_01" in result.leftover_placeholders


def _write_template_dir(tmp: Path, template_xml: str, field_id: str) -> Path:
    (tmp / "template").mkdir(parents=True)
    (tmp / "template" / "section0.template.xml").write_text(template_xml, encoding="utf-8")
    (tmp / "placeholder_map.json").write_text(
        json.dumps({"fields": [{"field_id": field_id, "placeholder": f"{{{{{field_id}}}}}",
                                "section": "section0.xml"}]}, ensure_ascii=False),
        encoding="utf-8",
    )
    return tmp


def test_fill_xml_escapes_values() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        tmp = _write_template_dir(Path(tmp), "<hp:p><hp:t>{{x}}</hp:t></hp:p>", "x")
        sections, _ = fill_template_sections(tmp, {"x": "A & B < C"})
        assert "A &amp; B &lt; C" in sections["Contents/section0.xml"]


def test_fill_removes_stale_linesegarray_after_text_replacement() -> None:
    template_xml = (
        "<hp:p><hp:run><hp:t>{{x}}</hp:t></hp:run>"
        '<hp:linesegarray><hp:lineseg textpos="0"/></hp:linesegarray></hp:p>'
    )
    with tempfile.TemporaryDirectory() as tmp:
        tmp = _write_template_dir(Path(tmp), template_xml, "x")
        sections, _ = fill_template_sections(tmp, {"x": "새로 채운 긴 본문"})

    section0 = sections["Contents/section0.xml"]
    assert "새로 채운 긴 본문" in section0
    assert "<hp:linesegarray" not in section0


def test_render_replaces_only_section_in_base_hwpx() -> None:
    section0 = zipfile.ZipFile(BROTHER_HWPX).read("Contents/section0.xml").decode("utf-8")
    # turn the first non-empty <hp:t> into a placeholder, keep the rest byte-identical
    target = next(t for t in re.findall(r"<hp:t>([^<]+)</hp:t>", section0) if t.strip())
    template_xml = section0.replace(f"<hp:t>{target}</hp:t>", "<hp:t>{{demo_field}}</hp:t>", 1)

    with tempfile.TemporaryDirectory() as tmp:
        tmp = _write_template_dir(Path(tmp), template_xml, "demo_field")
        out = Path(tmp) / "rendered.hwpx"
        result = render_hwpx_template(tmp, {"demo_field": "RENDER_OK"}, out, base_hwpx=BROTHER_HWPX)

        assert result.leftover_placeholders == []
        assert result.filled_fields == ["demo_field"]
        assert out.exists() and out.read_bytes()[:2] == b"PK"
        with zipfile.ZipFile(out) as z:
            assert z.namelist()[0] == "mimetype"           # base order preserved
            filled = z.read("Contents/section0.xml").decode("utf-8")
            assert "RENDER_OK" in filled and "{{" not in filled
            # everything else stays byte-identical to the base
            assert z.read("Contents/header.xml") == zipfile.ZipFile(BROTHER_HWPX).read("Contents/header.xml")


def test_self_contained_template_renders_without_external_base() -> None:
    """A template with a source.hwpx snapshot renders with no external base file."""
    section0 = zipfile.ZipFile(BROTHER_HWPX).read("Contents/section0.xml").decode("utf-8")
    target = next(t for t in re.findall(r"<hp:t>([^<]+)</hp:t>", section0) if t.strip())
    template_xml = section0.replace(f"<hp:t>{target}</hp:t>", "<hp:t>{{demo_field}}</hp:t>", 1)

    with tempfile.TemporaryDirectory() as tmp:
        tmp = _write_template_dir(Path(tmp), template_xml, "demo_field")
        snapshot_source_hwpx(BROTHER_HWPX, tmp)          # self-contain: byte copy of original
        assert (tmp / "source.hwpx").read_bytes() == BROTHER_HWPX.read_bytes()

        out = Path(tmp) / "rendered.hwpx"
        result = render_hwpx_template(tmp, {"demo_field": "RENDER_OK"}, out)  # no base_hwpx

        assert result.leftover_placeholders == []
        with zipfile.ZipFile(out) as z:
            assert z.namelist()[0] == "mimetype"
            assert "RENDER_OK" in z.read("Contents/section0.xml").decode("utf-8")


def test_render_validates_output_by_default() -> None:
    """Default validate=True: the rendered HWPX passes strict package validation."""
    section0 = zipfile.ZipFile(BROTHER_HWPX).read("Contents/section0.xml").decode("utf-8")
    target = next(t for t in re.findall(r"<hp:t>([^<]+)</hp:t>", section0) if t.strip())
    template_xml = section0.replace(f"<hp:t>{target}</hp:t>", "<hp:t>{{demo_field}}</hp:t>", 1)

    with tempfile.TemporaryDirectory() as tmp:
        tmp = _write_template_dir(Path(tmp), template_xml, "demo_field")
        out = Path(tmp) / "rendered.hwpx"
        render_hwpx_template(tmp, {"demo_field": "OK"}, out, base_hwpx=BROTHER_HWPX)  # validate=True
        validate_hwpx_output(out)  # explicit: no error means strict validation passed


def test_render_without_any_base_raises() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        tmp = _write_template_dir(Path(tmp), "<hp:p><hp:t>{{x}}</hp:t></hp:p>", "x")
        try:
            render_hwpx_template(tmp, {"x": "v"}, Path(tmp) / "out.hwpx")
        except HwpxTemplateRenderError as exc:
            assert "self-contained" in str(exc)
        else:
            raise AssertionError("expected HwpxTemplateRenderError when no base is available")


if __name__ == "__main__":
    test_fill_fss_full_content_has_no_leftover()
    test_fill_reports_missing_and_keeps_placeholder()
    test_fill_xml_escapes_values()
    test_fill_removes_stale_linesegarray_after_text_replacement()
    test_render_replaces_only_section_in_base_hwpx()
    test_self_contained_template_renders_without_external_base()
    test_render_validates_output_by_default()
    test_render_without_any_base_raises()
    print("PASS: HWPX template renderer (fill + honest missing + byte-perfect repack)")
