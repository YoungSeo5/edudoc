# HANDOFF

## Current Goal

Product direction reset is complete for the first documentation pass.

edudoc should be treated as a document task automation system:

```text
source/reference materials + user intent
-> generated task document
-> document-type validation
-> final rendering
```

It should not be treated as a simple file-format conversion tool.

Loop 8 sample filtering and DOCX form/table quality slice is complete.

Current status:
- SourceBundle intake foundation now exists: it builds a filtered source manifest
  and writes no outputs.
- Documentation now separates the product goal from exporter mechanics.
- Export remains the final rendering step, not the product goal.
- DOCX export remains the partially stabilized pip-native path.
- DOCX form/table quality is the current priority before PDF rendering work.
- Directory runs skip repository/control files and generated artifacts in `samples/`.
- Wide/form tables now use compact landscape DOCX handling and expose table quality metadata.
- PDF export remains fallback/experimental through `OfficeExporter`.
- HWPX now has an edudoc-owned minimal exporter in `core/exporters/hwpx_exporter.py`, marked experimental.
- Package-level HWPX validation lives in `validators/hwpx_package_rules.py`.
- HWP intake now has an edudoc-owned adapter in
  `core/adapters/hwpx_skill_adapter.py` that wraps the protected
  `skills/hwp-skill` HWP -> HWPX flow without editing the skill or doing
  hidden install/clone setup.
- `.hwp` intake prefers HWP -> temporary HWPX -> Markdown/DocumentModel when an
  installed or explicitly local `hwp2hwpx` engine is available. If not, the
  existing pyhwp fallback remains. HWP input does not imply HWPX final output.
- TargetDocumentProfile extraction now exists in
  `core/target_document_profiles.py` for `standard_gongmun`,
  `government_press_release`, and `public_institution_plan`. These profiles
  extract protected `skills/hwp-skill` document-type knowledge into
  edudoc-owned metadata. They do not execute protected scripts, generate final
  documents, or change exporter behavior.
- SourceProfile/DocumentPlan scaffold now exists. `core/source_profile.py`
  extracts deterministic source facts from Markdown/DocumentModel input, and
  `core/document_plan.py` maps them into the `public_institution_plan` planning
  scaffold. Reference PDFs are tracked as reference samples but not parsed.
  This is not yet a final report generator.
- Public-plan Markdown generation now exists in
  `core/generators/public_plan_generator.py`. It renders a
  `public_institution_plan` DocumentPlan into a conservative Markdown draft. It
  does not call an LLM, parse PDFs, export final files, or modify protected
  skills.
- Public-plan CLI connection now exists in
  `scripts/public_plan/generate_from_samples.py`. It reads source samples,
  builds SourceProfile and DocumentPlan JSON, writes a generated Markdown draft,
  and can optionally export DOCX through `DocxExporter`.
- Protected skill files under `skills/hwp/`, `skills/hwp-skill/`,
  `skills/rhwp-edit/`, `skills/rhwp-advanced/`, and
  `skills/hwp-skill/` remain reference-only and were not modified.

## Files Changed

Product direction reset:
- `core/source_bundle.py`
- `tests/test_source_bundle.py`
- `core/input_filter.py`
- `docs/product-direction.md`
- `docs/workflows.md`
- `AGENTS.md`
- `README.md`
- `samples/AGENTS.md`
- `samples/README.md`
- `docs/export-status.md`
- `docs/export-quality-criteria.md`
- `docs/test-plan.md`
- `docs/ROADMAP.md`
- `tasks/current_task.md`
- `tasks/HANDOFF.md`
- `MEMORY.md`

SourceBundle intake foundation:
- `core/source_bundle.py` (new)
- `core/input_filter.py` (adds skip reasons while preserving `is_processable_input`)
- `tests/test_source_bundle.py` (new)
- `docs/workflows.md`
- `docs/test-plan.md`
- `tasks/current_task.md`
- `tasks/HANDOFF.md`
- `MEMORY.md`

Loop 8 sample filtering / DOCX table quality slice:
- `core/input_filter.py` (new)
- `main.py` (watch filtering)
- `core/pipeline.py` (directory filtering + DOCX table metadata in export entries)
- `core/exporters/docx_exporter.py` (wide-table strategy + metadata)
- `tests/fixtures/export/wide_activity_report.md` (new)
- `tests/fixtures/export/business_plan_form.md` (new)
- `tests/test_sample_input_filtering.py` (new)
- `tests/test_docx_table_quality.py` (new)
- `tests/test_docx_wide_table_metadata.py` (new)
- `docs/export-status.md`
- `docs/export-quality-criteria.md`
- `docs/test-plan.md`
- `tasks/current_task.md`
- `tasks/HANDOFF.md`
- `MEMORY.md`

