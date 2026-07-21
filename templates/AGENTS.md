# templates/AGENTS.md

`templates/` stores reusable OUTPUT render templates, style profiles, and layout
assets used by exporters, plus project-wide template-quality rule defaults.

Keep these template responsibilities distinct:

- `templates/render/` — output render/style/layout assets.
- `core/templates/` — deterministic code that extracts template candidates and
  style profiles from reference documents.
- `templates/institutions/<institution>/<document_type>/` — stored institution template
  artifacts (`template.json`) that the generation flow loads and fills.
- `templates/quality/` — global success-rule and false-positive-rule
  defaults. Institution-specific rule memory belongs beside the institution
  template under `templates/institutions/`.

## Responsibility

Use this folder for files that define reusable output structure or style.

## Rules

- Templates are not random examples and not generated outputs.
- If a template is documentation-only or loadable-only, say so clearly.
- Add reusable template files here only when provided or requested.
- Do not create template folders for document types the user has not asked to
  implement.
