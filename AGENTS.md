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

## Core HWPX Template Pipeline

The project root is `C:\Users\work\edudoc`. Treat this as the canonical HWPX
template workflow:

1. Convert legacy HWP through the edudoc-owned adapter at
   `core/adapters/hwpx_skill_adapter.py`, using the prepared local engine under
   `tools/hwp2hwpx-python-refactor/hwp2hwpx/`. Do not auto-install or auto-clone.
2. Extract the HWPX package with
   `core/templates/hwpx_package_extractor.py`, then separate fixed XML structure
   from replaceable content with `core/templates/hwpx_content_separator.py`.
   The CLI entry point is
   `scripts/templates/separate_hwpx_template_content.py`.
3. Store template candidates under `skills/templates/<template-id>/`. The
   reusable assets live under `template/header.xml` and
   `template/section*.template.xml`; source evidence remains under `raw/`.
   Current FSS candidates are `fss_director_report/` and
   `fss_virtual_asset_report/`.
4. Load only explicitly approved `template.json` files through
   `core/templates/registry.py`.
5. Fill HWPX table cells through
   `core/adapters/hwpx_table_fill_adapter.py`, using the protected
   `skills/hwp-skill/scripts/fill_hwpx.py` as a reference/runtime boundary, and
   verify this behavior with `tests/test_hwpx_table_fill_adapter.py`.

The general renderer that turns every placeholder in
`section*.template.xml` into a final HWPX is not connected yet. Do not describe
table-cell filling as complete template rendering.

The earlier proposed files `core/templates/load.py`, `extract_style.py`, and
`extractor.py` do not exist in the current tree. Their responsibilities are
currently split across `registry.py`, `extractors/`, and `pipeline.py`; verify
the tree before documenting or extending them.

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
- This repo is public. Keep documents (`*.hwp/.hwpx/.docx/.pptx/.pdf`) out of git
  except under `references/`, `samples/`, and `skills/templates/`; those are
  git-ignored everywhere else. Put unvetted or possibly-sensitive test inputs in
  `sandbox/` (ignored), never in a committed path.
- Report uncertainty instead of pretending a feature is stable.

## Required Information Intake

When a user requests modification, development, extraction, generation, or
validation, first decide whether the task can be completed with the information
already available in the repository and the user's message.

If required information is missing, ask the user for that information before
implementing. Do not guess institution rules, target document type, required
output format, reference files, approval status, or external tool availability.

If a safe partial implementation is possible, clearly state the assumption and
keep the result marked as candidate, fallback, or experimental instead of
claiming it is final.

## Required Checks

When changing code, run the relevant focused tests.

When changing dependency, HWP/HWPX priority, or folder policy, run:

`python scripts/harness/check_dependency_policy.py`

`python scripts/harness/check_hwp_priority_drift.py`

If Python execution is blocked by the local environment, report that verification
could not run.

## HWPX Output Validation

Any HWPX presented as a finished output must pass strict package validation
before it is delivered:

```python
import hwpx
report = hwpx.validate_package(output_path)
assert report.ok, report.errors        # errors must be 0
```

- Do not deliver an HWPX that does not validate (`report.ok is False`). A file
  that merely opens in Hancom is not enough — a lenient reader accepts packages a
  validator rejects.
- If validation cannot pass (e.g. no complete base package is available), do not
  present the file as final. Mark it `incomplete` / `candidate` and state exactly
  which errors block validation.
- Never synthesize or drop package scaffolding (mimetype, version.xml,
  Preview/…, container references) just to make a file open. A template's `raw/`
  folder is intentionally incomplete and must not be repacked on its own.
- The supported way to render without the external original is a self-contained
  template: `core/adapters/hwpx_template_renderer.snapshot_source_hwpx` stores the
  exact original as `source.hwpx`, and `render_hwpx_template` uses it as the base
  so the output validates identically to the original.
