"""Evidence-based cell vertical-alignment reconciliation for HWP -> HWPX.

The hwp2hwpx converter drops table-cell vertical alignment and writes every cell
as ``vertAlign="TOP"``. This module does NOT guess: it reads the *original* HWP's
per-cell alignment (via pyhwp ``hwp5proc xml``) and applies those exact values to
the matching converted HWPX cells, addressed by (table index, column, row).

HWP ``valign`` -> HWPX ``vertAlign``:  middle -> CENTER, top -> TOP, bottom -> BOTTOM.

A cell with no matching original value is left unchanged (never guessed).
"""
from __future__ import annotations

import re
import subprocess
import sys
import zipfile
from pathlib import Path

_VALIGN_TO_HWPX = {"middle": "CENTER", "top": "TOP", "bottom": "BOTTOM"}
_HWP5PROC_XML = "import sys; sys.argv=['hwp5proc','xml',sys.argv[1]]; from hwp5.hwp5proc import main; main()"


def reconcile_hwpx_cell_valign(hwp_path: Path | str, hwpx_path: Path | str) -> dict:
    """Apply the original HWP's cell vertical alignment to the converted HWPX.

    Returns a stats dict; ``applied=False`` when the original alignment could not
    be read (then nothing is changed).
    """
    targets = extract_hwp_cell_valigns(hwp_path)
    if not targets:
        return {"applied": False, "reason": "no HWP cell valign extracted"}

    hwpx_path = Path(hwpx_path)
    with zipfile.ZipFile(hwpx_path) as zin:
        entries = [(info, zin.read(info.filename)) for info in zin.infolist()]

    total = {"matched": 0, "changed": 0, "unmatched": 0}
    rebuilt = []
    for info, data in entries:
        if re.search(r"Contents/section\d+\.xml$", info.filename, re.I):
            text, stats = apply_cell_valign_to_section(data.decode("utf-8"), targets)
            for k in total:
                total[k] += stats[k]
            data = text.encode("utf-8")
        rebuilt.append((info, data))

    tmp = hwpx_path.parent / (hwpx_path.name + ".tmp")
    with zipfile.ZipFile(tmp, "w") as zout:  # keep entry order (mimetype first) + compress types
        for info, data in rebuilt:
            zout.writestr(info, data)
    tmp.replace(hwpx_path)

    return {"applied": True, "cells_from_hwp": len(targets), **total}


def extract_hwp_cell_valigns(hwp_path: Path | str) -> dict[tuple[int, int, int], str]:
    """Return {(table_index, col, row): HWPX vertAlign} read from the original HWP."""
    xml = _hwp_to_xml(hwp_path)
    if xml is None:
        return {}
    targets: dict[tuple[int, int, int], str] = {}
    for table_index, segment in enumerate(re.split(r"<TableControl", xml)[1:]):
        body = segment.split("</TableControl", 1)[0]
        for cell in re.findall(r"<TableCell\b[^>]*>", body):
            col = re.search(r'\bcol="(\d+)"', cell)
            row = re.search(r'\brow="(\d+)"', cell)
            valign = re.search(r'\bvalign="([a-z]+)"', cell)
            if col and row and valign and valign.group(1) in _VALIGN_TO_HWPX:
                key = (table_index, int(col.group(1)), int(row.group(1)))
                targets[key] = _VALIGN_TO_HWPX[valign.group(1)]
    return targets


def apply_cell_valign_to_section(section: str, targets: dict) -> tuple[str, dict]:
    """Set each HWPX cell's subList vertAlign from ``targets`` (pure, no I/O)."""
    stats = {"matched": 0, "changed": 0, "unmatched": 0}
    out: list[str] = []
    last = 0
    for table_index, tbl_match in enumerate(re.finditer(r"<hp:tbl\b.*?</hp:tbl>", section, re.S)):
        out.append(section[last:tbl_match.start()])
        out.append(_reconcile_table(tbl_match.group(0), table_index, targets, stats))
        last = tbl_match.end()
    out.append(section[last:])
    return "".join(out), stats


def _reconcile_table(tbl: str, table_index: int, targets: dict, stats: dict) -> str:
    def replace_cell(cell_match: re.Match) -> str:
        tc = cell_match.group(0)
        col = re.search(r'\bcolAddr="(\d+)"', tc)
        row = re.search(r'\browAddr="(\d+)"', tc)
        if not (col and row):
            return tc
        target = targets.get((table_index, int(col.group(1)), int(row.group(1))))
        if target is None:
            stats["unmatched"] += 1
            return tc
        stats["matched"] += 1

        def set_valign(m: re.Match) -> str:
            if m.group(2) != target:
                stats["changed"] += 1
            return m.group(1) + target + m.group(3)

        return re.sub(r'(<hp:subList\b[^>]*\bvertAlign=")([A-Z]+)(")', set_valign, tc, count=1)

    return re.sub(r"<hp:tc\b.*?</hp:tc>", replace_cell, tbl, flags=re.S)


def _hwp_to_xml(hwp_path: Path | str) -> str | None:
    try:
        result = subprocess.run(
            [sys.executable, "-c", _HWP5PROC_XML, str(hwp_path)],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        )
    except Exception:  # noqa: BLE001 - pyhwp missing / unreadable
        return None
    return result.stdout if result.stdout.strip() else None
