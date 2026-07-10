# Institution Templates

This directory stores edudoc-owned, explicitly approved institution templates.

```text
skills/templates/<institution>/<document_type>/
├─ template.json
├─ template.validated.json
├─ template.candidate.json
├─ template.review.md
├─ extraction_report.md
├─ evidence.md
├─ success-rules.json
├─ false-positive-rules.json
├─ raw/
│  ├─ header.xml
│  ├─ content.hpf
│  └─ section*.xml
└─ template/
   ├─ header.xml
   ├─ content.hpf
   └─ section*.template.xml
```

Only `template.json` with `status: approved` is loadable by
`core.templates.registry.TemplateRegistry`.

The extraction pipeline writes candidates, review evidence, and reusable quality
rules automatically. A person approves the validated result; they are not
expected to repair the JSON manually.

An HWPX extraction package may initially contain `template.json` with
`status: candidate`. The registry still refuses to load it until explicit
approval changes the status to `approved`. Raw/template XML assets are copied
byte-for-byte and are never regenerated during extraction.
