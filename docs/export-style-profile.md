# Export Style Profile (Loop 8.5)

Loop 8.5 introduced a reusable **Gongmun export style profile** applied to DOCX output.

## What it is

- A small, deterministic style layer: `core/exporters/style_profile.py`.
- `DocumentStyleProfile` (frozen dataclass) + `DEFAULT_GONGMUN_STYLE_PROFILE`.
- Documented as project defaults in `templates/gongmun/gyeonggi_style_profile.toml`
  (loadable via `load_from_toml()` using the standard-library `tomllib`; no new dependency).

## Applied DOCX properties

`DocxExporter` applies the profile through `_apply_style_profile()`:

- page margins (top / bottom / left / right)
- Normal style font family (with East Asian font for Korean)
- Normal style font size
- Normal style line spacing
- Normal style paragraph spacing after
- Heading 1 font family + font size
- Heading 1 alignment (default: center)

Markdown parsing and block-to-Word conversion behavior are unchanged.

## Scope and honesty

- The profile is **project-local and reference-guided**, not an official
  institution-approved layout standard. It does **not** claim official
  formatting compliance.
- The reference PDF is treated as writing/layout guidance only and is **not parsed**
  in code or tests.
- DOCX style application is **smoke-tested, not layout-perfect**
  (`tests/test_gongmun_docx_style_profile.py`).

## TOML profile status

The TOML profile (`templates/gongmun/gyeonggi_style_profile.toml`) is loadable/reference
documentation. The default runtime path currently uses `DEFAULT_GONGMUN_STYLE_PROFILE`
(the Python constant); the pipeline does **not** read the TOML automatically. Automatic,
user-selectable style-profile loading is not implemented yet.

`load_from_toml()`, the committed TOML (drift guard vs the Python constant), and custom
`DocumentStyleProfile` injection into `DocxExporter` are tested in `tests/test_style_profile.py`.

## Reuse

Future pip-native PDF (`reportlab`) and HWPX (`python-hwpx`) exporters may reuse the
same `DocumentStyleProfile` so output styling stays consistent across formats.
Those exporters do not exist yet (planned).
