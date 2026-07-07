# Workflows

This document describes the intended product workflow for edudoc. It is a
direction document, not a full implementation spec.

## Product Workflow

```text
source documents
-> source bundle
-> document understanding
-> generation request
-> document planner
-> generator
-> validator
-> template/layout renderer
-> exporter
```

## Stage Meanings

- Source documents: user-provided files, examples, previous materials, templates,
  and reference documents.
- Source bundle: filtered, grouped source material. Repository control files such
  as `README.md` and `AGENTS.md` are not business source documents.
- Document understanding: extract facts, tables, attachments, section structure,
  style notes, and useful context.
- Generation request: interpret the user's task, audience, target document type,
  purpose, tone, and requested output format.
- Document planner: choose the target structure before writing.
- Generator: create a new Markdown draft for the task.
- Validator: run deterministic checks for the selected document type.
- Template/layout renderer: apply document-type layout and style decisions.
- Exporter: render the final draft to DOCX, HWPX, PDF, or PPTX.

## Boundary Rule

Export is the final rendering step. It should not define the whole product.

The project may still convert HWPX/HWP/Markdown into normalized Markdown or
DocumentModel(JSON), but that normalization is a foundation for understanding,
generation, validation, and final rendering.

## Implemented Intake Foundation

`core/source_bundle.py` provides the first small runtime layer for this workflow:

```text
source documents -> filtered source bundle manifest
```

It records processable source documents, ignored repository/control/generated
files, unsupported source candidates, and summary counts. It reuses the same
bulk-input filtering rules as the pipeline.

It does not perform document understanding, user request planning, generation,
validation, rendering, or export.

## Near-Term Implementation Candidates

- document understanding profile
- user request planner
- official report generator
- document-type validators
- template/render/export after generation
