# scripts/AGENTS.md

`scripts/` contains human-invoked command wrappers and utilities.

## Responsibility

Use this folder for scripts that call existing project logic.

## Rules

- Scripts may call `core/`, `validators/`, or `core/generators/`.
- Scripts should not duplicate core logic.
- Harness scripts should enforce project policy or drift checks.
- Do not add hidden install behavior.
- Do not auto-clone external repositories.