"""PptxExporter: Markdown -> PPTX (pip-native python-pptx).

Verifies a report Markdown becomes a valid multi-slide .pptx with a title slide,
one slide per section, bullet text, a table slide, and Korean text preserved.
"""
from __future__ import annotations

import re
import sys
import tempfile
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.exporters.pptx_exporter import PptxExporter

SAMPLE_MD = """\
# 2026학년도 1학기 활동 결과보고서

작성자: 오영서

| 구분 | 활동명 |
| --- | --- |
| 학습 | 스터디걸즈 |
| 창업 | 에어컨트롤 |

## Ⅰ. 개요

□ 두 활동을 종합 보고함

  ○ 학습공동체 참여

  ○ 창업과제 수행

## Ⅱ. 향후 계획

□ 최종 활동보고서 제출
"""


def _slide_texts(pptx_path: Path) -> str:
    with zipfile.ZipFile(pptx_path) as z:
        slides = [n for n in z.namelist() if re.match(r"ppt/slides/slide\d+\.xml$", n)]
        text = "".join(z.read(s).decode("utf-8") for s in slides)
    return text, len(slides)


def test_pptx_export_builds_valid_deck() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        md = tmp / "report.md"
        out = tmp / "report.pptx"
        md.write_text(SAMPLE_MD, encoding="utf-8")

        result = PptxExporter().export(md, out)
        assert result.ok, result.error
        assert out.exists() and out.stat().st_size > 0
        assert out.read_bytes()[:2] == b"PK", "not a valid pptx (zip)"
        assert result.meta["stabilized"] is True

        text, n_slides = _slide_texts(out)
        # title slide + 2 section slides + 1 table slide
        assert n_slides >= 4, f"expected >=4 slides, got {n_slides}"
        for token in ("활동 결과보고서", "개요", "향후 계획", "스터디걸즈", "에어컨트롤"):
            assert token in text, f"missing slide text: {token}"


def test_pptx_rejects_wrong_extension() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        md = tmp / "r.md"
        md.write_text("# t\n", encoding="utf-8")
        result = PptxExporter().export(md, tmp / "r.docx")
        assert not result.ok
        assert "Unsupported output extension" in result.error


if __name__ == "__main__":
    test_pptx_export_builds_valid_deck()
    test_pptx_rejects_wrong_extension()
    print("PASS: PptxExporter (valid multi-slide deck + Korean preserved)")
