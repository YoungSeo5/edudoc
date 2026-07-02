# Test Plan

This test plan follows the current HWPX-first MVP:

HWPX input -> DocumentModel(JSON)/Markdown -> gongmun_rules validation -> validation report.

Binary `.hwp` remains a legacy/fallback compatibility path. It is not the default MVP input for new harness checks.

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

When the draft is generated from a user brief, use `skills/gongmun_writer/SKILL.md` as the generation guide before running validation.

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
- validation report is created as `*.validation.txt`
- DOCX/PDF export is not attempted unless explicitly requested

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
- validation report is created as `*.validation.txt`
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
- `.hwp` -> Markdown compatibility path remains available when dependencies are installed
- no new architecture or tests should treat HWP as the default MVP input

## Output Checks

Loop 8 focused DOCX smoke test:

```bash
python tests/test_gongmun_docx_export.py
python tests/test_pipeline_docx_export.py
```

Expected:
- Gongmun brief is generated into Markdown
- generated Markdown passes `validators/gongmun_rules.py`
- validated Markdown exports through the pip-native `DocxExporter`
- DOCX output exists and has nonzero size
- visible DOCX text includes the title, `수신`, `관련`, `붙임`, and `끝.`
- pipeline-level `.docx` export uses `DocxExporter`, not Pandoc-backed `OfficeExporter`

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
python tests/test_pdf_export_status.py
```

- Smoke (levels 1–2): file created, non-empty, valid container, key text present
  (`test_gongmun_docx_export.py`, `test_pipeline_docx_export.py`, `test_docx_exporter.py`).
- Structure (level 3): realistic wide-table document — table count, wide-table columns,
  long-cell text, headings, style profile (`test_docx_realistic_structure_export.py`).
- Fallback status: PDF is flagged fallback/experimental, not stable
  (`test_pdf_export_status.py`, `test_real_sample_export_status.py`).
- Manual visual check: layout-aware rendering (level 4) is not auto-tested; review the
  generated DOCX/PDF by hand.
- Not yet automatically tested: layout fidelity, merged cells, page-break behavior, and
  reference-based generation (level 5) beyond the small Gongmun harness.

For DOCX/PDF output:
- output file exists
- output file size is greater than zero
- visible text roughly matches the Markdown source
- headings and lists remain readable

For HWPX output, when added:
- generated package opens in a supported editor
- namespace cleanup has run
- HWPX validation passes
