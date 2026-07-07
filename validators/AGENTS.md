# validators/AGENTS.md

`validators/` contains deterministic validation rules.

## Responsibility

Use validators to check:

- generated drafts
- normalized documents
- DocumentModel metadata
- writing rules
- export sanity

## Rules

- Validators do not generate documents.
- Validators do not export files.
- Validators do not mutate source documents.
- Different validation domains must remain separate.