"""Adapters from edudoc document plans to protected hwp-skill renderers.

The protected skill files under ``skills/hwp-skill`` are treated as read-only
reference/runtime tools. This module only creates small input contracts and
invokes those scripts as subprocesses.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

from core.document_plan import DocumentPlan, UNKNOWN


@dataclass(frozen=True)
class HwpSkillRenderResult:
    """Structured result returned by hwp-skill render adapters."""

    source_profile_id: str
    output: Path
    ok: bool
    error: str | None = None
    meta: dict = field(default_factory=dict)


class HwpSkillRenderer:
    """Render selected DocumentPlan types through protected hwp-skill scripts."""

    def __init__(self, repo_root: Path | str = ".") -> None:
        self.repo_root = Path(repo_root)
        self.skill_scripts_dir = self.repo_root / "skills" / "hwp-skill" / "scripts"

    def render_public_plan(
        self,
        plan: DocumentPlan,
        output_path: Path | str,
        *,
        contract_path: Path | str | None = None,
        include_title_page: bool = True,
        include_table_of_contents: bool = True,
    ) -> HwpSkillRenderResult:
        """Render a public-institution plan HWPX through ``gyehoek.py``."""
        output = Path(output_path)
        meta = {
            "renderer": "HwpSkillRenderer",
            "engine": "hwp-skill/gyehoek.py",
            "target_profile_id": plan.target_profile_id,
            "requires_optional_tool": False,
            "protected_skill": True,
        }

        if plan.target_profile_id != "public_institution_plan":
            return HwpSkillRenderResult(
                source_profile_id=plan.target_profile_id,
                output=output,
                ok=False,
                error=(
                    "render_public_plan requires target_profile_id "
                    "'public_institution_plan'"
                ),
                meta=meta,
            )

        script = self.skill_scripts_dir / "gyehoek.py"
        if not script.exists():
            return HwpSkillRenderResult(
                source_profile_id=plan.target_profile_id,
                output=output,
                ok=False,
                error=f"hwp-skill gyehoek.py not found: {script}",
                meta={**meta, "available": False},
            )

        contract = self._public_plan_contract(
            plan,
            include_title_page=include_title_page,
            include_table_of_contents=include_table_of_contents,
        )
        if contract_path is not None:
            path = Path(contract_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(
                json.dumps(contract, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            meta["contract_path"] = str(path)

        output.parent.mkdir(parents=True, exist_ok=True)
        cmd = [sys.executable, str(script), "--output", str(output)]
        if contract["include_title_page"]:
            cmd.extend(["--title", contract["title"]])
        else:
            cmd.append("--no-title")
        cmd.append("--toc" if contract["include_table_of_contents"] else "--no-toc")
        if contract.get("date"):
            cmd.extend(["--date", contract["date"]])

        try:
            completed = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
        except Exception as exc:  # noqa: BLE001 - return structured adapter errors.
            return HwpSkillRenderResult(
                source_profile_id=plan.target_profile_id,
                output=output,
                ok=False,
                error=repr(exc),
                meta={**meta, "contract": contract},
            )

        if completed.returncode != 0 or not output.exists():
            detail = (completed.stderr or completed.stdout or "gyehoek.py failed").strip()
            return HwpSkillRenderResult(
                source_profile_id=plan.target_profile_id,
                output=output,
                ok=False,
                error=detail[:800],
                meta={
                    **meta,
                    "contract": contract,
                    "returncode": completed.returncode,
                },
            )

        validation = self._validate(output)
        return HwpSkillRenderResult(
            source_profile_id=plan.target_profile_id,
            output=output,
            ok=validation["passed"] is not False,
            error=None if validation["passed"] is not False else validation["summary"],
            meta={
                **meta,
                "contract": contract,
                "returncode": completed.returncode,
                "validation": validation,
                "stdout": completed.stdout,
                "stderr": completed.stderr,
            },
        )

    def _public_plan_contract(
        self,
        plan: DocumentPlan,
        *,
        include_title_page: bool,
        include_table_of_contents: bool,
    ) -> dict:
        title = plan.title.strip() if plan.title and not _is_unknown(plan.title) else ""
        date = _date_candidate(plan)
        return {
            "target_profile_id": plan.target_profile_id,
            "renderer": "hwp-skill/gyehoek.py",
            "title": title or "public plan",
            "date": date,
            "include_title_page": include_title_page,
            "include_table_of_contents": include_table_of_contents,
            "source_document_count": plan.source_document_count,
            "reference_sample_paths": list(plan.reference_sample_paths),
            "missing_required_fields": list(plan.missing_required_fields),
        }

    def _validate(self, output_path: Path) -> dict:
        validate_script = self.skill_scripts_dir / "validate.py"
        if not validate_script.exists():
            return {"passed": None, "summary": "validate.py not found; validation skipped"}
        try:
            result = subprocess.run(
                [sys.executable, str(validate_script), str(output_path)],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
        except Exception as exc:  # noqa: BLE001
            return {"passed": False, "summary": repr(exc)}

        output = f"{result.stdout or ''}{result.stderr or ''}"
        passed = ("VALID" in output) and ("INVALID" not in output)
        first_line = next((line for line in output.splitlines() if line.strip()), "")
        return {
            "passed": passed,
            "summary": first_line.strip(),
            "returncode": result.returncode,
        }


def _date_candidate(plan: DocumentPlan) -> str | None:
    for section in plan.sections:
        for item in section.content:
            match = re.search(r"(\d{4})\.\s*(\d{1,2})\.", item)
            if match:
                year, month = match.groups()
                return f"{year}. {int(month)}."
    return None


def _is_unknown(value: str) -> bool:
    cleaned = value.strip()
    return not cleaned or cleaned == UNKNOWN or "확인 필요" in cleaned
