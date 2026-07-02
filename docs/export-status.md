# Export Status

This document records the Loop 8 exporter status audit.

## Export Truth Table

| Format | Default exporter | Status | Requires heavy external tool? | Real-sample tested? | Notes |
|---|---|---|---|---|---|
| Markdown (normalized) | input converters | usable | no | yes (hwp + hwpx samples) | most reliable output; normalization, not final render |
| DOCX | `DocxExporter` | partially stabilized | no (pip-native) | partial (wide-table fixture) | content preserved; not layout-perfect for large tables |
| PDF | `OfficeExporter` fallback (Pandoc/Typst) | not stabilized / fallback-experimental | yes (bundled binaries) | no (visual not asserted) | do NOT treat as stable; wide-table PDF is unusable |
| HWPX | none | planned | no stable path yet | no | future pip-native (`python-hwpx`) |
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

## Fallback Exporters

- Office fallback: `core/exporters/office_exporter.py`
  - Engine: Pandoc, with optional Typst PDF engine
  - Dependency type: external binary fallback
  - Heavy external binaries required by default: no
  - Current status: optional fallback/comparison path only

## PDF Export Status (Loop 8.97 triage)

- Real-sample finding: Markdown conversion is usable, but PDF output is NOT usable for complex/wide documents (the HWP form sample renders with split/overlapping cells).
- Root cause: there is no dedicated pip-native PDF exporter. `.pdf` export routes through `OfficeExporter` (Pandoc + Typst), a fallback/experimental path that still returns `ok=True` on a produced file.
- Therefore PDF is NOT a stabilized export. Only DOCX (pip-native `DocxExporter`) is stabilized.
- The pipeline now flags non-DOCX exports with `stabilized: False` + `experimental: True` in `meta["exports"]`; the CLI reports them as `출력(fallback·실험적)`, not plain success.
- Markdown conversion status is separate from export status: Markdown for real samples is currently more reliable than PDF export.
- A Gongmun validation failure on a non-gongmun sample (e.g. missing `끝.`) is a validation result, not an export failure — do not conflate the two.

## Planned Exporters

- PDF: planned pip-native exporter, likely `core/exporters/pdf_exporter.py`
  - Intended dependency: `reportlab`
  - Current status: no dedicated exporter file exists yet
- HWPX: planned pip-native exporter, likely `core/exporters/hwpx_exporter.py`
  - Intended dependency: `python-hwpx`
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
- Future PDF/HWPX exporters may reuse the same profile.
- The TOML profile is loadable/reference documentation; the runtime uses `DEFAULT_GONGMUN_STYLE_PROFILE`. Automatic style-profile selection is not implemented yet.
- Tested in `tests/test_style_profile.py`: default values, `load_from_toml()`, missing-key fallback, and custom-profile injection into DOCX.

## Loop 8 Decision

Stabilize validated Markdown -> DOCX first through the existing pip-native exporter.
Pipeline-level `.docx` export now routes to `DocxExporter` by default.
Keep PDF/HWPX planned until a narrow exporter implementation exists.
Pandoc and Typst remain optional fallback/comparison tools and must not become default requirements.
