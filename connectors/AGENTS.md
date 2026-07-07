# connectors/AGENTS.md

`connectors/` contains input triggers and integrations.

## Responsibility

Use this folder only for connector or ingestion logic.

## Rules

- Connectors do not validate documents.
- Connectors do not export files.
- Connectors do not generate content.
- Connectors should pass inputs into the pipeline.
- Do not add new external integrations unless the user explicitly asks.