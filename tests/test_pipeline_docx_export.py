"""Pipeline-level DOCX export should use the pip-native DocxExporter."""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from docx import Document

from core.exporters.style_profile import DEFAULT_PUBLIC_DOCUMENT_STYLE_PROFILE
from core.pipeline import Pipeline, PipelineConfig


def test_pipeline_docx_export_uses_pip_native_exporter() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        source = tmp_path / "gongmun.md"
        output_dir = tmp_path / "exports"
        source.write_text(
            "\n".join([
                "# 공문 테스트",
                "",
                "수신: 테스트 학교",
                "담당: 테스트 담당자",
                "",
                "관련: 테스트 계획",
                "",
                "관련 근거에 따라 아래와 같이 안내합니다.",
                "",
                "1. 대상: 테스트 대상",
                "2. 내용: 테스트 내용",
                "",
                "붙임  테스트 문서 1부.  끝.",
                "",
            ]),
            encoding="utf-8",
        )

        pipe = Pipeline(config=PipelineConfig(
            output_dir=output_dir,
            write_files=True,
            export_formats=("docx",),
        ))

        result = pipe.process_file(source)

        assert result.ok, result.error

        markdown_output = output_dir / "gongmun.md"
        docx_output = output_dir / "gongmun.docx"

        assert markdown_output.exists(), "Pipeline Markdown output missing"
        assert docx_output.exists(), "Pipeline DOCX output missing"
        assert docx_output.stat().st_size > 0, "Pipeline DOCX output is empty"

        exports = result.meta.get("exports", [])
        assert len(exports) == 1
        assert exports[0]["format"] == ".docx"
        assert exports[0]["ok"] is True, exports[0].get("error")
        assert exports[0]["exporter"] == "DocxExporter"

        document = Document(str(docx_output))
        visible_text = "\n".join(p.text for p in document.paragraphs)
        for token in ("공문 테스트", "수신: 테스트 학교", "관련: 테스트 계획", "붙임", "끝."):
            assert token in visible_text, f"DOCX visible text missing: {token}"

        # pipeline default path applies the neutral style profile (one stable property)
        assert abs(
            document.sections[0].top_margin.mm
            - DEFAULT_PUBLIC_DOCUMENT_STYLE_PROFILE.page_margin_top_mm
        ) < 0.5


if __name__ == "__main__":
    test_pipeline_docx_export_uses_pip_native_exporter()
    print("PASS: Pipeline DOCX export")
