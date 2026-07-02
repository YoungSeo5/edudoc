# Current Task

## Goal

Continue Loop 8: validated Markdown -> DOCX/HWPX/PDF export stabilization.

## Current Status

```text
Loop 1   = complete
Loop 2   = complete
Loop 2.5 = complete
Loop 3   = complete
Loop 3.5 = complete
Loop 4   = complete
Loop 5   = complete
Loop 5.5 = complete
Loop 6   = complete
Loop 7   = implemented early and now complete
Loop 8   = current canonical loop
```

Loop 8 status:

- Direct validated Gongmun Markdown -> DOCX export is covered by `tests/test_gongmun_docx_export.py`.
- Pipeline-level `.docx` export now routes to the pip-native `DocxExporter`.
- `OfficeExporter` remains available as optional Pandoc-backed fallback/comparison behavior for other formats.
- Loop 8.5 (complete): a reusable Gongmun style profile (`core/exporters/style_profile.py`) is applied to DOCX output (margins, font, size, line spacing, paragraph spacing, Heading 1 size/alignment), covered by `tests/test_gongmun_docx_style_profile.py`. Project-local/reference-guided, not official layout compliance.
- Loop 8.95 (complete): closed implementation gaps — `style_profile.py`, `load_from_toml()`, missing-key fallback, and custom-profile injection are now tested (`tests/test_style_profile.py`); pipeline DOCX test asserts the default style profile; TOML clarified as documentation/loadable (runtime uses the Python constant, no auto-selection).
- Loop 8.96 (complete): DocumentModel integrity validation (`validators/document_model_rules.py`) is now wired into the pipeline when a converter provides a DocumentModel — records `meta["document_model_validation"]` and writes a separate `<stem>.document.validation.txt`, non-blocking and separate from Gongmun validation. Closes the Loop 4 runtime-connection gap. Covered by `tests/test_pipeline_document_model_validation.py`.
- Loop 8.97 (complete): export-status triage. PDF has no dedicated pip-native exporter; `.pdf` routes through the `OfficeExporter` Pandoc/Typst fallback and was mis-reported as stabilized success. Pipeline now tags exports with `stabilized`/`experimental`; CLI shows fallback exports as `출력(fallback·실험적)`. DOCX remains the only stabilized pip-native export. Covered by `tests/test_real_sample_export_status.py`.
- Loop 8.97 (cont.): product-direction clarified — edudoc is **reference-based document generation**, not only format conversion (`docs/product-direction.md`, export truth table in `docs/export-status.md`). Export is not complete until real-sample regression exists; PDF/HWPX/PPTX are fallback/planned, not stable. No code change (docs/roadmap alignment only).
- Loop 8.99 (complete): export quality criteria + regression tests. Defined 5 quality levels (`docs/export-quality-criteria.md`); added realistic wide-table fixture (`tests/fixtures/export/wide_table_activity_report.md`) + DOCX structure regression (`tests/test_docx_realistic_structure_export.py`) + PDF fallback/status test (`tests/test_pdf_export_status.py`). Principle: `file exists != usable document`. No new exporter.
- Dedicated PDF and HWPX exporter files do not exist yet.

## Export Status

- DOCX is implemented through `core/exporters/docx_exporter.py` using `python-docx`.
- DOCX can run without Pandoc, Typst, LaTeX, LibreOffice, MS Office, or HWP installation.
- Pipeline DOCX export is covered by `tests/test_pipeline_docx_export.py`.
- Dedicated PDF and HWPX exporters remain planned until narrow pip-native exporters are added.

See `docs/export-status.md` for the current export audit.

## Loop 8 Scope

- Stabilize export from validated Markdown.
- Keep export work separate from HWP/HWPX input conversion.
- Preserve the HWPX-first normalization path.
- Preserve Gongmun generation and validation behavior.
- Keep heavy external tools optional unless the user explicitly chooses a fallback path.

## Out of Scope

- API/FastAPI/web UI
- Folder watching integration
- Broad Gongmun validation rule expansion
- HWP fallback rewrite
- Full HWPX AST
- Heavy dependency additions
- Making Pandoc, Typst, LaTeX, LibreOffice, MS Office, or HWP installation required

## Acceptance Criteria

- Pipeline-level DOCX export produces a non-empty DOCX file.
- Pipeline DOCX export uses `DocxExporter` by default.
- Existing tests and harness checks still pass.

## Verification

Run:

```bash
python tests/test_pipeline.py
python tests/test_hwpx_document_model.py
python tests/test_document_model_rules.py
python tests/test_pipeline_document_model_validation.py
python tests/test_gongmun_writer_examples.py
python tests/test_gongmun_generator.py
python tests/test_gongmun_cli.py
python tests/test_gongmun_docx_export.py
python tests/test_pipeline_docx_export.py
python tests/test_gongmun_docx_style_profile.py
python tests/test_style_profile.py
python tests/test_real_sample_export_status.py
python tests/test_docx_realistic_structure_export.py
python tests/test_pdf_export_status.py
python scripts/harness/check_dependency_policy.py
python scripts/harness/check_hwp_priority_drift.py
```