Loop 8 protected skill adapter/export stabilization slice:
- `core/exporters/hwpx_exporter.py` (new)
- `validators/hwpx_package_rules.py` (new)
- `core/pipeline.py` (HWPX exporter route + metadata contract)
- `core/exporters/__init__.py`
- `core/exporters/docx_exporter.py` (metadata)
- `core/exporters/office_exporter.py` (metadata)
- `tests/fixtures/gongmun/valid_gongmun.md` (new)
- `tests/test_gongmun_export_docx_stable.py` (new)
- `tests/test_gongmun_export_pdf_status.py` (new)
- `tests/test_gongmun_export_hwpx.py` (new)
- `tests/test_export_metadata_contract.py` (new)
- `tests/test_protected_skills_not_modified.py` (new)
- `docs/folder-responsibility.md` (new)
- `docs/export-status.md`
- `docs/export-quality-criteria.md`
- `docs/format-rules.md`
- `docs/test-plan.md`
- `tasks/current_task.md`
- `tasks/HANDOFF.md`
- `MEMORY.md`

Loop 8 safe HWP intake adapter slice:
- `core/adapters/__init__.py` (new)
- `core/adapters/hwpx_skill_adapter.py` (new)
- `core/hwp_converter.py` (prefers safe HWP -> HWPX normalization before pyhwp fallback)
- `tests/test_hwpx_skill_adapter.py` (new)
- `docs/test-plan.md`
- `tasks/current_task.md`
- `tasks/HANDOFF.md`
- `MEMORY.md`

Loop 8 TargetDocumentProfile extraction slice:
- `core/target_document_profiles.py` (new)
- `tests/test_target_document_profiles.py` (new)
- `docs/target-document-profiles.md` (new)
- `docs/test-plan.md`
- `tasks/current_task.md`
- `tasks/HANDOFF.md`
- `MEMORY.md`

Loop 8 SourceProfile/DocumentPlan scaffold slice:
- `core/source_profile.py` (new)
- `core/document_plan.py` (new)
- `tests/test_source_profile_document_plan.py` (new)
- `docs/target-document-profiles.md`
- `docs/test-plan.md`
- `tasks/current_task.md`
- `tasks/HANDOFF.md`
- `MEMORY.md`

Loop 8 public-plan Markdown generator slice:
- `core/generators/public_plan_generator.py` (new)
- `core/generators/__init__.py`
- `tests/test_public_plan_generator.py` (new)
- `docs/target-document-profiles.md`
- `docs/test-plan.md`
- `tasks/current_task.md`
- `tasks/HANDOFF.md`
- `MEMORY.md`

Loop 8 public-plan CLI connection slice:
- `scripts/public_plan/generate_from_samples.py` (new)
- `tests/test_public_plan_cli.py` (new)
- `docs/target-document-profiles.md`
- `docs/test-plan.md`
- `tasks/current_task.md`
- `tasks/HANDOFF.md`
- `MEMORY.md`

Loop 8.5 (style profile):
- `core/exporters/style_profile.py` (new)
- `templates/gongmun/gyeonggi_style_profile.toml` (new)
- `core/exporters/docx_exporter.py` (applies the profile)
- `tests/test_gongmun_docx_style_profile.py` (new)
- `docs/export-style-profile.md` (new)
- `docs/export-status.md`
- `docs/test-plan.md`
- `tasks/current_task.md`
- `tasks/HANDOFF.md`
- `MEMORY.md`

Previous Loop 8 step (DOCX routing, already complete):
- `core/pipeline.py`
- `tests/test_pipeline_docx_export.py`

## Latest Verification

`python -m pytest tests` was attempted, but pytest is not installed in this environment.
Focused tests were run individually instead.

Latest passing commands:
- `python tests/test_sample_input_filtering.py`
- `python tests/test_docx_table_quality.py`
- `python tests/test_docx_wide_table_metadata.py`
- `python tests/test_pipeline.py`
- `python tests/test_gongmun_docx_export.py`
- `python tests/test_pipeline_docx_export.py`
- `python tests/test_style_profile.py`
- `python tests/test_docx_realistic_structure_export.py`
- `python tests/test_pdf_export_status.py`
- `python tests/test_export_metadata_contract.py`
- `python tests/test_gongmun_export_docx_stable.py`
- `python scripts/harness/check_dependency_policy.py`
- `python scripts/harness/check_hwp_priority_drift.py`

