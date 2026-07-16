"""HWPX native locators are additive: they cite the source, they change nothing.

Guards the B0.5 contract. The converter now records source coordinates (paragraph
order, table cell addresses) so a generated report can point at the evidence it
came from. That must not disturb the existing pipeline, so the Markdown and every
pre-existing DocumentModel field are compared against snapshots taken before the
change (tests/fixtures/converter_baseline/).

Evidence comes from repository-tracked inputs only. Nothing under exports/ or any
generated artifact is used, and the source HWPX files are never written to.

Regenerate the snapshots only when the existing output is *meant* to change:
    python tests/fixtures/converter_baseline/make_baseline.py
"""
from __future__ import annotations

import hashlib
import json
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core import hwp_converter  # noqa: E402
from core.document_model import document_model_from_markdown  # noqa: E402
from core.hwp_converter import HwpSkillConverter  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
BASELINE_DIR = ROOT / "tests" / "fixtures" / "converter_baseline"

# Keys the locator work added. Everything else must match the baseline exactly.
NEW_KEYS = {"native_paragraphs", "native_table_cells", "locator_source"}


def _baselines() -> list[tuple[str, dict]]:
    """Both representative HWPX inputs, snapshotted before the locator change."""
    baselines = [
        (path.stem, json.loads(path.read_text(encoding="utf-8")))
        for path in sorted(BASELINE_DIR.glob("*.json"))
    ]
    assert len(baselines) == 2, "expected both tracked HWPX baselines"
    return baselines


def _convert(relative_path: str):
    result = HwpSkillConverter().convert(ROOT / relative_path)
    assert result.ok, result.error
    assert result.document_model is not None
    return result


def _digest(relative_path: str) -> str:
    return hashlib.sha256((ROOT / relative_path).read_bytes()).hexdigest()


def test_markdown_output_is_unchanged() -> None:
    for name, baseline in _baselines():
        result = _convert(baseline["source"])
        assert result.markdown == baseline["markdown"], f"{name}: Markdown changed"


def test_existing_document_model_fields_are_unchanged() -> None:
    for name, baseline in _baselines():
        expected = baseline["document_model"]
        actual = _convert(baseline["source"]).document_model.to_dict()
        actual["source_path"] = Path(actual["source_path"]).name

        assert not set(expected) - set(actual), f"{name}: a field disappeared"
        for key, value in expected.items():
            assert actual[key] == value, f"{name}: field '{key}' changed"

        # the locator fields are the only additions
        assert set(actual) - set(expected) <= NEW_KEYS, f"{name}: unexpected new field"


def test_hwpx_paragraphs_carry_source_coordinates() -> None:
    for name, baseline in _baselines():
        model = _convert(baseline["source"]).document_model

        assert model.locator_source == "hwpx_native", name
        assert model.native_paragraphs, name

        # source order within a section, not the Markdown round-trip's order
        indices = [p.index for p in model.native_paragraphs if p.section == 0]
        assert indices == list(range(len(indices))), name


def test_table_cells_are_addressable_by_row_and_column() -> None:
    for name, baseline in _baselines():
        model = _convert(baseline["source"]).document_model
        assert model.native_table_cells, name

        for cell in model.native_table_cells:
            assert cell.table >= 0 and cell.row >= 0 and cell.column >= 0

        # an address must resolve to exactly one cell, or a citation is ambiguous
        addresses = [(c.table, c.row, c.column) for c in model.native_table_cells]
        assert len(addresses) == len(set(addresses)), name


def test_locator_failure_keeps_the_conversion_and_is_recorded() -> None:
    """A broken locator reader must not fail a conversion, but must not hide either."""
    _, baseline = _baselines()[0]
    records: list[logging.LogRecord] = []

    class _Capture(logging.Handler):
        def emit(self, record: logging.LogRecord) -> None:
            records.append(record)

    handler = _Capture()
    logger = logging.getLogger("core.hwp_converter")
    logger.addHandler(handler)
    original = hwp_converter.read_native_locators

    def _boom(_path):
        raise RuntimeError("locator reader exploded")

    hwp_converter.read_native_locators = _boom
    try:
        result = HwpSkillConverter().convert(ROOT / baseline["source"])
    finally:
        hwp_converter.read_native_locators = original
        logger.removeHandler(handler)

    # the existing conversion still succeeds, unchanged
    assert result.ok
    assert result.markdown == baseline["markdown"]
    model = result.document_model
    assert model is not None

    # ...but the lost provenance is visible, in the data and in the log
    assert model.locator_source is None
    assert model.native_paragraphs == []
    assert model.native_table_cells == []
    assert "locator reader exploded" in model.raw_meta["locator_error"]
    assert [r for r in records if r.levelno >= logging.WARNING], "failure was not logged"


def test_markdown_input_carries_no_locators_and_keeps_its_shape() -> None:
    """Inputs whose coordinates cannot be recovered must not gain empty fields."""
    model = document_model_from_markdown(
        source_path=Path("draft.md"),
        file_format="markdown",
        markdown="# 제목\n\n본문 한 줄.\n",
    )
    serialized = model.to_dict()

    assert model.locator_source is None
    assert model.native_paragraphs == []
    assert not (NEW_KEYS & set(serialized))  # serialized shape is untouched


def test_source_documents_are_never_written_to() -> None:
    before = {name: _digest(baseline["source"]) for name, baseline in _baselines()}
    for _, baseline in _baselines():
        _convert(baseline["source"])
    after = {name: _digest(baseline["source"]) for name, baseline in _baselines()}

    assert before == after, "conversion modified a source document"


if __name__ == "__main__":
    test_markdown_output_is_unchanged()
    test_existing_document_model_fields_are_unchanged()
    test_hwpx_paragraphs_carry_source_coordinates()
    test_table_cells_are_addressable_by_row_and_column()
    test_locator_failure_keeps_the_conversion_and_is_recorded()
    test_markdown_input_carries_no_locators_and_keeps_its_shape()
    test_source_documents_are_never_written_to()
    print("PASS: HWPX locators are additive (Markdown + existing fields unchanged)")
