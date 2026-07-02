# Gongmun Writer Skill

This folder defines the project-local Gongmun Writer Skill.

Purpose:

- turn a user brief or notes into a conservative 공문-style Markdown draft
- keep generation separate from converters, validators, and exporters
- prepare drafts for later `validators/gongmun_rules.py` checks

This skill does not create DOCX, PDF, HWPX, or PPTX files. It only guides Markdown draft generation.

Files:

- `SKILL.md`: main skill instructions
- `templates/basic_notice.md`: reusable conservative draft template
- `source_notes/gyeonggi_rules_summary.md`: concise project-local summary of reference-backed writing rules
- `examples/input_brief.md`: sample user brief
- `examples/output_gongmun.md`: sample generated Markdown draft

The source note is not a complete institution-specific rulebook and should not be copied into validators wholesale.
