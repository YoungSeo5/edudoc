"""Evidence-based character-flag reconciliation for HWP -> HWPX.

The hwp2hwpx converter mis-maps HWP charshape flag bits: it swaps italic (bit 0)
and bold (bit 1). This is proven by pyhwp's own authoritative decoding — pyhwp
emits ``italic``/``bold`` attributes per CharShape, and its flag parser defines
``0='italic', 1='bold'``.

This module reconciles ONLY the flags pyhwp authoritatively decodes (italic,
bold), applying each original CharShape's value to the matching converted charPr
(the converter preserves charshape ids). Flags pyhwp does not decode — notably
the bit-15 value carried by the footnote/superscript run — are left untouched: no
authoritative evidence, so no guess.
"""
from __future__ import annotations

import re
import zipfile
from pathlib import Path

from .hwp_cell_valign import _hwp_to_xml

# only flags pyhwp authoritatively decodes into named attributes (Flags: 0=italic, 1=bold)
_PYHWP_CONFIRMED_FLAGS = ("italic", "bold")


def reconcile_hwpx_char_flags(hwp_path: Path | str, hwpx_path: Path | str) -> dict:
    """Apply the original HWP's pyhwp-decoded italic/bold to the converted HWPX.

    Returns a stats dict; ``applied=False`` when the original flags cannot be read.
    """
    flags = extract_hwp_char_flags(hwp_path)
    if not flags:
        return {"applied": False, "reason": "no HWP charshape flags extracted"}

    hwpx_path = Path(hwpx_path)
    with zipfile.ZipFile(hwpx_path) as zin:
        entries = [(info, zin.read(info.filename)) for info in zin.infolist()]

    changed = 0
    rebuilt = []
    for info, data in entries:
        if re.search(r"Contents/header\.xml$", info.filename, re.I):
            text, changed = apply_char_flags_to_header(data.decode("utf-8"), flags)
            data = text.encode("utf-8")
        rebuilt.append((info, data))

    if changed:
        tmp = hwpx_path.parent / (hwpx_path.name + ".tmp")
        with zipfile.ZipFile(tmp, "w") as zout:
            for info, data in rebuilt:
                zout.writestr(info, data)
        tmp.replace(hwpx_path)

    return {"applied": True, "charshapes_from_hwp": len(flags), "changed": changed}


def extract_hwp_char_flags(hwp_path: Path | str) -> dict[int, dict[str, str]]:
    """Return {charshape_id: {flag: "0"|"1"}} from pyhwp's authoritative decoding."""
    xml = _hwp_to_xml(hwp_path)
    if xml is None:
        return {}
    result: dict[int, dict[str, str]] = {}
    for shape_id, shape in enumerate(re.findall(r"<CharShape\b[^>]*>", xml)):
        values = {}
        for name in _PYHWP_CONFIRMED_FLAGS:
            m = re.search(rf'\b{name}="(\d)"', shape)
            if m:
                values[name] = m.group(1)
        result[shape_id] = values
    return result


def apply_char_flags_to_header(header: str, flags: dict) -> tuple[str, int]:
    """Set each charPr's italic/bold to the original values (pure, no I/O)."""
    changed = 0

    def reconcile(m: re.Match) -> str:
        nonlocal changed
        cid = int(m.group(1))
        attrs = m.group(2)
        target = flags.get(cid)
        if not target:
            return m.group(0)
        for name in _PYHWP_CONFIRMED_FLAGS:
            if name not in target:
                continue
            attrs, did = _set_bool_attr(attrs, name, target[name])
            changed += did
        return f'<hh:charPr id="{cid}"{attrs}>'

    return re.sub(r'<hh:charPr id="(\d+)"([^>]*)>', reconcile, header), changed


def _set_bool_attr(attrs: str, name: str, value: str) -> tuple[str, int]:
    """Set boolean attr to value; add when missing and value=='1'. Returns (attrs, changed)."""
    existing = re.search(rf'\s{name}="(\d)"', attrs)
    if existing:
        if existing.group(1) == value:
            return attrs, 0
        return attrs[: existing.start()] + f' {name}="{value}"' + attrs[existing.end():], 1
    if value == "1":  # absent means 0; only add when the original turns it on
        return attrs + f' {name}="1"', 1
    return attrs, 0
