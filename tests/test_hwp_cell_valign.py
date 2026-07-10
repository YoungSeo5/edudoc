"""core.adapters.hwp_cell_valign: evidence-based cell vertical-alignment fix.

The hwp2hwpx converter writes every cell as vertAlign="TOP". These tests prove the
reconciler applies the *original HWP's* real per-cell alignment (never a guess):
the apply step is address-driven, and extraction reads the reference HWP's actual
`valign="middle"` cells.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.adapters.hwp_cell_valign import apply_cell_valign_to_section, extract_hwp_cell_valigns

ROOT = Path(__file__).resolve().parent.parent
REFERENCE_HWP = (
    ROOT / "references" / "document-types" / "public-plan"
    / "대통령비서실 보고서의 표준서식_한장보고서의 표준.hwp"
)

# one table, two cells, both wrongly TOP from conversion
_SECTION = (
    '<hp:tbl><hp:tr>'
    '<hp:tc><hp:cellAddr colAddr="0" rowAddr="0"/>'
    '<hp:subList vertAlign="TOP"><hp:p/></hp:subList></hp:tc>'
    '<hp:tc><hp:cellAddr colAddr="1" rowAddr="0"/>'
    '<hp:subList vertAlign="TOP"><hp:p/></hp:subList></hp:tc>'
    '</hp:tr></hp:tbl>'
)


def _cell_valign(section: str, col: str) -> str:
    for tc in re.findall(r"<hp:tc>.*?</hp:tc>", section, re.S):
        if f'colAddr="{col}"' in tc:
            return re.search(r'<hp:subList\b[^>]*vertAlign="([A-Z]+)"', tc).group(1)
    raise AssertionError(f"cell colAddr={col} not found")


def test_apply_uses_targets_per_cell_address() -> None:
    # evidence: cell (0,0) should be CENTER, cell (0,1) should stay TOP
    targets = {(0, 0, 0): "CENTER", (0, 1, 0): "TOP"}
    result, stats = apply_cell_valign_to_section(_SECTION, targets)

    assert _cell_valign(result, "0") == "CENTER"   # changed to the original's value
    assert _cell_valign(result, "1") == "TOP"       # already matches target, left as-is
    assert stats == {"matched": 2, "changed": 1, "unmatched": 0}


def test_apply_leaves_unmatched_cells_untouched() -> None:
    # no target for any cell -> nothing is guessed
    result, stats = apply_cell_valign_to_section(_SECTION, {})
    assert _cell_valign(result, "0") == "TOP"
    assert _cell_valign(result, "1") == "TOP"
    assert stats == {"matched": 0, "changed": 0, "unmatched": 2}


def test_extract_reads_reference_hwp_middle_cells() -> None:
    # the reference HWP's 10 table cells are all valign="middle" -> CENTER
    targets = extract_hwp_cell_valigns(REFERENCE_HWP)
    assert len(targets) == 10
    assert set(targets.values()) == {"CENTER"}


if __name__ == "__main__":
    test_apply_uses_targets_per_cell_address()
    test_apply_leaves_unmatched_cells_untouched()
    test_extract_reads_reference_hwp_middle_cells()
    print("PASS: evidence-based cell vertAlign reconciliation")
