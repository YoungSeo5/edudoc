# tests/AGENTS.md

`tests/` contains automated tests and test fixtures.

## Responsibility

Use this folder for:

- unit tests
- smoke tests
- regression tests
- small sanitized fixtures

## Rules

- Tests should use temporary output directories.
- Tests must not depend on existing files in `exports/`.
- Private or sensitive real documents should not be committed as fixtures.
- Use `tests/fixtures/` for test-only inputs.

## Export testing rule

Do not treat “file exists” as sufficient proof of export quality.

Prefer checking:

- content preservation
- table presence
- structure preservation
- fallback vs stable export metadata
- known limitations