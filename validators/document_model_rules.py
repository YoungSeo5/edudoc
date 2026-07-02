"""DocumentModel integrity checks.

These rules validate conversion/document integrity facts that are already
present in DocumentModel and raw_meta. They are intentionally separate from
public-office writing rules in gongmun_rules.py.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from core.document_model import DocumentModel


@dataclass
class DocumentModelViolation:
    rule: str
    message: str
    severity: str = "error"


@dataclass
class DocumentModelValidationReport:
    violations: list[DocumentModelViolation] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return not any(v.severity == "error" for v in self.violations)

    def summary(self) -> str:
        if self.passed and not self.violations:
            return "DocumentModel validation: passed"

        errors = sum(1 for v in self.violations if v.severity == "error")
        warnings = sum(1 for v in self.violations if v.severity == "warning")
        lines = [f"DocumentModel validation: {errors} error(s), {warnings} warning(s)"]
        lines.extend(
            f"  - [{v.severity}] {v.rule}: {v.message}"
            for v in self.violations
        )
        return "\n".join(lines)


def validate(model: DocumentModel) -> DocumentModelValidationReport:
    """Validate deterministic DocumentModel integrity conditions."""
    report = DocumentModelValidationReport()
    report.violations.extend(check_structure_source(model))
    report.violations.extend(check_nonempty_document_structure(model))
    report.violations.extend(check_hwpx_package_metadata(model))
    report.violations.extend(check_xml_metadata_consistency(model))
    return report


def check_structure_source(model: DocumentModel) -> list[DocumentModelViolation]:
    if not model.raw_meta.get("structure_source"):
        return [
            DocumentModelViolation(
                "structure_source_present",
                "raw_meta.structure_source is required so fallback/native structure is explicit.",
            ),
        ]
    return []


def check_nonempty_document_structure(model: DocumentModel) -> list[DocumentModelViolation]:
    if not model.paragraphs and not model.tables:
        return [
            DocumentModelViolation(
                "document_structure_nonempty",
                "DocumentModel should contain at least one paragraph or table.",
            ),
        ]
    return []


def check_hwpx_package_metadata(model: DocumentModel) -> list[DocumentModelViolation]:
    if model.format.lower() != "hwpx":
        return []

    meta = model.raw_meta
    violations: list[DocumentModelViolation] = []

    if _hwpx_package_metadata_expected(meta) and meta.get("hwpx_package_detected") is not True:
        violations.append(
            DocumentModelViolation(
                "hwpx_package_detected",
                "HWPX package metadata was expected, but hwpx_package_detected is not true.",
            ),
        )

    if meta.get("native_metadata_available") is True and not _positive_int(meta.get("xml_file_count")):
        violations.append(
            DocumentModelViolation(
                "hwpx_xml_file_count",
                "native_metadata_available is true, but xml_file_count is not greater than zero.",
            ),
        )

    return violations


def check_xml_metadata_consistency(model: DocumentModel) -> list[DocumentModelViolation]:
    meta = model.raw_meta
    if meta.get("xml_metadata_available") is not True:
        return []

    violations: list[DocumentModelViolation] = []

    if not meta.get("extracted_xml_fields"):
        violations.append(
            DocumentModelViolation(
                "xml_metadata_fields",
                "xml_metadata_available is true, but extracted_xml_fields is empty.",
            ),
        )

    section_files = meta.get("section_files")
    has_section_files = isinstance(section_files, list) and len(section_files) > 0
    has_section_count = _positive_int(meta.get("section_file_count"))
    if not has_section_files and not has_section_count:
        violations.append(
            DocumentModelViolation(
                "hwpx_section_files",
                "xml_metadata_available is true, but no HWPX section XML file is recorded.",
            ),
        )

    return violations


def _hwpx_package_metadata_expected(meta: dict) -> bool:
    structure_source = str(meta.get("structure_source", ""))
    return (
        meta.get("native_metadata_available") is True
        or "hwpx_package_metadata" in structure_source
        or "hwpx_xml_metadata" in structure_source
    )


def _positive_int(value) -> bool:  # noqa: ANN001
    return isinstance(value, int) and not isinstance(value, bool) and value > 0
