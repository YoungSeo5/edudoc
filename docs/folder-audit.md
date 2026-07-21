# Folder and File Audit

This is a cleanup decision table based on current entry-point references, folder
policies, and tests. It does not authorize deletion or moves.

## Status labels

- **core**: reached by a supported entry point.
- **connected**: used by a narrower or optional supported path.
- **reference**: evidence or AI-facing knowledge, not runtime implementation.
- **optional**: external/fallback capability, not a default requirement.
- **generated**: output, scratch state, or cache; never source evidence.
- **inactive candidate**: no current caller found; inspect before removal.
- **mixed**: the folder currently owns multiple responsibilities.

## Root folder audit

| Current path | Current role and evidence | Status | Target / recommendation | Approval? |
|---|---|---|---|---|
| `core/` | Imported by `main.py` and supported scripts; owns conversion, models, generation, compose, rendering, export, and template-processing code. | core | Keep as edudoc runtime; enforce nested `AGENTS.md` boundaries. | No |
| `validators/` | Explicit model, Gongmun, and HWPX-package validation routes. | core | Keep separate from generators and exporters. | No |
| `scripts/` | User-facing Gongmun, public-plan, compose, template, and policy wrappers. | core | Keep wrappers thin; runtime logic stays in `core/`. | No |
| `connectors/` | `folder_watcher.py` is called by `main.py watch`. | connected | Keep while `watch` is supported. | No |
| `tests/` | Unit, regression, routing, and exporter verification plus fixtures. | core | Keep; use temporary output directories. | No |
| `docs/` | Durable architecture, routing, status, roadmap, and archive. | core docs | Keep current docs separate from `docs/archive/`. | No |
| `tasks/` | Current task and handoff state only. | development state | Keep small; durable decisions go to `docs/`. | No |
| `references/` | Raw source documents and evidence used by profiles/rules. | reference | Keep immutable; never store generated output. | No |
| `samples/` | Mutable manual `run/watch` inputs. | manual input | Keep separate from `tests/fixtures/`. | No |
| `skills/` | AI-writing knowledge and protected external/reference packs. | reference / mixed | Keep institution data outside AI-skill sources. | Yes for protected-pack moves |
| `templates/` | Institution templates, render/style assets, and template-quality defaults. | connected / mixed | Keep explicit institution, render, and quality namespaces. | Yes for further moves |
| `tools/` | Optional HWP conversion, Pandoc, and Typst tooling. | optional | Keep isolated and non-default. | Yes for major changes |
| `config/` | `settings.toml` exists, but no production loader/reference was found. | inactive candidate | Remove if obsolete or connect through one explicit config boundary. | Yes |
| `assets/` | Local fonts exist, but no canonical runtime reference was found. | inactive candidate | Move used fonts to `templates/render/fonts/`; otherwise remove. | Yes |
| `exports/` | Pipeline/script output and template candidates. | generated | Keep as output root; clean separately from source refactoring. | Yes for bulk cleanup |
| `sandbox/` | Unvetted or one-off inputs and outputs. | scratch | Keep ignored; clean only after checking user files. | Yes |
| `.agents/` | Agent configuration, not product runtime. | tool metadata | Preserve tool-owned path; exclude from architecture evidence. | Yes |
| `.omo/` | Agent plan/evidence state. | generated metadata | Ignore; never use as implementation evidence. | Yes for cleanup |
| `.codegraph/` | Regenerable code-analysis database. | generated metadata | Exclude from product architecture. | No |
| `.pytest_cache/`, `__pycache__/` | Disposable caches. | generated | Ignore/remove as needed. | No |
| `.git/` | Repository metadata. | repository metadata | Preserve. | Yes for destructive work |

## Mixed-folder and root-file audit

| Current path | Actual responsibility / connection | Proposed destination | Decision |
|---|---|---|---|
| `skills/gongmun_writer/` | AI-facing Gongmun writing knowledge used by the dedicated authoring flow. | Keep in place. | Keep; it is knowledge, not renderer code. |
| `templates/institutions/` | Approved institution templates loaded by `TemplateRegistry`. | Keep in place. | Migrated from the former skill-side location on 2026-07-21; runtime, tests, and current docs use this path. |
| `skills/hwp-skill/` | Protected external implementation invoked by selected adapters/renderers. | `vendor/skills/hwp-skill/` only if approved. | Do not edit/delete; moving affects adapters, `.gitmodules`, docs, and tests. |
| `skills/hwp/`, `skills/rhwp-*`, `skills/skills-main/` | Protected external/reference packs. | `vendor/skills/<name>/` only if approved. | Audit individually; never fold their source into `core/`. |
| `templates/render/gongmun/` | Explicit Gongmun render/style asset. | Keep in place. | Migrated from the former flat template path on 2026-07-21. |
| `templates/quality/` | Global template success and false-positive defaults. | Keep in place. | Migrated from the former flat template path on 2026-07-21; institution rules remain beside institution templates. |
| `templates/html/`, `templates/styles/` | Legacy HTML/CSS experiment assets; no runtime caller was found. | Removed on 2026-07-21. | Cleanup complete; restore only through a newly approved feature. |
| `generate.py` | Unreferenced Jinja2/WeasyPrint experiment. | Removed on 2026-07-21. | Cleanup complete; no replacement runtime was added. |
| `main.py` | Generic supported `run/watch` entry point. | Keep. | core |
| `AGENTS.md` | Root agent contract and repeated-mistake invariants. | Keep concise. | core docs |
| `README.md` | Human navigation to architecture and support status. | Keep as navigation, not duplicate specification. | core docs |
| `MEMORY.md` | Historical record, explicitly not current instruction. | Keep or archive older sections later. | history |

## Cleanup gates

Before deleting or moving a candidate:

1. Search current code, scripts, tests, and non-archive docs for callers and path references.
2. Confirm it is not a submodule, protected pack, optional adapter dependency, or user-owned untracked input.
3. Run focused tests before and after the change.
4. Update only the path-owning docs and policies.
5. Run the full suite, link check, stale-path search, and diff review.
6. Record the decision in `tasks/HANDOFF.md`.

## Recommended order

1. Completed: remove the unreferenced `generate.py` and HTML/CSS experiment assets.
2. Decide whether `config/settings.toml` and `assets/fonts/` have a future owner.
3. Completed: migrate institution templates to `templates/institutions/`.
4. Completed: move render assets and quality defaults under explicit namespaces.
5. Only then consider moving protected packs to `vendor/skills/`.
6. Add a check for undocumented root folders and forbidden runtime dependencies on AI-facing skills.
