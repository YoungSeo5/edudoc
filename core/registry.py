"""
변환기 레지스트리.

여러 변환기를 등록해두고, 파일 확장자에 맞는 변환기를 골라준다.
Phase 0 기본값은 hwp 스킬 변환기 하나뿐이지만,
나중에 hwp2md / pdf / docx 변환기를 여기에 추가하기만 하면 확장된다.
"""
from __future__ import annotations

from pathlib import Path

from .converter_base import BaseConverter
from .hwp_converter import HwpSkillConverter
from .markdown_converter import MarkdownConverter


class ConverterRegistry:
    def __init__(self) -> None:
        self._converters: list[BaseConverter] = []

    def register(self, converter: BaseConverter) -> None:
        self._converters.append(converter)

    def find(self, path: Path) -> BaseConverter | None:
        """가장 먼저 등록된, 처리 가능한 변환기를 반환."""
        for c in self._converters:
            if c.can_handle(path):
                return c
        return None

    @property
    def supported_ext(self) -> set[str]:
        exts: set[str] = set()
        for c in self._converters:
            exts.update(c.supported_ext)
        return exts


def default_registry() -> ConverterRegistry:
    """Phase 0 기본 구성: Markdown 초안과 HWP/HWPX 입력을 등록."""
    reg = ConverterRegistry()
    reg.register(MarkdownConverter())
    reg.register(HwpSkillConverter())
    # 나중에:
    # reg.register(Hwp2mdConverter())   # Rust 크로스체크
    # reg.register(PdfConverter())
    # reg.register(DocxConverter())
    return reg
