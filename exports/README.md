# exports/

`exports/` is the ignored runtime-output directory for generated Markdown,
rendered documents, export metadata, template candidates, and failure records.
Its generated contents are operational artifacts, not source or reference
material, and must not be committed or used as implementation evidence.

Failure events are written under `exports/failures/*.json` with:

- `timestamp`
- `entry_point`
- `stage`
- `error_code`
- `fingerprint`
- `source`
- `error`
- `meta`

`python main.py failures` reads those files and prints a JSON summary grouped
by stable fingerprint. Logging and aggregation do not replace the existing
`ExportResult.error`, CLI JSON/stderr output, or exit codes.

Source inputs belong in `samples/` or `references/`. Approved institution
templates belong in `templates/institutions/`.
