---
name: gongmun-writer
description: Generate Korean public-office gongmun Markdown drafts from a user brief, source notes, or rough requirements. Use when Codex or an LLM agent needs to draft a 공문-style notice, request, guidance, or announcement in Markdown before validation with validators/gongmun_rules.py; do not use for file conversion, DOCX/PDF/HWPX export, HWPX parsing, or final layout work.
---

# Gongmun Writer

## Role

Use this skill to generate a public-office-style Markdown draft from a brief.

This is a generation skill, not an exporter. It produces Markdown drafts only.
Final DOCX, PDF, HWPX, or PPTX files are handled later by exporters.
Validation is handled later by `validators/gongmun_rules.py`.

## Input Brief

Accept a brief with any of these fields:

- purpose
- recipient
- sender or department
- 담당자/contact
- related basis or legal basis
- target audience
- main content
- schedule or deadline
- action required
- attachment names and counts
- tone or institution-specific constraints

If a required fact is missing, do not invent it. Write `확인 필요`.

## Draft Workflow

1. Identify the document purpose and likely title.
2. Extract known facts from the brief.
3. Mark unknown dates, recipients, legal bases, 담당자, and attachment details as `확인 필요`.
4. Write a conservative Markdown draft.
5. Include `관련:` when a basis or source document is known; use `관련: 확인 필요` when the basis is required but missing.
6. Include `붙임` only when an attachment is known or expected; mark uncertain attachment names/counts as `확인 필요`.
7. End the draft with `끝.`.
8. Keep the output ready for deterministic validation where possible.

## Output Shape

Use this conservative shape unless the user provides an institution-specific template:

```markdown
# 문서 제목

수신: 확인 필요
담당: 확인 필요

관련: 확인 필요

관련 근거에 따라 아래와 같이 안내합니다.

1. 대상: 확인 필요
2. 내용: 확인 필요
3. 기한: 확인 필요
4. 제출 방법: 확인 필요

붙임  문서명 1부.  끝.
```

## Writing Rules

- Use formal, concise public-office wording.
- Prefer neutral verbs such as `안내합니다`, `요청합니다`, `제출하여 주시기 바랍니다`.
- Keep numbered items explicit and scannable.
- For nested numbering, prefer `1.` -> `가.` -> `1)` -> `가)` -> `(1)` -> `(가)`.
- If there is only one body item, do not force `1.` just to create a list.
- Prefer numeric date notation such as `2026. 7. 15.`.
- Prefer 24-hour time notation such as `15:00`.
- Avoid promotional, emotional, or speculative language.
- Avoid adding facts not present in the brief.
- Do not fabricate institution names, dates, deadlines, legal bases, budgets, recipients, contacts, or attachment counts.
- Use `확인 필요` for unknown fields.
- Do not use `붙임:`.
- If institution-specific rules are unavailable, use the conservative general structure above.
- Preserve user-provided official terms unless they are clearly typos.

For reference-backed drafting notes, see `source_notes/gyeonggi_rules_summary.md`.
Treat the note as a project summary, not a complete official rulebook.

## Validation Preparation

Before returning a draft, check that:

- the draft has one title heading
- `관련` appears when a basis/source is needed
- attachment text uses `붙임` when attachments exist
- the draft ends with `끝.`
- uncertain fields are visibly marked as `확인 필요`

The goal is to make the draft easy for `validators/gongmun_rules.py` to inspect.

## Boundaries

Do not:

- parse HWPX XML
- convert HWP/HWPX/PDF/DOCX/PPTX files
- export final office documents
- alter validator rules
- claim that the Markdown is final approved 공문 formatting
- hide missing facts by writing vague filler

Use converters for source normalization, validators for rule checking, and exporters for final files.
