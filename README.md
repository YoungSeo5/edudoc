# edudoc

edudoc generates new documents from reference material and an explicit document task. File formats are rendering channels, not document-type rules.

## Current entry points

| Entry point | Role | Gongmun rules |
|---|---|---|
| `python main.py run <file-or-dir>` / `watch [dir]` | Shared input normalization, `DocumentModel` integrity checks when available, and optional export | Never runs Gongmun writing rules |
| `python main.py failures` | Read-only JSON summary of runtime failures grouped by stable fingerprint | Not applicable |
| `python scripts/gongmun/generate_from_brief.py <brief.md> --out <dir>` | Dedicated Gongmun draft generation and `gongmun_rules` validation | Yes |
| `python scripts/public_plan/generate_from_samples.py <samples-dir>` | Public-institution plan generation from source profiles; optional render | No implicit Gongmun routing |
| `python scripts/compose/render_plan.py --plan <plan.json> --to ...` | Renders an explicit `ComposedReport` plan | Only an explicit compose `profile_family="gongmun"` applies Gongmun policy |
| `python scripts/templates/qa_hwpx_template.py --source <source.hwpx> ...` | Creates and round-trip validates an unapproved HWPX template candidate | Not applicable |

`main.py` accepts Markdown (`.md`, `.markdown`) and HWP/HWPX (`.hwp`, `.hwpx`). HWPX is the preferred structured input; HWP is a legacy fallback. Input or output extension never determines document type or Gongmun policy.

The four document-generation entry points (`main.py run`/`watch`, Gongmun,
public-plan, and compose) write one ignored JSON event per failure to
`exports/failures/`. `python main.py failures` reports occurrence count and
first/last timestamps by stable fingerprint without changing the original CLI
errors or exit codes. See [exports/README.md](exports/README.md).

## Export status at current code

| Format | Route | Status | Scope caveat |
|---|---|---|---|
| DOCX | `DocxExporter`, shared Pipeline, compose | implemented, connected, tested, partially stabilized | content/structure tested; layout-perfect output is not claimed |
| PPTX | `PptxExporter`, shared Pipeline, compose | implemented, connected, tested, partially stabilized | title, bullets, tables, and optional charts are tested; slide visual design is not claimed |
| HWPX | `HwpxExporter` in Pipeline; hwp-skill route in compose | implemented and tested, experimental | package/content smoke coverage; not a full official-layout exporter |
| PDF | `OfficeExporter` Pandoc/Typst fallback | connected when tools exist, experimental fallback | optional external tools; complex layout is not stabilized |

## Architecture documents

- [Architecture](docs/architecture.md)
- [Document routing](docs/document-routing.md)
- [Validation profiles](docs/validation-profiles.md)
- [Export status](docs/export-status.md)
- [Institution template contract](templates/institutions/README.md)
- [Product direction](docs/product-direction.md)
- [Workflow notes](docs/workflows.md)

## Quick checks

The project uses uv. `uv venv` reads [.python-version](.python-version) and creates
`.venv` with CPython 3.13; nothing else in the repository enforces that version. On a
fresh clone, create the environment and install the test dependencies
(`requirements.txt` plus `pytest>=8,<9`) first.

Windows PowerShell:

```powershell
uv venv
uv pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pytest tests/ -q
.\.venv\Scripts\python.exe scripts/harness/check_dependency_policy.py
.\.venv\Scripts\python.exe scripts/harness/check_hwp_priority_drift.py
```

macOS/Linux Bash:

```bash
uv venv
uv pip install -r requirements-dev.txt
./.venv/bin/python -m pytest tests/ -q
./.venv/bin/python scripts/harness/check_dependency_policy.py
./.venv/bin/python scripts/harness/check_hwp_priority_drift.py
```

Read [AGENTS.md](AGENTS.md) before changing code or documentation. `MEMORY.md` is an archived decision record, not a source of current instructions.

## Acknowledgements

### Reference material

- **범정부오피스 (KISA버전)** — used as a public reference for exercising the HWPX
  template extraction and QA path. Post: `[공문서 편집 자동화 프로그램] 범정부오피스(KISA버전)
  다운로드`, published by 행정안전부 on 2026-08-04 on the 소통 서비스 board
  (`sotong.go.kr`, `board_id=240`, `menu_id=606`); attachments `범피스1100가이드북.pdf`
  and `KISA 범피스 1310.zip`. The page states no license or terms of use, so none is
  claimed here.

### Skills

- **[hwpx-skill](https://github.com/jkf87/hwpx-skill)** by jkf87 — upstream of the
  `skills/hwp-skill` submodule, which this project vendors as
  [edudoc_hwp_skill](https://github.com/YoungSeo5/edudoc_hwp_skill) and calls through
  adapters in `core/adapters/`. Its template-filling scripts informed how edudoc
  approaches template generation. The submodule's own `README.md` carries its further
  credits.

### HWP → HWPX conversion

Two distinct paths, credited separately.

- **[hwp2hwpx-python-refactor](https://github.com/jkf87/hwp2hwpx-python-refactor)** —
  performs the actual HWP → HWPX conversion. `skills/hwp-skill/scripts/convert_hwp.py`
  imports `hwp2hwpx` from it, cloning the repository on demand; it is neither vendored
  here nor listed in `requirements.txt`. `core/adapters/hwpx_skill_adapter.py` drives
  that script.
- **[pyhwp](https://pypi.org/project/pyhwp/)** (imported as `hwp5`) with **markdownify**
  — a separate fallback in `core/hwp_converter.py` that goes HWP → HTML → Markdown. It
  does not produce HWPX.

### Runtime dependencies

`python-hwpx`, `lxml`, `fonttools`, `pyhwp`, `markdownify`, `markdown-it-py`,
`python-docx`, `python-pptx`, `reportlab`, `watchdog`. See
[requirements.txt](requirements.txt) for what each one is used for.
