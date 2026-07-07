# Target Document Profiles

TargetDocumentProfile is the first small bridge between source/reference
understanding and document generation.

It does not generate documents by itself. It records what a target document type
requires so later planners and generators can map source facts into the right
shape.

Implemented runtime metadata:

- `core/target_document_profiles.py`
- `tests/test_target_document_profiles.py`
- `core/source_profile.py`
- `core/document_plan.py`
- `core/generators/public_plan_generator.py`
- `scripts/public_plan/generate_from_samples.py`
- `tests/test_source_profile_document_plan.py`
- `tests/test_public_plan_generator.py`
- `tests/test_public_plan_cli.py`

## Current Profiles

The first profiles are extracted from the protected reference skill
`skills/hwp-skill/`.

Protected skill files are not modified, copied into `core/`, or made required by
the default runtime.

### 행안부 표준 기안문

Profile id:

```text
standard_gongmun
```

Purpose:

- conservative public-office draft generation
- Gongmun writing validation through `validators.gongmun_rules.py`
- optional HWPX rendering through a future adapter around
  `skills/hwp-skill/scripts/gonmun.py`

Key source-profile fields:

- source titles
- institutions
- dates
- document numbers
- legal or policy basis
- attachments
- key actions

### 정부 표준 보도자료

Profile id:

```text
government_press_release
```

Purpose:

- fact-preserving government-style press release drafts
- planned press-release validation
- optional HWPX rendering through a future adapter around
  `skills/hwp-skill/scripts/bodojaryo.py`

Key source-profile fields:

- source titles
- institutions
- dates
- people or departments
- statistics
- quoted claims
- key actions

### 공공기관 계획서

Profile id:

```text
public_institution_plan
```

Purpose:

- public-institution planning document drafts
- explicit title-page and table-of-contents decisions
- planned public-plan validation
- optional HWPX rendering through a future adapter around
  `skills/hwp-skill/scripts/gyehoek.py`

Key source-profile fields:

- source titles
- institutions
- dates
- tables
- statistics
- budgets
- schedules
- key actions
- risks

## Boundary

Profiles are not exporters.

They do not call protected skill scripts directly, do not install dependencies,
and do not clone repositories. They only define the target structure, required
fields, source-profile facts, unknown-field policy, validation target, and
optional renderer reference.

Default generation should still produce Markdown or DocumentModel first.

Final rendering to DOCX/PDF/HWPX remains a downstream exporter or optional
renderer step.

## SourceProfile And DocumentPlan

`SourceProfile` is the current deterministic source-understanding scaffold.

It can collect reusable facts from normalized Markdown or DocumentModel objects:

- source titles
- institutions
- dates
- document numbers
- table summaries
- statistics
- budgets
- schedules
- key actions
- risks
- attachments

It does not parse PDF reference samples. PDF files in
`references/document-types/*/samples/` are tracked as reference samples only
until a separate extraction or source-note step is introduced.

`DocumentPlan` combines:

```text
SourceProfile + TargetDocumentProfile
```

and creates a section-level planning scaffold.

For `public_institution_plan`, the current plan covers:

- 표지 및 목차 결정
- 추진 배경
- 현황 및 문제점
- 추진 목표
- 주요 추진 과제
- 추진 일정
- 예산
- 기대 효과
- 향후 계획

Missing facts are preserved as `확인 필요`.

This bridge now feeds `core/generators/public_plan_generator.py`, which can
produce a conservative public-plan Markdown draft without inventing missing
facts.

## Next Integration Step

The current implemented flow is:

```text
SourceBundle
-> SourceProfile
-> TargetDocumentProfile
-> DocumentPlan
-> Markdown/DocumentModel draft
```

For `public_institution_plan`, `generate_public_plan_markdown()` renders the
DocumentPlan into a Markdown draft with:

- 작성 기준
- 추진 배경
- 현황 및 문제점
- 추진 목표
- 주요 추진 과제
- 추진 일정
- 예산
- 기대 효과
- 향후 계획
- 기준 참고 문서
- 확인 필요

The implemented command path is:

```text
SourceBundle
-> SourceProfile
-> TargetDocumentProfile
-> DocumentPlan
-> public-plan Markdown draft
-> validation
-> optional final rendering
```

The command path is now available:

```bash
python scripts/public_plan/generate_from_samples.py samples --out exports/public-plan
python scripts/public_plan/generate_from_samples.py samples --out exports/public-plan --export docx
```

It writes:

- `public_plan.source_profile.json`
- `public_plan.document_plan.json`
- `public_plan.generated.md`
- `public_plan.docx` when `--export docx` is used

This is what will let edudoc answer requests like:

```text
Use the files in samples and create a public-institution report in another format.
```
