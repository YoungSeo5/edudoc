# edudoc Harness

## Purpose

This harness prevents coding agents from drifting away from the HWPX-first MVP.

## Current Validation Boundary

The earlier Phase 0 harness used this flow:

```text
HWPX input -> DocumentModel(JSON)/Markdown -> gongmun_rules validation -> validation report
```

That is historical Phase 0 behavior, not a responsibility of the current public
CLI or `Pipeline`. `main.py run` normalizes HWP/HWPX/Markdown without
dispatching document-type writing validators. Gongmun rules remain isolated in
the dedicated Gongmun compatibility flow; file extensions and target profiles
do not select them in the public Pipeline.

## Agent Roles

- Planner: defines task scope, acceptance criteria, and constraints.
- Executor: implements only the current task.
- Reviewer: checks whether the result satisfies the harness and MVP direction.
- Harness Gate: automated checks such as tests, dependency policy checks, and generated-file cleanup checks.

## Non-negotiable Rules

- HWPX is the default MVP input.
- HWP is legacy/fallback only.
- The default workflow must not require LibreOffice, MS Office, HWP installation, LaTeX, Pandoc, or Typst.
- Pandoc and Typst may remain optional fallback/comparison tools only.
- Generated files and cache files must not become part of the source tree.
- Validation rules must not be weakened to make tests pass.
- Exporters must not be treated as the core MVP gate.

## Current Required Verification

- `python tests/test_pipeline.py`
- `python tests/test_hwpx_document_model.py`
- `python tests/test_document_model_rules.py`
- `python scripts/harness/check_dependency_policy.py`
- `python scripts/harness/check_hwp_priority_drift.py`

## Future Harness Checks

- generated file cleanup check
- richer HWPX sample pipeline smoke test
