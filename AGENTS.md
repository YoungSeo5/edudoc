# AGENTS.md

Project-level contract for Codex, Claude, and other coding agents. Keep this file short; durable architecture belongs in `README.md` and `docs/`.

## Project goal

edudoc is a reference-based document generation system, not a file-format converter.

## Absolute prohibitions

- Never invent missing facts, institution rules, output formats, template meaning, field values, or extracted styles. Use `확인 필요` or `null`.
- Do not silently make code match stale documentation. Reproduce the current behavior and report unresolved conflicts as `확인 필요`.
- Do not infer document policy, template identity, or Gongmun rules from a file format.
- Do not apply Gongmun rules outside `scripts/gongmun/generate_from_brief.py` or an explicit compose `profile_family="gongmun"`.
- Do not silently fall back to another renderer, exporter, template, profile, or generic `md2hwpx` route.
- Do not modify protected skills under `skills/hwp/`, `skills/hwp-skill/`, `skills/rhwp-edit/`, `skills/rhwp-advanced/`, or `skills/skills-main/`.
- Do not auto-install, auto-clone, change global state, call paid LLM APIs, commit, push, or delete files without explicit approval.
- Scope changes to the request and preserve user working-tree changes.
- Never use `exports/`, `sandbox/`, `.omo/`, caches, logs, or untracked output files as implementation evidence.
- Do not claim completion, validation, usability, approval, or deployment without current source, connection, and test evidence.

## Implementation scope

- Before implementation or refactoring, read and follow the [Minimal Abstraction Policy](docs/agent-policies/minimal-abstraction.md).
- If its stop conditions apply, pause implementation and report why the additional structure is necessary before adding it.

## Test and build requirements

- The current code at Git `HEAD` and its automated tests are the highest-priority evidence of current behavior.
- Every task that adds, changes, fixes, or removes executable behavior MUST create and run at least one new automated test dedicated to that task.
- Reusing or modifying existing tests alone does not satisfy the new task-specific test requirement.
- A behavior-changing task without a new task-specific automated test is not `구현됨`, `검증됨`, `사용 가능`, or `완료`.
- Run focused tests first, then directly affected tests, then the requested full test or build command.
- Report the exact validation commands and results, including failures and warnings.
- If any relevant test fails or warns, do not report the task as `검증됨`, `사용 가능`, or `완료`.
- Final HWPX output must pass strict `hwpx.validate_package` and the semantic and structural checks defined in [HWPX template rendering policy](docs/agent-policies/hwpx-template-rendering.md).
- Every behavior-changing task MUST read and follow [Task-Scoped Testing Policy](docs/agent-policies/task-scoped-testing.md). A task without a newly created and executed task-specific automated test is not complete. If the policy file is missing or unreadable, stop the task and report it.

## Commands

```bash
python main.py run samples/
python main.py watch
python main.py failures
python scripts/gongmun/generate_from_brief.py <brief.md> --out exports/gongmun
python scripts/public_plan/generate_from_samples.py <samples-dir>
python scripts/compose/render_plan.py --plan <plan.json> --to docx,pptx,hwpx
python scripts/templates/qa_hwpx_template.py --source <source.hwpx> --output-dir <new-candidate-dir> --institution <institution> --document-type <document-type> [--template-id <template-id>]
python -m pytest tests/ -q
python scripts/harness/check_dependency_policy.py
python scripts/harness/check_hwp_priority_drift.py
```

## Documentation changes

Before creating, moving, renaming, splitting, consolidating, shortening, archiving, or deleting documentation, read and follow:

- [Documentation Migration Safety](docs/agent-policies/documentation-migration-safety.md)

This policy is mandatory for all documentation changes.

If the referenced policy file does not exist or cannot be read, stop the documentation task and report the missing policy. Do not modify any documentation until the policy is available.
