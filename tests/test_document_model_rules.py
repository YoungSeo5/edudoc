"""Focused tests for DocumentModel integrity validation."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.document_model import DocumentModel, ParagraphNode
from validators.document_model_rules import validate


def _valid_hwpx_model() -> DocumentModel:
    return DocumentModel(
        source_path="samples/example.hwpx",
        format="hwpx",
        paragraphs=[ParagraphNode(index=0, text="Sample paragraph")],
        raw_meta={
            "structure_source": "hwpx_xml_metadata_plus_markdown_fallback",
            "hwpx_package_detected": True,
            "native_metadata_available": True,
            "xml_file_count": 3,
            "section_file_count": 1,
            "section_files": ["Contents/section0.xml"],
            "xml_metadata_available": True,
            "extracted_xml_fields": [
                "content_hpf_present",
                "manifest_present",
                "section_files",
            ],
        },
    )


def _rules(report) -> set[str]:  # noqa: ANN001
    return {violation.rule for violation in report.violations}


def test_valid_hwpx_document_model_metadata_passes() -> None:
    report = validate(_valid_hwpx_model())

    assert report.passed
    assert not report.violations


def test_missing_structure_source_fails() -> None:
    model = _valid_hwpx_model()
    del model.raw_meta["structure_source"]

    report = validate(model)

    assert not report.passed
    assert "structure_source_present" in _rules(report)


def test_empty_paragraphs_and_tables_fails() -> None:
    model = _valid_hwpx_model()
    model.paragraphs = []
    model.tables = []

    report = validate(model)

    assert not report.passed
    assert "document_structure_nonempty" in _rules(report)


def test_xml_metadata_available_with_empty_extracted_fields_fails() -> None:
    model = _valid_hwpx_model()
    model.raw_meta["extracted_xml_fields"] = []

    report = validate(model)

    assert not report.passed
    assert "xml_metadata_fields" in _rules(report)


if __name__ == "__main__":
    test_valid_hwpx_document_model_metadata_passes()
    test_missing_structure_source_fails()
    test_empty_paragraphs_and_tables_fails()
    test_xml_metadata_available_with_empty_extracted_fields_fails()
    print("PASS: DocumentModel integrity rules")
