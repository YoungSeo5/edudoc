# HWPX template rendering: agent vs. runtime code roles

Referenced from root `AGENTS.md` under **Templates**. This is the full rule that
bullet summarizes.

## Role split

- **AI agent**: selects an approved `template_id` (institution × document type)
  and produces explicit `field_values` from source material. The agent decides
  *meaning* — which template fits, what content goes in which field.
- **Runtime code**: only resolves the given `template_id`, validates
  `placeholder_map.json`, replaces the mapped XML locations, preserves fixed
  structure, and strictly validates the output package.

Runtime code MUST NOT:

- infer which template or field a piece of content belongs to
- invent a value for a missing field
- silently fall back to the generic `md2hwpx` path when an institution template
  was explicitly requested (it must raise instead)

## Extraction → storage → approval pipeline

1. Convert legacy HWP through the edudoc-owned adapter at
   `core/adapters/hwpx_skill_adapter.py`, using the local engine under
   `tools/hwp2hwpx-python-refactor/hwp2hwpx/`. Do not auto-install or auto-clone.
2. Extract the HWPX package with `core/templates/hwpx_package_extractor.py`,
   then separate fixed XML structure from replaceable content with
   `core/templates/hwpx_content_separator.py`. CLI entry point:
   `scripts/templates/separate_hwpx_template_content.py`.
3. Store templates under `templates/institutions/<institution>/<document-type>/`.
   Reusable assets live under `template/header.xml` and
   `template/section*.template.xml`; source evidence stays under `raw/`. Current
   examples: `금융감독원/금감원 원장보고/` (`fss_director_report`),
   `금융감독원/금감원 원장보고 가상자산/` (`fss_virtual_asset_report`),
   `금융감독원/금감원 원페이지/` (`fss_one_page`).
4. Load only explicitly approved `template.json` files through
   `core/templates/registry.py` (`TemplateRegistry.find`, default root
   `templates/institutions`). A candidate is not an approved template.
5. Fill content two ways, both connected to runtime entry points:
   - **Table cells**: `core/adapters/hwpx_table_fill_adapter.py`, which shells
     out to the protected `skills/hwp-skill/scripts/fill_hwpx.py`. Covered by
     `tests/test_hwpx_table_fill_adapter.py`.
   - **General `{{placeholder}}` text**: `core/adapters/hwpx_template_renderer.py`
     (`render_hwpx_template` / `fill_template_sections`). Connected through
     `core/compose/render.py`'s `render_report_to_hwpx()` when `institution`,
     `document_type`, and `template_content` are supplied — reachable from
     `scripts/compose/render_plan.py --institution --document-type
     --template-content`. If no approved template is found for the given
     institution/document type, it raises rather than falling back to generic
     `md2hwpx`.

## Template-first generation flow

1. User request — e.g. "read these source files and produce a report" or "make
   a document shaped like this example."
2. Look up whether a template for that institution × document type already
   exists under `templates/institutions/`.
3. If it exists and is `approved`: the agent fills each template block with
   content drawn from the source material.
4. If it does not exist: extract a template candidate from a user-provided
   example, then fill it.
5. If no example was provided and none exists: ask the user for one before
   generating — do not bulk-template every reference file by default.

## Honesty rules

- Deterministic code under `core/templates/` only produces a *candidate*.
- A human promotes a candidate to an official `template.json`; code never
  self-declares officialness.
- Style is extracted only, never hardcoded. Unknown style stays `확인 필요` / null.
- Do not claim a style is official unless it was actually extracted from the
  reference; prose that merely describes a style is evidence, not parsed style.
- The agent fills blocks; missing facts stay `확인 필요` and are never invented.
