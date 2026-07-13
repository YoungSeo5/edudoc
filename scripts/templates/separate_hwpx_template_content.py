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
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--template-id", required=True)
    parser.add_argument("--template-name")
    parser.add_argument("--institution", default="확인 필요")
    args = parser.parse_args(argv)

    result = separate_hwpx_template_content(
        args.source,
        args.output_dir,
        template_id=args.template_id,
        template_name=args.template_name,
        institution=args.institution,
    )
    print(f"template: {result.extraction.template_json}")
    print(f"content_sample: {result.content_sample}")
    print(f"placeholder_map: {result.placeholder_map}")
    print(f"review: {result.review}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
