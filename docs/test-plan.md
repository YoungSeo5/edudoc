# Test Plan

This test plan follows the current HWPX-first foundation, but the product
direction is document task automation:

```text
source/reference materials + user intent
-> generated task document
-> document-type validation
-> final rendering
```

The earlier Phase 0 HWPX harness used this flow:

HWPX input -> DocumentModel(JSON)/Markdown -> gongmun_rules validation -> validation report.

The current generic `main.py run` command and public `Pipeline` normalize inputs
without dispatching a document-type writing validator. Tests expecting a
Gongmun validation report must exercise the isolated dedicated Gongmun workflow.
HWP/HWPX/Markdown extensions and target profiles never select Gongmun validation
in the public Pipeline.

Binary `.hwp` remains a legacy/fallback compatibility path. It is not the default MVP input for new harness checks.

Export tests verify final-rendering channels. They do not by themselves prove the
full product workflow unless source-bundle, request-planning, generation, and
document-type validation are also covered.

## SourceBundle Intake Check

Run:

```bash
python tests/test_source_bundle.py
```

Expected:
- real source-like Markdown/HWP/HWPX files are included in the manifest
- repository/control files such as `README.md`, `README.txt`, `AGENTS.md`,
  `AGENT.md`, `CLAUDE.md`, and `.gitkeep` are ignored
- generated artifacts such as validation reports, document JSON, DOCX, PDF,
  PPTX, and generated HWPX companions are ignored with clear reasons
- unsupported source candidates are recorded separately
- bundle creation writes no outputs into the input directory
- the bundle is JSON-serializable
- no conversion, generation, validation, or export is performed

## Target Document Profile Check

Run:

```bash
python tests/test_target_document_profiles.py
python tests/test_source_profile_document_plan.py
python tests/test_public_plan_generator.py
python tests/test_public_plan_cli.py
```

Expected:
- three target profiles exist: `standard_gongmun`,
  `government_press_release`, and `public_institution_plan`
- profiles are edudoc-owned metadata extracted from protected
  `skills/hwp-skill/` references
- referenced protected skill files exist, but are not modified or copied into
  `core/`
- canonical generation output remains Markdown or DocumentModel
- HWPX skill scripts are recorded only as optional final-renderer references
- missing facts must be marked as `확인 필요`
- `SourceProfile` extracts deterministic source facts from Markdown/
  DocumentModel input: titles, institutions, dates, tables, statistics, budgets,
  schedules, key actions, risks, and attachments
- `DocumentPlan` maps `SourceProfile` facts into the `public_institution_plan`
  scaffold and preserves missing values as `확인 필요`
- `public_plan_generator` renders the DocumentPlan into a conservative
  public-institution plan Markdown draft
- `scripts/public_plan/generate_from_samples.py` connects sample inputs to
  SourceProfile, DocumentPlan, public-plan Markdown, optional DOCX export, and
  optional public-plan HWPX rendering through the protected hwp-skill
  `gyehoek.py` adapter
- PDF files in `references/document-types/*/samples/` are tracked as reference
  samples but are not parsed by this layer

Manual public-plan CLI check:

```bash
python scripts/public_plan/generate_from_samples.py samples --out exports/public-plan
python scripts/public_plan/generate_from_samples.py samples --out exports/public-plan --export docx
python scripts/public_plan/generate_from_samples.py samples --out exports/public-plan --export hwpx
```

Expected:
- `public_plan.source_profile.json`
- `public_plan.document_plan.json`
- `public_plan.generated.md`
- `public_plan.docx` when `--export docx` is used
- `public_plan.hwpskill.input.json`, `public_plan.hwpx`, and
  `public_plan.export.hwpx.json` when `--export hwpx` is used

## Basic Pipeline Check

Run:

```bash
python tests/test_pipeline.py
```

Expected:
- supported input files are converted to Markdown
- unsupported files return a structured failure
- generated Markdown files are saved under `exports/`

## Markdown Draft Workflow

The generic Markdown workflow performs normalization only. The dedicated
Gongmun compatibility workflow is tested separately below.

Prepare a UTF-8 Markdown file with:
- title heading
- body text
- `관련` text when applicable
- `붙임` text when applicable
- ending marker `끝.`

Run:

```bash
python main.py run samples/
```

Expected:
- Markdown is copied or normalized into `exports/`
- no Gongmun `*.validation.txt` report is created by generic `main.py run`
- Gongmun generation and validation are checked through the dedicated workflow below
- DOCX/PDF export is not attempted unless explicitly requested
- `samples/README.md`, `samples/AGENTS.md`, `samples/AGENT.md`, `CLAUDE.md`, `.gitkeep`, validation reports, document JSON, and generated Office outputs are skipped during directory runs
- generated outputs are written to `exports/` or the configured output directory, not back into `samples/`

