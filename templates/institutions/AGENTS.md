# templates/institutions/AGENTS.md

Institution templates live here as `<institution>/<document_type>/`.

Read `README.md` in this directory for the full folder layout before you add,
edit, approve, or render a template. This file states only the invariants.

## Invariants (do not violate)

- **Loading**: the registry (`core.templates.registry.TemplateRegistry`) loads a
  `template.json` only when `status: approved` **and** it sits at
  `templates/institutions/<institution>/<document_type>/template.json`.
- **Approval is a human gate**: extraction code only writes a `candidate`. A
  person promotes it to `approved`; code never claims officialness on its own.
- **Rendering needs a complete base**: `raw/` is intentionally incomplete (no
  `mimetype`, `version.xml`, `Preview/`), so each template keeps a byte-perfect
  `source.hwpx` as its self-contained base. Without it (or an explicit
  `base_hwpx`) the renderer cannot produce a validated HWPX. Add it with
  `core.adapters.hwpx_template_renderer.snapshot_source_hwpx`.
- **Honesty**: `raw/` and `template/` XML are copied byte-for-byte, never
  regenerated. Missing facts stay `확인 필요` / null and are never invented.
