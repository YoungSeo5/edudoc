# License Notes

This project should not copy third-party skill or tool source code directly into the repository unless the license and maintenance plan are explicit.

Use external tools through:
- pip dependencies
- installed CLI binaries
- subprocess wrappers
- documented manual installation steps

## Current Tool Decisions

### Pandoc

Status:
- allowed as an optional output adapter
- used by `core/exporters/office_exporter.py`

Purpose:
- Markdown -> DOCX
- Markdown -> PDF
- later Markdown -> PPTX

Notes:
- Pandoc may be placed at `tools/pandoc/pandoc.exe` for project-local use
- Pandoc may also be installed separately and available on `PATH`
- the exporter should return a structured failure when Pandoc is missing
- the default local workflow must not require Pandoc unless export is explicitly requested
- local tool binaries should not be committed to the source repository by default

### `jkf87/hwpx-skill`

Status:
- reference for future HWPX output and validation

Purpose:
- Markdown/Text/URL -> HWPX patterns
- HWPX validation and namespace cleanup patterns

Notes:
- do not vendor source code without explicit review
- use as implementation reference or external dependency only after license confirmation

### `hephaex/hwp2md`

Status:
- later experimental adapter

Purpose:
- binary HWP/HWPX -> Markdown comparison path
- possible fallback CLI

Notes:
- low-star repository, so treat as optional
- review license and output quality before making it a core dependency

### Claude Marketplace HWP Skill

Status:
- reference for HWP/HWPX ingestion behavior

Purpose:
- understand expected HWP/HWPX -> Markdown behavior

Notes:
- do not copy marketplace skill source into this repository

### Claude Marketplace `md-to-office`

Status:
- reference for Markdown -> Office/PDF export behavior

Purpose:
- validate Pandoc-based exporter design

Notes:
- keep this repository's implementation as a small wrapper, not a vendored copy
