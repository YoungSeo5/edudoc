#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.templates.hwpx_content_separator import separate_hwpx_template_content  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    # 흐름 1: 이 CLI는 입력값만 해석한다. HWPX 추출과 콘텐츠 분리 로직은
    # core.templates.hwpx_content_separator에 위임한다.
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--template-id", required=True)
    parser.add_argument("--template-name")
    parser.add_argument("--institution", default="확인 필요")
    parser.add_argument("--rules", type=Path)
    args = parser.parse_args(argv)

    # 흐름 2: 호출 한 번으로 패키지 추출 → 고정/가변 콘텐츠 분류 →
    # {{placeholder}} 템플릿 생성까지 수행한다.
    result = separate_hwpx_template_content(
        args.source,
        args.output_dir,
        template_id=args.template_id,
        template_name=args.template_name,
        institution=args.institution,
        rules_path=args.rules,
    )

    # 흐름 3: 생성된 기관 템플릿 폴더의 핵심 산출물 위치를 사용자에게 알린다.
    # 이 단계에서는 템플릿을 approved로 승격하지 않는다.
    print(f"template: {result.extraction.template_json}")
    print(f"content_sample: {result.content_sample}")
    print(f"placeholder_map: {result.placeholder_map}")
    print(f"review: {result.review}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
