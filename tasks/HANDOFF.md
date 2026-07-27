# HANDOFF

## Current state

- No active task or unresolved blocker is recorded.
- Approved institution-template rendering now preserves the `template_id` from
  `content.json` and rejects it when it differs from the resolved approved
  template. It does not produce an HWPX or fall back to generic rendering.
- Architecture and HWPX agent policy now describe the connected general
  placeholder route and the inactive table-fill adapter accurately.

## Next action

- Start the user's next concrete product task. Do not promote historical output
  cleanup, dead-code candidates, or export-document cleanup ahead of it.

## Current verification

- Focused institution-template tests:
  `python -m pytest tests/test_compose_render_cli.py tests/test_institution_template_rendering.py tests/test_hwpx_template_renderer.py -q`
  -> **28 passed**.
- Full suite: `python -m pytest tests/ -q` -> **186 passed**.
- `python scripts/harness/check_dependency_policy.py` -> **PASS**.
- `python scripts/harness/check_hwp_priority_drift.py` -> **PASS**.

## Non-blocking baseline

- The optional strict Python audit still reports six pre-existing findings in
  `RenderResult`, placeholder-map metadata typing, and existing compose
  `ValueError` boundaries. This task introduced no new audit category. Do not
  treat those findings as the next task without an explicit user request.