## Gongmun Writer Skill Check

Use `skills/gongmun_writer/examples/input_brief.md` as source material.
Use `skills/gongmun_writer/source_notes/gyeonggi_rules_summary.md` as reference guidance when revising Gongmun Writer behavior.
Do not parse `references/gongmun/gyeonggi_office_format_example.pdf` in automated tests.

Run:

```bash
python tests/test_gongmun_writer_examples.py
python tests/test_gongmun_generator.py
python tests/test_gongmun_cli.py
```

Expected:
- generated output is Markdown, not DOCX/PDF/HWPX
- unknown facts are marked as `확인 필요`
- the draft includes a title, recipient/contact fields, `관련`, numbered body items, `붙임` when applicable, and `끝.`
- validation remains the responsibility of `validators/gongmun_rules.py`
- the tiny local generator can turn the sample brief into validation-ready Markdown without an external LLM runtime
- the CLI can write `<brief-stem>.generated.md` and `<brief-stem>.validation.txt`

Manual CLI check:

```bash
python scripts/gongmun/generate_from_brief.py skills/gongmun_writer/examples/input_brief.md --out exports/gongmun
```

## HWPX MVP Workflow

Use a representative `.hwpx` sample.

Run:

```bash
python main.py run samples/
```

Expected:
- HWPX input is converted to normalized Markdown and, later, DocumentModel(JSON)-compatible structure
- when a DocumentModel is available, its integrity report may be written as
  `*.document.validation.txt`; no Gongmun writing-validation report is produced
- HWPX remains the first input path considered when adding new structure-preserving checks

Focused smoke test:

```bash
python tests/test_hwpx_document_model.py
python tests/test_pipeline_document_model_validation.py
```

Expected:
- HWPX input produces Markdown
- HWPX input produces `.document.json`
- JSON includes `source_path`, `format`, `paragraphs`, `tables`, `attachments`, and `raw_meta`
- `raw_meta.structure_source` is explicit about whether structure came from a fallback path
- when a DocumentModel is available, the pipeline also runs DocumentModel integrity validation (`validators/document_model_rules.py`), records `meta["document_model_validation"]`, and writes a separate `<stem>.document.validation.txt` report — this is non-blocking and separate from Gongmun writing validation
- when no DocumentModel exists (e.g. plain Markdown input), `meta["document_model_validation"]["available"]` is `False`

Optional DOCX/PDF export:

```bash
python main.py run samples/ --export docx,pdf
```

Expected:
- DOCX/PDF export is attempted
- if Pandoc is missing, export failure is reported without crashing

## Folder Watch Workflow

Run:

```bash
python main.py watch samples/
```

Expected:
- newly added `.md`, `.hwpx`, or `.hwp` files are detected
- supported files flow through the same pipeline as `run`
- failures are printed as structured messages

Optional export mode:

```bash
python main.py watch samples/ --export docx,pdf
```

## HWP Binary Legacy/Fallback Check

Use the `.hwp` sample to prevent regressions in compatibility support.

Expected for now:
- `.hwp` first tries the safe edudoc-owned hwpx-skill adapter path when an
  already installed or explicitly local `hwp2hwpx` engine is available
- the adapter does not auto-install packages, clone repositories, or modify
  protected `skills/` files
- if the adapter is unavailable or the intermediate HWPX read fails, the
  existing pyhwp -> HTML -> markdownify fallback remains available when its
  dependencies are installed
- HWP input does not imply HWPX final output; final rendering is still selected
  later by the user/export pipeline
- no new architecture or tests should treat HWP as the default MVP input

Focused adapter smoke test:

```bash
python tests/test_hwpx_skill_adapter.py
```

Expected:
- a local fake `hwp2hwpx` engine can be called without install/clone behavior
- a missing engine returns a clear structured adapter error
- `HwpSkillConverter` keeps the pyhwp fallback path when the adapter is
  unavailable
- `HwpSkillConverter` prefers the HWP -> HWPX -> Markdown path when the adapter
  succeeds

## Output Checks

Loop 8 focused DOCX smoke test:

```bash
python tests/test_gongmun_docx_export.py
python tests/test_pipeline_docx_export.py
python tests/test_gongmun_export_docx_stable.py
```

Expected:
- Gongmun brief is generated into Markdown
- generated Markdown passes `validators/gongmun_rules.py`
- validated Markdown exports through the pip-native `DocxExporter`
- DOCX output exists and has nonzero size
- visible DOCX text includes the title, `수신`, `관련`, `붙임`, and `끝.`
- pipeline-level `.docx` export uses `DocxExporter`, not Pandoc-backed `OfficeExporter`
- export metadata includes `format`, `ok`, `path`, `exporter`, `stabilized`,
  `experimental`, `requires_optional_tool`, `status`, `note`, and `error`

