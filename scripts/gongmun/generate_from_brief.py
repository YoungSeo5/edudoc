"""Generate a Gongmun Markdown draft and validation report from a brief file."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.failure_log import DEFAULT_FAILURES_DIR, FailureRecord, record_failure  # noqa: E402
from core.generators.gongmun_generator import generate_and_validate  # noqa: E402


def main(argv: list[str] | None = None, *, failures_dir: Path | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate Gongmun Markdown from a structured brief.",
    )
    parser.add_argument(
        "brief",
        type=Path,
        help="Path to a UTF-8 Markdown brief with key: value lines.",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("exports") / "gongmun",
        help="Output directory for generated Markdown and validation report.",
    )
    args = parser.parse_args(argv)

    brief_path = args.brief
    out_dir = args.out
    failures_dir = DEFAULT_FAILURES_DIR if failures_dir is None else failures_dir

    try:
        result = generate_and_validate(brief_path)
        out_dir.mkdir(parents=True, exist_ok=True)

        generated_path = out_dir / f"{brief_path.stem}.generated.md"
        report_path = out_dir / f"{brief_path.stem}.validation.txt"

        generated_path.write_text(result.markdown, encoding="utf-8")
        report_path.write_text(result.validation_report.summary(), encoding="utf-8")
    except Exception as exc:  # noqa: BLE001
        record_failure(
            failures_dir,
            FailureRecord(
                entry_point="gongmun_cli",
                stage="gongmun_generate",
                source=str(brief_path),
                error=repr(exc),
            ),
        )
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    print(f"generated: {generated_path}")
    print(f"validation_report: {report_path}")
    print(f"validation_passed: {result.passed}")

    if not result.passed:
        record_failure(
            failures_dir,
            FailureRecord(
                entry_point="gongmun_cli",
                stage="gongmun_validate",
                source=str(brief_path),
                error=result.validation_report.summary(),
            ),
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
