# Folder Responsibility

This document records the current folder responsibilities used by repository
agents. It describes implemented structure only; it does not claim planned
features are complete.

For cleanup status, caller evidence, target paths, and approval gates, see
[folder-audit.md](folder-audit.md).

| Folder | Responsibility |
|---|---|
| `core/` | Runtime conversion, normalization, template extraction/quality control, generation, pipeline orchestration, and exporter coordination. |
| `core/exporters/` | Final Markdown/DocumentModel rendering to output formats only. Exporters do not invent missing content. |
| `core/generators/` | Deterministic or future AI-assisted draft generation into Markdown/structured content. |
| `validators/` | Deterministic validation rules and integrity checks. Validators do not generate or export. |
| `connectors/` | Input triggers such as folder watching. Connectors pass files into the pipeline. |
| `scripts/` | Human-invoked wrappers and harness utilities that call existing runtime logic. |
| `skills/` | Project-local skills and protected external/reference skill packs. Protected skill files are read-only by default. |
| `references/` | Raw reference documents and source materials. |
| `templates/` | Institution data under `templates/institutions/`, render assets under `templates/render/`, and global rules under `templates/quality/`. |
| `samples/` | Representative source inputs for manual or documented checks. |
| `tests/` | Automated tests and immutable fixtures. Tests should use temp output directories. |
| `docs/` | Durable architecture, roadmap, status, and test documentation. |
| `tasks/` | Current task and handoff state only. |
| `tools/` | Optional local external binaries. These are not default runtime requirements. |
| `exports/` | Runtime output directory. Tests must not depend on existing files here. |
