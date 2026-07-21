# Current Task

## Goal

Separate Gongmun render assets into `templates/render/gongmun/` and global template-quality defaults into `templates/quality/` without introducing test regressions.

## Completion conditions

- Renderer/profile references use `templates/render/gongmun/`; extraction defaults use `templates/quality/`.
- Both source directories are moved intact and current code, tests, and non-archive docs have no stale path references.
- Focused style/quality tests and the full pytest suite introduce no failures beyond the two baseline institution-rendering failures.
- The namespace migration and exact verification result are recorded in `tasks/HANDOFF.md`.
