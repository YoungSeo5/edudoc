# Institution Templates

This directory stores edudoc-owned institution templates, keyed by
`<institution>/<document_type>` (the same names the registry looks up).

```text
templates/institutions/<institution>/<document_type>/
├─ template.json          # the template contract; loadable only when status: approved
├─ template.review.md     # human-readable review of the separation result
├─ content.sample.json    # sample field values captured from the reference
├─ placeholder_map.json   # field_id ↔ {{placeholder}} ↔ location map
├─ extraction_report.md   # what the extraction pipeline found
├─ source.hwpx            # byte-perfect original HWPX — the self-contained render base
├─ raw/                   # reference package, copied byte-for-byte, never regenerated
│  ├─ header.xml
│  ├─ section*.xml
│  ├─ content.hpf
│  ├─ settings.xml
│  ├─ META-INF/
│  └─ Scripts/
└─ template/              # fixed structure with content replaced by {{placeholders}}
   ├─ header.xml
   ├─ content.hpf
   └─ section*.template.xml
```

## Loading

Only `template.json` with `status: approved` is loadable by
`core.templates.registry.TemplateRegistry`. The registry resolves a template by
`root / <institution> / <document_type> / template.json`, so a template must sit
at that path to be found.

An HWPX extraction package initially writes `template.json` with
`status: candidate`. The registry refuses to load it until a person changes the
status to `approved`. The extraction pipeline writes candidates, review, and the
placeholder map automatically; a person approves the result and is not expected
to repair the JSON by hand.

## `source.hwpx` and rendering

`raw/` is intentionally incomplete — it omits package-level entries (`mimetype`,
`version.xml`, `Preview/`), so it cannot be repacked into a valid HWPX on its
own. Rendering therefore needs a complete base package.

`source.hwpx` is a byte-perfect copy of the original reference HWPX, stored so
the template is **self-contained**: `core.adapters.hwpx_template_renderer`
renders (replacing only `Contents/section*.xml`) with no external file, and the
output passes strict package validation identically to the original.

Templates extracted with the current
`core.templates.hwpx_content_separator` snapshot `source.hwpx` automatically.
Older templates extracted before that change may lack it; without `source.hwpx`
(or an explicit `base_hwpx`) the renderer cannot produce a validated document.
