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
Loop 8.5 = Gongmun reference style profile / DOCX style profile integration (inserted Loop 8 sub-loop)
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

## Numbering Policy

- Do not rename loops because work happened in a different order.
- Do not treat the most recently implemented feature as the next canonical loop.
- If a later loop is implemented early, mark it as implemented early.
- If a lower-numbered loop remains pending, backfill it before moving to the next canonical loop unless the user explicitly approves skipping it.
- When proposing the next loop, choose the lowest-numbered pending canonical loop by default.

## Current Canonical Loop

```text
Loop 8 — validated Markdown -> DOCX/HWPX/PDF export stabilization
```

Validation-rule expansion and folder workflow integration are valid future tasks, but they are not the next canonical loop unless explicitly inserted by the user.

Loop 8.5 (Gongmun DOCX style profile integration) is an inserted Loop 8 sub-loop and is complete. It does not replace Loop 9 or Loop 10.

## Product Direction (goal beyond format conversion)

edudoc is not only a file-format converter. The product goal is **reference-based
document generation**: learn reusable writing rules, structure patterns, and style
profiles from reference documents, then generate new documents (공문, 활동보고서,
신청서/사업계획서, 홍보용 자료, 안내문, 발표/배포용 문서) and export them.

See `docs/product-direction.md` for the four workflows (normalization / reference
capture / generation / export) and folder responsibilities.

Implications for loop planning:

- Loop 8 remains export stabilization; the immediate work is **export reality alignment**
  (honest status + real-sample regression), not API/web/folder workflow.
- Export must not be treated as complete until real-sample regression coverage exists.
- PDF/HWPX/PPTX are not stable just because they are listed as desired outputs.
- Reference-based generation (including promotional materials) is a future product
  direction, not an implemented feature, and does not renumber the canonical loops.
