# HANDOFF

## Current state

The current routing contract is aligned to source/test behavior: generic `main.py run/watch` normalizes and exports only; it never runs Gongmun writing rules. Gongmun generation/validation is explicit, and compose applies Gongmun attachment/style policy only for `profile_family="gongmun"`. Historical Loop 8 notes moved to [docs/archive/handoff-loop8-history.md](../docs/archive/handoff-loop8-history.md).

Institution templates now live under `templates/institutions/<institution>/<document_type>/`. `TemplateRegistry`, template-dependent tests/fixtures, current documentation, and the document-binary Git exception use that path; protected AI/reference skills were not moved.

Gongmun render assets now live under `templates/render/gongmun/`; global template success and false-positive defaults live under `templates/quality/`. The extraction CLI and style-profile test use these explicit namespaces.

## Verification results

- Focused adapter, compose, Pipeline DOCX/PPTX, and validation-routing tests: **40 passed**.
- Pre-migration baseline `python -m pytest tests/ -q`: **149 passed, 2 failed, 0 pytest warnings**.
- The two failures are from untracked `tests/test_institution_template_rendering.py`: one expects an unsupported `institution` argument on `render_report_to_hwpx`; the other expects structural fields to be absent from the current one-page placeholder map. The migration changed paths only, not the compose signature or template contents.
- Legacy HTML/CSS cleanup: removed unreferenced root `generate.py`, `templates/html/`, and `templates/styles/`. A full post-delete run remained **149 passed, the same 2 pre-existing failures**, so the deletion introduced no new failures.
- Institution-template focused tests: **33 passed, the same 2 baseline failures**; all 8 move-induced missing-path failures were eliminated.
- Move integrity: **57 source files / 57 destination files**. Git-filtered content matches the former tree except `AGENTS.md`, `CLAUDE.md`, and `README.md`, whose internal path documentation was intentionally updated.
- Post-migration full command `python -m pytest tests/ -q`: **150 passed, the same 2 baseline failures, 0 pytest warnings**. The added passing test fixes the registry default path at `templates/institutions/`.
- Render/quality namespace baseline `python -m pytest tests/ -q`: **150 passed, 2 failed, 0 pytest warnings**.
- Focused style-profile and template-quality tests: **8 passed**.
- Manual extraction QA with `scripts/templates/extract_template.py` and the default global quality rules: **exit 0, status=validated, gate_passed=True**.
- Post-namespace full command `python -m pytest tests/ -q`: **150 passed, the same 2 baseline failures, 0 pytest warnings**; no path-related failure was introduced.
- Folder-policy checks: dependency policy and HWPX-first wording policy both passed.
- Current-source stale-path search found no reference to the former institution-template path. A split-component search found only the intentional protected pack path `skills/hwp-skill/templates/report/header.xml`, which is a different runtime boundary and was not changed.
- Markdown relative-link check: passed. `git diff --check`: no whitespace errors (only line-ending notices). The named editor residue `core/pipeline.py.tmp.81788.a7595ec5b763` is absent and unreferenced.

## Remaining work

- HWPX Pipeline export remains experimental; PDF remains an optional external-tool fallback; the generic HWPX placeholder renderer is implemented/tested but not end-to-end connected.
- Protected/untracked `skills/hwp-skill` still contains its own historical `Workflow G` references. Do not edit protected skills without explicit approval.
