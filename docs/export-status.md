# Export Status

This document records the Loop 8 exporter status audit.

Export is the final rendering step in edudoc's document task automation flow.
DOCX, PDF, HWPX, and PPTX are output channels, not the product goal. The product
goal is to use source/reference materials and user intent to generate a new
task-oriented document, validate it, and then render it when needed.

Do not pursue PDF/HWPX stability as if simple file conversion were the whole
product. DOCX table quality still matters because final deliverables must be
usable, but exporter work remains downstream of generation and validation.

## Export Truth Table

| Format | Default exporter | Status | Requires heavy external tool? | Real-sample tested? | Notes |
|---|---|---|---|---|---|
| Markdown (normalized) | input converters | usable | no | yes (hwp + hwpx samples) | most reliable output; normalization, not final render |
| DOCX | `DocxExporter` | partially stabilized | no (pip-native) | partial (wide-table + form + Gongmun fixtures) | table metadata and compact wide-table strategy; not layout-perfect |
| PDF | `OfficeExporter` fallback (Pandoc/Typst) | not stabilized / fallback-experimental | yes (bundled binaries) | no (visual not asserted) | do NOT treat as stable; wide-table PDF is unusable |
| HWPX | `HwpxExporter` | experimental | no | package/content smoke tested | minimal pip-native package; not a full layout-compliant HWPX exporter |
| PPTX | none | planned | no stable path yet | no | future pip-native (`python-pptx`) |

Export is not considered complete until real-sample regression coverage exists.
See `docs/product-direction.md` for how export fits the broader generation goal.
See `docs/export-quality-criteria.md` for conversion quality levels (format / content /
structure / layout / reference-based generation). DOCX has partial structure regression
coverage (`tests/test_docx_realistic_structure_export.py`); PDF layout/visual correctness
is not claimed or asserted (`tests/test_pdf_export_status.py`).

## Implemented Exporters

- DOCX: `core/exporters/docx_exporter.py`
  - Engine: `python-docx`
  - Dependency type: pip-native
  - Heavy external binaries required: no
  - Current Loop 8 status: direct exporter and pipeline-level default route are stabilized
- HWPX: `core/exporters/hwpx_exporter.py`
  - Engine: stdlib ZIP/XML package writer
  - Dependency type: pip-native/stdlib only
  - Heavy external binaries required: no
  - Current Loop 8 status: experimental; preserves visible text in a minimal HWPX package and runs package-level validation, but does not claim official layout compliance

## Fallback Exporters

- Office fallback: `core/exporters/office_exporter.py`
  - Engine: Pandoc, with optional Typst PDF engine
  - Dependency type: external binary fallback
  - Heavy external binaries required by default: no
  - Current status: optional fallback/comparison path only

## PDF Export Status (Loop 8.97 triage)

- Real-sample finding: Markdown conversion is usable, but PDF output is NOT usable for complex/wide documents (the HWP form sample renders with split/overlapping cells).
- Root cause: there is no dedicated pip-native PDF exporter. `.pdf` export routes through `OfficeExporter` (Pandoc + Typst), a fallback/experimental path that still returns `ok=True` on a produced file.
- Therefore PDF is NOT a stabilized export. DOCX form/table quality must be acceptable before PDF rendering is prioritized.
- The pipeline now flags non-DOCX exports with `stabilized: False` + `experimental: True` in `meta["exports"]`; the CLI reports them as `출력(fallback·실험적)`, not plain success.
- Markdown conversion status is separate from export status: Markdown for real samples is currently more reliable than PDF export.
- A Gongmun validation failure on a non-gongmun sample (e.g. missing `끝.`) is a validation result, not an export failure — do not conflate the two.

## Planned Exporters

- PDF: planned pip-native exporter, likely `core/exporters/pdf_exporter.py`
  - Intended dependency: `reportlab`
  - Current status: no dedicated exporter file exists yet
- PPTX: planned pip-native exporter
  - Intended dependency: `python-pptx`
  - Current status: no dedicated exporter file exists yet

## Style Profile (Loop 8.5)

- `core/exporters/style_profile.py` defines `DocumentStyleProfile` and
  `DEFAULT_GONGMUN_STYLE_PROFILE` (project-local, conservative public-office defaults).
- `templates/gongmun/gyeonggi_style_profile.toml` documents the same values
  (loadable via stdlib `tomllib`; no new dependency).
- `DocxExporter` applies the profile: page margins, Normal font family/size,
  line spacing, paragraph spacing after, Heading 1 font size, and heading alignment.
- The profile is reference-guided, not an official layout-compliance guarantee;
  the reference PDF is not parsed. DOCX styling is smoke-tested, not layout-perfect.
- Future PDF exporters and HWPX exporter improvements may reuse the same profile.
- The TOML profile is loadable/reference documentation; the runtime uses `DEFAULT_GONGMUN_STYLE_PROFILE`. Automatic style-profile selection is not implemented yet.
- Tested in `tests/test_style_profile.py`: default values, `load_from_toml()`, missing-key fallback, and custom-profile injection into DOCX.

## HWPX Export Status (Loop 8 protected skill adapter slice)

- Protected skill sources under `skills/hwp-skill/` were inspected for package and validation behavior.
- Protected skill files remain reference-only; the runtime implementation lives outside `skills/`.
- `core/exporters/hwpx_exporter.py` writes a minimal HWPX ZIP package with `mimetype`, `META-INF/manifest.xml`, `Contents/content.hpf`, `Contents/header.xml`, `Contents/section0.xml`, and `Preview/PrvText.txt`.
- `validators/hwpx_package_rules.py` checks required files, mimetype ordering/storage/content, and XML well-formedness.
- HWPX export is marked `experimental`, not stabilized. It preserves basic visible text, not layout-perfect or institution-approved HWPX formatting.

## DOCX Form/Table Quality (Loop 8 sample filtering/table slice)

- Directory runs skip repository/control files such as `samples/README.md`, `samples/AGENTS.md`, `samples/AGENT.md`, `CLAUDE.md`, `.gitkeep`, validation reports, document JSON, and generated Office outputs.
- Runtime outputs belong in the configured output directory, normally `exports/`; generated files should not be written back into `samples/`.
- `DocxExporter` reports table quality metadata: `table_count`, `max_table_column_count`, `wide_table_detected`, `wide_table_strategy`, and `warnings`.
- Wide tables use the `landscape_compact_table` strategy: landscape orientation, compact margins, table grid style, smaller table font, cell margins, and tighter cell paragraph spacing.
- This improves DOCX form/table usability but still does not claim exact original layout reconstruction, merged-cell fidelity, or final public-office layout compliance.

## Loop 8 Decision

Stabilize validated Markdown -> DOCX first through the existing pip-native exporter.
Pipeline-level `.docx` export now routes to `DocxExporter` by default.
Current Loop 8 priority is DOCX form/table structure quality, not PDF rendering.
Keep PDF fallback explicit. Treat HWPX as experimental until stronger package/rendering coverage exists.
Pandoc and Typst remain optional fallback/comparison tools and must not become default requirements.
