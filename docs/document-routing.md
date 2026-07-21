# Document routing

## Generic input routing

| Input extension | Converter | Result |
|---|---|---|
| `.md`, `.markdown` | `MarkdownConverter` | normalized Markdown |
| `.hwpx` | `HwpSkillConverter` | Markdown plus `DocumentModel` when parsing succeeds |
| `.hwp` | `HwpSkillConverter` | HWP→HWPX adapter then Markdown/`DocumentModel`; pyhwp fallback if adapter unavailable |

Unsupported extensions are rejected by `ConverterRegistry`. HWPX priority is an intake preference only; it does not mean “Gongmun”.

## Template and policy routing

`TemplateRegistry` loads only `status: approved` `template.json` files from `templates/institutions/<institution>/<document_type>/`. A template candidate is not an approved template and does not select a document profile.

Compose uses `profile_family` only when supplied explicitly:

| `profile_family` | attachment policy | DOCX style |
|---|---|---|
| `gongmun` | `[붙임]`; only the final attachment receives `끝.` | `DEFAULT_GONGMUN_STYLE_PROFILE` |
| absent or unknown | `[첨부]`; no `끝.` | `DEFAULT_PUBLIC_DOCUMENT_STYLE_PROFILE` |

No input extension, output extension, target-profile metadata, or generic Pipeline option implies this family.

## Output routing

`PipelineConfig.export_formats` chooses an exporter by requested extension:

| Output extension | Exporter |
|---|---|
| `.docx` | `DocxExporter` with public-document default style |
| `.pptx` | `PptxExporter` |
| `.hwpx` | `HwpxExporter` |
| other requested extensions, including `.pdf` | `OfficeExporter` fallback |

Export routing affects the container only. It cannot add an attachment, end marker, recipient, policy, or validation result.
