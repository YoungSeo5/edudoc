# core/generators/AGENTS.md

`core/generators/` contains draft and content generation logic.

## Responsibility

Generate Markdown drafts or structured content payloads from user input and
reference material. When a template exists, fill its blocks with content instead
of inventing structure.

## Rules

- Generators do not export DOCX/PDF/HWPX directly.
- Generators do not parse source HWP/HWPX files.
- Generators do not mutate templates.
- Generators do not invent missing facts; unknown values stay `확인 필요`.
- Generators may call validators only as explicit result checks.
- Do not create new generator files unless the user explicitly asks for that document type.