#!/usr/bin/env python3
"""Extract, review, refine, and optionally approve an institution template."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.generators.one_page_report_generator import build_skeleton  # noqa: E402
from core.templates.pipeline import run_template_pipeline  # noqa: E402
from core.templates.quality.false_positive import load_false_positive_rules  # noqa: E402
from core.templates.quality.success_rules import load_success_rules  # noqa: E402
from core.templates.serialization import write_pipeline_artifacts  # noqa: E402

DEFAULT_SUCCESS_RULES = ROOT / "templates" / "quality" / "success-rules.json"
DEFAULT_FALSE_POSITIVE_RULES = (
    ROOT / "templates" / "quality" / "false-positive-rules.json"
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference", required=True, type=Path)
    parser.add_argument("--institution", required=True)
    parser.add_argument("--document-type", required=True)
    parser.add_argument("--out-dir", required=True, type=Path)
    parser.add_argument("--route")
    parser.add_argument("--success-rules", type=Path)
    parser.add_argument(
        "--false-positive-rules",
        action="append",
        type=Path,
        default=[],
    )
    parser.add_argument(
        "--approve",
        action="store_true",
        help="Write template.json only when the automatic success gate passes.",
    )
    args = parser.parse_args(argv)

    if not args.reference.is_file():
        raise SystemExit(f"ERROR: 참조 파일 없음: {args.reference}")

    local_success_rules = args.out_dir / "success-rules.json"
    success_rules_path = (
        args.success_rules
        or (local_success_rules if local_success_rules.is_file() else DEFAULT_SUCCESS_RULES)
    )
    local_false_positive_rules = args.out_dir / "false-positive-rules.json"
    fp_paths = [
        DEFAULT_FALSE_POSITIVE_RULES,
        local_false_positive_rules,
        *args.false_positive_rules,
    ]
    success_rules = load_success_rules(success_rules_path)
    false_positive_rules = load_false_positive_rules(fp_paths)
    candidate, gate = run_template_pipeline(
        args.reference,
        institution=args.institution,
        document_type=args.document_type,
        route=args.route,
        success_rules=success_rules,
        false_positive_rules=false_positive_rules,
    )
    paths = write_pipeline_artifacts(
        candidate,
        gate,
        args.out_dir,
        approve=args.approve,
        success_rules=success_rules,
        false_positive_rules=false_positive_rules,
    )
    skeleton_path = args.out_dir / "template.skeleton.md"
    skeleton_path.write_text(build_skeleton(candidate), encoding="utf-8")
    paths["skeleton"] = skeleton_path

    print(f"status={candidate.status} gate_passed={gate.passed}")
    for name, path in paths.items():
        print(f"{name}: {path}")
    return 0 if gate.passed else 2


if __name__ == "__main__":
    raise SystemExit(main())
