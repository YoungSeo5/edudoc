"""HWP/HWPX input converter.

HWPX is the preferred structured input. Binary HWP remains legacy compatibility,
but the converter now tries a safe HWP -> HWPX normalization step first:

- .hwpx: python-hwpx(HwpxDocument.export_markdown) -> Markdown + DocumentModel.
- .hwp: hwpx-skill adapter converts HWP -> temporary HWPX, then the same HWPX
  Markdown/DocumentModel path is reused.
- .hwp fallback: if the safe HWP -> HWPX adapter is unavailable, use
  pyhwp -> HTML -> markdownify -> Markdown.

The adapter never installs packages, clones repositories, or modifies files in
``skills/``. Final output format is still decided later by the pipeline/exporter
settings; HWP input does not imply final HWPX output.
"""
from __future__ import annotations

from pathlib import Path

from .adapters.hwpx_skill_adapter import HwpToHwpxAdapterError, convert_hwp_to_hwpx
from .converter_base import BaseConverter, ConvertResult
from .document_model import DocumentModel, document_model_from_markdown
from .hwpx_metadata import inspect_hwpx_package


class HwpSkillConverter(BaseConverter):
    supported_ext = (".hwp", ".hwpx")

    def convert(self, path: Path) -> ConvertResult:
        try:
            markdown, meta, document_model = self._convert_to_markdown(path)
            return ConvertResult(
                source=path,
                markdown=markdown,
                ok=True,
                meta={"converter": self.name, **meta},
                document_model=document_model,
            )
        except NotImplementedError as e:
            return ConvertResult(
                source=path,
                markdown="",
                ok=False,
                error=str(e),
                meta={"converter": self.name},
            )
        except Exception as e:  # noqa: BLE001 - keep failures structured
            return ConvertResult(
                source=path,
                markdown="",
                ok=False,
                error=repr(e),
                meta={"converter": self.name},
            )

    def _convert_to_markdown(
        self,
        path: Path,
    ) -> tuple[str, dict, DocumentModel | None]:
        ext = path.suffix.lower()
        if ext == ".hwpx":
            markdown = self._convert_hwpx(path)
            document_model = self._document_model_from_hwpx(
                source_path=path,
                hwpx_path=path,
                markdown=markdown,
                file_format="hwpx",
                extra_meta={},
            )
            return markdown, {"input_conversion_strategy": "hwpx_direct"}, document_model
        if ext == ".hwp":
            return self._convert_hwp(path)
        raise NotImplementedError(f"{ext} conversion is not supported")

    def _convert_hwpx(self, path: Path) -> str:
        """Convert HWPX to Markdown with python-hwpx."""
        import logging

        from hwpx import HwpxDocument

        logging.getLogger("hwpx").setLevel(logging.ERROR)

        doc = HwpxDocument.open(str(path))
        try:
            return doc.export_markdown()
        finally:
            doc.close()

    def _convert_hwp(self, path: Path) -> tuple[str, dict, DocumentModel | None]:
        try:
            return self._convert_hwp_via_hwpx_adapter(path)
        except HwpToHwpxAdapterError as adapter_error:
            markdown = self._convert_hwp_legacy(path)
            return (
                markdown,
                {
                    "input_conversion_strategy": "pyhwp_html_markdown_fallback",
                    "hwp_to_hwpx_available": False,
                    "hwp_to_hwpx_error": str(adapter_error),
                },
                None,
            )

    def _convert_hwp_via_hwpx_adapter(
        self,
        path: Path,
    ) -> tuple[str, dict, DocumentModel | None]:
        import tempfile

        try:
            with tempfile.TemporaryDirectory() as tmp:
                intermediate_hwpx = Path(tmp) / f"{path.stem}.hwpx"
                adapter_result = convert_hwp_to_hwpx(path, intermediate_hwpx)
                markdown = self._convert_hwpx(adapter_result.output_path)
                adapter_meta = adapter_result.to_meta()
                meta = {
                    "input_conversion_strategy": "hwp_to_hwpx_then_markdown",
                    "intermediate_format": "hwpx",
                    "intermediate_hwpx_retained": False,
                    **adapter_meta,
                }
                document_model = self._document_model_from_hwpx(
                    source_path=path,
                    hwpx_path=adapter_result.output_path,
                    markdown=markdown,
                    file_format="hwp",
                    extra_meta=meta,
                )
                return markdown, meta, document_model
        except HwpToHwpxAdapterError:
            raise
        except Exception as exc:  # noqa: BLE001 - preserve legacy HWP fallback
            raise HwpToHwpxAdapterError(
                f"HWP -> HWPX adapter path failed: {exc!r}"
            ) from exc

    def _document_model_from_hwpx(
        self,
        *,
        source_path: Path,
        hwpx_path: Path,
        markdown: str,
        file_format: str,
        extra_meta: dict,
    ) -> DocumentModel:
        native_meta = inspect_hwpx_package(hwpx_path)
        structure_source = (
            "hwpx_xml_metadata_plus_markdown_fallback"
            if native_meta.get("xml_metadata_available")
            else
            "hwpx_package_metadata_plus_markdown_fallback"
            if native_meta.get("native_metadata_available")
            else "markdown_fallback"
        )
        return document_model_from_markdown(
            source_path=source_path,
            file_format=file_format,
            markdown=markdown,
            raw_meta={
                "converter": self.name,
                "structure_source": structure_source,
                **extra_meta,
                **native_meta,
            },
        )

    def _convert_hwp_legacy(self, path: Path) -> str:
        """Convert binary HWP to Markdown through pyhwp HTML output."""
        import contextlib
        import io
        import re
        import tempfile

        from hwp5.hwp5html import HTMLTransform
        from hwp5.xmlmodel import Hwp5File
        from markdownify import markdownify

        with tempfile.TemporaryDirectory() as tmp:
            with contextlib.redirect_stderr(io.StringIO()):
                HTMLTransform().transform_hwp5_to_dir(Hwp5File(str(path)), tmp)
            html = (Path(tmp) / "index.xhtml").read_text(encoding="utf-8")

        html = re.sub(r"<\?xml[^>]*\?>", "", html)
        md = markdownify(html, heading_style="ATX", strip=["span", "img"])
        md = "\n".join(line.rstrip() for line in md.splitlines())
        return re.sub(r"\n{3,}", "\n\n", md).strip() + "\n"
