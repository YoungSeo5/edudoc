from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from core.exporters.hwpx_via_hwpskill import HwpxViaHwpSkillExporter


ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "tests" / "fixtures" / "export" / "wide_table_activity_report.md"


def test_hwp_skill_export_uses_utf8_for_korean_preview_output(tmp_path: Path) -> None:
    # Given: the renderer prints a Korean preview while Windows defaults to CP949.
    output = tmp_path / "report.hwpx"

    # When: edudoc invokes the protected renderer through its owned adapter.
    result = HwpxViaHwpSkillExporter(template="report", title="한글 보고서").export(
        FIXTURE,
        output,
    )

    # Then: preview output cannot terminate the subprocess with UnicodeEncodeError.
    assert result.ok, result.error
    assert output.is_file()
