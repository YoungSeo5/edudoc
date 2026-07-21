# edudoc

edudoc generates new documents from reference material and an explicit document task. File formats are rendering channels, not document-type rules.

## Current entry points

| Entry point | Role | Gongmun rules |
|---|---|---|
| `python main.py run <file-or-dir>` / `watch [dir]` | Shared input normalization, `DocumentModel` integrity checks when available, and optional export | Never runs Gongmun writing rules |
| `python scripts/gongmun/generate_from_brief.py <brief.md> --out <dir>` | Dedicated Gongmun draft generation and `gongmun_rules` validation | Yes |
| `python scripts/public_plan/generate_from_samples.py <samples-dir>` | Public-institution plan generation from source profiles; optional render | No implicit Gongmun routing |
| `python scripts/compose/render_plan.py --plan <plan.json> --to ...` | Renders an explicit `ComposedReport` plan | Only an explicit compose `profile_family="gongmun"` applies Gongmun policy |

`main.py` accepts Markdown (`.md`, `.markdown`) and HWP/HWPX (`.hwp`, `.hwpx`). HWPX is the preferred structured input; HWP is a legacy fallback. Input or output extension never determines document type or Gongmun policy.

## Export status at current code

| Format | Route | Status | Scope caveat |
|---|---|---|---|
| DOCX | `DocxExporter`, shared Pipeline, compose | implemented, connected, tested, partially stabilized | content/structure tested; layout-perfect output is not claimed |
| PPTX | `PptxExporter`, shared Pipeline, compose | implemented, connected, tested, partially stabilized | title, bullets, tables, and optional charts are tested; slide visual design is not claimed |
| HWPX | `HwpxExporter` in Pipeline; hwp-skill route in compose | implemented and tested, experimental | package/content smoke coverage; not a full official-layout exporter |
| PDF | `OfficeExporter` Pandoc/Typst fallback | connected when tools exist, experimental fallback | optional external tools; complex layout is not stabilized |

## Architecture documents

- [Architecture](docs/architecture.md)
- [Document routing](docs/document-routing.md)
- [Validation profiles](docs/validation-profiles.md)
- [Export status](docs/export-status.md)
- [Institution template contract](templates/institutions/README.md)
- [Product direction](docs/product-direction.md)
- [Workflow notes](docs/workflows.md)

## Quick checks

```powershell
python -m pytest tests/ -q
python scripts/harness/check_dependency_policy.py
python scripts/harness/check_hwp_priority_drift.py
```

Read [AGENTS.md](AGENTS.md) before changing code or documentation. `MEMORY.md` is an archived decision record, not a source of current instructions.
