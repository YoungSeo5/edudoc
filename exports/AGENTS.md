# exports/AGENTS.md

`exports/` holds runtime generated outputs (drafts, rendered DOCX/HWPX/PDF/PPTX,
export metadata, and template candidates).

## Responsibility

Use this folder for files produced by running the pipeline, scripts, or the
template/compose flow.

## Rules

- This is an output folder — do not treat its contents as source or reference.
- Generated outputs are not committed unless a specific artifact is explicitly
  documented; the folder is gitignored except for control files.
- Do not hand-author reference material here.
- Do not point tests at existing files in `exports/` — tests use temporary dirs
  and `tests/fixtures/`.
- Template candidates are written under `exports/template-candidates/<name>/`
  (`template.candidate.json`, `template.evidence.md`, `template.skeleton.md`) and
  remain candidates until a human promotes them.
- Failure records are written under `exports/failures/` by `core/failure_log.py`
  (`record_failure`), one JSON file per failure event: filename
  `<UTC timestamp>-<stage>-<slug(source)>.json`, content
  `{timestamp, entry_point, stage, source, error, meta}`. All four generation
  entry points (`main.py` shared `Pipeline`, `scripts/gongmun`,
  `scripts/public_plan`, `scripts/compose`) write to this same folder. Records
  beyond the retention limit (newest 500 kept by default) are pruned
  automatically on write — do not hand-edit or hand-prune this folder.
  **Diagnostic/operational data only** — per root `AGENTS.md`, never cite files
  under `exports/` (including `exports/failures/`) as implementation evidence
  for architecture or bug claims.

Source inputs belong in `samples/` or `references/`.
Official institution templates belong in `skills/templates/`.
