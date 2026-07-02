# Gongmun Writing Skill

`skills/gongmun_writer/` defines the project-local Gongmun Writer Skill.

## Purpose

The skill covers the generation side of the public-office workflow:

```text
User brief / notes / source material
-> Gongmun Writer Skill
-> Gongmun Markdown draft
-> gongmun_rules validation
-> validation report
-> optional export later
```

This differs from the current HWPX normalization path:

```text
HWPX input
-> DocumentModel(JSON)/Markdown
-> gongmun_rules validation
-> validation report
```

## Boundaries

- Gongmun Writer is a generation skill, not a converter.
- It produces Markdown drafts, not final DOCX/PDF/HWPX/PPTX files.
- Final document export is handled later by exporters.
- Validation is handled by `validators/gongmun_rules.py`.
- Unknown dates, recipients, legal bases, 담당자, or attachment details must not be invented.
- If institution-specific rules are unavailable, use a conservative general structure and mark uncertain fields as `확인 필요`.

## Files

- `skills/gongmun_writer/SKILL.md`
- `skills/gongmun_writer/source_notes/gyeonggi_rules_summary.md`
- `skills/gongmun_writer/templates/basic_notice.md`
- `skills/gongmun_writer/examples/input_brief.md`
- `skills/gongmun_writer/examples/output_gongmun.md`

## Source Note

`skills/gongmun_writer/source_notes/gyeonggi_rules_summary.md` records concise, project-relevant Gongmun writing notes from the local reference PDF:

- `references/gongmun/gyeonggi_office_format_example.pdf`

The source note is for generation guidance and future narrow validation tasks.
It is not a complete official rulebook.
Automated tests must not parse the PDF.

## Local Harness

`core/generators/gongmun_generator.py` provides the smallest local harness for this skill.
It reads a structured Markdown brief, fills missing fields with `확인 필요`, generates a conservative Markdown draft, and can run `validators/gongmun_rules.py`.

It is not an LLM runtime, API, exporter, or final layout engine.

## CLI Wrapper

`scripts/gongmun/generate_from_brief.py` wraps the local generator for manual use:

```bash
python scripts/gongmun/generate_from_brief.py skills/gongmun_writer/examples/input_brief.md --out exports/gongmun
```

Expected output files:

- `exports/gongmun/input_brief.generated.md`
- `exports/gongmun/input_brief.validation.txt`

The CLI exits with code `0` when validation passes and nonzero when generation or validation fails.

## Future Integration Candidates

A later loop may connect this CLI to a folder workflow if needed.

This is not the next canonical loop unless explicitly selected by the user.

According to the canonical roadmap, after Loop 6 source note integration and the already-implemented Loop 7 generation/CLI flow, the next canonical loop is Loop 8: validated Markdown -> DOCX/HWPX/PDF export stabilization.
