# edudoc AGENTS.md

This file is the shared working contract for Codex, Claude, and other coding agents in this repository.
Agent-specific files such as `CLAUDE.md` may add local guidance, but this file is the project-level source of truth.

## Project Goal

edudoc is an HWPX-first local document normalization, validation, and content generation engine.

edudoc is not merely a file-format converter. The product goal is reference-based document generation: learn reusable writing rules, structure patterns, and style profiles from reference documents, then generate new documents (공문, 활동보고서, 신청서/사업계획서, 홍보용 자료, 안내문, 발표/배포용 문서) and export them. See `docs/product-direction.md`.

Current MVP:
- HWPX-first local document processing
- HWPX input -> DocumentModel(JSON) and/or Markdown
- gongmun_rules validation
- validation report output
- DOCX/PDF/HWPX/PPTX export is optional and not part of the core MVP gate

Generation-side companion workflow:
- user brief / notes / source material -> Gongmun Writer Skill
- Gongmun Writer Skill -> Gongmun Markdown draft
- Gongmun Markdown draft -> gongmun_rules validation -> validation report

Default input priority:
1. HWPX
2. Markdown
3. HWP legacy/fallback compatibility input
4. DOCX/PDF/PPTX future adapters

HWP binary input may be supported for compatibility, but new architecture, tests, and harness checks must be designed around HWPX first.

Input formats may include:
- HWP
- HWPX
- PDF
- DOCX
- plain text
- Markdown

Output formats may include:
- Markdown
- DOCX
- PPTX
- PDF
- HWPX

The current normalized human-readable format is Markdown.
The intended structured internal model is DocumentModel(JSON), introduced incrementally.
HWPX-first work should preserve structure in metadata or DocumentModel-compatible fields when possible.

## Core Rules

- **User convenience first** — the end user must run the service without manually installing or configuring extra tools; anything required must come through `pip install -r requirements.txt`.
- **Keep the project lightweight** — prefer pip-native dependencies as the default engine; treat heavy binaries (Pandoc, LaTeX, bundled `.exe`) as optional fallback that the default workflow never requires.
- Always normalize source documents to Markdown before generating final outputs.
- Prefer structure-preserving conversion over OCR when source structure is available.
- Keep transformation layers separate: input adapters, normalization, generation, validators, and output adapters.
- Keep input conversion separate from output export.
- Do not hardcode secrets, server credentials, API keys, or private machine paths.
- Validate round-trip quality when possible.
- Use code-based validators for rules that can be checked deterministically.
- Do not copy third-party skill or tool source code into this repository unless the license and maintenance plan are explicit.

## Current Architecture

### `core/converter_base.py`

Defines the common interface for input converters.
Input converters should produce Markdown.

### `core/document_model.py`

Defines the minimal DocumentModel(JSON)-serializable structure.
Current HWPX models may be derived from Markdown fallback structure and must say so in `raw_meta.structure_source`.

### `core/markdown_converter.py`

Handles existing Markdown drafts as already-normalized input.
This is a secondary input path after HWPX for authoring and testing.

### `core/hwp_converter.py`

Handles HWP/HWPX input conversion.

Current responsibility:
- `.hwpx` -> Markdown (python-hwpx `HwpxDocument.export_markdown`)
- `.hwp` -> Markdown (pyhwp HTML transform -> markdownify); legacy/fallback compatibility path, verified on sample

Do not add DOCX, PPTX, PDF, or HWPX export behavior here.

### `core/registry.py`

Selects an input converter by file extension.
New input converters should be registered here instead of branching inside unrelated converters.

### `core/pipeline.py`

Coordinates source file processing.

Current responsibility:
- source file -> converter lookup -> Markdown output under `exports/`
- write `exports/<stem>.document.json` when a converter provides `ConvertResult.document_model`
- optional public-office validation
- optional DOCX/PDF export through `core/exporters/`

Future responsibility:
- HWPX export when a stable HWPX exporter is added

