# Validation profiles

`validation_profile` is retired as a shared-Pipeline runtime concept. `PipelineConfig` has no `validation_profile`, `validate_gongmun`, or `target_document_profile` field, and `main.py` rejects the removed command-line option.

| Validator | Input | Actual execution path | Scope |
|---|---|---|---|
| `validators/document_model_rules.py` | `DocumentModel` | `Pipeline.process_file()` when a converter provides a model | deterministic structure/provenance integrity; non-Gongmun |
| `validators/gongmun_rules.py` | Gongmun Markdown draft | `core.generators.gongmun_generator.generate_and_validate()` and `scripts/gongmun/generate_from_brief.py` | dedicated Gongmun writing rules only |
| `validators/hwpx_package_rules.py` | emitted `.hwpx` package | `HwpxExporter` and package-focused tests | ZIP/package/XML requirements, not document writing rules |

A validation report’s existence is evidence only for the validator listed above. Generic HWPX normalization may run `document_model_rules` but never automatically runs `gongmun_rules`. Output format also never chooses a validator.
