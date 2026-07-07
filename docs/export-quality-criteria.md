# Export / Conversion Quality Criteria

A created file is **not** the same as a usable document. To stop shallow smoke
tests from implying otherwise, edudoc distinguishes six quality levels. The
highest level is document task automation, not file conversion.

## Levels

### 1. Format conversion
- Meaning: a file with the requested extension was created.
- Auto-testable: file exists, non-empty, valid container such as DOCX ZIP.
- Not guaranteed: any content or structure fidelity.
- Reached by: DOCX, HWPX experimental package export, and PDF fallback.

### 2. Content-preserving conversion
- Meaning: important text and table cell contents are preserved.
- Auto-testable: expected text tokens and long-cell text appear in output.
- Not guaranteed: ordering, layout, styling.
- Reached by: DOCX and Markdown normalization on current samples.

### 3. Structure-preserving conversion
- Meaning: headings, paragraphs, lists, tables, and sections remain recognizable.
- Auto-testable: table count, wide-table column count, heading styles, list styles.
- Not guaranteed: visual spacing, merged cells, exact column widths.
- Reached by: DOCX partial structure and table regression tests.

### 4. Layout-aware rendering
- Meaning: tables, page layout, spacing, and template-like regions are reasonably usable.
- Auto-testable: hard without a real renderer; currently manual review only.
- Not guaranteed today for any exporter.
- Reached by: none. DOCX is not layout-perfect; fallback PDF fails this for wide tables.

### 5. Reference-based generation
- Meaning: the system uses examples, templates, source notes, and style profiles
  to generate a new document matching a desired format and purpose.
- Auto-testable: generated draft passes deterministic validators.
- Not guaranteed today: only the small deterministic Gongmun harness exists.
- Reached by: partial for Gongmun drafts; a product goal, not a general feature.

### 6. Document task automation
- Meaning: the system reads source/reference materials, understands the user's
  requested task, plans the target document type, generates a new document,
  validates it by document type, and exports it only as the final rendering step.
- Auto-testable: requires source-bundle, request-planning, generation,
  validation, and export regression coverage.
- Not guaranteed today: this is the product direction, not an implemented
  end-to-end general workflow.
- Reached by: none as a general capability.

## Current Status

- DOCX: levels 1-2 solid, level 3 partial through structure/table regression
  tests and table quality metadata. Not layout-perfect.
- PDF: level 1 only through fallback/experimental Pandoc/Typst. Not stabilized.
- HWPX: experimental minimal package export with package-level validation and
  preview text preservation. Not layout-aware and not official-format compliant.
- PPTX: no exporter file yet.
- Markdown normalization: reliable content preservation for real samples.
- Document task automation: product goal; not yet implemented end to end.

`file exists != usable document`, and `converted file != completed user task`.
See `docs/export-status.md` for the exporter truth table and
`docs/product-direction.md` for the document task automation goal.
