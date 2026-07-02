# MEMORY.md

edudoc 프로젝트의 중요한 결정 기록. (CLAUDE.md의 '기억과 연속성' 규칙에 따라 관리)

## 결정 로그

### 2026-07-02 — Export quality criteria added

- Identified that previous tests verified file creation and text presence, not usable document quality.
- Added conversion quality levels: format conversion, content preservation, structure preservation, layout-aware rendering, and reference-based generation (`docs/export-quality-criteria.md`).
- Added realistic export regression coverage for wide-table/document-form Markdown (`tests/fixtures/export/wide_table_activity_report.md`, `tests/test_docx_realistic_structure_export.py`).
- Added PDF fallback/status test so experimental PDF output is not mistaken for stable export (`tests/test_pdf_export_status.py`).
- Reaffirmed that edudoc's product goal is reference-based document generation, not simple file extension conversion.

### 2026-07-02 — Export status and generation goal realigned

- Real sample Markdown conversion is more reliable than current PDF export.
- DOCX remains the only pip-native export target with smoke and pipeline tests.
- PDF export is not stabilized unless a dedicated pip-native PDF exporter exists; fallback PDF is marked experimental.
- The project goal is clarified as reference-based document generation, not simple format conversion only (`docs/product-direction.md`).
- Future generation workflows should use references, source notes, templates, and style profiles to create new documents such as Gongmun, reports, applications, and promotional materials.

### 2026-07-02 — Real sample PDF export gap identified

- Real sample Markdown conversion is usable, but PDF export is not yet stabilized.
- PDF output currently depends on fallback/experimental behavior (`OfficeExporter` via Pandoc/Typst); there is no dedicated pip-native PDF exporter.
- DOCX remains the only stabilized pip-native export target.
- Pipeline now tags exports with `stabilized`/`experimental`, and the CLI shows fallback exports as `출력(fallback·실험적)` instead of plain success (fixes mis-reporting fallback PDF as stabilized).
- Future PDF work must be handled as a narrow Loop 8 exporter slice with real-sample regression coverage.

### 2026-07-02 — DocumentModel integrity validation connected to pipeline

- Connected the existing DocumentModel integrity validator to the pipeline when converters provide a DocumentModel.
- The validation result is reported separately from Gongmun writing validation (meta `document_model_validation` + optional `<stem>.document.validation.txt`), and is non-blocking.
- This closes the remaining Loop 4 runtime-connection gap without changing HWPX parsing, Gongmun generation, or export behavior.
- Housekeeping: cleared stale generated files from `exports/` and added `exports/.gitkeep` (folder is the runtime output dir; tests use temp dirs).

### 2026-07-02 — Loop 8.95 implementation gaps closed before next loop

- Audited Loop 8 and Loop 8.5 implementation substance.
- Distinguished runtime-connected files from documentation-only and planned placeholders.
- Added or verified focused tests for the DOCX style profile and TOML/custom-profile behavior (`tests/test_style_profile.py`); pipeline DOCX test now asserts the default style profile.
- Recorded that `document_model_rules.py` remains test-only (not wired into the pipeline) and the TOML profile is documentation/loadable (runtime uses the Python constant `DEFAULT_GONGMUN_STYLE_PROFILE`).
- Confirmed PDF/HWPX/PPTX exporters remain planned unless dedicated exporter files exist.
- No new feature loop was started.

### 2026-07-02 — Loop 8.9 audit gate completed

- Audited code, tests, dependency policy, HWPX-first policy, exporter routing, and roadmap documentation before starting the next loop.
- Existing Loop 1 through Loop 8.5 work was verified: all 12 individual test/harness checks pass in this environment (pytest module is not installed, so tests were run individually).
- Narrow fix applied: `docs/ROADMAP.md` now lists Loop 8.5 as an inserted Loop 8 sub-loop (it was only recorded in tasks/MEMORY before).
- No new feature loop was started.
- The repository is ready for the user to choose the next Loop 8 slice or explicitly move to the next canonical loop.

### 2026-07-02 — Loop 8.5 Gongmun DOCX style profile introduced

- Added a reusable Gongmun export style profile for DOCX output.
- The style profile applies conservative public-office defaults such as Korean-capable font, font size, margins, paragraph spacing, and line spacing.
- The profile is project-local and reference-guided, not an official layout-compliance guarantee.
- DOCX export remains pip-native through `python-docx`.
- PDF/HWPX exporters may reuse the style profile in future Loop 8 slices.

### 2026-07-02 — Pipeline DOCX export routed to pip-native exporter

- Pipeline-level DOCX export now uses `DocxExporter` by default.
- `OfficeExporter` remains optional fallback/comparison behavior.
- Default DOCX export does not require Pandoc, Typst, LaTeX, LibreOffice, MS Office, or HWP installation.
- Export remains separate from input conversion, Gongmun generation, and validation.

### 2026-07-02 — Loop 8 export stabilization started

