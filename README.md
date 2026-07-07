# edudoc

edudoc is a **document task automation system** focused on reference-based
document generation.

It is not primarily a file-format converter. The intended product flow is:

```text
source/reference materials + user intent
-> generated task document
-> document-type validation
-> final rendering to DOCX / HWPX / PDF / PPTX when needed
```

HWPX/HWP/Markdown normalization, validation reports, and exporters are supporting
layers for that goal.

## Current Reality

- HWPX is the default structured input direction.
- HWP remains a legacy/fallback compatibility path.
- Markdown drafts can be validated and exported.
- The small Gongmun generator can create a conservative Markdown draft from a
  structured brief.
- DOCX is the most mature final-rendering path, but still not layout-perfect.
- PDF is fallback/experimental.
- HWPX export is experimental.

## Core Layers

```text
source documents
-> source bundle / filtering
-> document understanding
-> generation request
-> document planner
-> generator
-> validator
-> template/layout renderer
-> exporter
```

See:

- `docs/product-direction.md`
- `docs/workflows.md`
- `docs/export-status.md`
- `docs/export-quality-criteria.md`

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

The default workflow must not require LibreOffice, MS Office, HWP installation,
LaTeX, Pandoc, or Typst. Heavy binaries may remain optional fallback/comparison
tools only.

## Development Harness

Read these first:

- `AGENTS.md`
- `docs/HARNESS.md`
- `MEMORY.md`
- `CLAUDE.md`

Important direction:

```text
HWPX is the default structured input direction.
HWP is legacy/fallback compatibility input.
Export is the final rendering step, not the product goal.
```

Future work should not infer that binary HWP or any single export format is the
default product direction.
