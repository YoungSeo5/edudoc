# scripts/AGENTS.md

`scripts/` contains human-invoked command wrappers and utilities.

## Responsibility

Use this folder for scripts that call existing project logic.

## Rules

- Scripts may call `core/` (incl. `core/templates/`), `validators/`, or `core/generators/`.
- `scripts/templates/` runs the template extraction, lint, false-positive memory,
  refinement, success-gate, and explicit approval workflow.
- `scripts/templates/extract_hwpx_template.py` opens one HWPX directly as a ZIP,
  preserves selected package assets byte-for-byte, and performs analysis only.
- Scripts should not duplicate core logic.
- Harness scripts should enforce project policy or drift checks.
- Do not add hidden install behavior.
- Do not auto-clone external repositories.
