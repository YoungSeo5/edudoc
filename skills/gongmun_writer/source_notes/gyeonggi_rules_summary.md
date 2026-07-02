# Gyeonggi Office Format Example - Project Source Note

Source reference:

- `references/gongmun/gyeonggi_office_format_example.pdf`

This is a concise project-local summary for Gongmun Writer generation and future deterministic validation.
It is not a complete official rulebook and must not be treated as institution-approved final formatting.

## Project-Relevant Rules

- Write Korean clearly and concisely.
- Avoid unnecessary abbreviations, obscure jargon, and hard-to-understand expressions.
- Do not invent unknown dates, recipients, legal bases, 담당자, amounts, or attachment details.
- Mark missing or uncertain facts as `확인 필요`.
- Prefer numeric date notation such as `2026. 7. 15.`.
- Prefer 24-hour time notation such as `15:00`.
- Use item numbering in this order when nested structure is required:
  `1.` -> `가.` -> `1)` -> `가)` -> `(1)` -> `(가)`.
- If there is only one body item, do not force `1.` just to create a list.
- Do not use `붙임:`.
- Prefer attachment notation such as `붙임  문서명 1부.  끝.`.
- End the document with `끝.`.

## Current Project Use

For now, Gongmun Writer and the deterministic generator should use these as conservative drafting hints only.
Do not broaden `validators/gongmun_rules.py` into institution-specific validation without a separate narrow task and representative examples.

Automated tests must not parse the PDF.
