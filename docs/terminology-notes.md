# Terminology Notes

## "gongmun" vs "gonmun" (공문)

Both spellings refer to the same Korean word 공문 (official/public document). They
come from two independently-created codebases and are **not** a bug or drift:

- **`gongmun`** — the correct romanization (공=gong, 문=mun). Used throughout
  edudoc's own code: `validators/gongmun_rules.py`, `core/generators/gongmun_generator.py`,
  `skills/gongmun_writer/`, and related tests/docs. This existed from the project's
  earliest Phase 0 skeleton.
- **`gonmun`** — used inside `skills/hwp-skill/` (external git submodule,
  `YoungSeo5/edudoc_hwp_skill`), e.g. `scripts/gonmun.py`, `gonmun_lint.py`,
  `templates/gonmun/`. Likely a missing-batchim typo by that skill's original author.
  `skills/hwp-skill/` is a **protected, read-only reference** (see `skills/AGENTS.md`) —
  do not rename its internals to match edudoc's spelling.

**Decision:** keep both spellings as-is. Do not rename edudoc's `gongmun` to match
the external skill's `gonmun` — `gongmun` is the accurate romanization, the two
namespaces never collide functionally, and matching external skill naming is not
guaranteed to stay stable if the submodule updates or if other external skills use
yet another spelling. When referring to hwp-skill's `gonmun.py`, call it out
explicitly (e.g. "gonmun.py, inside the protected hwp-skill") to avoid confusion.
