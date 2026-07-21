# Architecture

## Code-based flow

```text
input file → ConverterRegistry → converter → Markdown + optional DocumentModel
          → Pipeline document_model_rules (when a model exists)
          → optional exporter selected by requested output extension
```

`main.py run/watch` owns the generic flow. It registers `MarkdownConverter` for `.md`/`.markdown` and `HwpSkillConverter` for `.hwp`/`.hwpx`. HWPX converts directly to Markdown and a `DocumentModel`; HWP first attempts the owned HWP→HWPX adapter, then retains the legacy pyhwp fallback. No converter selects a document type or Gongmun rule.

## Dedicated generation routes

- `scripts/gongmun/generate_from_brief.py` calls `core/generators/gongmun_generator.py` and `validators/gongmun_rules.py`.
- `scripts/public_plan/generate_from_samples.py` builds `SourceProfile` and `DocumentPlan`, then calls `public_plan_generator`.
- `scripts/compose/render_plan.py` loads a `ComposedReport`; compose applies attachment and DOCX style policy only from an explicit `profile_family`.

Approved institution templates are data, not AI skills. `TemplateRegistry` resolves an explicitly requested institution and document type under `templates/institutions/<institution>/<document_type>/` and loads only `status: approved` `template.json` files. Candidate extraction remains deterministic code under `core/templates/`; the general HWPX placeholder renderer remains inactive until a supported end-to-end entry point selects and supplies a template explicitly.

## Layer boundaries

| Layer | Responsibility | Must not do |
|---|---|---|
| Converter | Read supported source format into normalized Markdown and optional `DocumentModel` | choose document-type policy |
| DocumentModel | carry deterministic normalized structure/provenance | generate semantic text |
| Generator | create a document draft from an explicit task/profile | write DOCX/HWPX/PPTX/PDF directly |
| Validator | check a named model, Gongmun draft, or HWPX package contract | add semantic content or select itself from an extension |
| Renderer/Exporter | render already-authored Markdown/report into a requested format | invent meaning, Gongmun rules, or missing facts |

## Connection state

- **Connected:** shared Pipeline conversion/export; dedicated Gongmun generation/validation; public-plan generation; compose DOCX/PPTX/HWPX rendering; DOCX/PPTX exporters.
- **Inactive:** `core/adapters/hwpx_template_renderer.py` is implemented and tested but has no end-to-end entry point. It is not full template rendering.
- **Experimental:** Pipeline HWPX output is a minimal package writer; PDF is an optional Office fallback.

See [document-routing.md](document-routing.md) for decisions and [validation-profiles.md](validation-profiles.md) for validator scope.
