#!/usr/bin/env python3
"""Render an agent-authored ComposedReport plan to final deliverables.

This is the user/agent-facing CLI for the compose flow. The writing step
(sources -> a good plan.json) is done by the agent in-session (no LLM API is
called here); this command takes that plan.json and deterministically renders it
to the requested formats, validating each output.

Usage:
    python scripts/compose/render_plan.py --plan report.plan.json --to docx,hwpx,pptx
    python scripts/compose/render_plan.py --plan report.plan.json --to pptx --out exports/compose

Formats:
    docx  -> pip-native DocxExporter (stabilized)
    pptx  -> pip-native PptxExporter (stabilized)
    hwpx  -> hwp-skill md2hwpx adapter (validated)
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.adapters.hwpx_template_renderer import load_content_fields  # noqa: E402
from core.compose.render import (  # noqa: E402
    load_plan,
    render_report_to_docx,
    render_report_to_hwpx,
    render_report_to_pptx,
)

_RENDERERS = {
    "docx": render_report_to_docx,
    "hwpx": render_report_to_hwpx,
    "pptx": render_report_to_pptx,
}


def _parse_formats(value: str) -> list[str]:
    formats = [f.strip().lower().lstrip(".") for f in value.split(",") if f.strip()]
    unknown = [f for f in formats if f not in _RENDERERS]
    if unknown:
        raise SystemExit(f"ERROR: unknown format(s) {unknown}; supported: {sorted(_RENDERERS)}")
    return formats


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--plan", required=True, type=Path, help="에이전트가 작성한 plan.json")
    parser.add_argument("--to", default="docx", help="쉼표로 구분한 출력 형식 (docx,hwpx,pptx)")
    parser.add_argument("--out", type=Path, help="출력 디렉터리 (기본: plan 파일과 같은 폴더)")
    parser.add_argument("--stem", help="출력 파일명(확장자 제외). 기본: plan 파일명에서 '.plan' 제거")
    parser.add_argument("--charts", action="store_true",
                        help="pptx에서 숫자 표를 차트 슬라이드로 시각화 (기본: 글 문서, 표 슬라이드)")
    parser.add_argument("--institution", help="승인된 HWPX 기관 템플릿의 기관명")
    parser.add_argument("--document-type", help="승인된 HWPX 기관 템플릿의 문서 유형")
    parser.add_argument("--template-content", type=Path, help="기관 템플릿 content.json 경로")
    args = parser.parse_args(argv)

    if not args.plan.is_file():
        raise SystemExit(f"ERROR: plan 파일 없음: {args.plan}")

    formats = _parse_formats(args.to)
    institution_options = (args.institution, args.document_type, args.template_content)
    has_institution_options = any(value is not None for value in institution_options)
    has_all_institution_options = all(value is not None for value in institution_options)
    if has_institution_options and not has_all_institution_options:
        parser.error("institution template options must be provided together: "
                     "--institution, --document-type, --template-content")
    if has_all_institution_options and "hwpx" not in formats:
        parser.error("institution template options require hwpx in --to")

    template_content = None
    if has_all_institution_options:
        try:
            template_content = load_content_fields(args.template_content)
        except (OSError, json.JSONDecodeError) as exc:
            parser.error(f"cannot read --template-content {args.template_content}: {exc}")

    report = load_plan(args.plan)

    out_dir = args.out or args.plan.parent
    out_dir.mkdir(parents=True, exist_ok=True)
    stem = args.stem or args.plan.name.replace(".plan.json", "").replace(".json", "")
    md_path = out_dir / f"{stem}.md"

    outputs = []
    problems: list[str] = []
    for fmt in formats:
        out_path = out_dir / f"{stem}.{fmt}"
        kwargs = {"include_charts": args.charts} if fmt == "pptx" else {}
        if fmt == "hwpx" and template_content is not None:
            kwargs = {
                "institution": args.institution,
                "document_type": args.document_type,
                "template_content": template_content,
            }
        probs, result = _RENDERERS[fmt](report, md_path, out_path, **kwargs)
        problems = probs  # same plan -> same validation each time
        outputs.append({
            "format": fmt,
            "ok": result.ok,
            "output": str(result.output) if result.ok else None,
            "error": result.error,
            "stabilized": result.meta.get("stabilized"),
        })

    summary = {
        "title": report.title,
        "doc_type": report.doc_type,
        "markdown": str(md_path),
        "validation_problems": problems,
        "outputs": outputs,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if all(o["ok"] for o in outputs) else 1


if __name__ == "__main__":
    raise SystemExit(main())
