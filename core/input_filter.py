"""Input filtering helpers for directory pipeline runs."""
from __future__ import annotations

from pathlib import Path


CONTROL_BASENAMES = {
    ".gitkeep",
    "agent.md",
    "agents.md",
    "claude.md",
    "readme.md",
    "readme.txt",
}

GENERATED_OUTPUT_EXTS = {
    ".docx",
    ".pdf",
    ".pptx",
}


def input_filter_reason(path: Path | str) -> str | None:
    """Return the reason a bulk input file should be skipped, if any."""
    p = Path(path)
    name = p.name.lower()

    if name in CONTROL_BASENAMES:
        return "repository_control_file"
    if name.endswith(".document.validation.txt"):
        return "generated_document_validation_report"
    if name.endswith(".validation.txt"):
        return "generated_validation_report"
    if name.endswith(".document.json"):
        return "generated_document_model"
    if p.suffix.lower() in GENERATED_OUTPUT_EXTS:
        return "generated_office_output"
    if _looks_like_generated_hwpx(p):
        return "generated_hwpx_artifact"
    return None


def is_processable_input(path: Path | str) -> bool:
    """Return whether a file should be processed during a directory run.

    Explicit single-file runs may still process ordinary Markdown files. This
    helper is for bulk directory scans, where repository/control files and
    generated artifacts should not be converted again.
    """
    return input_filter_reason(path) is None


def _looks_like_generated_hwpx(path: Path) -> bool:
    """Best-effort guard for generated HWPX outputs left beside inputs."""
    if path.suffix.lower() != ".hwpx":
        return False
    stem = path.with_suffix("")
    generated_companions = (
        stem.with_suffix(".validation.txt"),
        stem.with_suffix(".document.validation.txt"),
        stem.with_suffix(".document.json"),
        stem.with_suffix(".docx"),
        stem.with_suffix(".pdf"),
        stem.with_suffix(".pptx"),
    )
    return any(companion.exists() for companion in generated_companions)
