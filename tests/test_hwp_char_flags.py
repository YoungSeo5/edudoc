"""core.adapters.hwp_char_flags: evidence-based italic/bold reconciliation.

The hwp2hwpx converter swaps italic (bit 0) and bold (bit 1). These tests prove
the reconciler restores pyhwp's authoritative italic/bold per charshape id, and
never touches flags pyhwp does not decode (e.g. the bit-15 footnote value).
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.adapters.hwp_char_flags import apply_char_flags_to_header, extract_hwp_char_flags

ROOT = Path(__file__).resolve().parent.parent
REFERENCE_HWP = (
    ROOT / "references" / "document-types" / "public-plan"
    / "대통령비서실 보고서의 표준서식_한장보고서의 표준.hwp"
)

# converter output: id 1 wrongly bold (should be italic), id 2 wrongly italic (should be bold),
# id 3 has an unrelated attribute the reconciler must not touch
_HEADER = (
    '<hh:charPr id="1" height="1000" bold="1"><hh:fontRef/></hh:charPr>'
    '<hh:charPr id="2" height="1000" italic="1"><hh:fontRef/></hh:charPr>'
    '<hh:charPr id="3" height="1300" engrave="1"><hh:fontRef/></hh:charPr>'
)


def _attr(header: str, cid: int, name: str) -> str | None:
    tag = re.search(rf'<hh:charPr id="{cid}"([^>]*)>', header).group(1)
    m = re.search(rf'{name}="(\w+)"', tag)
    return m.group(1) if m else None


def test_apply_restores_italic_bold_from_targets() -> None:
    targets = {
        1: {"italic": "1", "bold": "0"},   # was bold -> should become italic
        2: {"italic": "0", "bold": "1"},   # was italic -> should become bold
    }
    result, changed = apply_char_flags_to_header(_HEADER, targets)

    assert _attr(result, 1, "italic") == "1" and _attr(result, 1, "bold") == "0"
    assert _attr(result, 2, "italic") == "0" and _attr(result, 2, "bold") == "1"
    assert _attr(result, 3, "engrave") == "1"   # bit-15 value left untouched (no evidence)
    assert changed == 4


def test_extract_reads_reference_hwp_italic_bold() -> None:
    flags = extract_hwp_char_flags(REFERENCE_HWP)
    # verified from the reference: charshape 11 is italic, 14 is bold
    assert flags[11] == {"italic": "1", "bold": "0"}
    assert flags[14] == {"italic": "0", "bold": "1"}


if __name__ == "__main__":
    test_apply_restores_italic_bold_from_targets()
    test_extract_reads_reference_hwp_italic_bold()
    print("PASS: evidence-based italic/bold char-flag reconciliation")