Loop 8.5 DOCX style profile test:

```bash
python tests/test_gongmun_docx_style_profile.py
python tests/test_style_profile.py
```

Expected:
- validated Gongmun Markdown exports to DOCX through the pip-native `DocxExporter`
- visible text still includes the title, `수신`, `관련`, `붙임`, and `끝.`
- the Gongmun style profile is applied: page margins, Normal font family/size,
  line spacing, paragraph spacing after, and Heading 1 size/alignment
- assertions check property presence/approximate values, not exact Word rendering
- no external office software and no PDF parsing are used
- `tests/test_style_profile.py` also checks default values, `load_from_toml()`, missing-key fallback, and that a custom `DocumentStyleProfile` changes DOCX output

Loop 8.97 export status honesty test:

```bash
python tests/test_real_sample_export_status.py
```

Expected:
- DOCX export is the stabilized pip-native target: `stabilized: True` and non-empty file
- PDF export is flagged `stabilized: False` + `experimental: True` (fallback via Pandoc/Typst), regardless of whether the fallback engine is installed
- the test uses a wide-table Markdown fixture and does not require Pandoc/Typst or HWP/HWPX parsing
- fallback PDF layout is not asserted to be correct (it is not a stabilized exporter)

## Export Quality Tests

`file exists != usable document`. Export tests are layered by quality level
(see `docs/export-quality-criteria.md`):

```bash
python tests/test_docx_realistic_structure_export.py
python tests/test_sample_input_filtering.py
python tests/test_docx_table_quality.py
python tests/test_docx_wide_table_metadata.py
python tests/test_pdf_export_status.py
```

- Smoke (levels 1–2): file created, non-empty, valid container, key text present
  (`test_gongmun_docx_export.py`, `test_pipeline_docx_export.py`, `test_docx_exporter.py`).
- Structure (level 3): realistic wide-table document — table count, wide-table columns,
  long-cell text, headings, style profile (`test_docx_realistic_structure_export.py`).
- Form/table baseline: sample control-file filtering and sanitized form fixtures lock
  DOCX table count, wide-table detection, compact landscape strategy, and table metadata
  (`test_sample_input_filtering.py`, `test_docx_table_quality.py`,
  `test_docx_wide_table_metadata.py`).
- Fallback status: PDF is flagged fallback/experimental, not stable
  (`test_pdf_export_status.py`, `test_real_sample_export_status.py`).
- Manual visual check: layout-aware rendering (level 4) is not auto-tested; review the
  generated DOCX/PDF by hand.
- Not yet automatically tested: layout fidelity, merged cells, page-break behavior, and
  reference-based generation (level 5) beyond the small Gongmun harness.

## Template Quality Pipeline

```bash
python tests/test_extract_style.py
python tests/test_extract_structure.py
python tests/test_template_candidate_public_plan.py
python tests/test_template_quality_pipeline.py
python tests/test_hwpx_template_extraction.py
python tests/test_apply_style.py
python tests/test_build_header.py
```

Expected:
- one `TemplateCandidate` shape is used for HWPX and legacy HWP references
- fake extracted values and unproven styles cannot pass the success gate
- scoped false-positive rules remove known bad candidates before validation
- automatic refinement is bounded to three passes
- validated output does not become `template.json` without explicit approval
- extracted style mapping remains separate from template extraction
- HWPX extraction preserves raw/template XML bytes without namespace rewriting
- unsafe ZIP paths are rejected and partial output is removed
- visible `hp:t` text, section paragraph/table counts, table dimensions, and
  placeholder candidates are reported without modifying section XML

For DOCX/PDF output:
- output file exists
- output file size is greater than zero
- visible text roughly matches the Markdown source
- headings and lists remain readable

For HWPX output:
- generated package exists and is a valid ZIP package
- required package files are present
- mimetype ordering/storage/content is valid
- XML files are well-formed
- preview text preserves key Gongmun text
- editor opening/layout compliance is not claimed by automated tests yet

Loop 8 protected skill adapter/export status tests:

```bash
python tests/test_gongmun_export_docx_stable.py
python tests/test_gongmun_export_pdf_status.py
python tests/test_gongmun_export_hwpx.py
python tests/test_export_metadata_contract.py
python tests/test_protected_skills_not_modified.py
```

Expected:
- tests use `tests/fixtures/gongmun/valid_gongmun.md`, not mutable `samples/`
- DOCX export is pip-native and partially stabilized
- PDF export remains fallback/experimental or structured failure; it is not stable
- HWPX export creates a minimal package through `core/exporters/hwpx_exporter.py`
- HWPX package-level validation runs through `validators/hwpx_package_rules.py`
- HWPX export is marked experimental, not layout-perfect or institution-approved
- protected skill directories under `skills/` are not modified and are not used for hidden setup
