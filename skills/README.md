# skills/

## Project-local skills

- `gongmun_writer/`: generation skill for drafting public-office-style Markdown from a user brief. It is not a converter, validator, exporter, or API runtime.

## External references

This folder also records external skill and repository references.
Do not copy third-party skill source into this repository unless licensing and maintenance are explicit.

## Current Execution Status

`hwp-skill/` is currently the only skill folder in this repository with a
concrete local script/template execution flow.

It contains runnable scripts, HWPX templates, reference assets, technical
references, and tests. edudoc can wrap those paths with edudoc-owned adapters
and route a document task to a specific script/template.

Other skill folders have different roles:

- `skills-main/` is mostly a collection of `SKILL.md` instruction files. It is
  reference material for future exporters, parsers, generators, and workflows;
  it is not currently a local script/template runtime pack.
- `hwp/`, `rhwp-edit/`, and `rhwp-advanced/` describe external CLI workflows
  such as `kordoc`, `k-skill-rhwp`, and `rhwp`. They need separate availability
  checks and edudoc-owned adapters before runtime use.
- `gongmun_writer/` is a project-local generation skill for Markdown drafts,
  not a converter or exporter.

Skill instructions, templates, and font notes affect edudoc output only when
edudoc routes the task through a matching implemented adapter.

| Reference | Role | Notes |
| --- | --- | --- |
| Claude Marketplace HWP skill | input conversion reference | HWP/HWPX -> Markdown reference |
| hwpx-skill | HWPX output reference | MD -> HWPX, license must stay explicit |
| md-to-office | office output reference | MD -> DOCX/PPTX/PDF, verify dependency/license chain |
| hwp2md | optional comparison adapter | Rust CLI, experimental fallback only |
