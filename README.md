# edudoc

edudoc is currently an **HWPX-first local document normalization and validation engine**.

Phase 0.5 focuses on this flow:

```text
HWPX input
-> normalized Markdown and/or DocumentModel(JSON)
-> gongmun_rules validation
-> validation report output
```

The current development harness is CLI-first. API and web wrappers should wait until the CLI flow is stable.

## Current Direction

Default MVP input:
- HWPX

Supported compatibility input:
- HWP legacy/fallback input
- Markdown draft input

Current user interface:
- CLI
- local folder watcher

Future user interface:
- API/web wrapper after CLI validation is stable

Export formats such as DOCX, PDF, HWPX, and PPTX are useful, but they are not the core MVP gate. The core MVP gate is structure-preserving normalization plus validation report generation.

## Core Workflow

```text
source document
-> input converter
-> normalized Markdown / future DocumentModel(JSON)
-> validators/gongmun_rules.py
-> exports/*.validation.txt
```

When a converter provides structured data, the pipeline also writes:

```text
exports/<stem>.document.json
```

Optional explicit export:

```text
normalized Markdown
-> exporter
-> DOCX / PDF / HWPX / PPTX
```

## Project Structure

```text
edudoc/
├── main.py
├── requirements.txt
├── AGENTS.md
├── CLAUDE.md
├── MEMORY.md
├── core/
│   ├── converter_base.py
│   ├── hwp_converter.py          # HWPX primary input, HWP legacy fallback
│   ├── markdown_converter.py     # Markdown draft passthrough
│   ├── registry.py
│   ├── pipeline.py
│   └── exporters/                # optional output adapters
├── validators/
│   └── gongmun_rules.py
├── connectors/
│   └── folder_watcher.py
├── docs/
│   ├── HARNESS.md
│   ├── SUCCESS_CRITERIA.md
│   ├── format-rules.md
│   ├── license-notes.md
│   └── test-plan.md
├── samples/
├── exports/
├── tasks/
└── tests/
```

## Run

```bash
pip install -r requirements.txt
python main.py run samples/
python main.py watch
python tests/test_pipeline.py
python tests/test_hwpx_document_model.py
```

Optional export path:

```bash
python main.py run samples/ --export docx,pdf
```

The default workflow must not require LibreOffice, MS Office, HWP installation, LaTeX, Pandoc, or Typst. Heavy binaries may remain optional fallback/comparison tools only.

## Development Harness

Read these first:

- `AGENTS.md`
- `docs/HARNESS.md`
- `MEMORY.md`
- `CLAUDE.md`

The important rule is:

```text
HWPX is the default MVP input.
HWP is legacy/fallback compatibility input.
```

Future work should not infer that binary HWP is the default product direction merely because the repository contains HWP fallback code.

## Notes

- Do not vendor third-party tool source code into this repository.
- Keep setup lightweight: `pip install -r requirements.txt` should be enough for the default workflow.
- Generated outputs and cache files should not become part of the source tree.
- Validation rules should be improved, not weakened, to make tests pass.
