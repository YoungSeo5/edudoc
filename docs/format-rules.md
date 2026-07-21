# Format Rules

edudoc uses Markdown as the internal hub format.
Format-specific logic should stay outside input converters unless it is required to extract structure.

## Markdown Drafts

Markdown is the current human-readable normalized format.
For the MVP, HWPX is the default source input and Markdown is one normalized output of that source.

Expected Gongmun structure for the dedicated Gongmun generation workflow:
- one clear title heading
- body text organized by headings or paragraphs
- `관련` section when a source document or basis is needed
- `붙임` section when attachments are referenced
- document ending marker such as `끝.`

Gongmun validation is handled by `validators/gongmun_rules.py` only within the
dedicated Gongmun generator/validator path. Generic normalization and the public
`Pipeline` perform no document-type writing validation; input extensions and
target profiles do not select a Gongmun validator.

## DOCX

DOCX is the first output priority.

Rules:
- generate from Markdown
- prefer the pip-native `DocxExporter`
- use reference DOCX templates when layout consistency matters
- do not add DOCX export behavior to input converters

## PDF

PDF is the second output priority.

Rules:
- generate from Markdown after validation
- PDF currently uses the `OfficeExporter` fallback unless a dedicated pip-native PDF exporter is added
- do not report fallback PDF as stabilized
- treat PDF layout validation as a separate output check

## HWPX

HWPX is the default MVP input and now has an experimental minimal output target.

Rules:
- prioritize HWPX structure preservation for new parsing and validation work
- preserve structure in metadata or future DocumentModel(JSON)-compatible fields when possible
- keep HWPX export in a dedicated exporter
- do not mix HWPX output with HWP/HWPX input conversion
- run package-level validation for generated HWPX
- do not claim stable/layout-compliant HWPX export until stronger tests prove it

## PPTX

PPTX is the fourth output priority.

Rules:
- generate from Markdown only when presentation output is explicitly needed
- keep slide-specific layout rules separate from public-office document rules

## HWP Binary

Binary `.hwp` handling is a legacy/fallback compatibility path.

Rules:
- do not design new MVP harness checks around HWP first
- prefer HWP -> HWPX -> Markdown if reliable tooling is available
- keep `hwp2md` as a later experimental adapter
- do not claim stable round-trip quality until sample checks pass
