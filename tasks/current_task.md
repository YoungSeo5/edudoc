# Current Task

## Goal

Loop 11 — Template-first reference-based generation (user-directed active work).
edudoc checks whether a template for the requested institution × document type
exists; uses it if so; otherwise extracts a candidate from a user-provided
example; otherwise asks for one. See root `AGENTS.md` "Template-first Generation"
and `docs/ROADMAP.md` Loop 11.

Export stabilization (Loop 8) remains useful but is the final rendering step, not
the product goal.

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
Loop 8   = export slices complete (PDF/HWPX/PPTX fallback/experimental)
Loop 11  = in progress (current active loop)
```

Loop 11 status:

- Deterministic extraction (done): `core/templates/extract_style.py` (HWPX-only,
  evidence + confidence), `extract_structure.py`, `.hwp` text candidate
  (`one_page_report.py`), CLI `scripts/templates/extract_template.py`.
- Extracted-style application (done): DOCX (`apply_style.py`) and HWPX custom
  header (`build_header.py`), with `fallback_used` honesty.
- Pending: `load_template()`, official `template.json` under
  `skills/templates/<institution>/<document_type>/`, human curation of candidates
  (code never auto-promotes to official). template.json to be created during
  testing.

Loop 8 status:

- SourceBundle intake foundation (complete): `core/source_bundle.py` builds a
  filtered source manifest using the same bulk input filtering rules as the
  pipeline. It does not convert, generate, validate, or export documents.
- Direction reset (complete): documentation now frames edudoc as
  source/reference materials + user intent -> generated task document ->
  validation -> final rendering. Simple conversion is not the product goal.
- Direct validated Gongmun Markdown -> DOCX export is covered by `tests/test_gongmun_docx_export.py`.
- Pipeline-level `.docx` export now routes to the pip-native `DocxExporter`.
- `OfficeExporter` remains available as optional Pandoc-backed fallback/comparison behavior for other formats.
- Loop 8.5 (complete): a reusable Gongmun style profile (`core/exporters/style_profile.py`) is applied to DOCX output (margins, font, size, line spacing, paragraph spacing, Heading 1 size/alignment), covered by `tests/test_gongmun_docx_style_profile.py`. Project-local/reference-guided, not official layout compliance.
- Loop 8.95 (complete): closed implementation gaps — `style_profile.py`, `load_from_toml()`, missing-key fallback, and custom-profile injection are now tested (`tests/test_style_profile.py`); pipeline DOCX test asserts the default style profile; TOML clarified as documentation/loadable (runtime uses the Python constant, no auto-selection).
- Loop 8.96 (complete): DocumentModel integrity validation (`validators/document_model_rules.py`) is now wired into the pipeline when a converter provides a DocumentModel — records `meta["document_model_validation"]` and writes a separate `<stem>.document.validation.txt`, non-blocking and separate from Gongmun validation. Closes the Loop 4 runtime-connection gap. Covered by `tests/test_pipeline_document_model_validation.py`.
- Loop 8.97 (complete): export-status triage. PDF has no dedicated pip-native exporter; `.pdf` routes through the `OfficeExporter` Pandoc/Typst fallback and was mis-reported as stabilized success. Pipeline now tags exports with `stabilized`/`experimental`; CLI shows fallback exports as `출력(fallback·실험적)`. DOCX remains the only stabilized pip-native export. Covered by `tests/test_real_sample_export_status.py`.
- Loop 8.97 (cont.): product-direction clarified — edudoc is **reference-based document generation**, not only format conversion (`docs/product-direction.md`, export truth table in `docs/export-status.md`). Export is not complete until real-sample regression exists; PDF/HWPX/PPTX are fallback/planned, not stable. No code change (docs/roadmap alignment only).
- Loop 8.99 (complete): export quality criteria + regression tests. Defined 5 quality levels (`docs/export-quality-criteria.md`); added realistic wide-table fixture (`tests/fixtures/export/wide_table_activity_report.md`) + DOCX structure regression (`tests/test_docx_realistic_structure_export.py`) + PDF fallback/status test (`tests/test_pdf_export_status.py`). Principle: `file exists != usable document`.
- compose Phase 1 (complete): HWPX render adapter `core/exporters/hwpx_via_hwpskill.py` wraps hwp-skill `md2hwpx` → real structured HWPX (tables `hp:tbl` + Korean preserved), validated via the skill's `validate.py`. Connects the HWPX generation skill to edudoc logic (was the biggest unwired gap). Covered by `tests/test_hwpx_via_hwpskill.py`. Pipeline/compose wiring = Phase 2.
- Loop 8 protected skill adapter/export stabilization slice (complete): inspected protected HWPX skill references and added edudoc-owned minimal HWPX export/validation outside `skills/`; expanded export metadata contract and added validated Gongmun export fixtures/tests. HWPX export is experimental, not stable/layout-compliant.
- Loop 8 sample filtering / DOCX table quality slice (complete): directory runs now skip sample control files and generated artifacts; DOCX wide/form tables use a compact landscape table strategy with table quality metadata. PDF remains downstream/fallback and HWPX remains experimental.
- Loop 8 safe HWP intake adapter slice (complete): `core/adapters/hwpx_skill_adapter.py`
  wraps the protected `skills/hwpx-skill-main` HWP -> HWPX flow without editing
  the skill, copying it into core, installing packages, or cloning repositories.
  `.hwp` intake prefers HWP -> temporary HWPX -> Markdown/DocumentModel only
  when an installed or explicitly local `hwp2hwpx` engine is available; the
  pyhwp legacy fallback remains in place. HWP input still does not imply HWPX
  final output.
- Loop 8 TargetDocumentProfile extraction slice (complete):
  `core/target_document_profiles.py` defines edudoc-owned profiles extracted
  from protected `skills/hwpx-skill-main` references for `standard_gongmun`,
  `government_press_release`, and `public_institution_plan`. Profiles define
  required fields, source-profile facts, sections, unknown-field policy,
  validation targets, and optional HWPX renderer references. They do not run
  protected skill scripts, install dependencies, clone repositories, generate
  final documents, or change exporter behavior.
- Loop 8 SourceProfile/DocumentPlan scaffold slice (complete):
  `core/source_profile.py` extracts deterministic source facts from normalized
  Markdown/DocumentModel input, and `core/document_plan.py` maps those facts
  into the `public_institution_plan` planning scaffold. Reference PDFs under
  `references/document-types/*/samples/` are tracked as reference samples, not
  parsed. The output is still a planning scaffold, not a final generated report.
- Loop 8 public-plan Markdown generator slice (complete):
  `core/generators/public_plan_generator.py` renders a
  `public_institution_plan` DocumentPlan into a conservative Markdown draft with
  public-plan sections, reference sample paths, and `확인 필요` for missing facts.
  It does not call an LLM, parse PDF/HWPX, export DOCX/PDF/HWPX, or modify
  protected skills.
- Loop 8 public-plan CLI connection slice (complete):
  `scripts/public_plan/generate_from_samples.py` reads sample files through the
  existing converter registry, builds SourceProfile and DocumentPlan artifacts,
  writes `public_plan.generated.md`, and can optionally export DOCX through the
  pip-native `DocxExporter`. It does not parse reference PDFs or add new
  dependencies.
- Dedicated PDF exporter file does not exist yet; PDF remains fallback/experimental through `OfficeExporter`.

## Export Status

- DOCX is implemented through `core/exporters/docx_exporter.py` using `python-docx`.
- DOCX can run without Pandoc, Typst, LaTeX, LibreOffice, MS Office, or HWP installation.
- Pipeline DOCX export is covered by `tests/test_pipeline_docx_export.py`.
- DOCX table/form quality is the current Loop 8 priority before PDF stabilization.
- `DocxExporter` reports `table_count`, `max_table_column_count`, `wide_table_detected`, `wide_table_strategy`, and `warnings`.
- HWPX has an experimental minimal exporter in `core/exporters/hwpx_exporter.py`.
- HWPX package integrity checks live in `validators/hwpx_package_rules.py`.
- Dedicated PDF exporter remains planned until a narrow pip-native exporter is added.

See `docs/export-status.md` for the current export audit.

## Loop 8 Scope

- Stabilize export from validated Markdown.
- Keep export work separate from HWP/HWPX input conversion.
- Keep export downstream of document generation and validation.
- Preserve the HWPX-first normalization path.
- Preserve Gongmun generation and validation behavior.
- Keep heavy external tools optional unless the user explicitly chooses a fallback path.

## Product Direction Reset

The next implementation work should not be framed as "convert samples to another
extension." It should move toward:

- document understanding profile
- user request planner
- official report generator
- document-type validators
- template/render/export after generation

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
- Pipeline HWPX export uses `HwpxExporter` and is marked experimental.
- Pipeline PDF export remains fallback/experimental or structured failure.
- Export entries expose the current metadata contract.
- Directory runs skip repository/control files such as `README.md` and `AGENTS.md`.
- Generated outputs are written to the configured output directory, not back into `samples/`.
- SourceBundle creation writes no outputs and records ignored/generated/control
  files as manifest entries.
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
python tests/test_source_bundle.py
python tests/test_sample_input_filtering.py
python tests/test_docx_table_quality.py
python tests/test_docx_wide_table_metadata.py
python tests/test_gongmun_export_docx_stable.py
python tests/test_gongmun_export_pdf_status.py
python tests/test_gongmun_export_hwpx.py
python tests/test_export_metadata_contract.py
python tests/test_protected_skills_not_modified.py
python tests/test_hwpx_skill_adapter.py
python tests/test_target_document_profiles.py
python tests/test_source_profile_document_plan.py
python tests/test_public_plan_generator.py
python tests/test_public_plan_cli.py
python scripts/harness/check_dependency_policy.py
python scripts/harness/check_hwp_priority_drift.py
```