- Began validated Markdown export stabilization.
- DOCX is the first stabilized export target because it can use the pip-native exporter.
- Added a Gongmun validated Markdown -> DOCX smoke test.
- Export remains separate from input conversion, Gongmun generation, and validation.
- PDF and HWPX export remain planned because no dedicated lightweight exporter files exist yet.
- Heavy external tools remain optional fallback only.

### 2026-07-02 — Roadmap next-loop signal realigned

- Canonical loop numbering is preserved.
- Loop 6 Gongmun reference PDF source note integration is complete.
- Loop 7 brief -> Gongmun Markdown -> validation report flow was implemented early and is now considered complete.
- The next canonical loop is Loop 8: validated Markdown -> DOCX/HWPX/PDF export stabilization.
- Validation-rule expansion and folder workflow integration remain useful future tasks, but they must not be presented as the next canonical loop unless explicitly inserted by the user.

### 2026-07-02 — Gongmun reference PDF source note added

- Added a concise source note for project-relevant public-office writing rules from the local Gongmun reference PDF.
- The source note is a generation reference summary, not a complete institution-specific validator.
- Automated tests must not parse the PDF.
- No generator, CLI, exporter, API, HWPX parser, or heavy dependency was added.

### 2026-07-02 — Tiny Gongmun CLI wrapper introduced

- Added a tiny CLI wrapper that turns a brief file into a generated Markdown draft and validation report.
- It uses the local deterministic Gongmun generator.
- Output files use `<brief-stem>.generated.md` and `<brief-stem>.validation.txt`.
- It does not use an external LLM runtime, API, exporter, HWPX parser, or heavy dependency.

### 2026-07-02 — Tiny Gongmun generation harness introduced

- Added a tiny local Gongmun generation harness that turns a structured Markdown brief into a conservative Markdown draft.
- The harness does not use an external LLM runtime, API, exporter, HWPX parser, or heavy dependency.
- Missing brief fields are filled with `확인 필요`.
- Validation remains separate through `validators/gongmun_rules.py`.

### 2026-07-02 — Tiny HWPX XML metadata subset added

- Added safe XML metadata extraction for known HWPX package files using the Python standard library.
- DocumentModel `raw_meta` may now include `content_hpf_present`, `manifest_present`, `header_xml_present`, `section_files`, `manifest_item_count`, `document_title_candidate`, `creator_candidate`, and `extracted_xml_fields`.
- Paragraphs and tables are still Markdown-derived fallback; `raw_meta.structure_source` uses `hwpx_xml_metadata_plus_markdown_fallback` only to indicate XML metadata was parsed, not full content-structure extraction.
- HWP fallback behavior and exporter behavior are unchanged.

### 2026-07-02 — HWPX package metadata added to DocumentModel

- Added lightweight HWPX-native package metadata inspection using the Python standard library.
- DocumentModel still derives paragraphs/tables from Markdown fallback, but `raw_meta.structure_source` now distinguishes package metadata plus Markdown fallback when ZIP/XML metadata is available.
- Recorded package-level fields include entry names and XML/section/binary/media counts.
- This does not implement a full HWPX AST and does not change HWP fallback behavior.

### 2026-07-02 — Minimal DocumentModel loop stabilized

- Minimal DocumentModel(JSON) support is now part of the HWPX-first pipeline.
- The current model may be Markdown-derived fallback and must explicitly mark `raw_meta.structure_source`.
- Next development should focus on carefully extracting HWPX-native metadata without building a full HWPX AST.

### 2026-07-02 — Minimal DocumentModel layer introduced

- Added the first `DocumentModel(JSON)` path for HWPX-derived structure.
- HWPX conversion still preserves existing Markdown output.
- The initial HWPX DocumentModel is intentionally conservative and may be derived from Markdown fallback structure, marked with `raw_meta.structure_source = "markdown_fallback"`.
- The pipeline writes `exports/<stem>.document.json` only when a converter provides structured document data.
- This does not remove or rewrite the HWP legacy/fallback path.

### 2026-07-02 — MVP input priority redefined as HWPX-first

- The MVP default input is redefined as `.hwpx`, because HWPX is XML-based and better suited for structure-preserving parsing, validation, and regeneration.
- Binary `.hwp` input remains as a legacy/fallback compatibility path, but new features, tests, and harness rules should prioritize HWPX.
- The MVP scope is fixed as: `HWPX input -> DocumentModel(JSON)/Markdown normalized representation -> gongmun_rules validation -> validation report output`.
- DOCX/PDF/HWPX/PPTX export remains optional and post-MVP from the perspective of the core validation harness.
- Future agents must not promote HWP binary input back to the default path without an explicit new decision.

### MVP 방향 확정
- MVP는 **폴더에 문서를 넣으면 자동 변환되는 로컬 서비스**로 진행한다.
- 최종 사용자 시나리오:
  공문 초안을 Markdown으로 작성하면 교육청 공문 형식 규칙을 검사하고 HWPX/PDF로 출력한다.
