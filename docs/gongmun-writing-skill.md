# Gongmun Writing Skill

`skills/gongmun_writer/` and `scripts/gongmun/generate_from_brief.py` are the dedicated Gongmun generation route.

```text
brief / source notes → Gongmun Markdown draft → gongmun_rules validation → optional export
```

It is separate from shared HWPX normalization:

```text
.hwpx input → HwpSkillConverter → Markdown + optional DocumentModel → document_model_rules
```

The shared `Pipeline`, `python main.py run`, and HWPX input never select `gongmun_rules` from an extension, template, or output format. The Gongmun generator may use Gongmun attachment wording and `끝.`; general reports, plans, proposals, and press releases may not.

The generator is not an LLM runtime or layout engine. It writes conservative Markdown, preserves unknown facts as `확인 필요`, and `validators/gongmun_rules.py` checks only the dedicated route. See [validation-profiles.md](validation-profiles.md) for validator scope.
