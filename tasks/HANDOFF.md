# HANDOFF

## Current state

- One unresolved limitation is recorded below: the one-page template extraction
  no longer reproduces its stored contract.
- Approved institution-template rendering now preserves the `template_id` from
  `content.json` and rejects it when it differs from the resolved approved
  template. It does not produce an HWPX or fall back to generic rendering.
- Architecture and HWPX agent policy now describe the connected general
  placeholder route and the inactive table-fill adapter accurately.

## Next action

- Start the user's next concrete product task. Do not promote historical output
  cleanup, dead-code candidates, or export-document cleanup ahead of it.

## Current verification

Measured 2026-08-06. **The suite is not green.** Five failures stand, each
attributed below.

- Focused institution-template tests:
  `python -m pytest tests/test_compose_render_cli.py tests/test_institution_template_rendering.py tests/test_hwpx_template_renderer.py -q`
  -> **2 failed, 32 passed**.
- Full suite: `python -m pytest tests/ -q -p no:randomly` -> **5 failed, 295 passed**.
- `python scripts/harness/check_dependency_policy.py` -> **PASS**.
- `python scripts/harness/check_hwp_priority_drift.py` -> **PASS**.

`-p no:randomly` is required for a reproducible count. Under the default random
order, `pytest-randomly` surfaces additional order-dependent failures, so runs
without the flag do not compare against this record.

### The five failures

1. `test_hwpx_content_separator.py::test_separator_preserves_footer_instruction_as_fixed_text`
   — belongs to the uncommitted 2026-07-27 separator work. The test already
   asserts the new expectation (`※` footer stays fixed text) while the
   implementation does not produce it yet.
2. `test_institution_template_rendering.py::test_compose_refuses_an_institution_template_without_a_metadata_contract`
3. `test_institution_template_rendering.py::test_compose_cli_rejects_content_for_a_different_template`
4. `test_render_hwpx_template_cli.py::test_cli_refuses_a_template_without_a_metadata_contract`
5. `test_render_hwpx_template_cli.py::test_cli_rejects_content_for_a_different_template`

Items 2-5 share one cause. They used `금감원 원페이지` and
`금감원 원장보고 가상자산` as the "approved template that has no `alias_map.json`"
fixture. Both were deliberately demoted to `status: candidate` on 2026-08-06
because they carry no repeat or spacing contract, so `TemplateRegistry.find()`
no longer returns them and the tests now hit `institution_template_not_found`
instead of the later-stage error they assert. The production code is behaving
correctly; the tests' premise changed. That demotion is still uncommitted.

## Unresolved limitation: one-page extraction regression

Re-extracting `금감원 원페이지` from its own unchanged `source.hwpx` no longer
reproduces the stored contract. The stored contract is the correct one.

- stored `placeholder_map.json`: **27** fields, `replacement_mode: hp_t_text_only`
- current re-extraction: **23** fields, `replacement_mode: mixed`
- compared by `text_node_index`, not by `field_id` (field IDs are sequential and
  do not line up between runs)

Six positions differ:

| node | text | stored | current | correct |
|---|---|---|---|---|
| 24 | `〈◈◈◈◈ 관련 현황〉` | field | dropped | field |
| 25 | `※ 맑은고딕 13pt` | field | dropped | field |
| 26 | `◦ 맑은고딕 13pt` | field | dropped | field |
| 27 | `* 맑은고딕 11pt` | field | dropped | field |
| 4 | `◆◆◆◆◆ 진행상황` | field | dropped | field |
| 3 | `Ⅰ.` | fixed | field | fixed |

Nodes 24-27 are the "관련 현황" box. They sit inside a table, so the current
separator treats them as neither `hp_t_text` nor `table_cell` and drops them
entirely. Node 3 is a chapter number that must stay fixed; making it a field
would force the user to type `Ⅰ.` and lose the numbering when omitted.

The `mixed` replacement mode points at the table-cell path as the likely cause.

Consequences and constraints:

- One-page `alias_map.json` work uses the **stored 27-field contract**. Do not
  re-extract the template while this regression stands.
- Strict HWPX validation does not catch this. The candidate QA round-trip passes
  (`source.hwpx` byte-identical, only `Contents/section0.xml` rewritten, zero
  leftover placeholders). Input-contract correctness needs its own check.
- Before touching the separator, review the uncommitted 2026-07-27 changes in
  `core/templates/hwpx_content_separator.py`, `hwpx_content_artifacts.py`, and
  `tests/test_hwpx_content_separator.py`. Their author and intent are unknown.
  `core/templates/hwpx_content_classifier.py` is clean and unmodified.

## Non-blocking baseline

- The optional strict Python audit still reports six pre-existing findings in
  `RenderResult`, placeholder-map metadata typing, and existing compose
  `ValueError` boundaries. This task introduced no new audit category. Do not
  treat those findings as the next task without an explicit user request.
