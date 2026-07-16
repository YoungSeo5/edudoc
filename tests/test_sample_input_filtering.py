"""Directory runs should skip repository control files and generated artifacts."""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.input_filter import is_processable_input
from core.pipeline import Pipeline, PipelineConfig


def test_is_processable_input_skips_control_and_generated_files() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        generated_hwpx = root / "generated.hwpx"
        generated_hwpx.write_bytes(b"not a real hwpx")
        (root / "generated.validation.txt").write_text("report", encoding="utf-8")

        skipped = [
            root / "README.md",
            root / "README.txt",
            root / "AGENTS.md",
            root / "AGENT.md",
            root / "CLAUDE.md",
            root / ".gitkeep",
            root / "sample.validation.txt",
            root / "sample.document.validation.txt",
            root / "sample.document.json",
            root / "sample.docx",
            root / "sample.pdf",
            root / "sample.pptx",
            generated_hwpx,
        ]
        for path in skipped:
            if not path.exists():
                path.write_text("skip", encoding="utf-8")
            assert not is_processable_input(path), f"should skip {path.name}"

        assert is_processable_input(root / "actual_sample.md")
        assert is_processable_input(root / "actual_sample.hwp")
        assert is_processable_input(root / "actual_sample.hwpx")


def test_directory_run_skips_sample_control_files_and_writes_only_to_output_dir() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        samples = root / "samples"
        out = root / "exports"
        samples.mkdir()

        (samples / "actual_sample.md").write_text("# 실제 샘플\n\n본문입니다. 끝.\n", encoding="utf-8")
        (samples / "README.md").write_text("# 안내\n", encoding="utf-8")
        (samples / "AGENTS.md").write_text("# 규칙\n", encoding="utf-8")
        (samples / ".gitkeep").write_text("", encoding="utf-8")
        (samples / "actual_sample.validation.txt").write_text("old", encoding="utf-8")
        (samples / "actual_sample.docx").write_bytes(b"old")

        pipe = Pipeline(config=PipelineConfig(
            output_dir=out,
            write_files=True,
            export_formats=("docx",),
        ))

        results = pipe.process_dir(samples)

        assert [r.source.name for r in results] == ["actual_sample.md"]
        assert (out / "actual_sample.md").exists()
        assert (out / "actual_sample.docx").exists()
        assert not (out / "actual_sample.validation.txt").exists()

        assert not (out / "README.md").exists()
        assert not (out / "README.docx").exists()
        assert not (out / "AGENTS.md").exists()
        assert not (out / "AGENTS.docx").exists()

        assert not (samples / "README.docx").exists()
        assert not (samples / "AGENTS.docx").exists()
        assert not (samples / "actual_sample.pdf").exists()


if __name__ == "__main__":
    test_is_processable_input_skips_control_and_generated_files()
    test_directory_run_skips_sample_control_files_and_writes_only_to_output_dir()
    print("PASS: sample input filtering")
