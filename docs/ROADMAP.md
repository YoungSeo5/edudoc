# Canonical Loop Roadmap

This document is the canonical source for loop numbering in the edudoc project.

Loop numbers must not be reassigned based on implementation order.

## Canonical Roadmap

```text
Loop 1   = HWPX-first harness alignment
Loop 2   = Minimal DocumentModel(JSON) introduction
Loop 2.5 = DocumentModel harness stabilization
Loop 3   = HWPX package-level metadata extraction
Loop 3.5 = tiny HWPX XML metadata subset extraction
Loop 4   = DocumentModel metadata-based integrity validation
Loop 5   = Gongmun Writer Skill definition
Loop 5.5 = Connect Gongmun Writer example to gongmun_rules validation
Loop 6   = Summarize Gongmun reference PDF as Skill source note
Loop 7   = brief -> Gongmun Markdown -> validation report flow
Loop 8   = validated Markdown -> DOCX/HWPX/PDF export stabilization
Loop 8.5 = Gongmun reference style profile / DOCX style profile integration
Loop 9   = pre-commit/CI-based harness automation
Loop 10  = API/Web wrapper after CLI stabilization
Loop 11  = Template-first reference-based generation (extract candidate -> curate -> reuse)
```

## Current Status

```text
Loop 1   = complete
Loop 2   = complete
Loop 2.5 = complete
Loop 3   = complete
Loop 3.5 = complete
Loop 4   = complete
Loop 5   = complete
Loop 5.5 = complete
Loop 6   = complete
Loop 7   = implemented early and now complete
Loop 8   = export slices complete (PDF/HWPX/PPTX remain fallback/experimental)
Loop 8.5 = complete (inserted Loop 8 sub-loop; does not replace Loop 9/10)
Loop 9   = pending
Loop 10  = pending
Loop 11  = in progress (implemented early; user-directed active work)
```

## Known Deviation Resolved

Loop 7 was implemented early through:

- `core/generators/gongmun_generator.py`
- `scripts/gongmun/generate_from_brief.py`
- `tests/test_gongmun_generator.py`
- `tests/test_gongmun_cli.py`

Loop 6 was then backfilled through:

- `skills/gongmun_writer/source_notes/gyeonggi_rules_summary.md`

Both Loop 6 and Loop 7 were then completed, which at the time advanced the
canonical loop to Loop 8. (The current active loop is now Loop 11 — see below.)

Loop 8.5 is an inserted Loop 8 sub-loop and is complete. It does not replace
Loop 9 or Loop 10.

## Loop 11 — Template-first reference-based generation (in progress)

User-directed active work. edudoc generates on demand: check whether a template
for the requested institution × document type exists, use it if so; otherwise
extract a candidate from a user-provided example; otherwise ask for one. See the
"Template-first Generation" section in root `AGENTS.md`.

Status:

- Unified deterministic extraction (done): `core/templates/models.py`,
  `core/templates/extractors/`, and `core/templates/pipeline.py`.
- Quality controls (done): lint, scoped false-positive memory, automatic
  refinement, success gate, review output, and per-template rule persistence.
- Style application (done): extracted style -> DOCX
  (`core/exporters/extracted_style_mapper.py`) and HWPX custom header
  (`core/exporters/hwp_skill_header_builder.py`), with `fallback_used` honesty.
- Approved-template registry (done): `core/templates/registry.py` loads only
  explicitly approved `template.json` artifacts.
- HWPX template extraction MVP (done): read-only ZIP inspection, exact raw and
  template XML copying, section/table/text analysis, and unapplied placeholder
  candidate reporting.
- Remaining product integration: select a registry template from a general user
  request and feed its blocks into the matching document generator.

Numbering note: Loops 9 (CI) and 10 (API) remain pending. Loop 11 is user-inserted
active work and does not renumber them; it generalizes the fixed style profile of
Loop 8.5 into extracted, per-institution templates.

## Numbering Policy

- Do not rename loops because work happened in a different order.
- Do not treat the most recently implemented feature as the next canonical loop.
- If a later loop is implemented early, mark it as implemented early.
- If a lower-numbered loop remains pending, backfill it before moving to the next
  canonical loop unless the user explicitly approves skipping it.
- When proposing the next loop, choose the lowest-numbered pending canonical loop
  by default.

## Current Canonical Loop

```text
Loop 11 - Template-first reference-based generation (user-directed active work)
```

Loop 8 export slices are complete (PDF/HWPX/PPTX remain fallback/experimental).
Loops 9 (CI) and 10 (API) remain valid pending future loops; Loop 11 is the
user-directed active loop and does not skip or renumber them.

## Product Direction

edudoc is a document task automation system, not a file-format conversion tool.
The product goal is reference-based document generation:

```text
source/reference materials + user intent
-> generated task document
-> document-type validation
-> final rendering
```

Target document tasks include 공문, 공식 보고서, 활동보고서, 신청서/사업계획서,
홍보 안내문, 카드뉴스 문구, 발표자료 초안, and 영상 스크립트/스토리보드.

See `docs/product-direction.md` and `docs/workflows.md` for the product workflow.

## Planning Implications

- Loop 8 remains export stabilization, but export is a final rendering layer, not
  the whole product.
- Export must not be treated as complete until real-sample regression coverage exists.
- PDF/HWPX/PPTX are not stable just because they are listed as desired outputs.
- Document task automation requires future source-bundle, document-understanding,
  request-planning, generation, document-type validation, and rendering/export work.
