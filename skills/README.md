# skills/

## Project-local skills

- `gongmun_writer/`: generation skill for drafting public-office-style Markdown from a user brief. It is not a converter, validator, exporter, or API runtime.

## External references

This folder also records external skill and repository references.
Do not copy third-party skill source into this repository unless licensing and maintenance are explicit.

| Reference | Role | Notes |
| --- | --- | --- |
| Claude Marketplace HWP skill | input conversion reference | HWP/HWPX -> Markdown reference |
| hwpx-skill | HWPX output reference | MD -> HWPX, license must stay explicit |
| md-to-office | office output reference | MD -> DOCX/PPTX/PDF, verify dependency/license chain |
| hwp2md | optional comparison adapter | Rust CLI, experimental fallback only |
