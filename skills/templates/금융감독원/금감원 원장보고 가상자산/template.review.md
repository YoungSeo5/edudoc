# Template Content Separation Review

- Template ID: `fss_virtual_asset_report`
- Status: `candidate`
- XML structure, style IDs, and table shapes are preserved.
- Rendering removes `linesegarray` caches from changed sections so Hancom can recalculate text layout.
- Rendering retains `linesegarray` caches in unchanged sections.
- Only selected `<hp:t>` text contents were replaced with placeholders.

## Sections

- `section0.xml`: text_nodes=19, placeholders=11

## Placeholder Fields

- `date_01` -> `{{date_01}}` [date] (table=0, row=0, col=0)
- `document_title_01` -> `{{document_title_01}}` [document_title] (table=0, row=0, col=2)
- `checkbox_line_01` -> `{{checkbox_line_01}}` [checkbox_line] (table=0, row=1, col=2)
- `body_paragraph_01` -> `{{body_paragraph_01}}` [body_paragraph]
- `body_bullet_01` -> `{{body_bullet_01}}` [body_bullet]
- `stat_note_01` -> `{{stat_note_01}}` [stat_note]
- `detail_note_01` -> `{{detail_note_01}}` [detail_note]
- `conclusion_01` -> `{{conclusion_01}}` [conclusion] (table=2, row=0, col=0)
- `department_01` -> `{{department_01}}` [department] (table=3, row=0, col=0)
- `contact_01` -> `{{contact_01}}` [contact] (table=3, row=0, col=1)
- `contact_02` -> `{{contact_02}}` [contact] (table=3, row=0, col=2)