- 기준 샘플은 `.hwp` 바이너리를 Markdown으로 변환하는 흐름이며,
  **`.hwp` 입력 변환(.hwp -> Markdown)은 핵심 입력 경로로 격상**한다(사용자 지시, 2026-07-01).
  → pyhwp(HTML) -> markdownify 로 구현·샘플 검증 완료. (출력측 HWP 바이너리 *생성*은 여전히 후순위)
- 위 2026-07-01 결정은 역사적 맥락으로 보존한다. 기본 MVP 입력 우선순위는 2026-07-02 결정에 의해 HWPX-first로 재정의되었다.
- 출력 우선순위는 DOCX -> PDF -> HWPX -> PPTX -> HWP 바이너리 직접 처리 순서다(출력 한정).
- 외부 도구는 Pandoc 사용을 허용한다.
  다만 기본 로컬 워크플로우가 Pandoc 설치를 요구해서는 안 되며, 명시적 export 옵션에서만 사용한다.
  `hwp2md`는 나중에 실험 어댑터로 검토한다.

### 제작 기준 · 출력 엔진 확정 (2026-07-01)
- 제작 기준 2축 확정: (1) 사용자 편의 최우선(무설치: `pip install -r requirements.txt` 한 줄까지만 허용),
  (2) 프로젝트 경량 유지.
- 출력 엔진 방향 확정: **pip-native 기본 + Pandoc/typst fallback**.
  - 기본: markdown-it-py(파싱) → python-docx / reportlab / python-hwpx / python-pptx.
  - fallback: pandoc + typst (고충실도·복잡표·비교검증). `office_exporter` → `pandoc_exporter`로 격하 예정.
- PDF 엔진 결정: pip `typst`는 VC++ 런타임 요구로 폐기. 독립 `typst.exe`는 fallback(pandoc)의 PDF 엔진으로만 유지.
  기본 PDF는 reportlab(한글 시스템 폰트 등록).
- 문서 기준: AGENTS.md=영문, CLAUDE.md=국문 유지(청중별). 범위=AGENTS/CLAUDE/MEMORY+README.

### Phase 0 설계
- 프로젝트 목표를 특정 도메인(SICHIMI/eduroam) 전용이 아닌 **범용 변환 엔진**으로 확정.
- 입력·출력 형식 무관. Phase 0은 로컬 문서로 변환 흐름 검증에 집중.
- Notion·Google Drive 수집은 목표에서 제외(확장 과제).

### 도구 선정
- 입력 변환 주력: `hwp` 스킬(Python). 보조·크로스체크: `hwp2md`(Rust, stars 낮아 제한 사용).
- 출력: `md-to-office`(오피스), `hwpx-skill`(한글, MIT 확인).
- 외부 도구는 소스 복사 금지, 의존성/바이너리로만 참조.

### 라이선스 확인
- `hwpx-skill`: MIT 확인됨.
- `md-to-office`: 소속 저장소는 MIT지만 폴더별 라이선스 별도 확인 필요(pandoc GPL 계열).
- `hwp` 스킬 원본 저장소 라이선스: 미확인(도입 전 확인 필요).

### 공문서 처리 방식
- '생성-검증 루프' 채택: AI 초안 → 규칙 검증기 → 위반 시 재생성 → 통과 시 출력.
- 성공 기준: 형식 보존 + 표현 규칙 + 실행 안내 + 배포 안정성 (docs/SUCCESS_CRITERIA.md).

### 해소됨
- ~~`pyhwp` vs `pyhwp5` 패키지명 상충~~ → **해소**: `pyhwp`(import명 `hwp5`)가 Python 3.13에서 동작 확인.

### 미해결 / 확인 필요
- 공문서 세부 규칙은 대상 교육청 최신 지침으로 보정 필요(원본 PDF 미확인).

## 세션 요약

### (최근 세션)
- 완료: Phase 0 스켈레톤(core/connectors/validators/docs), 프로젝트명 edudoc으로 변경,
  성공 기준 문서와 공문서 규칙 검증기 추가, CLAUDE.md·MEMORY.md 작성.
- 진행 중: 없음.
- 다음 할 일: `hwp_converter._run_hwp_skill` 실제 연결, 출력단(md→DOCX/HWPX/PDF) 통합,
  hwp2md 크로스체크 변환기 추가.

### 2026-07-01 (Claude · 입력단)
- 완료: `.hwpx`(python-hwpx `export_markdown`) + `.hwp`(pyhwp→HTML→markdownify) 입력 변환 실장.
  두 샘플로 검증 — 표·본문 보존, UTF-8 정상. `core/hwp_converter.py`만 수정.
- 결정: 사용자 지시로 **.hwp 입력을 핵심 경로로 격상** → AGENTS.md 우선순위 조항 반영.
- 주의: 이 저장소는 다중 에이전트 동시 작업 중(같은 날 오후 출력단/pandoc은 다른 에이전트가 구현).
  `hwp_converter.py` 입력 로직은 이 세션 산출물 — 되돌리기 전 확인 필요.
- 설치: `pyhwp`, `markdownify` (requirements.txt 반영).
