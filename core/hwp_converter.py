"""
HWPX-first input converter with HWP legacy fallback.

- .hwpx: python-hwpx(HwpxDocument.export_markdown) -> Markdown.
- .hwp: pyhwp -> HTML -> markdownify -> Markdown, kept as legacy/fallback compatibility.

For HWPX, this converter also attaches a minimal DocumentModel. The current
paragraph/table structure is still Markdown-derived fallback, while package/XML
metadata is recorded separately in raw_meta when available.

나중에 hwp2md(Rust)로 크로스체크를 붙이려면
core/hwp2md_converter.py 를 같은 인터페이스로 추가하고
pipeline 의 변환기 목록에만 등록하면 된다.
"""
from __future__ import annotations

from pathlib import Path

from .converter_base import BaseConverter, ConvertResult
from .document_model import document_model_from_markdown
from .hwpx_metadata import inspect_hwpx_package


class HwpSkillConverter(BaseConverter):
    supported_ext = (".hwp", ".hwpx")

    def convert(self, path: Path) -> ConvertResult:
        try:
            markdown = self._run_hwp_skill(path)
            document_model = None
            if path.suffix.lower() == ".hwpx":
                native_meta = inspect_hwpx_package(path)
                structure_source = (
                    "hwpx_xml_metadata_plus_markdown_fallback"
                    if native_meta.get("xml_metadata_available")
                    else
                    "hwpx_package_metadata_plus_markdown_fallback"
                    if native_meta.get("native_metadata_available")
                    else "markdown_fallback"
                )
                document_model = document_model_from_markdown(
                    source_path=path,
                    file_format="hwpx",
                    markdown=markdown,
                    raw_meta={
                        "converter": self.name,
                        "structure_source": structure_source,
                        **native_meta,
                    },
                )
            return ConvertResult(
                source=path,
                markdown=markdown,
                ok=True,
                meta={"converter": self.name},
                document_model=document_model,
            )
        except NotImplementedError as e:
            # 아직 실제 변환 로직을 붙이기 전 단계
            return ConvertResult(
                source=path, markdown="", ok=False, error=str(e),
                meta={"converter": self.name},
            )
        except Exception as e:  # noqa: BLE001  (Phase 0에선 폭넓게 잡아 로그)
            return ConvertResult(
                source=path, markdown="", ok=False, error=repr(e),
                meta={"converter": self.name},
            )

    def _run_hwp_skill(self, path: Path) -> str:
        """
        입력 파일을 Markdown 문자열로 변환한다.

        - .hwpx (ZIP+XML)   : python-hwpx(HwpxDocument.export_markdown)
        - .hwp  (OLE 바이너리): pyhwp(HTML) -> markdownify(Markdown)
        """
        ext = path.suffix.lower()
        if ext == ".hwpx":
            return self._convert_hwpx(path)
        if ext == ".hwp":
            return self._convert_hwp(path)
        raise NotImplementedError(f"{ext} 변환 미지원 (.hwp/.hwpx만 지원)")

    def _convert_hwpx(self, path: Path) -> str:
        """python-hwpx 로 .hwpx -> Markdown."""
        import logging

        from hwpx import HwpxDocument

        # 라이브러리가 manifest fallback 등을 WARNING 으로 남겨 콘솔을 어지럽히므로 낮춘다.
        logging.getLogger("hwpx").setLevel(logging.ERROR)

        doc = HwpxDocument.open(str(path))
        try:
            return doc.export_markdown()
        finally:
            doc.close()

    def _convert_hwp(self, path: Path) -> str:
        """
        pyhwp 로 .hwp(OLE 바이너리) -> HTML -> Markdown.

        pyhwp 의 순수 텍스트 변환은 표 내용을 버리므로,
        표·본문을 보존하는 HTML 변환을 거쳐 markdownify 로 Markdown 을 만든다.
        """
        import contextlib
        import io
        import re
        import tempfile

        from hwp5.hwp5html import HTMLTransform
        from hwp5.xmlmodel import Hwp5File
        from markdownify import markdownify

        with tempfile.TemporaryDirectory() as tmp:
            # pyhwp 가 stderr 로 남기는 로그는 무시한다.
            with contextlib.redirect_stderr(io.StringIO()):
                HTMLTransform().transform_hwp5_to_dir(Hwp5File(str(path)), tmp)
            html = (Path(tmp) / "index.xhtml").read_text(encoding="utf-8")

        html = re.sub(r"<\?xml[^>]*\?>", "", html)  # XML 선언 제거(본문 아님)
        md = markdownify(html, heading_style="ATX", strip=["span", "img"])
        md = "\n".join(line.rstrip() for line in md.splitlines())
        return re.sub(r"\n{3,}", "\n\n", md).strip() + "\n"
