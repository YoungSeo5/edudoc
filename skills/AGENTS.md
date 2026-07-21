# skills/AGENTS.md

`skills/` contains AI-facing skills, source notes, examples, and external reference skill packs.

## Protected directories

The following directories are read-only by default:

- `skills/hwp/`
- `skills/hwp-skill/`
- `skills/rhwp-edit/`
- `skills/rhwp-advanced/`
- `skills/skills-main/`

Do not edit, delete, rename, move, or refactor these directories unless the user explicitly asks for that exact change.

Institution templates are not AI skills and no longer live in this folder. They
are edudoc-owned data under `templates/institutions/`; read that directory's
`AGENTS.md` and `README.md` before editing or approving one.

## Rule

Use protected skills as reference material.

Do not turn protected skills into editable edudoc internals.

When edudoc needs behavior from a protected skill, create an adapter or wrapper outside `skills/`.

## Allowed

- read protected skill files
- summarize their behavior
- create adapters outside `skills/`
- create tests outside `skills/`
- write integration notes in `docs/`

## Not allowed by default

- modify protected skill files
- copy large skill source code into `core/`
- make protected skill dependencies required by default
- keep auto-install, auto-clone, npm, npx, or hidden setup behavior in the default runtime

If unsure, do not modify `skills/`.
