"""HWPX renderer adapter around the protected hwp-skill `md2hwpx.py`.

edudoc-owned wrapper (compose Phase 1). The hwp-skill packs are read-only reference
sources; this adapter *calls* `skills/hwp-skill/scripts/md2hwpx.py` as a subprocess
and never modifies it. It renders Markdown -> a real structured HWPX (headings and
tables preserved), then validates the package with the skill's `validate.py`.

Dependencies are pip-native (`python-hwpx`, `lxml`) — no heavy external tool. If the
skill is not present, a structured failure is returned instead of crashing.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from .export_base import BaseExporter, ExportResult

# md2hwpx --template choices
_TEMPLATES = ("base", "gonmun", "report", "minutes", "proposal")


class HwpxViaHwpSkillExporter(BaseExporter):
    """Markdown file -> HWPX via the hwp-skill md2hwpx renderer."""

    supported_ext = (".hwpx",)

    def __init__(
        self,
        template: str = "report",
        title: str | None = None,
        custom_header: Path | None = None,
    ) -> None:
        self.template = template if template in _TEMPLATES else "report"
        self.title = title
        # optional patched header.xml (e.g. from an ExtractedStyleProfile); passed
        # straight to md2hwpx --header. The skill template stays untouched.
        self.custom_header = Path(custom_header) if custom_header else None

    def _skill_scripts_dir(self) -> Path | None:
        """Locate a usable hwp-skill scripts dir (skill is read-only reference)."""
        repo_root = Path(__file__).resolve().parents[2]
        for name in ("hwp-skill",):
            scripts = repo_root / "skills" / name / "scripts"
            if (scripts / "md2hwpx.py").exists():
                return scripts
        return None

    def export(self, markdown_path: Path, output_path: Path) -> ExportResult:
        markdown_path = Path(markdown_path)
        output_path = Path(output_path)
        meta = {
            "exporter": self.name,
            "engine": "hwp-skill/md2hwpx",
            "template": self.template,
            "requires_optional_tool": False,
        }

        if not self.can_export(output_path):
            return ExportResult(
                source=markdown_path, output=output_path, ok=False,
                error=f"Unsupported output extension: {output_path.suffix} "
                      f"(supported: {sorted(self.supported_ext)})",
                meta={**meta, "stabilized": False},
            )
        if not markdown_path.exists():
            return ExportResult(
                source=markdown_path, output=output_path, ok=False,
                error=f"Markdown source does not exist: {markdown_path}",
                meta={**meta, "stabilized": False},
            )

        scripts = self._skill_scripts_dir()
        if scripts is None:
            return ExportResult(
                source=markdown_path, output=output_path, ok=False,
                error="hwp-skill md2hwpx.py not found under skills/; HWPX rendering unavailable",
                meta={**meta, "available": False, "stabilized": False},
            )

        output_path.parent.mkdir(parents=True, exist_ok=True)
        cmd = [
            sys.executable, str(scripts / "md2hwpx.py"),
            str(markdown_path), "--output", str(output_path),
            "--template", self.template,
        ]
        if self.title:
            cmd += ["--title", self.title]
        if self.custom_header and self.custom_header.exists():
            cmd += ["--header", str(self.custom_header)]
            meta["custom_header"] = str(self.custom_header)

        try:
            build = subprocess.run(
                cmd, capture_output=True, text=True, encoding="utf-8", errors="replace",
            )
        except Exception as e:  # noqa: BLE001 - structured adapter failure
            return ExportResult(
                source=markdown_path, output=output_path, ok=False,
                error=repr(e), meta={**meta, "stabilized": False},
            )

        if build.returncode != 0 or not output_path.exists():
            detail = (build.stderr or build.stdout or "md2hwpx failed").strip()
            return ExportResult(
                source=markdown_path, output=output_path, ok=False,
                error=detail[:800],
                meta={**meta, "stabilized": False, "returncode": build.returncode},
            )

        validation = self._validate(scripts, output_path)
        ok = validation["passed"]
        return ExportResult(
            source=markdown_path, output=output_path, ok=ok,
            error=None if ok else validation["summary"],
            meta={**meta, "stabilized": ok, "validation": validation},
        )

    def _validate(self, scripts: Path, output_path: Path) -> dict:
        """Run the skill's validate.py; rely on VALID/INVALID text, not exit code."""
        validate_script = scripts / "validate.py"
        if not validate_script.exists():
            return {"passed": True, "summary": "validate.py not found; validation skipped"}
        try:
            r = subprocess.run(
                [sys.executable, str(validate_script), str(output_path)],
                capture_output=True, text=True, encoding="utf-8", errors="replace",
            )
        except Exception as e:  # noqa: BLE001
            return {"passed": False, "summary": repr(e)}
        out = f"{r.stdout or ''}{r.stderr or ''}"
        passed = ("VALID" in out) and ("INVALID" not in out)
        first_line = next((ln for ln in out.splitlines() if ln.strip()), "")
        return {"passed": passed, "summary": first_line.strip()}
