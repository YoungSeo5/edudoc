# Export Status

Export is the final rendering layer. It does not choose a document type, add missing semantic content, or infer Gongmun policy from HWP/HWPX/PDF/DOCX/PPTX.

| Format | Runtime exporter | Connection and verification | Current status |
|---|---|---|---|
| DOCX | `core/exporters/docx_exporter.py` | Shared `Pipeline` and compose render; covered by DOCX and compose tests | partially stabilized; pip-native content/structure checks, not layout-perfect |
| PPTX | `core/exporters/pptx_exporter.py` | Shared `Pipeline` and compose render; `tests/test_pptx_exporter.py` and `tests/test_pptx_wiring.py` | partially stabilized; pip-native title/bullet/table/chart behavior is tested, not visual-design-perfect |
| HWPX | `core/exporters/hwpx_exporter.py` | Shared `Pipeline`; package/content tests | experimental; minimal package writer, not full official layout output |
| PDF | `core/exporters/office_exporter.py` | Optional Pandoc/Typst fallback | experimental fallback; complex layout is not stabilized |

`Pipeline._export_status()` records the export result as `partially_stabilized`, `experimental`, `fallback`, or `failed`; `stabilized: true` for DOCX/PPTX means their tested scope is usable, not that every source layout is reproduced.

For routing and boundaries, see [architecture.md](architecture.md) and [document-routing.md](document-routing.md).
