# core/exporters/AGENTS.md

`core/exporters/` handles final file rendering.

## Responsibility

Convert Markdown or DocumentModel-derived content into final output files.

## Rules

- Exporters do not generate missing facts.
- Exporters do not perform AI reasoning.
- Exporters do not validate Gongmun writing rules.
- Exporters do not parse source HWP/HWPX input.
- Pip-native exporters are the default direction.
- External binary exporters are fallback or experimental only.

## Status language

Do not call an exporter stable unless tests prove it.

Use honest status terms:

- implemented
- partially stabilized
- fallback
- experimental
- planned
- unsupported

## Testing

Do not treat “file exists” as enough.

Prefer checking:

- visible text preservation
- table presence
- rough structure preservation
- style profile application
- stable vs fallback metadata