"""compose Phase 1: HWPX render adapter around hwp-skill md2hwpx.

Proves the edudoc-owned adapter turns a realistic report Markdown into a real,
structurally valid HWPX with tables and Korean text preserved. Skips gracefully if
the hwp-skill pack is not present in this checkout.
"""
from __future__ import annotations

import re
import sys
import tempfile
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.exporters.hwpx_via_hwpskill import HwpxViaHwpSkillExporter

FIXTURE = (
    Path(__file__).resolve().parent
    / "fixtures" / "export" / "wide_table_activity_report.md"
)


def test_hwpx_via_hwpskill_renders_valid_hwpx() -> None:
    assert FIXTURE.exists(), f"fixture missing: {FIXTURE}"

    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "report.hwpx"
        result = HwpxViaHwpSkillExporter(
            template="report", title="1학기 결과보고서"
        ).export(FIXTURE, out)

        if result.meta.get("available") is False:
            print("SKIP: hwp-skill not present; HWPX adapter not exercised")
            return

        assert result.ok, result.error
        assert out.exists() and out.stat().st_size > 0, "HWPX missing/empty"
        assert out.read_bytes()[:2] == b"PK", "not a valid HWPX (zip)"

        with zipfile.ZipFile(out) as zf:
            section = zf.read("Contents/section0.xml").decode("utf-8")

        # tables preserved as real HWPX tables (toy exporter could not do this)
        assert len(re.findall(r"<hp:tbl", section)) >= 1, "no HWPX table in output"
        # Korean text + section labels preserved
        for token in ("학습공동체", "중간 활동보고서", "일반 현황", "예시모둠"):
            assert token in section, f"missing text: {token}"
        # skill-level structural validation passed
        assert result.meta.get("validation", {}).get("passed") is True, result.meta.get("validation")

    print("PASS: HWPX via hwp-skill (tables + Korean preserved, structurally valid)")
    return


if __name__ == "__main__":
    test_hwpx_via_hwpskill_renders_valid_hwpx()
