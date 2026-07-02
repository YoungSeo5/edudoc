"""Smoke test for Gongmun Writer Skill examples."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from validators.gongmun_rules import validate


def test_gongmun_writer_output_example_passes_validation() -> None:
    root = Path(__file__).resolve().parent.parent
    example = root / "skills" / "gongmun_writer" / "examples" / "output_gongmun.md"

    text = example.read_text(encoding="utf-8")
    report = validate(text)

    assert report.passed, report.summary()
    assert text.startswith("# "), "Gongmun example should start with a Markdown title"
    assert "관련:" in text, "Gongmun example should include a related-basis line"
    assert "1. 대상:" in text, "Gongmun example should include a numbered body"
    assert "붙임" in text, "Gongmun example should include attachment text"
    assert "끝." in text, "Gongmun example should include the ending marker"
    assert "2026. 7. 15." in text, "Gongmun example should use numeric date notation"


if __name__ == "__main__":
    test_gongmun_writer_output_example_passes_validation()
    print("PASS: Gongmun Writer example validation")
