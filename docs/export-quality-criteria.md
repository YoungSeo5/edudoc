# Export / Conversion Quality Criteria

A created file is **not** the same as a usable document. To stop shallow smoke tests
from implying otherwise, edudoc distinguishes five quality levels.

## Levels

### 1. Format conversion
- Meaning: a file with the requested extension was created.
- Auto-testable: file exists, non-empty, valid container (e.g. DOCX = `PK` zip).
- Not guaranteed: any content or structure fidelity.
- Reached by: DOCX, and PDF fallback (a file is produced).

### 2. Content-preserving conversion
- Meaning: important text and table cell contents are preserved.
- Auto-testable: expected text tokens and long-cell text appear in output.
- Not guaranteed: ordering, layout, styling.
- Reached by: DOCX (tested). Markdown normalization (tested on real samples).

### 3. Structure-preserving conversion
- Meaning: headings, paragraphs, lists, tables, and sections remain recognizable.
- Auto-testable: table count, wide-table column count, heading styles, list styles.
- Not guaranteed: visual spacing, merged cells, exact column widths.
- Reached by: DOCX — partial (`tests/test_docx_realistic_structure_export.py`).

### 4. Layout-aware rendering
- Meaning: tables, page layout, spacing, and template-like regions are reasonably usable.
- Auto-testable: hard/brittle without a real renderer; currently manual review only.
- Not guaranteed today for any exporter.
- Reached by: none. DOCX is not layout-perfect; fallback PDF fails this for wide tables.

### 5. Reference-based generation
- Meaning: the system uses examples/templates/source notes to generate a new document
  matching a desired format and purpose (공문, 보고서, 신청서, 홍보물 등).
- Auto-testable: generated draft passes deterministic validators.
- Not guaranteed today: only the small deterministic Gongmun harness exists.
- Reached by: partial for Gongmun drafts; a product goal, not a general feature.

## Current status (honest)

- DOCX: levels 1–2 solid; level 3 partial (structure regression test). Not layout-perfect (level 4).
- PDF: level 1 only, via **fallback/experimental** Pandoc/Typst. Not stabilized; wide-table PDF is unusable.
- HWPX / PPTX: no exporter files yet — planned.
- Markdown normalization: reliable content preservation for real samples.

`file exists != usable document`. See `docs/export-status.md` for the exporter truth
table and `docs/product-direction.md` for the reference-based generation goal.
