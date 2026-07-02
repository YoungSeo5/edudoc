# Product Direction

edudoc is **not merely a file-format converter**. The product goal is
**reference-based document generation**: learn reusable writing rules, structure
patterns, and style profiles from reference documents, then generate new documents
that match a desired format and purpose, and export them when a stable exporter exists.

Desired generation targets include: 공문, 활동보고서, 신청서/사업계획서, 홍보용 자료,
안내문, 발표/배포용 문서.

## Four Separate Workflows

Keep these layers distinct. Do not merge them.

```text
1. Normalization
   HWPX / HWP / DOCX / PDF / Markdown  ->  Markdown / DocumentModel(JSON)

2. Reference capture
   official examples / past documents / templates
   ->  source notes / style profiles / structure profiles / reusable examples

3. Generation
   user brief + reference profiles
   ->  new 공문 / report / application / promotional-material draft (Markdown)

4. Export
   generated or normalized Markdown / DocumentModel
   ->  DOCX / PDF / HWPX / PPTX
```

## What "learning from files" means (for now)

```text
reference corpus + source notes + style profiles + templates + deterministic extraction
```

It does **not** mean model fine-tuning or calling external LLM APIs unless explicitly
added later as its own decision.

## Folder Responsibilities

```text
references/          -> raw official examples and source documents
skills/              -> AI-facing writing/generation instructions and source notes
templates/           -> style profiles, template files, output layout references
core/generators/     -> deterministic or AI-assisted draft generation logic
core/exporters/      -> final format rendering only
validators/          -> deterministic checks only
```

Possible future folders (planned only — do not create large empty structures):

```text
references/promo/
skills/promo_writer/
templates/promo/
```

## Current Reality (be honest)

- Normalization (HWPX/HWP -> Markdown) is the most reliable part today.
- Generation exists only as the small deterministic Gongmun harness (`core/generators/gongmun_generator.py`).
- Export: only DOCX is partially stabilized (pip-native `DocxExporter`). PDF is
  fallback/experimental; HWPX/PPTX are planned. See `docs/export-status.md`.
- Export is **not** considered complete until real-sample regression coverage exists.
- Reference-based generation for reports/applications/promotional materials is a
  product goal, not an implemented feature.
