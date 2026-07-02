"""
문서 출력 스타일 프로파일 (Loop 8.5).

공문(Gongmun) DOCX 출력에 적용할 **보수적이고 결정론적인** 프로젝트 로컬
기본 서식 값이다. 나중에 PDF/HWPX exporter가 같은 프로파일을 재사용할 수 있도록
exporter와 분리해 둔다.

주의:
- 이 값들은 참조 문서를 보고 정한 **프로젝트 기본값**이며,
  기관 공식 서식 표준을 그대로 재현했다고 보장하지 않는다.
- 참조 PDF는 파싱하지 않는다. 값은 사람이 정한 상수다.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class DocumentStyleProfile:
    page_margin_top_mm: float
    page_margin_bottom_mm: float
    page_margin_left_mm: float
    page_margin_right_mm: float
    font_family: str
    font_size_pt: float
    heading_font_size_pt: float
    line_spacing: float
    paragraph_space_after_pt: float
    heading_alignment: str  # "left" | "center" | "right" | "justify"


# 공문 기본 프로파일 (보수적, 한글 렌더 가능한 폰트 사용).
DEFAULT_GONGMUN_STYLE_PROFILE = DocumentStyleProfile(
    page_margin_top_mm=30.0,
    page_margin_bottom_mm=20.0,
    page_margin_left_mm=20.0,
    page_margin_right_mm=20.0,
    font_family="Malgun Gothic",
    font_size_pt=11.0,
    heading_font_size_pt=16.0,
    line_spacing=1.15,
    paragraph_space_after_pt=6.0,
    heading_alignment="center",
)


def load_from_toml(path: Path | str) -> DocumentStyleProfile:
    """TOML 파일에서 프로파일을 읽는다(표준 라이브러리 tomllib, 새 의존성 없음).

    누락된 키는 기본 프로파일 값으로 채운다. `[style]` 테이블 또는 최상위 키를 받는다.
    """
    import tomllib

    data = tomllib.loads(Path(path).read_text(encoding="utf-8"))
    section = data.get("style", data)
    values = asdict(DEFAULT_GONGMUN_STYLE_PROFILE)
    values.update({k: v for k, v in section.items() if k in values})
    return DocumentStyleProfile(**values)
