"""Project-local document export style profiles.

The defaults are conservative Korean public-document oriented values. They are
not an institution-approved official layout, but they give pip-native exporters
a better baseline than raw Markdown-to-Word defaults.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, replace
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
    page_width_mm: float = 210.0
    page_height_mm: float = 297.0
    heading2_font_size_pt: float = 14.0
    heading3_font_size_pt: float = 12.0
    table_font_size_pt: float = 9.5
    table_header_fill: str = "D9EAF7"
    table_cell_margin_twips: int = 90
    body_first_line_indent_mm: float = 0.0
    profile_id: str = "custom"


# Neutral baseline for general documents: exporters that receive no explicit
# profile must fall back to this, never to the Gongmun profile.
DEFAULT_PUBLIC_DOCUMENT_STYLE_PROFILE = DocumentStyleProfile(
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
    profile_id="default_public_document",
)

# Gongmun paths must select this explicitly (profile family "gongmun"); it is
# never an implicit default. Style values share the conservative baseline.
DEFAULT_GONGMUN_STYLE_PROFILE = replace(
    DEFAULT_PUBLIC_DOCUMENT_STYLE_PROFILE, profile_id="default_gongmun"
)


def load_from_toml(path: Path | str) -> DocumentStyleProfile:
    """Read a style profile from TOML using stdlib tomllib.

    Missing keys fall back to ``DEFAULT_GONGMUN_STYLE_PROFILE``.
    """
    import tomllib

    data = tomllib.loads(Path(path).read_text(encoding="utf-8"))
    section = data.get("style", data)
    values = asdict(DEFAULT_GONGMUN_STYLE_PROFILE)
    values.update({k: v for k, v in section.items() if k in values})
    return DocumentStyleProfile(**values)