Result: all focused commands passed. Python commands required elevated execution
because the default sandbox hit the known Windows logon-session error.

## Style Profile Added

- `DocumentStyleProfile` (frozen dataclass) + `DEFAULT_GONGMUN_STYLE_PROFILE` in `core/exporters/style_profile.py`.
- `templates/gongmun/gyeonggi_style_profile.toml` documents the same values; loadable via stdlib `tomllib` (`load_from_toml`), no new dependency.

## DOCX Style Properties Applied

`DocxExporter._apply_style_profile()` applies:
- page margins (top / bottom / left / right)
- Normal style font family (+ East Asian font for Korean)
- Normal style font size
- Normal style line spacing
- Normal style paragraph spacing after
- Heading 1 font family + font size
- Heading 1 alignment (default center)

Markdown parsing / block-to-Word conversion is unchanged.

## Style Profile Is Project-Local

The profile is project-local and reference-guided. It does NOT claim official
institution-approved layout compliance. The reference PDF is not parsed in code or tests.

## Tests Run

- python tests/test_pipeline.py
- python tests/test_hwpx_document_model.py
- python tests/test_document_model_rules.py
- python tests/test_gongmun_writer_examples.py
- python tests/test_gongmun_generator.py
- python tests/test_gongmun_cli.py
- python tests/test_gongmun_docx_export.py
- python tests/test_pipeline_docx_export.py
- python tests/test_gongmun_docx_style_profile.py
- python tests/test_docx_exporter.py
- python scripts/harness/check_dependency_policy.py
- python scripts/harness/check_hwp_priority_drift.py

Result: all 12 passed in this environment.

## Current Status

- Loop 8 is the current canonical loop; Loop 8.5 is an inserted sub-loop and is complete.
- Pipeline-level `.docx` export uses the pip-native `DocxExporter` by default.
- DOCX output now applies the conservative Gongmun style profile.
- `OfficeExporter` remains optional Pandoc/Typst fallback/comparison behavior.
- Default DOCX export does not require Pandoc, Typst, LaTeX, LibreOffice, MS Office, or HWP installation.

## Known Limitations

- DOCX style application is smoke-tested, not layout-perfect, and not officially compliant.
- Only `Heading 1` gets heading-level styling (Gongmun title). Deeper headings use default styles.
- Style values are conservative project defaults, not derived from a verified official template.
- Dedicated pip-native PDF/HWPX/PPTX exporters still do not exist.

## Next Recommended Loop 8 Step

Continue by choosing one narrow product-direction slice:

- public-plan validation rules for generated Markdown
- user request planner
- official report generator
- document-type validators
- template/render/export after generation

Exporter work such as PDF/HWPX/DOCX stabilization remains valid, but it should be
framed as final rendering after generation and validation, not as the whole product.

Do not recommend validation-rule expansion or folder workflow integration as the next canonical loop unless the user explicitly inserts an extra loop.

## Known Local Execution Issue

On this Windows environment, Python commands may fail in the default sandbox with a logon-session error.

If this happens, rerun the same verification command with approved elevated execution and report the result:

- `python tests/test_pipeline.py`
- `python tests/test_hwpx_document_model.py`
- `python tests/test_document_model_rules.py`
- `python tests/test_gongmun_writer_examples.py`
- `python tests/test_gongmun_generator.py`
- `python tests/test_gongmun_cli.py`
- `python tests/test_gongmun_docx_export.py`
- `python tests/test_pipeline_docx_export.py`
- `python tests/test_gongmun_docx_style_profile.py`
- `python scripts/harness/check_dependency_policy.py`
- `python scripts/harness/check_hwp_priority_drift.py`

Do not use elevated execution for install, delete, deploy, network, or global configuration commands without explicit user approval.

## Loop 8.9 Audit Gate

### Audit Scope

