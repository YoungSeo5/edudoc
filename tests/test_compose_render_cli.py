"""scripts/compose/render_plan.py: one command renders a plan to multiple formats.

Proves the compose CLI takes an agent-authored plan.json and produces validated
docx/pptx (and hwpx when the skill is present) deliverables in one call.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CLI = ROOT / "scripts" / "compose" / "render_plan.py"

PLAN = {
    "title": "테스트 결과보고서",
    "doc_type": "activity_report",
    "sections": [
        {"no": "Ⅰ", "title": "개요", "blocks": [
            {"marker": "□", "text": "요약"}, {"marker": "○", "text": "세부"},
        ]},
    ],
    "attachments": ["첨부 1부."],
}


def test_render_plan_cli_docx_pptx() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        plan = tmp / "report.plan.json"
        plan.write_text(json.dumps(PLAN, ensure_ascii=False), encoding="utf-8")

        proc = subprocess.run(
            [sys.executable, str(CLI), "--plan", str(plan), "--to", "docx,pptx", "--out", str(tmp)],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        )
        assert proc.returncode == 0, proc.stderr or proc.stdout
        summary = json.loads(proc.stdout)

        assert summary["validation_problems"] == []
        by_fmt = {o["format"]: o for o in summary["outputs"]}
        assert by_fmt["docx"]["ok"] is True
        assert by_fmt["pptx"]["ok"] is True
        assert (tmp / "report.docx").exists()
        assert (tmp / "report.pptx").exists()
        assert (tmp / "report.md").exists()


def test_render_plan_cli_rejects_unknown_format() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        plan = tmp / "r.plan.json"
        plan.write_text(json.dumps(PLAN, ensure_ascii=False), encoding="utf-8")
        proc = subprocess.run(
            [sys.executable, str(CLI), "--plan", str(plan), "--to", "xlsx"],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        )
        assert proc.returncode != 0
        assert "unknown format" in (proc.stderr + proc.stdout)


if __name__ == "__main__":
    test_render_plan_cli_docx_pptx()
    test_render_plan_cli_rejects_unknown_format()
    print("PASS: compose render CLI (multi-format)")
