"""Detect wording that promotes HWP binary input back to the default path."""
from __future__ import annotations

from pathlib import Path


BAD_PHRASES = (
    "HWP is the default input",
    "HWP 우선",
    "hwp 기본 입력",
    "기본 입력 변환기는 hwp",
)


def _files_to_scan(root: Path) -> list[Path]:
    files = [
        root / "AGENTS.md",
        root / "CLAUDE.md",
        root / "README.md",
        root / "MEMORY.md",
    ]
    files.extend(sorted((root / "docs").glob("*.md")))
    return [p for p in files if p.exists()]


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    findings: list[tuple[Path, str]] = []

    for path in _files_to_scan(root):
        text = path.read_text(encoding="utf-8")
        for phrase in BAD_PHRASES:
            if phrase in text:
                findings.append((path.relative_to(root), phrase))

    if findings:
        print("HWP priority drift detected:")
        for path, phrase in findings:
            print(f"  - {path}: {phrase}")
        return 1

    print("PASS: HWPX-first wording policy")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
