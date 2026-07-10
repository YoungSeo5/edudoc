# core/AGENTS.md

`core/` contains edudoc runtime implementation code.

## Responsibility

Use `core/` for runtime logic.

This includes:

- input conversion
- normalization
- DocumentModel handling
- pipeline orchestration
- template extraction and style-profile handling (`core/templates/`)
- generation logic
- export coordination

## Rules

- Do not place generated outputs in `core/`.
- Do not place samples or reference documents in `core/`.
- Do not place tests in `core/`.
- Do not place AI-facing skill instructions in `core/`.
- Keep input conversion, template extraction, generation, validation, and export responsibilities separate.
- `core/templates/` owns the unified `TemplateCandidate`, deterministic
  extractors, lint/false-positive/refinement/success-gate pipeline, serialization,
  and approved-template registry.
- Automatic checks may mark a candidate `validated`; only explicit approval may
  write an official `template.json`.
- Document-type draft generation belongs in `core/generators/`; extracted-style
  render mapping belongs in `core/exporters/`.
- Prefer small adapters over broad rewrites.

## Protected skills

Do not copy large code from protected `skills/` directories into `core/`.

If skill behavior is needed, create a small adapter with tests.
