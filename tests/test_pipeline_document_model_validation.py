"""Loop 8.96: DocumentModel integrity validation is wired into the pipeline.

Proves that when a converter provides a DocumentModel (HWPX path), the pipeline
runs `validators.document_model_rules` without dispatching a document-type
writing validator.
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.pipeline import Pipeline, PipelineConfig


def test_pipeline_runs_document_model_validation() -> None:
    root = Path(__file__).resolve().parent.parent
    sample = root / "samples" / "참가신청서 및 사업계획서 양식_기창 (1).hwpx"
    assert sample.exists(), f"HWPX sample not found: {sample}"

    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "exports"
        pipe = Pipeline(config=PipelineConfig(
            output_dir=out,
            write_files=True,
            write_validation_report=True,
        ))

        result = pipe.process_file(sample)
        assert result.ok, result.error

        # DocumentModel integrity validation ran and is structured
        dmv = result.meta.get("document_model_validation")
        assert dmv is not None, "document_model_validation missing from meta"
        assert dmv["available"] is True, dmv
        assert isinstance(dmv["passed"], bool)
        assert isinstance(dmv["summary"], str) and dmv["summary"].strip()

        # existing outputs preserved
        assert (out / f"{sample.stem}.md").exists(), "Markdown output missing"
        assert (out / f"{sample.stem}.document.json").exists(), "DocumentModel JSON missing"
        assert not (out / f"{sample.stem}.validation.txt").exists()

        # new, separate DocumentModel validation report
        assert (out / f"{sample.stem}.document.validation.txt").exists(), (
            "DocumentModel validation report missing"
        )


def test_pipeline_marks_document_model_validation_unavailable_for_markdown() -> None:
    # A plain Markdown input has no DocumentModel; the pipeline should say so.
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        src = tmp_path / "draft.md"
        src.write_text("# 제목\n\n본문. 끝.\n", encoding="utf-8")
        pipe = Pipeline(config=PipelineConfig(output_dir=tmp_path / "exports"))

        result = pipe.process_file(src)
        assert result.ok, result.error

        dmv = result.meta.get("document_model_validation")
        assert dmv is not None
        assert dmv["available"] is False
        assert "reason" in dmv


if __name__ == "__main__":
    test_pipeline_runs_document_model_validation()
    test_pipeline_marks_document_model_validation_unavailable_for_markdown()
    print("PASS: pipeline DocumentModel validation wiring")
