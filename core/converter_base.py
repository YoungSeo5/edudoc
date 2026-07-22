"""
변환기 추상 베이스.

모든 입력 변환기(HWP -> Markdown 등)는 이 인터페이스를 구현한다.
이렇게 해두면 나중에 hwp2md(Rust)나 다른 변환기로 갈아끼울 때
core 바깥 코드는 건드리지 않아도 된다.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path

from .document_model import DocumentModel


@dataclass
class ConvertResult:
    """변환 결과 한 건."""
    source: Path                 # 원본 파일 경로
    markdown: str                # 변환된 Markdown 본문
    ok: bool = True              # 변환 성공 여부
    error: str | None = None     # 실패 시 사유
    meta: dict = field(default_factory=dict)  # 페이지 수, 표 개수 등 부가정보
    document_model: DocumentModel | None = None  # 구조화 표현(있을 때만)
    error_code: str | None = None  # 실패 유형을 나타내는 안정적인 코드


class BaseConverter(ABC):
    """입력 파일 -> Markdown 변환기 공통 인터페이스."""

    #: 이 변환기가 처리할 수 있는 확장자 (소문자, 점 포함)
    supported_ext: tuple[str, ...] = ()

    @property
    def name(self) -> str:
        return self.__class__.__name__

    def can_handle(self, path: Path) -> bool:
        return path.suffix.lower() in self.supported_ext

    @abstractmethod
    def convert(self, path: Path) -> ConvertResult:
        """단일 파일을 Markdown으로 변환해 결과를 돌려준다."""
        raise NotImplementedError
