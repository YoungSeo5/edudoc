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

# 이 CLI의 경계:
# 참조 문서 → 일반 구조·스타일 후보 → 품질 검사 산출물
# HWPX의 raw/template XML 분리나 {{placeholder}} 생성은 수행하지 않는다.

def main(argv: list[str] | None = None) -> int:
    # 흐름 1: 참조 문서와 기관/문서 유형, 품질 규칙, 명시적 승인 여부를 받는다.
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

    # 흐름 2: 규칙 우선순위는 명시한 파일 → 출력 폴더에 축적된 로컬 규칙
    # → 프로젝트 공통 기본 규칙이다.
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

    # 흐름 3: core.templates.pipeline이 추출 → lint → 오탐 규칙 적용 →
    # 반복 보정 → 최종 성공 게이트를 수행한다.
    candidate, gate = run_template_pipeline(
        args.reference,
        institution=args.institution,
        document_type=args.document_type,
        route=args.route,
        success_rules=success_rules,
        false_positive_rules=false_positive_rules,
    )

    # 흐름 4: 품질 결과를 파일로 기록한다. --approve가 있어도 게이트를
    # 통과한 경우에만 registry가 읽을 template.json이 생성된다.
    paths = write_pipeline_artifacts(
        candidate,
        gate,
        args.out_dir,
        approve=args.approve,
        success_rules=success_rules,
        false_positive_rules=false_positive_rules,
    )

    # 흐름 5: 실제 출력 템플릿이 아니라, 후보 구조를 사람이 읽을 수 있는
    # Markdown 골격으로 함께 제공한다.
    skeleton_path = args.out_dir / "template.skeleton.md"
    skeleton_path.write_text(build_skeleton(candidate), encoding="utf-8")
    paths["skeleton"] = skeleton_path

    print(f"status={candidate.status} gate_passed={gate.passed}")
    for name, path in paths.items():
        print(f"{name}: {path}")
    return 0 if gate.passed else 2


if __name__ == "__main__":
    raise SystemExit(main())
