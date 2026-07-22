"""Pandoc-backed exporter for Office-style deliverables."""
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from .export_base import BaseExporter, ExportResult


class OfficeExporter(BaseExporter):
    """Export Markdown to DOCX, PDF, PPTX, HTML, LaTeX, or EPUB via Pandoc."""

    supported_ext = (".docx", ".pdf", ".pptx", ".html", ".tex", ".epub")

    def __init__(self, pandoc_path: str | None = None) -> None:
        self.pandoc_path = pandoc_path or self._resolve_pandoc_path()

    def _resolve_pandoc_path(self) -> str:
        """Prefer a project-local Pandoc binary, then fall back to PATH."""
        repo_root = Path(__file__).resolve().parents[2]
        candidates = [
            repo_root / "tools" / "pandoc" / "pandoc.exe",
            repo_root / "tools" / "pandoc.exe",
            repo_root / "tools" / "pandoc" / "pandoc",
        ]
        for candidate in candidates:
            if candidate.exists():
                return str(candidate)
        return "pandoc"

    def _pandoc_available(self) -> bool:
        pandoc = Path(self.pandoc_path)
        if pandoc.parent != Path("."):
            return pandoc.exists()
        return shutil.which(self.pandoc_path) is not None

    def _resolve_typst_path(self) -> str | None:
        """Prefer a project-local Typst binary, used as Pandoc's PDF engine.

        Typst is a lightweight, self-contained PDF engine (no LaTeX/VC++ needed).
        Returns a filesystem path or a PATH name, or None when unavailable.
        """
        repo_root = Path(__file__).resolve().parents[2]
        candidates = [
            repo_root / "tools" / "typst" / "typst.exe",
            repo_root / "tools" / "typst.exe",
            repo_root / "tools" / "typst" / "typst",
        ]
        for candidate in candidates:
            if candidate.exists():
                return candidate.as_posix()
        if shutil.which("typst"):
            return "typst"
        return None

    def export(
        self,
        markdown_path: Path,
        output_path: Path,
        *,
        reference_doc: Path | None = None,
        extra_args: list[str] | None = None,
    ) -> ExportResult:
        markdown_path = Path(markdown_path)
        output_path = Path(output_path)

        if not self.can_export(output_path):
            return ExportResult(
                source=markdown_path,
                output=output_path,
                ok=False,
                error=(
                    f"Unsupported output extension: {output_path.suffix} "
                    f"(supported: {sorted(self.supported_ext)})"
                ),
                meta={"exporter": self.name, "requires_optional_tool": True},
                error_code="export_unsupported_extension",
            )

        if not markdown_path.exists():
            return ExportResult(
                source=markdown_path,
                output=output_path,
                ok=False,
                error=f"Markdown source does not exist: {markdown_path}",
                meta={"exporter": self.name, "requires_optional_tool": True},
                error_code="export_source_missing",
            )

        if not self._pandoc_available():
            return ExportResult(
                source=markdown_path,
                output=output_path,
                ok=False,
                error=(
                    "Pandoc executable was not found. "
                    "Place pandoc.exe under tools/pandoc/ or pass pandoc_path."
                ),
                meta={
                    "exporter": self.name,
                    "pandoc": self.pandoc_path,
                    "requires_optional_tool": True,
                },
                error_code="export_dependency_unavailable",
            )

        output_path.parent.mkdir(parents=True, exist_ok=True)

        cmd = [self.pandoc_path, str(markdown_path), "-o", str(output_path)]
        if reference_doc is not None:
            cmd.extend(["--reference-doc", str(reference_doc)])
        # PDF: use the bundled Typst engine (avoids a LaTeX/pdflatex dependency).
        engine_given = bool(extra_args) and any(
            a.startswith("--pdf-engine") for a in extra_args
        )
        if output_path.suffix.lower() == ".pdf" and not engine_given:
            typst = self._resolve_typst_path()
            if typst is not None:
                cmd.append(f"--pdf-engine={typst}")
        if extra_args:
            cmd.extend(extra_args)

        try:
            completed = subprocess.run(
                cmd,
                check=True,
                capture_output=True,
                text=True,
            )
            return ExportResult(
                source=markdown_path,
                output=output_path,
                ok=True,
                meta={
                    "exporter": self.name,
                    "pandoc": self.pandoc_path,
                    "requires_optional_tool": True,
                    "stdout": completed.stdout,
                    "stderr": completed.stderr,
                },
            )
        except subprocess.CalledProcessError as e:
            return ExportResult(
                source=markdown_path,
                output=output_path,
                ok=False,
                error=e.stderr.strip() or e.stdout.strip() or repr(e),
                meta={
                    "exporter": self.name,
                    "pandoc": self.pandoc_path,
                    "requires_optional_tool": True,
                    "returncode": e.returncode,
                },
                error_code="export_subprocess_failed",
            )