### `core/exporters/`

Handles Markdown -> final deliverables.

Default exporter direction: pip-native exporters (no external binary required).
- `markdown_blocks.py`: parse Markdown once (markdown-it-py) into a shared block structure
- implemented: `docx_exporter.py`: Markdown -> DOCX (python-docx)
- planned: `pdf_exporter.py`: Markdown -> PDF (reportlab; register a Korean-capable system font)
- planned: `hwpx_exporter.py`: Markdown -> HWPX (python-hwpx)
- planned: `pptx_exporter.py`: Markdown -> PPTX (python-pptx)

Fallback engine (optional; higher fidelity, complex tables, or comparison only):
- `pandoc_exporter.py`: Markdown -> DOCX/PDF/... via Pandoc, with Typst as the PDF engine

Migration note: `office_exporter.py` (Pandoc + Typst) is being refactored into
`pandoc_exporter.py` as the fallback; the pip-native exporters above are the default.

### `validators/`

Contains rule-based validation.

Use this layer for:
- public-office document rules
- education-office document conventions
- heading structure
- attachment consistency
- date, amount, and unit formatting
- risky or forbidden expressions
- output sanity checks

### `connectors/`

Contains input triggers and integrations.

Current responsibility:
- local folder watching

Future integrations may include:
- Google Drive
- Notion
- web upload
- API ingestion

### `skills/gongmun_writer/`

Defines the project-local Gongmun Writer Skill.
This is a generation guide for public-office-style Markdown drafts, not a converter, validator, exporter, API, or runtime.
Generated drafts should be validated later by `validators/gongmun_rules.py`.

## Primary Workflow

1. Ingest HWPX source document by default.
2. Convert source to DocumentModel(JSON)-compatible structure and/or Markdown.
3. Validate normalized representation with `gongmun_rules`.
4. Optionally enrich or generate content.
5. Export Markdown to the requested final format.
6. Verify output against target format rules.
7. Save or report validation results when possible.

## Format Strategy

### HWP/HWPX

- Prefer HWPX for structured processing.
- HWPX is the default MVP input and must drive new architecture, tests, and harness checks.
- For binary `.hwp`, prefer HWP -> HWPX -> Markdown when a reliable converter is available.
- `hwp2md` may be used as an external CLI fallback or comparison adapter.
- Do not assume binary HWP round-trip quality without representative sample checks.
- Baseline sample binary `.hwp` -> Markdown is implemented (pyhwp -> HTML -> markdownify), but it is a legacy/fallback compatibility path, not the default MVP direction.

### DOCX/PPTX/PDF

- Use Markdown or DocumentModel(JSON)-derived data as the source for generated outputs.
- Use pip-native libraries as the default export engine: python-docx (DOCX), reportlab (PDF), python-pptx (PPTX), python-hwpx (HWPX).
- Use Pandoc (with Typst as the PDF engine) only as an optional high-fidelity or comparison fallback, never in the default install-and-run path.
- Use reference templates when layout consistency matters.
- Validate generated files when possible.
- Current output priority is DOCX -> PDF -> HWPX -> PPTX -> direct binary HWP handling.

### HWPX Output

- Keep HWPX output separate from HWP/HWPX input conversion.
- Add HWPX generation in a dedicated exporter such as `core/exporters/hwpx_exporter.py`.
- Apply namespace fixes, layout cleanup, and validation before treating HWPX output as deliverable.

## External Tool Policy

Approved reference tools and repositories:
- Claude Marketplace HWP skill
- `jkf87/hwpx-skill`
- `hephaex/hwp2md`
- Claude Marketplace `md-to-office`
- Anthropic official `pdf`, `pptx`, and `docx` skills

