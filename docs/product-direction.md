# Product Direction

edudoc is a **document task automation system**, not a file-format conversion
tool.

The product goal is:

```text
source/reference materials + user intent
-> newly generated task document
-> document-type validation
-> final rendering to DOCX / HWPX / PDF / PPTX when needed
```

File conversion remains useful, but it is a supporting capability. The core
product is not `input file -> same content in another extension`. The core
product is `source materials + requested task -> new document`.

## What Source Documents Mean

Source documents are reference material. They may provide:

- facts and evidence
- table data and attachment names
- section structure
- tone and style examples
- institutional wording patterns
- layout or template clues

They should not be blindly converted as if the user always wants the same
document in another format.

## User Request Controls The Output

The user request determines:

- the task
- target document type
- audience
- purpose
- tone
- required output format
- which source materials are evidence, examples, or templates

Example user request:

```text
이 파일들을 읽어서 교육청에 보고하는 공식문서 HWPX 형태 보고서를 작성해줘.
```

Expected interpretation:

- task: generate a new document
- document type: official report
- audience: education office
- output format: HWPX
- source material: provided files
- tone: formal
- purpose: reporting

## Target Document Tasks

edudoc should grow toward generating and validating task-oriented documents such
as:

- 공문
- 공식 보고서
- 활동보고서
- 신청서 / 사업계획서
- 홍보 안내문
- 카드뉴스 문구
- 발표자료 초안
- 영상 스크립트 / 스토리보드

## Examples

### Gongmun

```text
User request:
행사 안내 내용을 바탕으로 학교에 보낼 공문 초안을 만들어줘.

System goal:
source notes -> 공문 Markdown draft -> gongmun_rules validation -> final export if requested
```

### Promotional Material

```text
User request:
이 사업계획서를 읽고 학부모 대상 홍보 안내문을 만들어줘.

System goal:
source facts -> audience-appropriate 안내문 draft -> promotional-document checks -> export
```

### Card News

```text
User request:
보고서 내용을 카드뉴스 6장 분량의 문구로 바꿔줘.

System goal:
source document -> slide/card outline -> short copy per card -> reviewable Markdown
```

### Presentation Draft

```text
User request:
이 활동보고서를 발표자료 초안으로 정리해줘.

System goal:
source document -> presentation outline -> slide titles and bullets -> PPTX export later
```

### Video Script

```text
User request:
이 안내문을 1분 홍보 영상 스크립트와 스토리보드로 바꿔줘.

System goal:
source content -> scene plan -> narration/script -> storyboard notes
```

## Workflow Boundary

Keep these layers separate:

```text
1. Source intake
   collect source/reference documents and ignore repository control files

2. Document understanding
   extract facts, structure, tables, sections, style notes, and context

3. Request interpretation
   understand the user's task and target document type

4. Generation
   create a new task-oriented Markdown draft

5. Validation
   check the draft according to the target document type

6. Rendering/export
   render the validated draft to DOCX / HWPX / PDF / PPTX when needed
```

Export quality matters, but export is downstream of generation. DOCX table
quality, PDF stability, and HWPX package quality are final-deliverable concerns,
not the whole product direction.

## What "Learning From Files" Means For Now

For now, "learning" means:

```text
reference corpus + source notes + style profiles + templates + deterministic extraction
```

It does not mean model fine-tuning or calling external LLM APIs unless that is
added later as a separate decision.

## Current Reality

- HWPX/HWP/Markdown normalization is still an important foundation.
- The only implemented generation flow is the small deterministic Gongmun
  harness.
- DOCX is partially stabilized as a pip-native final-rendering path.
- PDF remains fallback/experimental.
- HWPX export is experimental and not layout-compliant.
- General report, application, promotional, card-news, presentation, and video
  script generation are product goals, not implemented general features yet.

## Next Implementation Themes

Future implementation should move in this order unless the user chooses a
different slice:

- source bundle and input filtering
- document understanding profile
- user request planner
- official report generator
- document-type validators
- template/layout rendering and export after generation
