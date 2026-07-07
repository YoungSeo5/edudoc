"""Guardrails for protected skill adapter integration."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import core.exporters.hwpx_exporter as hwpx_exporter


ROOT = Path(__file__).resolve().parent.parent
PROTECTED_DIRS = (
    ROOT / "skills" / "hwp",
    ROOT / "skills" / "hwp-skill",
    ROOT / "skills" / "rhwp-edit",
    ROOT / "skills" / "rhwp-advanced",
)


def test_hwpx_adapter_lives_outside_protected_skills() -> None:
    exporter_path = Path(hwpx_exporter.__file__).resolve()
    assert ROOT / "core" / "exporters" in exporter_path.parents
    for protected in PROTECTED_DIRS:
        assert protected.exists(), f"protected skill directory missing: {protected}"
        assert protected not in exporter_path.parents


def test_default_runtime_does_not_call_hidden_skill_setup() -> None:
    runtime_roots = [ROOT / "core", ROOT / "validators", ROOT / "scripts" / "gongmun"]
    forbidden = (
        "_ensure_dependencies",
        "_ensure_hwp2hwpx",
        "git clone",
        "npm ",
        "npx ",
    )
    offenders: list[str] = []
    for runtime_root in runtime_roots:
        for path in runtime_root.rglob("*.py"):
            text = path.read_text(encoding="utf-8", errors="ignore")
            for token in forbidden:
                if token in text:
                    offenders.append(f"{path.relative_to(ROOT)} contains {token!r}")
    assert not offenders, "\n".join(offenders)


if __name__ == "__main__":
    test_hwpx_adapter_lives_outside_protected_skills()
    test_default_runtime_does_not_call_hidden_skill_setup()
    print("PASS: protected skills remain reference-only")
