# edudoc AGENTS.md

This file is the project-level contract for Codex, Claude, and other coding agents.

Keep this file short. Folder-specific rules belong in each folder's `AGENTS.md`.
Long-form policy and background belong in `docs/`.

## Project Goal

edudoc is a document task automation system focused on reference-based document
generation.

edudoc is not merely a file-format converter. Export formats are output
channels, not the product goal.

The product goal is:

- source/reference documents, templates, and previous materials
- user intent and target document type
- reusable facts, writing rules, structure patterns, and style profiles
- newly generated task documents
- final rendering to DOCX / PDF / HWPX / PPTX when needed

Target document tasks include:

- 공문
- 공식 보고서 / 활동보고서
- 신청서 / 사업계획서
- 홍보 안내문 / 카드뉴스 문구
- 발표자료 초안
- 영상 스크립트 / 스토리보드

Detailed workflow belongs in `docs/product-direction.md` and `docs/workflows.md`.

## Default Direction

HWPX is the default structured input direction.

Default input priority:

1. HWPX
2. Markdown
3. HWP legacy/fallback
4. Other formats only when explicitly implemented

The default runtime must remain lightweight:

`pip install -r requirements.txt`

Heavy or external tools must remain optional/fallback unless the user explicitly
approves them.

## Layer Boundaries

Keep these layers separate:

1. source intake / input converters
2. normalization / DocumentModel
3. generators
4. validators
5. renderers / exporters

Do not mix these responsibilities.

- Input converters do not decide the user's final task.
- Generators do not write DOCX/PDF/HWPX directly.
- Validators do not generate or export documents.
- Exporters do not invent missing content or perform AI reasoning.
- Export is the final rendering step after generation and validation.
- Templates and style profiles are reusable assets, not a layer: generators fill
  a template's blocks with content; exporters apply its style profile.

## Template-first Generation

edudoc generates on demand from a user request, not by bulk-templating every
reference file. The flow:

1. User request — e.g. "read these repo/source files and produce a report", or
   "make a document in the shape of this example".
2. Look up whether a template for that institution × document type already exists
   under `skills/templates/`.
3. If it exists: the agent fills each template block with content drawn from the
   source materials.
4. If it does not exist: extract a template candidate from the user-provided
   example, then fill it.
5. If no example was provided and none exists: ask the user for an example or
   form before generating.

Template honesty rules:

- Deterministic code (`core/templates/`) only produces a *candidate*.
- A human promotes a candidate to an official `template.json`; code never
  auto-claims officialness.
- Style is extracted only — never hardcoded. Unknown style stays `확인 필요` / null.
- Do not claim a style is official unless it was actually extracted from the
  reference. Text that merely describes a style is evidence, not parsed style.
- The agent fills blocks; missing facts stay `확인 필요` and are never invented.

## Protected Skills Rule

The following directories are protected external/reference skill sources:

- `skills/hwp/`
- `skills/hwp-skill/`
- `skills/rhwp-edit/`
- `skills/rhwp-advanced/`
- `skills/skills-main/`

Do not directly modify protected skill files unless the user explicitly asks for
that exact change.

Use protected skills as reference material only.

When edudoc needs behavior from protected skills, implement it through
edudoc-owned adapters, wrappers, exporters, validators, generators, scripts, or
tests outside `skills/`.

For detailed rules, read `skills/AGENTS.md`.

Note: `skills/hwp-skill/` internally spells 공문 as `gonmun` (its own author's
naming), while edudoc's own code uses `gongmun` (correct romanization). This is
not drift — see `docs/terminology-notes.md`. Do not rename either side to match
the other.

## Folder-Specific Rules

Before editing files in a folder, check whether that folder has its own
`AGENTS.md`.

If a folder has no `AGENTS.md`, follow this root file and
`docs/folder-responsibility.md`.

## Work Process

The project tracks work in `docs/ROADMAP.md` and `tasks/`. Before starting new
work, read `tasks/current_task.md`, `tasks/HANDOFF.md`, and `MEMORY.md` for
current state; keep `docs/ROADMAP.md` as the canonical process log.

Do not renumber past entries, and do not start new work without user approval.

Note: `docs/ROADMAP.md` currently ends at the export-stabilization phase and does
not yet include the template-first direction. Until the roadmap is updated, that
direction is authoritative here and in `docs/product-direction.md`.

## Required Discipline

- Keep edits scoped.
- Prefer adapters over broad rewrites.
- Do not delete user/reference files without approval.
- Do not install external tools without approval.
- Do not change global machine state without approval.
- Do not commit generated outputs unless explicitly documented.
- Report uncertainty instead of pretending a feature is stable.

## Required Checks

When changing code, run the relevant focused tests.

When changing dependency, HWP/HWPX priority, or folder policy, run:

`python scripts/harness/check_dependency_policy.py`

`python scripts/harness/check_hwp_priority_drift.py`

If Python execution is blocked by the local environment, report that verification
could not run.
