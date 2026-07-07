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
Loop 8   = current canonical loop
Loop 8.5 = complete (inserted Loop 8 sub-loop; does not replace Loop 9/10)
```

## Known Deviation Resolved

Loop 7 was implemented early through:

- `core/generators/gongmun_generator.py`
- `scripts/gongmun/generate_from_brief.py`
- `tests/test_gongmun_generator.py`
- `tests/test_gongmun_cli.py`

Loop 6 was then backfilled through:

- `skills/gongmun_writer/source_notes/gyeonggi_rules_summary.md`

Now that both Loop 6 and Loop 7 are complete, the current canonical loop is Loop 8.

Loop 8.5 is an inserted Loop 8 sub-loop and is complete. It does not replace
Loop 9 or Loop 10.

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
Loop 8 - validated Markdown -> DOCX/HWPX/PDF export stabilization
```

Validation-rule expansion and folder workflow integration are valid future tasks,
but they are not the next canonical loop unless explicitly inserted by the user.

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
