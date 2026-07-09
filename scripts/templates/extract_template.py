#!/usr/bin/env python3
"""Extract an honest template candidate from a reference document.

Deterministic and honest: parsed style comes only from HWPX (extract_style).
For a legacy .hwp / PDF the style stays unknown/low; whatever the reference text
deterministically states is recorded as evidence, never as a parsed style value.

Emits three artifacts to the output dir:
    template.candidate.json   the candidate (style/structure/evidence/unknown_fields)
    template.evidence.md      what was extracted vs left unknown, and why
    template.skeleton.md      a structure-only one-page report skeleton (확인 필요 slots)

Usage:
    python scripts/templates/extract_template.py \
        --reference "references/document-types/public-plan/대통령비서실 ....hwp" \
        --institution 대통령비서실 --document-type 한장보고서 \
        --out-dir exports/template-candidates/presidential-one-page-report
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.templates.one_page_report import build_candidate_from_reference, build_skeleton  # noqa: E402


def _evidence_md(candidate: dict) -> str:
    sp = candidate["style_profile"]
    lines = [
        f"# {candidate['institution']} / {candidate['document_type']} — 추출 근거",
        "",
        f"- 참조 파일: `{candidate['reference_path']}`",
        f"- 형식: `{candidate['reference_format']}`",
        f"- 스타일 추출 지원: **{candidate['style_extraction_supported']}**",
        f"- 종합 신뢰도: **{candidate['confidence']}**",
        "",
        "## 스타일 (parsed style_profile)",
        f"- source: `{sp['source']}` / confidence: `{sp['confidence']}`",
        f"- font_family: `{sp['font_family']}`",
        f"- body_font_size_pt: `{sp['body_font_size_pt']}`",
        f"- line_spacing: `{sp['line_spacing']}`",
        f"- page_margins_mm: `{sp['page_margins_mm']}`",
        f"- reason: {sp['reason']}",
        "",
        "## 구조 (deterministic)",
        f"- marker_system: `{candidate['structure'].get('marker_system')}`",
        f"- table_mentions: `{candidate['structure'].get('table_mentions')}`",
        f"- paragraph_count: `{candidate['structure'].get('paragraph_count')}`",
        "",
        "## 문서 텍스트가 언급한 서식 (parsed style 아님 — 사람 확인용)",
    ]
    mentions = candidate.get("style_text_mentions") or []
    if mentions:
        lines += [f"- {m}" for m in mentions]
        lines.append("")
        lines.append(
            "> 위 항목은 참조 문서의 **본문 텍스트가 스스로 서술한 서식**이며, "
            "스타일 레코드에서 파싱한 값이 아님. style_profile로 승격 금지."
        )
    else:
        lines.append("- (없음)")
    lines += ["", "## 근거 로그", *[f"- {e}" for e in candidate["evidence"]]]
    lines += ["", "## 미확정 필드", *[f"- `{u}`" for u in candidate["unknown_fields"]]]
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--reference", required=True, type=Path)
    parser.add_argument("--institution", required=True)
    parser.add_argument("--document-type", required=True)
    parser.add_argument("--out-dir", required=True, type=Path)
    args = parser.parse_args(argv)

    if not args.reference.is_file():
        raise SystemExit(f"ERROR: 참조 파일 없음: {args.reference}")

    candidate = build_candidate_from_reference(
        args.reference, institution=args.institution, document_type=args.document_type
    )

    args.out_dir.mkdir(parents=True, exist_ok=True)
    (args.out_dir / "template.candidate.json").write_text(
        json.dumps(candidate, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (args.out_dir / "template.evidence.md").write_text(_evidence_md(candidate), encoding="utf-8")
    (args.out_dir / "template.skeleton.md").write_text(build_skeleton(candidate), encoding="utf-8")

    print(f"candidate: {args.out_dir}/template.candidate.json")
    print(f"  format={candidate['reference_format']} "
          f"style_supported={candidate['style_extraction_supported']} "
          f"confidence={candidate['confidence']}")
    print(f"  marker_system={candidate['structure'].get('marker_system')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
