# samples/AGENTS.md

`samples/` contains small local input samples for manual pipeline testing.

It is not a user workspace and not a place for generated deliverables.

## Responsibility

Use this folder for representative source inputs.

## Rules

- Do not store generated exports here.
- Do not store private or sensitive real user documents unless explicitly approved.
- Keep samples small and reproducible.
- Tests should not depend on mutable `samples/` contents unless explicitly documented.
- `README.md`, `AGENTS.md`, and similar repository/control files are control files, not source documents.
- Actual product-style source materials should eventually be represented as filtered source/reference bundles, not blindly converted files.

Generated outputs belong in `exports/`.

Automated test fixtures belong in `tests/fixtures/`.
