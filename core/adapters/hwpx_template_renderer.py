"""Render a filled HWPX from a template's {{placeholder}}s and a content mapping.

Deterministic. Reads the template's ``placeholder_map.json`` +
``template/section*.template.xml``, replaces each ``{{field_id}}`` (kept inside its
``<hp:t>``) with the XML-escaped content value, then writes the filled sections into
a byte-perfect copy of the *base* HWPX (only ``Contents/section*.xml`` change).

Honesty:
- Missing fields (in the placeholder map but absent from content) are left as
  ``{{placeholder}}`` and reported — never invented.
- Any ``{{...}}`` still present after filling is reported as a leftover placeholder.
- The base HWPX is required: the template's ``raw/`` folder omits package entries
  (mimetype, version.xml, Preview/…), so it cannot be repacked into a valid HWPX
  on its own.
"""
from __future__ import annotations

import json
import re
import zipfile
from dataclasses import dataclass, field
from pathlib import Path
from xml.sax.saxutils import escape

_PLACEHOLDER_RE = re.compile(r"\{\{([A-Za-z0-9_]+)\}\}")
_SECTION_TEMPLATE_RE = re.compile(r"^section(\d+)\.template\.xml$", re.IGNORECASE)

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
        filled_sections[internal] = _fill_xml(xml, content, filled, missing)

    if on_missing == "error" and missing:
        raise HwpxTemplateRenderError(f"missing content for fields: {sorted(missing)}")
    if on_missing == "unknown" and missing:
        # second pass turns still-unfilled placeholders into 확인 필요
        for internal, xml in filled_sections.items():
            filled_sections[internal] = _PLACEHOLDER_RE.sub(
                lambda m: escape(UNKNOWN) if m.group(1) in missing else m.group(0), xml
            )

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
    base_hwpx: Path | str,
    template_dir: Path | str,
    content: dict[str, object],
    output_path: Path | str,
    *,
    on_missing: str = "keep",
) -> RenderResult:
    """Fill the template and write a filled HWPX using ``base_hwpx`` as a byte-perfect base."""
    base_hwpx = Path(base_hwpx)
    output_path = Path(output_path)
    if not zipfile.is_zipfile(base_hwpx):
        raise HwpxTemplateRenderError(f"base is not a readable HWPX ZIP: {base_hwpx}")

    filled_sections, result = fill_template_sections(template_dir, content, on_missing=on_missing)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    replaced: set[str] = set()
    with zipfile.ZipFile(base_hwpx) as zin, zipfile.ZipFile(output_path, "w") as zout:
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
    result.output = output_path
    return result


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
