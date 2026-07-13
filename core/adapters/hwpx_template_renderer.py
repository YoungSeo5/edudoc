"""Render a filled HWPX from a template's {{placeholder}}s and a content mapping.

Deterministic. Reads the template's ``placeholder_map.json`` +
``template/section*.template.xml``, replaces each ``{{field_id}}`` (kept inside its
``<hp:t>``) with the XML-escaped content value, then writes the filled sections into
a byte-perfect copy of the *base* HWPX (only ``Contents/section*.xml`` change).
Changed sections discard ``hp:linesegarray`` caches so Hancom recalculates the
new text layout instead of reusing character positions from the sample content.

Honesty:
- Missing fields (in the placeholder map but absent from content) are left as
  ``{{placeholder}}`` and reported — never invented.
- Any ``{{...}}`` still present after filling is reported as a leftover placeholder.
- The output is validated with strict HWPX package validation before it is returned
  (``validate=True``); a file that only opens in Hancom is not treated as finished.
- A base package is required. The template's ``raw/`` folder omits entries
  (mimetype, version.xml, Preview/…) and cannot be repacked on its own, so a
  self-contained template stores the exact original as ``source.hwpx`` (see
  ``snapshot_source_hwpx``); the renderer uses it when no ``base_hwpx`` is given.
"""
from __future__ import annotations

import json
import re
import shutil
import zipfile
from dataclasses import dataclass, field
from pathlib import Path
from xml.sax.saxutils import escape

_PLACEHOLDER_RE = re.compile(r"\{\{([A-Za-z0-9_]+)\}\}")
_SECTION_TEMPLATE_RE = re.compile(r"^section(\d+)\.template\.xml$", re.IGNORECASE)
_LINESEGARRAY_RE = re.compile(
    r"<hp:linesegarray\b[^>]*/>|<hp:linesegarray\b[^>]*>.*?</hp:linesegarray>",
    re.DOTALL,
)

UNKNOWN = "확인 필요"


class HwpxTemplateRenderError(RuntimeError):
    """Raised when a template cannot be rendered."""


@dataclass
class RenderResult:
    output: Path
    filled_fields: list[str] = field(default_factory=list)
    missing_fields: list[str] = field(default_factory=list)
    leftover_placeholders: list[str] = field(default_factory=list)

    def to_meta(self) -> dict:
        return {
            "output": str(self.output),
            "filled_fields": self.filled_fields,
            "missing_fields": self.missing_fields,
            "leftover_placeholders": self.leftover_placeholders,
        }


def fill_template_sections(
    template_dir: Path | str,
    content: dict[str, object],
    *,
    on_missing: str = "keep",
) -> tuple[dict[str, str], RenderResult]:
    """Fill each template section's placeholders. Returns ({internal_path: xml}, result).

    ``on_missing``: "keep" leaves ``{{field}}`` (default), "unknown" writes
    ``확인 필요``, "error" raises if any mapped field is absent from content.
    """
    template_dir = Path(template_dir)
    _load_placeholder_map(template_dir)  # validated for presence; fields carry the map
    filled: set[str] = set()
    missing: set[str] = set()

    filled_sections: dict[str, str] = {}
    template_files = sorted((template_dir / "template").glob("section*.template.xml"))
    if not template_files:
        raise HwpxTemplateRenderError(f"no template/section*.template.xml in {template_dir}")
    for template_file in template_files:
        match = _SECTION_TEMPLATE_RE.fullmatch(template_file.name)
        if match is None:
            continue
        internal = f"Contents/section{int(match.group(1))}.xml"
        xml = template_file.read_text(encoding="utf-8")
        filled_xml = _fill_xml(xml, content, filled, missing)
        if filled_xml != xml:
            filled_xml = _LINESEGARRAY_RE.sub("", filled_xml)
        filled_sections[internal] = filled_xml

    if on_missing == "error" and missing:
        raise HwpxTemplateRenderError(f"missing content for fields: {sorted(missing)}")
    if on_missing == "unknown" and missing:
        # second pass turns still-unfilled placeholders into 확인 필요
        for internal, xml in filled_sections.items():
            filled_xml = _PLACEHOLDER_RE.sub(
                lambda m: escape(UNKNOWN) if m.group(1) in missing else m.group(0), xml
            )
            if filled_xml != xml:
                filled_xml = _LINESEGARRAY_RE.sub("", filled_xml)
            filled_sections[internal] = filled_xml

    leftover = sorted(
        {m.group(1) for xml in filled_sections.values() for m in _PLACEHOLDER_RE.finditer(xml)}
    )
    result = RenderResult(
        output=Path(),
        filled_fields=sorted(filled),
        missing_fields=sorted(missing),
        leftover_placeholders=leftover,
    )
    return filled_sections, result


