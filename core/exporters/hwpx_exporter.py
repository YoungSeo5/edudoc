"""Minimal pip-native Markdown -> HWPX package exporter.

The protected HWPX skill packs are treated as references only. This exporter
implements a tiny edudoc-owned package writer that preserves visible text and
basic paragraph structure, then validates the generated package at a structural
level. It is not a full HWPX layout engine.
"""
from __future__ import annotations

import zipfile
from pathlib import Path
from xml.sax.saxutils import escape as xml_escape

from validators.hwpx_package_rules import validate as validate_hwpx_package

from .export_base import BaseExporter, ExportResult
from .markdown_blocks import Heading, ListBlock, Paragraph, Table, parse_markdown


HWPX_MIMETYPE = "application/hwp+zip"


class HwpxExporter(BaseExporter):
    """Markdown file -> minimal HWPX package."""

    supported_ext = (".hwpx",)

    def export(self, markdown_path: Path, output_path: Path) -> ExportResult:
        markdown_path = Path(markdown_path)
        output_path = Path(output_path)

        if not self.can_export(output_path):
            return ExportResult(
                source=markdown_path,
                output=output_path,
                ok=False,
                error=(
                    f"Unsupported output extension: {output_path.suffix} "
                    f"(supported: {sorted(self.supported_ext)})"
                ),
                meta={"exporter": self.name, "requires_optional_tool": False},
            )
        if not markdown_path.exists():
            return ExportResult(
                source=markdown_path,
                output=output_path,
                ok=False,
                error=f"Markdown source does not exist: {markdown_path}",
                meta={"exporter": self.name, "requires_optional_tool": False},
            )

        try:
            markdown = markdown_path.read_text(encoding="utf-8")
            blocks = parse_markdown(markdown)
            visible_lines = _visible_lines(blocks)
            title = _document_title(visible_lines, markdown_path.stem)

            output_path.parent.mkdir(parents=True, exist_ok=True)
            self._write_package(output_path, title, visible_lines)

            report = validate_hwpx_package(output_path)
            return ExportResult(
                source=markdown_path,
                output=output_path,
                ok=report.passed,
                error=None if report.passed else report.summary(),
                meta={
                    "exporter": self.name,
                    "blocks": len(blocks),
                    "visible_line_count": len(visible_lines),
                    "requires_optional_tool": False,
                    "validation_passed": report.passed,
                    "validation_summary": report.summary(),
                    "note": (
                        "minimal pip-native HWPX package; preserves visible text "
                        "but does not claim final institution-approved layout"
                    ),
                },
            )
        except Exception as exc:  # noqa: BLE001 - structured exporter failure
            return ExportResult(
                source=markdown_path,
                output=output_path,
                ok=False,
                error=repr(exc),
                meta={"exporter": self.name, "requires_optional_tool": False},
            )

    def _write_package(
        self,
        output_path: Path,
        title: str,
        visible_lines: list[str],
    ) -> None:
        with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("mimetype", HWPX_MIMETYPE, compress_type=zipfile.ZIP_STORED)
            zf.writestr("META-INF/manifest.xml", _manifest_xml())
            zf.writestr("Contents/content.hpf", _content_hpf(title))
            zf.writestr("Contents/header.xml", _header_xml())
            zf.writestr("Contents/section0.xml", _section_xml(visible_lines))
            zf.writestr("Preview/PrvText.txt", "\n".join(visible_lines))


def _visible_lines(blocks) -> list[str]:  # noqa: ANN001
    lines: list[str] = []
    for block in blocks:
        if isinstance(block, Heading):
            lines.append(_runs_text(block.runs))
        elif isinstance(block, Paragraph):
            text = _runs_text(block.runs)
            if text:
                lines.append(text)
        elif isinstance(block, ListBlock):
            for idx, item in enumerate(block.items, 1):
                prefix = f"{idx}. " if block.ordered else "- "
                lines.append(prefix + _runs_text(item))
        elif isinstance(block, Table):
            if block.header:
                lines.append(" | ".join(_runs_text(cell) for cell in block.header))
            for row in block.rows:
                lines.append(" | ".join(_runs_text(cell) for cell in row))
    return [line for line in lines if line.strip()]


def _runs_text(runs) -> str:  # noqa: ANN001
    return "".join(run.text for run in runs).strip()


def _document_title(visible_lines: list[str], fallback: str) -> str:
    return visible_lines[0] if visible_lines else fallback


def _manifest_xml() -> str:
    return """<?xml version="1.0" encoding="UTF-8"?>
<manifest xmlns="urn:oasis:names:tc:opendocument:xmlns:manifest:1.0">
  <file-entry full-path="/" media-type="application/hwp+zip"/>
  <file-entry full-path="Contents/content.hpf" media-type="text/xml"/>
  <file-entry full-path="Contents/header.xml" media-type="text/xml"/>
  <file-entry full-path="Contents/section0.xml" media-type="text/xml"/>
</manifest>
"""


def _content_hpf(title: str) -> str:
    safe_title = xml_escape(title)
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0">
  <metadata>
    <title>{safe_title}</title>
    <creator>edudoc</creator>
  </metadata>
  <manifest>
    <item id="header" href="Contents/header.xml" media-type="text/xml"/>
    <item id="section0" href="Contents/section0.xml" media-type="text/xml"/>
  </manifest>
  <spine>
    <itemref idref="section0"/>
  </spine>
</package>
"""


def _header_xml() -> str:
    return """<?xml version="1.0" encoding="UTF-8"?>
<hh:head xmlns:hh="http://www.hancom.co.kr/hwpml/2011/head"
         xmlns:hp="http://www.hancom.co.kr/hwpml/2011/paragraph"
         xmlns:hc="http://www.hancom.co.kr/hwpml/2011/core">
  <hh:beginNum page="1" footnote="1" endnote="1" pic="1" tbl="1" equation="1"/>
  <hh:refList/>
  <hh:docOption/>
</hh:head>
"""


def _section_xml(visible_lines: list[str]) -> str:
    paragraphs = []
    for idx, line in enumerate(visible_lines, 1):
        escaped = xml_escape(line)
        paragraphs.append(
            f'  <hp:p id="{1000000000 + idx}" paraPrIDRef="0" '
            'styleIDRef="0" pageBreak="0" columnBreak="0" merged="0">'
            f'<hp:run charPrIDRef="0"><hp:t>{escaped}</hp:t></hp:run></hp:p>'
        )
    if not paragraphs:
        paragraphs.append(
            '  <hp:p id="1000000001" paraPrIDRef="0" styleIDRef="0" '
            'pageBreak="0" columnBreak="0" merged="0">'
            '<hp:run charPrIDRef="0"><hp:t/></hp:run></hp:p>'
        )
    body = "\n".join(paragraphs)
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<hs:sec xmlns:hs="http://www.hancom.co.kr/hwpml/2011/section"
        xmlns:hp="http://www.hancom.co.kr/hwpml/2011/paragraph"
        xmlns:hc="http://www.hancom.co.kr/hwpml/2011/core">
{body}
</hs:sec>
"""