Rules:
- Prefer subprocess wrappers, pip dependencies, or separately installed binaries.
- Lightweight, cross-platform pip dependencies declared in `requirements.txt` are pre-approved and need no separate confirmation, because users install them with `pip install -r requirements.txt`. Heavyweight or platform-specific binaries and engines (e.g. bundled Pandoc, a LaTeX/`pdflatex` engine) stay optional and require confirmation before install.
- Do not vendor large third-party source trees into this repository.
- Record license constraints in `docs/license-notes.md` when that file is added.
- Treat low-trust, low-star, or unclear-license tools as optional adapters, not core dependencies.

## Required Checks

When changing input conversion:
- Prioritize HWPX sample conversion.
- Run representative sample conversion.
- Check headings, paragraphs, tables, images, and attachments when available.
- Confirm Markdown output is readable and stable.

When changing output exporters:
- Generate at least one sample output when the required external tool is available.
- Confirm the output file exists and has nonzero size.
- Return structured failure results when external tools are missing.
- Keep heavyweight external tools optional unless the user explicitly chooses that output path.

When changing validators:
- Add or update a focused test case.
- Confirm both passing and failing cases are handled.
- Keep conversion/document integrity rules separate from public-office writing rules.

Current basic test command:

```bash
python tests/test_pipeline.py
python tests/test_hwpx_document_model.py
python tests/test_document_model_rules.py
python tests/test_gongmun_writer_examples.py
python tests/test_gongmun_generator.py
python tests/test_gongmun_cli.py
python scripts/harness/check_dependency_policy.py
python scripts/harness/check_hwp_priority_drift.py
```

Current manual run commands:

```bash
python main.py run samples/
python main.py watch
```

## Canonical Loop Roadmap Policy

Before proposing, naming, or starting a new loop, read:

- `docs/ROADMAP.md`
- `tasks/current_task.md`
- `tasks/HANDOFF.md`
- `MEMORY.md`

`docs/ROADMAP.md` is the canonical source for loop numbering.

Do not reassign loop numbers based on implementation order.

Do not treat the most recently implemented feature as the next canonical loop.

If a later-loop feature was implemented early, do not renumber it. Record it as implemented early.

Do not skip pending lower-numbered loops unless the user explicitly approves the skip.

When choosing the next loop, select the lowest-numbered pending canonical loop by default.

Current canonical next loop:

```text
Loop 8 — validated Markdown -> DOCX/HWPX/PDF export stabilization
```

Validation-rule expansion and folder workflow integration are useful future tasks, but they are not the next canonical loop unless explicitly inserted by the user.

## Documentation Map

Existing project docs:
- `CLAUDE.md`: Claude-specific guidance and project communication rules
- `MEMORY.md`: durable project decisions and session continuity notes
- `docs/ROADMAP.md`: canonical loop numbering and next-loop policy
- `docs/HARNESS.md`: practical harness rules for coding agents
- `docs/SUCCESS_CRITERIA.md`: current conversion success criteria
- `docs/format-rules.md`: format-specific rules
- `docs/test-plan.md`: verification procedures
- `docs/license-notes.md`: third-party tool and license constraints
- `docs/gongmun-writing-skill.md`: Gongmun Writer Skill purpose and boundaries
- `docs/product-direction.md`: four workflows and the reference-based generation goal
- `docs/export-status.md`: exporter truth table and honest export status
- `docs/export-quality-criteria.md`: conversion quality levels (format/content/structure/layout/generation)
- `skills/README.md`: notes about external skill references

## Change Discipline

- Keep edits scoped to the requested task.
- Do not rewrite existing architecture unless explicitly asked.
- Prefer small adapters over broad refactors.
- Preserve existing behavior when adding new layers.
- Explain high-impact changes before making them.
- Ask before deleting files, overwriting large documents, installing external tools, or changing global machine state.

## Codex Notes

- Read Markdown files containing Korean text with explicit UTF-8 handling.
- When working in PowerShell, use `Get-Content -Encoding UTF8` for Korean project docs.
- If Python execution is blocked by the local environment, report that verification could not run instead of assuming failure in the code.
- If Git reports dubious ownership, do not change global Git config without user approval.
