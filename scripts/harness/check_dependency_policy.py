"""Fail when forbidden heavyweight tools become default requirements."""
from __future__ import annotations

from pathlib import Path


FORBIDDEN = {
    "libreoffice",
    "unoconv",
    "pypandoc-binary",
    "texlive",
    "latex",
    "pdflatex",
    "comtypes",
    "win32com",
}


def _package_name(line: str) -> str:
    line = line.split("#", 1)[0].strip().lower()
    for marker in ("==", ">=", "<=", "~=", ">", "<", "["):
        if marker in line:
            line = line.split(marker, 1)[0]
    return line.strip()


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    req = root / "requirements.txt"
    violations: list[str] = []

    for raw in req.read_text(encoding="utf-8").splitlines():
        name = _package_name(raw)
        if name and name in FORBIDDEN:
            violations.append(name)

    if violations:
        print("Forbidden default dependencies found:")
        for name in violations:
            print(f"  - {name}")
        return 1

    print("PASS: dependency policy")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
