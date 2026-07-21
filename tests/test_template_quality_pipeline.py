"""Template lint, false-positive memory, refinement, gate, and approval tests."""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path
from zipfile import ZipFile

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.templates.models import (
    ExtractedStyleProfile,
    TemplateCandidate,
    TemplateIdentity,
)
from core.templates.pipeline import run_template_pipeline
from core.templates.quality.false_positive import FalsePositiveRule
from core.templates.quality.lint import lint_candidate
from core.templates.quality.refine import refine_candidate
from core.templates.quality.success_rules import SuccessRules
from core.templates.registry import TemplateRegistry
from core.templates.serialization import write_pipeline_artifacts


def test_registry_defaults_to_institution_template_directory() -> None:
    # Given: the registry is created without a custom root.
    # When: its configured root is inspected.
    registry = TemplateRegistry()

    # Then: it targets the canonical institution-template directory.
    assert registry.root == Path("templates/institutions")


def _reference(path: Path) -> Path:
    section = (
        '<?xml version="1.0"?>'
        '<hs:sec xmlns:hp="x" xmlns:hs="y">'
        '<hp:p charPrIDRef="0"><hp:run><hp:t>1. 추진 배경</hp:t></hp:run></hp:p>'
        '<hp:p charPrIDRef="0"><hp:run><hp:t>2026년 예산 10,000원</hp:t></hp:run></hp:p>'
        '<hp:margin top="5669" bottom="5669" left="5669" right="5669"/>'
        "</hs:sec>"
    )
    header = (
        '<?xml version="1.0"?>'
        '<hh:head xmlns:hh="h">'
        '<hh:fontface lang="HANGUL"><hh:font id="1" face="테스트 글꼴"/></hh:fontface>'
        '<hh:charPr id="0" height="1100"><hh:fontRef hangul="1"/></hh:charPr>'
        '<hh:paraPr id="0"><hh:lineSpacing type="PERCENT" value="160"/></hh:paraPr>'
        "</hh:head>"
    )
    with ZipFile(path, "w") as package:
        package.writestr("Contents/header.xml", header)
        package.writestr("Contents/section0.xml", section)
    return path


def test_false_positive_memory_is_applied_before_gate() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        reference = _reference(Path(tmp) / "reference.hwpx")
        rule = FalsePositiveRule(
            rule_id="FP-TEST-BUDGET",
            target="structure.line_candidates",
            pattern=r"예산",
            reason="예시 예산값은 구조 후보가 아닙니다.",
        )
        candidate, gate = run_template_pipeline(
            reference,
            institution="테스트기관",
            document_type="계획서",
            false_positive_rules=[rule],
        )
        assert gate.passed
        assert "2026년 예산 10,000원" not in candidate.structure["line_candidates"]
        assert any(item.rule_id == "FP-TEST-BUDGET" for item in candidate.diagnostics)


def test_gate_writes_validated_and_requires_explicit_approval_for_template() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        reference = _reference(root / "reference.hwpx")
        candidate, gate = run_template_pipeline(
            reference,
            institution="테스트기관",
            document_type="계획서",
        )
        output = root / "output"
        paths = write_pipeline_artifacts(candidate, gate, output)
        assert "validated" in paths
        assert not (output / "template.json").exists()
        assert (output / "success-rules.json").is_file()
        assert (output / "false-positive-rules.json").is_file()
        assert TemplateRegistry(root).find("테스트기관", "계획서") is None

        registry_output = root / "테스트기관" / "계획서"
        approved = write_pipeline_artifacts(candidate, gate, registry_output, approve=True)
        assert json.loads(approved["template"].read_text(encoding="utf-8"))["status"] == "approved"
        loaded = TemplateRegistry(root).find("테스트기관", "계획서")
        assert loaded is not None and loaded.status == "approved"


def test_lint_refinement_removes_unproven_style() -> None:
    candidate = TemplateCandidate(
        identity=TemplateIdentity("테스트기관", "보고서"),
        reference_path="reference.pdf",
        reference_format="pdf",
        structure={"marker_system": ["1."], "line_candidates": ["1. 개요"]},
        style_profile=ExtractedStyleProfile(
            source="unknown",
            font_family="근거 없는 글꼴",
            confidence="low",
        ),
        evidence=["reference_path: reference.pdf"],
    )
    diagnostics = lint_candidate(candidate, SuccessRules())
    assert any(item.rule_id == "STYLE001" for item in diagnostics)
    assert refine_candidate(candidate, diagnostics)
    assert candidate.style_profile.font_family is None


if __name__ == "__main__":
    test_false_positive_memory_is_applied_before_gate()
    test_gate_writes_validated_and_requires_explicit_approval_for_template()
    test_lint_refinement_removes_unproven_style()
    print("PASS: template quality pipeline")
