# AGENTS.md

Project-level contract for Codex, Claude, and other coding agents. Keep this file short; durable architecture belongs in `README.md` and `docs/`.

## Source of truth and document order

- The current code at Git `HEAD` and its automated tests are the highest-priority statement of current behavior. A document describes that behavior; it does not override it.
- When code, tests, and documentation disagree: reproduce the behavior with the relevant test or command, update the stale document, and record an unresolved code/test conflict as `확인 필요`. Do not silently make code match a stale document.
- Read in this order: this file; folder-level `AGENTS.md`; `README.md`; the relevant document under `docs/`; then `tasks/current_task.md` and `tasks/HANDOFF.md` for transient state. `MEMORY.md` is history, not instruction.
- Evidence must come from canonical source plus a current run/test. Never use `exports/`, `sandbox/`, `.omo/`, caches, or logs as implementation evidence.

## Architecture invariants

- **edudoc is reference-based document generation, not a file-format converter.** Layers remain intake/converter → normalization/`DocumentModel` → generator → validator → renderer/exporter.
- **Roles are separate:** document type defines the requested artifact; a template supplies approved structure/style evidence; a profile supplies explicit document-family policy; a validator checks a defined contract; an output format selects only an exporter. Exporters and renderers never invent document meaning.
- **Generic route:** `python main.py run` / `watch` uses the shared `Pipeline` to normalize supported input and optionally export. It does not run Gongmun writing rules and has no `validation_profile` or `target_document_profile` runtime field.
- **Explicit Gongmun isolation:** only `scripts/gongmun/generate_from_brief.py` and an explicit compose `profile_family="gongmun"` may apply Gongmun rules, attachment wording, or style. `끝.` is allowed only there. General reports, plans, proposals, and press releases do not inherit Gongmun rules.
- **No inference from file format:** HWP, HWPX, PDF, DOCX, or PPTX never selects a Gongmun profile. Unknown profile families use neutral policy.
- **DOCX default:** shared `Pipeline` and `DocxExporter()` use `DEFAULT_PUBLIC_DOCUMENT_STYLE_PROFILE`; Gongmun style requires an explicit request.
- **HWPX-first intake:** `.hwpx` is the default structured input; `.hwp` is legacy/fallback. Do not promote HWP to the default path.
* **Templates:** AI skills select an approved `template_id` and produce explicit `field_values`. Runtime code only resolves that ID, validates `placeholder_map.json`, replaces mapped XML locations, preserves fixed structure, and strictly validates the HWPX output. Runtime MUST NOT infer template or field meaning, invent values, or silently fall back to generic `md2hwpx`. See `docs/agent-policies/hwpx-template-rendering.md`.
- **HWPX delivery:** final HWPX must pass strict `hwpx.validate_package`; do not synthesize or remove package scaffolding simply to make a file open.
- Protected skills (`skills/hwp/`, `skills/hwp-skill/`, `skills/rhwp-edit/`, `skills/rhwp-advanced/`, `skills/skills-main/`) are reference-only. Add edudoc-owned adapters outside `skills/`.

## Implementation-status terms

- **설계됨:** an intended interface or document exists, with no production implementation claim.
- **구현됨:** source code exists for the behavior.
- **연결됨:** a supported entry point invokes that implementation.
- **검증됨:** a current automated test or reproducible command checks the behavior.
- **사용 가능:** implemented, connected, and verified for its stated scope; this never implies layout-perfect or institution-approved output.
- **비활성:** implementation exists but no supported entry point invokes it.
- **폐기됨:** retained only for history/compatibility and not a current supported route.

## Working discipline

- Never invent missing facts, institution rules, output formats, or extracted style. Use `확인 필요`/`null` for missing facts.
- Do not auto-install, auto-clone, change global state, call paid LLM APIs, or commit/push without approval. Keep documents out of Git except under `references/`, `samples/`, and `templates/institutions/`; use ignored `sandbox/` for unvetted files.
- Scope changes to the request. Preserve user working-tree changes. Do not delete files without explicit approval unless this request explicitly names the file and the removal is verified safe.
- At completion, submit the exact validation commands, their results (including failures/warnings), and source/test evidence for behavior claims. Run focused tests first, then the requested full test command; do not hide failures or warnings.

## Documentation Changes

Before creating, moving, renaming, splitting, consolidating, shortening, archiving, or deleting documentation, read and follow:

- [Documentation Migration Safety](docs/agent-policies/documentation-migration-safety.md)

This policy is mandatory for all documentation changes.

If the referenced policy file does not exist or cannot be read, stop the documentation task and report the missing policy. Do not modify any documentation until the policy is available.

## Commands

```bash
python main.py run samples/
python main.py watch
python scripts/gongmun/generate_from_brief.py <brief.md> --out exports/gongmun
python scripts/public_plan/generate_from_samples.py <samples-dir>
python scripts/compose/render_plan.py --plan <plan.json> --to docx,pptx,hwpx
python -m pytest tests/ -q
python scripts/harness/check_dependency_policy.py
python scripts/harness/check_hwp_priority_drift.py
```