def render_hwpx_template(
    template_dir: Path | str,
    content: dict[str, object],
    output_path: Path | str,
    *,
    base_hwpx: Path | str | None = None,
    on_missing: str = "keep",
    validate: bool = True,
) -> RenderResult:
    """Fill the template and write a filled HWPX.

    The base package is ``base_hwpx`` if given, otherwise the self-contained
    ``<template_dir>/source.hwpx`` snapshot. Only ``Contents/section*.xml`` change;
    every other entry (mimetype, version.xml, Preview/…, styles, BinData) is copied
    byte-for-byte — so a self-contained template renders with no external file.

    ``validate`` (default True) runs strict HWPX package validation on the output
    and raises if it does not pass — a file that only opens in Hancom is not enough.
    Set ``validate=False`` only to intentionally inspect an unvalidated result.
    """
    template_dir = Path(template_dir)
    output_path = Path(output_path)
    base = Path(base_hwpx) if base_hwpx is not None else template_dir / "source.hwpx"
    if not base.is_file() or not zipfile.is_zipfile(base):
        raise HwpxTemplateRenderError(
            f"no base HWPX: pass base_hwpx or add a self-contained {template_dir / 'source.hwpx'}"
        )

    filled_sections, result = fill_template_sections(template_dir, content, on_missing=on_missing)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    replaced: set[str] = set()
    with zipfile.ZipFile(base) as zin, zipfile.ZipFile(output_path, "w") as zout:
        for info in zin.infolist():  # keep entry order (mimetype first) + compress types
            data = zin.read(info.filename)
            if info.filename in filled_sections:
                data = filled_sections[info.filename].encode("utf-8")
                replaced.add(info.filename)
            zout.writestr(info, data)

    unmatched = sorted(set(filled_sections) - replaced)
    if unmatched:
        raise HwpxTemplateRenderError(
            f"filled sections not present in base HWPX: {unmatched}"
        )
    if validate:
        validate_hwpx_output(output_path)
    result.output = output_path
    return result


def validate_hwpx_output(output_path: Path | str) -> None:
    """Run strict HWPX package validation; raise ``HwpxTemplateRenderError`` if it fails.

    Uses ``python-hwpx``. If that library is not installed, validation was
    requested but cannot run, so this raises rather than silently passing.
    """
    try:
        import hwpx  # local import: keep the renderer importable without python-hwpx
    except ImportError as exc:  # pragma: no cover - depends on environment
        raise HwpxTemplateRenderError(
            "validate=True requires python-hwpx (pip install python-hwpx); "
            "pass validate=False to skip validation"
        ) from exc

    report = hwpx.validate_package(Path(output_path))
    if not report.ok:
        raise HwpxTemplateRenderError(
            f"rendered HWPX failed strict package validation: {list(report.errors)}"
        )


def snapshot_source_hwpx(source_hwpx: Path | str, template_dir: Path | str) -> Path:
    """Store a byte copy of the source HWPX as ``<template_dir>/source.hwpx``.

    Makes the template self-contained: ``render_hwpx_template`` can then render
    with no external base file, using this exact original package as the base.
    """
    source_hwpx = Path(source_hwpx)
    if not zipfile.is_zipfile(source_hwpx):
        raise HwpxTemplateRenderError(f"source is not a readable HWPX ZIP: {source_hwpx}")
    destination = Path(template_dir) / "source.hwpx"
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source_hwpx, destination)
    return destination


def load_content_fields(content_json: Path | str) -> dict[str, object]:
    """Read a content.json ({template_id, fields:{...}}) and return its ``fields`` mapping."""
    data = json.loads(Path(content_json).read_text(encoding="utf-8"))
    return dict(data.get("fields", data))


def _load_placeholder_map(template_dir: Path) -> dict:
    path = template_dir / "placeholder_map.json"
    if not path.is_file():
        raise HwpxTemplateRenderError(f"placeholder_map.json not found in {template_dir}")
    return json.loads(path.read_text(encoding="utf-8"))


def _fill_xml(xml: str, content: dict[str, object], filled: set[str], missing: set[str]) -> str:
    def replace(match: re.Match) -> str:
        field_id = match.group(1)
        value = content.get(field_id)
        if value is not None:
            filled.add(field_id)
            return escape(str(value))
        missing.add(field_id)
        return match.group(0)  # keep {{field_id}} unfilled (never invented)

    return _PLACEHOLDER_RE.sub(replace, xml)