Inspected across Loops 1??.5: roadmap/task docs (AGENTS.md, CLAUDE.md, MEMORY.md, docs/ROADMAP.md, docs/HARNESS.md, docs/test-plan.md, docs/export-status.md, docs/gongmun-writing-skill.md, tasks/current_task.md, tasks/HANDOFF.md); HWPX/DocumentModel/metadata code (core/document_model.py, core/hwp_converter.py, core/hwpx_metadata.py, core/pipeline.py, core/registry.py, validators/document_model_rules.py); Gongmun generation/validation (validators/gongmun_rules.py, core/generators/gongmun_generator.py, scripts/gongmun, skills/gongmun_writer); exporters/style profile (core/exporters/*, templates/gongmun, docs/export-style-profile.md); harness scripts; all tests; requirements.txt.

### Verification Run

- pytest discovery: `python -m pytest tests -q` ??pytest module NOT installed; ran test files individually instead.
- Individual: all 10 test files + 2 harness checks (test_pipeline, test_hwpx_document_model, test_document_model_rules, test_gongmun_writer_examples, test_gongmun_generator, test_gongmun_cli, test_gongmun_docx_export, test_pipeline_docx_export, test_gongmun_docx_style_profile, test_docx_exporter, check_dependency_policy, check_hwp_priority_drift).

### Results

- 12 / 12 passed. No failures. No skips (pytest discovery unavailable, covered by individual runs).

### Fixes Applied

- Documentation only: added Loop 8.5 to `docs/ROADMAP.md` as an inserted Loop 8 sub-loop (canonical list + status + note that it does not replace Loop 9/10). No code changes.

### Remaining Limitations

- pytest is not installed in this environment; there is no aggregate test-discovery run (individual runs cover all files).
- `reportlab` and `python-pptx` are declared in requirements.txt ahead of their (planned) exporters; not forbidden and pip-native, but not yet used by committed code.
- MEMORY.md retains the historical 2026-07-01 ".hwp 寃⑹긽" note; it is explicitly marked superseded by the 2026-07-02 HWPX-first decision (drift check passes).
- DOCX styling is smoke-tested, not layout-perfect; PDF/HWPX/PPTX exporters remain planned.

### Next Recommended Step

Stay within Loop 8. Candidate slices: narrow pip-native PDF exporter (reportlab) reusing the style profile; narrow HWPX exporter feasibility slice (python-hwpx) reusing the style profile; or DOCX template-file support if the user provides a real template. Do not jump to Loop 9 unless the user explicitly approves.

## Loop 8.95 Gap Closure

### Implementation Substance Check

| Area | Runtime-connected? | Test coverage | Notes |
|---|---|---|---|
| DOCX exporter (`docx_exporter.py`) | yes | yes | pipeline + direct; applies style profile |
| Style profile module (`style_profile.py`) | yes | yes | `DEFAULT_GONGMUN_STYLE_PROFILE` used by `DocxExporter` |
| `load_from_toml()` | no (utility, not called at runtime) | yes | tested in `test_style_profile.py` |
| TOML profile (`gyeonggi_style_profile.toml`) | documentation-only | yes (drift guard) | runtime uses the Python constant, not the TOML |
| Pipeline DOCX route (`pipeline._select_exporter`) | yes | yes | `.docx` -> `DocxExporter`; default style now asserted |
| `markdown_blocks.py` | yes | yes | shared parser used by the exporter |
| `office_exporter.py` (Pandoc/Typst) | fallback only | indirect | non-docx formats; optional |
| `document_model_rules.py` (Loop 4) | no (test-only) | yes | implemented + tested but not wired into the pipeline |
| PDF exporter | planned | no | no file exists |
| HWPX exporter | planned | no | no file exists |
| PPTX exporter | planned | no | no file exists |
| `pandoc_exporter.py` | planned | no | migration target; not created |

### Gaps Closed

- `style_profile.py` is now tested (`tests/test_style_profile.py`): default sane values, `load_from_toml()`, missing-key fallback, and custom-profile injection into DOCX.
- Custom `DocumentStyleProfile` injection is proven to change DOCX output (not hardcoded).
- Pipeline-level DOCX test now asserts the default style profile is applied (top margin).
- TOML status documented honestly (documentation/loadable; runtime uses the Python constant; no auto-selection).
- Consolidated `test_style_profile_toml.py` into `test_style_profile.py`.

### Remaining Planned Areas

- PDF / HWPX / PPTX exporters (no files yet) and `pandoc_exporter.py` migration target.
- `document_model_rules.py` is implemented + tested but not wired into the runtime pipeline (connecting it changes runtime behavior; left for an explicit decision).
- `reportlab` / `python-pptx` are declared in `requirements.txt` ahead of their exporters.

### Verification Run

- `python -m pytest tests -q` -> pytest module not installed; ran test files individually.
- 11 test files + 2 harness checks run individually.

### Result

- 13 / 13 passed. No failures. pytest discovery unavailable (covered by individual runs).

### Next Recommended Step

Stay within Loop 8. One of: narrow pip-native PDF exporter slice (reportlab, reusing the style profile); narrow HWPX exporter feasibility/smoke slice (python-hwpx, reusing the style profile); or optional real DOCX/HWPX template-file support if the user provides an actual template. Do not recommend validation-rule expansion, folder workflow, API, or web UI as the next canonical loop.

## Loop 8.96 ??DocumentModel integrity validation pipeline wiring

### Files Changed

- `core/pipeline.py` ??wired DocumentModel integrity validation
- `tests/test_pipeline_document_model_validation.py` (new)
- `docs/test-plan.md`, `tasks/current_task.md`, `tasks/HANDOFF.md`, `MEMORY.md`
- Housekeeping: cleared stale generated files from `exports/`, added `exports/.gitkeep`

### How DocumentModel Validation Is Connected

In `Pipeline.process_file`, after a converter provides `ConvertResult.document_model`
and the `.document.json` is written, the pipeline runs `validators.document_model_rules.validate`.
It is non-blocking (reports only, never fails the pipeline) and runs independently of
`validate_gongmun`. When no DocumentModel is present, it records an `available: False` result.

### Separate Report File

Yes ??when `write_validation_report` is enabled, a separate
`exports/<stem>.document.validation.txt` is written. The Gongmun
`<stem>.validation.txt` report is left untouched.

### Metadata Recorded

`result.meta["document_model_validation"]`:
- available: `{ "available": True, "passed": bool, "summary": str }`
- unavailable: `{ "available": False, "reason": "converter did not provide document_model" }`
- when a report file is written: `result.meta["document_model_validation_report"]` holds its path.

### Tests Run

- 12 test files + 2 harness checks (individually; pytest not installed).

### Result

- 14 / 14 passed.

### Current Status

- The Loop 4 DocumentModel integrity validator is now runtime-connected (was test-only in the 8.95 table above).
- HWPX input parsing, Gongmun generation/validation, DOCX export, and style profile behavior are unchanged.

### Remaining Limitations

- DocumentModel validation is metadata/structure integrity only, not a full HWPX AST validator.
- It runs only when a converter provides a DocumentModel (currently the HWPX path).
- PDF/HWPX/PPTX exporters remain planned.

### Next Recommended Loop 8 Step

Narrow pip-native PDF exporter slice (reportlab, reusing the style profile), or a narrow HWPX exporter feasibility slice (python-hwpx), or DOCX/HWPX template-file support if the user provides an actual template. Do not recommend validation-rule expansion, folder workflow, API, or web UI as the next canonical loop.

## Loop 8.97 Real Sample Export Triage

### Real Sample Findings

- Markdown: produced and readable for all real samples (`.hwp`, `.hwpx`, `.md`).
- DOCX: produced and non-empty (hwp ~41KB, hwpx ~45KB); content preserved but wide-table layout is not layout-perfect.
- PDF: produced via fallback (~198KB/~275KB) but NOT usable for wide/complex tables (split/overlapping cells); was previously reported as plain `異쒕젰 ?깃났`.
- Validation report: Gongmun rules report `?뺤씤 ?꾩슂` (e.g. missing `??`) ??expected for non-gongmun samples; this is a validation result, not an export failure.

### Root Cause

There is no dedicated pip-native PDF exporter. `.pdf` export routes through `OfficeExporter` (Pandoc + Typst binary), a fallback path that returns `ok=True` on any produced file, so fallback PDF was presented as stabilized success.

### Change Made

PDF remains available via fallback but is now marked honestly. `meta["exports"]` entries carry `stabilized` (True only for the pip-native `DocxExporter`) and, for fallback formats, `experimental: True` + a layout-warning `note`. The CLI prints fallback exports as `異쒕젰(fallback쨌?ㅽ뿕??` instead of `異쒕젰 ?깃났`. No PDF exporter was implemented.

### Regression Coverage

- `tests/test_real_sample_export_status.py` ??wide-table Markdown fixture; asserts DOCX is `stabilized: True` + non-empty and PDF is `stabilized: False` + `experimental: True`, independent of whether Pandoc/Typst is installed.

### Remaining Limitations

- No dedicated pip-native PDF exporter; fallback PDF layout is unreliable for wide/complex documents.
- DOCX preserves content but is not layout-perfect for large form tables.
- Real HWP/HWPX -> PDF visual fidelity is not asserted automatically (too brittle); covered by the status/honesty test plus a documented manual check.

### Next Recommended Loop 8 Step

Narrow pip-native PDF exporter slice using `reportlab` + the style profile, with real-sample/wide-table regression coverage. Alternatives: HWPX exporter feasibility slice; real template support. Do not recommend validation-rule expansion, folder workflow, API, or web UI as the next canonical loop.

## Loop 8.97 Export Reality Alignment (product direction)

### User-Observed Problem

Markdown conversion for real samples is usable, but DOCX/PDF rendering for real wide-table samples is not trustworthy; fallback PDF was previously reported as plain success.

### Export Status

See the truth table in `docs/export-status.md`. Summary: Markdown normalization = most reliable; DOCX (`DocxExporter`) = partially stabilized, pip-native; PDF (`OfficeExporter` via Pandoc/Typst) = not stabilized / fallback-experimental; HWPX/PPTX = planned.

### Root Cause

No dedicated pip-native PDF exporter; `.pdf` uses the Pandoc/Typst fallback. Misleading "success" was fixed in the prior 8.97 triage (`meta["exports"]` `stabilized`/`experimental` + CLI `異쒕젰(fallback쨌?ㅽ뿕??`).

### Real-Sample Coverage

`tests/test_real_sample_export_status.py` (wide-table Markdown fixture): DOCX `stabilized: True` + non-empty; PDF `stabilized: False` + `experimental: True`. Real HWP/HWPX -> PDF visual fidelity is not asserted (brittle).

### Product Direction Clarification

Added `docs/product-direction.md`: edudoc is not only a converter; it is intended to generate new documents (怨듬Ц, ?쒕룞蹂닿퀬?? ?좎껌???ъ뾽怨꾪쉷?? ?띾낫???먮즺, ?덈궡臾? 諛쒗몴/諛고룷??臾몄꽌) from references, templates, source notes, style profiles, and user briefs. Four workflows: normalization / reference capture / generation / export. "Learning from files" = reference corpus + source notes + style profiles + templates + deterministic extraction (no fine-tuning / no external LLM API unless later decided). ROADMAP.md and AGENTS.md updated to point at it.

### Remaining Limitations

No dedicated pip-native PDF/HWPX/PPTX exporters; fallback PDF layout unreliable; DOCX not layout-perfect for large tables; generation beyond the small deterministic Gongmun harness is not implemented.

### Next Recommended Loop 8 Step

One narrow step: dedicated pip-native PDF exporter slice (reportlab + style profile) with real-sample regression; or HWPX exporter feasibility slice; or reference/template ingestion workflow for new-document generation; or promotional-material generation skill planning. Do not recommend API/web/folder workflow as the next canonical loop unless the user explicitly asks.

## Loop 8.99 Export Quality Criteria

### Problem

Previous tests checked file creation and basic text preservation, not usable document quality ??so broken wide-table DOCX/PDF could pass.

### Quality Levels Defined

`docs/export-quality-criteria.md`: (1) format conversion, (2) content-preserving, (3) structure-preserving, (4) layout-aware rendering, (5) reference-based generation. Current: DOCX levels 1?? solid + level 3 partial; PDF level 1 only (fallback); HWPX/PPTX planned; layout (4) manual-only; generation (5) only the small Gongmun harness.

### Fixtures Added

- `tests/fixtures/export/wide_table_activity_report.md` ??sanitized, fake-data activity report: 10-column table, 8-column table, long cells, section headings, checklist markers, photo placeholder text, multiple sections.

### Tests Added

- `tests/test_docx_realistic_structure_export.py` ??DOCX structure regression: >=3 tables incl. a >=8-column table, long-cell text preserved, headings recognizable, style profile applied, key text present.
- `tests/test_pdf_export_status.py` ??PDF is `OfficeExporter` (not DocxExporter), `stabilized: False`, `experimental: True`; structured failure if the engine is missing. No visual assertion.

### What Is Now Prevented

- PDF fallback can no longer be mistaken for stable export (locked by metadata test).
- DOCX is tested beyond file existence (tables/columns/long cells/headings/style), so a shallow "file created" pass no longer implies a usable document.

### Remaining Limitations

- DOCX not layout-perfect; PDF not stabilized; HWPX/PPTX planned.
- Layout-aware rendering (level 4) and reference-based generation (level 5) are not auto-tested; visual quality still needs manual review or a future renderer-specific check.

### Next Recommended Step

One narrow next Loop 8 step: dedicated pip-native PDF exporter (reportlab) with real-sample regression; or DOCX template support; or HWPX exporter feasibility; or reference/template ingestion planning for generation. Do not start API/web/folder workflow or a full generator prematurely.


