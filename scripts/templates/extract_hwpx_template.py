#!/usr/bin/env python3
"""Extract a reusable, read-only template package from one source HWPX."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.templates.hwpx_package_extractor import extract_hwpx_template  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--template-id", required=True)
    parser.add_argument("--template-name")
    parser.add_argument("--institution", default="확인 필요")
    parser.add_argument(
        "--fixture-dir",
        type=Path,
        help="Optional extracted Contents directory used only for byte comparison.",
    )
    args = parser.parse_args(argv)

    result = extract_hwpx_template(
        args.source,
        args.output_dir,
        template_id=args.template_id,
        template_name=args.template_name,
        institution=args.institution,
        fixture_dir=args.fixture_dir,
    )
    print(f"template: {result.template_json}")
    print(f"report: {result.extraction_report}")
    print(f"sections: {len(result.candidate.structure['sections'])}")
    print(
        "placeholder_candidates: "
        f"{len(result.candidate.structure['candidate_placeholders'])}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
