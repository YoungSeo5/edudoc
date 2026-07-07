# PDFKit Tables

## Basic Table Rendering

Use `doc.table()` to add a table to a PDF document.

```js
doc.table({
  data: [
    ['Column 1', 'Column 2', 'Column 3'],
    ['One value goes here', 'Another one here', 'Status value']
  ]
});
```

Tables can also be built row by row.

```js
doc.table()
  .row(['Column 1', 'Column 2', 'Column 3'])
  .row(['One value goes here', 'Another one here', 'Status value']);
```

Implementation requirements:

* Use `doc.table()` for structured data such as comparison tables, schedules, summaries, and feature lists.
* Prefer the `data` array format when rendering a complete table from structured input.
* Use the row builder format only when rows must be appended dynamically.
* Keep table rendering logic inside the PDF exporter layer.

## Table Flow Behavior

PDFKit tracks the current table position automatically. Content added after a table is placed below the table.

```js
doc
  .text('Before table')
  .table({
    data: [
      ['Column 1', 'Column 2', 'Column 3'],
      ['One value goes here', 'Another one here', 'Status value']
    ]
  })
  .text('After table');
```

Implementation requirements:

* Use table flow behavior for report-style documents.
* Test text placement after tables to prevent overlapping content.
* Use explicit table positions only when fixed layout placement is required.

## Column Widths

Use `columnStyles` to define table column widths.

Column width values:

* `'*'`: Distributes remaining width equally.
* Fixed number: Uses an exact width in PDF points.

```js
doc.table({
  columnStyles: [100, '*', 200, '*'],
  data: [
    ['width=100', 'star-sized', 'width=200', 'star-sized'],
    [
      'fixed-width cells use the specified width',
      { text: 'Secondary value', textColor: 'grey' },
      { text: 'Another secondary value', textColor: 'grey' },
      { text: 'Additional value', textColor: 'grey' }
    ]
  ]
});
```

Implementation requirements:

* Use fixed widths for predictable columns such as numbers, dates, and labels.
* Use `'*'` for flexible text-heavy columns.
* Define column widths explicitly for production templates.
* Test long Korean text inside fixed-width columns.

## Row Heights

Use `rowStyles` to define row heights.

Different height per row:

```js
doc.table({
  rowStyles: [20, 50, 70],
  data: [
    ['row 1 with height 20', 'column B'],
    ['row 2 with height 50', 'column B'],
    ['row 3 with height 70', 'column B']
  ]
});
```

Same height for all rows:

```js
doc.table({
  rowStyles: 40,
  data: [
    ['row 1', 'column B'],
    ['row 2', 'column B'],
    ['row 3', 'column B']
  ]
});
```

Dynamic height from a function:

```js
doc.table({
  rowStyles: (row) => (row + 1) * 25,
  data: [
    ['row 1', 'column B'],
    ['row 2', 'column B'],
    ['row 3', 'column B']
  ]
});
```

Implementation requirements:

* Use fixed row heights only when the template requires strict visual alignment.
* Use automatic or dynamic row heights for variable-length content.
* Validate that text does not overflow fixed-height rows.

## Column Span and Row Span

Cells can define `colSpan` and `rowSpan`.

```js
doc.table({
  columnStyles: [200, '*', '*'],
  data: [
    [{ colSpan: 2, text: 'Header with colspan = 2' }, 'Header 3'],
    ['Header 1', 'Header 2', 'Header 3'],
    ['Sample value 1', 'Sample value 2', 'Sample value 3'],
    [
      {
        rowSpan: 3,
        text: 'rowspan set to 3\nLong text content can be placed here.'
      },
      'Sample value 2',
      'Sample value 3'
    ],
    ['Sample value 2', 'Sample value 3'],
    ['Sample value 2', 'Sample value 3'],
    [
      'Sample value 1',
      {
        colSpan: 2,
        rowSpan: 2,
        text: 'Both rowspan and colspan can be defined at the same time.'
      }
    ],
    ['Sample value 1']
  ]
});
```

Implementation requirements:

* Use `colSpan` for grouped headers and merged summary cells.
* Use `rowSpan` only when the table structure requires vertical grouping.
* Avoid complex spans in early MVP templates unless they are required.
* Test span behavior with long text and page breaks.

## Border Styling

Use `rowStyles`, `columnStyles`, `defaultStyle`, or cell-level styles to control borders.

No borders:

```js
doc.table({
  rowStyles: { border: false },
  data: [
    ['Header 1', 'Header 2', 'Header 3'],
    ['Sample value 1', 'Sample value 2', 'Sample value 3'],
    ['Sample value 1', 'Sample value 2', 'Sample value 3']
  ]
});
```

Header bottom border only:

```js
doc.table({
  rowStyles: (i) => {
    return i < 1 ? { border: [0, 0, 1, 0] } : { border: false };
  },
  data: [
    ['Header 1', 'Header 2', 'Header 3'],
    ['Sample value 1', 'Sample value 2', 'Sample value 3'],
    ['Sample value 1', 'Sample value 2', 'Sample value 3']
  ]
});
```

Light horizontal lines:

```js
doc.table({
  rowStyles: (i) => {
    return i < 1
      ? { border: [0, 0, 2, 0], borderColor: 'black' }
      : { border: [0, 0, 1, 0], borderColor: '#aaa' };
  },
  data: [
    ['Header 1', 'Header 2', 'Header 3'],
    ['Sample value 1', 'Sample value 2', 'Sample value 3'],
    ['Sample value 1', 'Sample value 2', 'Sample value 3']
  ]
});
```

Implementation requirements:

* Use light horizontal lines for report-style tables.
* Avoid heavy full borders unless the document type requires them.
* Use stronger borders for headers and summary rows.
* Keep border styling consistent across generated documents.

## Custom Cell Styling

Use `defaultStyle` for all cells, `columnStyles` for column-based styling, `rowStyles` for row-based styling, and cell-level options for individual cells.

```js
doc.table({
  defaultStyle: {
    border: 1,
    borderColor: 'gray'
  },
  columnStyles: (i) => {
    if (i === 0) {
      return {
        border: { left: 2 },
        borderColor: { left: 'black' }
      };
    }

    if (i === 2) {
      return {
        border: { right: 2 },
        borderColor: { right: 'black' }
      };
    }
  },
  rowStyles: (i) => {
    if (i === 0) {
      return {
        border: { top: 2 },
        borderColor: { top: 'black' }
      };
    }

    if (i === 3) {
      return {
        border: { bottom: 2 },
        borderColor: { bottom: 'black' }
      };
    }
  },
  data: [
    ['Header 1', 'Header 2', 'Header 3'],
    ['Sample value 1', 'Sample value 2', 'Sample value 3'],
    ['Sample value 1', 'Sample value 2', 'Sample value 3'],
    ['Sample value 1', 'Sample value 2', 'Sample value 3']
  ]
});
```

Implementation requirements:

* Use `defaultStyle` for common table styling.
* Use `rowStyles` for header, body, and summary row styling.
* Use `columnStyles` for label columns, numeric columns, and fixed layout columns.
* Use cell-level styles only for exceptional cells.

## Zebra Row Styling

Use `rowStyles` to apply alternating background colors.

```js
doc.table({
  rowStyles: (i) => {
    if (i % 2 === 0) {
      return { backgroundColor: '#ccc' };
    }
  },
  data: [
    ['Sample value 1', 'Sample value 2', 'Sample value 3'],
    ['Sample value 1', 'Sample value 2', 'Sample value 3'],
    ['Sample value 1', 'Sample value 2', 'Sample value 3'],
    ['Sample value 1', 'Sample value 2', 'Sample value 3']
  ]
});
```

Implementation requirements:

* Use zebra styling only when it improves readability.
* Keep background colors subtle for official documents.
* Avoid zebra styling in minimal official-letter layouts unless required.

## Optional Cell Borders

A cell can define borders using boolean values, numeric values, arrays, or side-specific objects.

Examples:

```js
doc.table({
  data: [
    [
      {
        border: [true, false, false, false],
        backgroundColor: '#eee',
        text: 'Top border only'
      },
      {
        border: false,
        backgroundColor: '#ddd',
        text: 'No border'
      },
      {
        border: true,
        backgroundColor: '#eee',
        text: 'All borders'
      }
    ],
    [
      {
        rowSpan: 3,
        border: true,
        backgroundColor: '#eef',
        text: 'rowSpan: 3\nAll borders'
      },
      {
        border: undefined,
        backgroundColor: '#eee',
        text: 'Default border'
      },
      {
        border: [false, false, false, true],
        backgroundColor: '#ddd',
        text: 'Left border only'
      }
    ],
    [
      {
        colSpan: 2,
        border: true,
        backgroundColor: '#efe',
        text: 'colSpan: 2\nAll borders'
      }
    ],
    [
      {
        border: 0,
        backgroundColor: '#eee',
        text: 'No border'
      },
      {
        border: [false, true, true, false],
        backgroundColor: '#ddd',
        text: 'Top and right borders'
      }
    ]
  ]
});
```

Implementation requirements:

* Use side-specific borders for header dividers, section separators, and summary rows.
* Prefer simple border rules for maintainability.
* Avoid highly complex per-cell border rules unless a template requires them.

## Style Precedence

When multiple styles are defined, the final cell style follows this precedence order:

1. `defaultStyle`
2. `columnStyles`
3. `rowStyles`
4. Cell-level style

Example:

```js
doc.table({
  defaultStyle: { border: 1 },
  columnStyles: { border: { right: 2 } },
  rowStyles: { border: { bottom: 3 } },
  data: [
    [{ border: { left: 4 }, text: 'Styled cell' }]
  ]
});
```

Resulting merged style:

```js
{
  border: {
    top: 1,
    right: 2,
    bottom: 3,
    left: 4
  }
}
```

Implementation requirements:

* Define shared styling in `defaultStyle`.
* Apply broad layout rules through `columnStyles` and `rowStyles`.
* Use cell-level styles only for overrides.
* Keep this precedence in mind when debugging unexpected table styles.

## Table Options

Common table options:

* `position`: Table position. Defaults to `{ x: doc.x, y: doc.y }`.
* `maxWidth`: Maximum width the table can expand to.
* `columnStyles`: Column definitions.
* `rowStyles`: Row definitions.
* `defaultStyle`: Default style applied to every cell.
* `data`: Table data to render.
* `debug`: Shows debug lines for all cells when enabled.

Implementation requirements:

* Use `maxWidth` to prevent tables from exceeding the content area.
* Use `position` for fixed-layout tables.
* Use `debug: true` only during development.

## Cell Options

Common cell options:

* `text`: Cell value. `null` and `undefined` are not rendered, but the cell is still outlined.
* `rowSpan`: Number of rows the cell covers.
* `colSpan`: Number of columns the cell covers.
* `padding`: Cell padding.
* `border`: Cell border.
* `borderColor`: Cell border color.
* `font`: Cell font options.
* `backgroundColor`: Cell background color.
* `align`: Cell text alignment.
* `textStroke`: Text stroke.
* `textStrokeColor`: Text stroke color.
* `textColor`: Cell text color.
* `type`: Cell type for accessibility. Defaults to `TD`.
* `textOptions`: Text options such as rotation.
* `debug`: Shows debug lines for the cell when enabled.

Implementation requirements:

* Use `padding` for readable table cells.
* Use `textColor` and `backgroundColor` for header or emphasis styling.
* Use `align` for numeric values, labels, and centered status values.
* Use `type` when accessibility tagging is required.

## Column Options

Column options extend cell options.

Additional column options:

* `width`: Column width. Defaults to `'*'`.
* `minWidth`: Minimum column width.
* `maxWidth`: Maximum column width.

Implementation requirements:

* Use `minWidth` and `maxWidth` when table data is dynamic.
* Use fixed `width` for predictable export templates.

## Row Options

Row options extend cell options.

Additional row options:

* `height`: Row height. Defaults to automatic.
* `minHeight`: Minimum row height.
* `maxHeight`: Maximum row height.

Implementation requirements:

* Use `minHeight` for rows that need visual consistency.
* Use `maxHeight` only when overflow or clipping behavior is acceptable.

## Recommended Table Patterns

Simple report table:

```js
doc.table({
  maxWidth: 500,
  columnStyles: ['*', '*', '*'],
  rowStyles: (i) => {
    return i === 0
      ? { border: [0, 0, 2, 0], borderColor: 'black' }
      : { border: [0, 0, 1, 0], borderColor: '#aaa' };
  },
  data: [
    ['Category', 'Description', 'Priority'],
    ['PDF', 'Report and document export', 'High'],
    ['PPTX', 'Presentation export', 'High'],
    ['HWPX', 'Official document export', 'Medium']
  ]
});
```

Label-value table:

```js
doc.table({
  maxWidth: 500,
  columnStyles: [140, '*'],
  rowStyles: { border: [0, 0, 1, 0], borderColor: '#aaa' },
  data: [
    ['Document title', 'AI Content Generation Report'],
    ['Output format', 'PDF'],
    ['Generated by', 'PDF Exporter'],
    ['Status', 'Draft']
  ]
});
```

Comparison table:

```js
doc.table({
  maxWidth: 500,
  columnStyles: [120, '*', '*'],
  rowStyles: (i) => {
    return i === 0
      ? {
          backgroundColor: '#eee',
          border: [0, 0, 2, 0],
          borderColor: 'black'
        }
      : {
          border: [0, 0, 1, 0],
          borderColor: '#aaa'
        };
  },
  data: [
    ['Feature', 'Current method', 'Generated output'],
    ['Document creation', 'Manual writing', 'Structured automatic generation'],
    ['Format conversion', 'Separate tools', 'Unified exporter pipeline'],
    ['Template reuse', 'Manual copy and edit', 'Template-based generation']
  ]
});
```

## Exporter Requirements

The PDF exporter should support these table features:

* Basic table rendering
* Row-based table construction
* Column width control
* Row height control
* Flexible `'*'` column sizing
* Fixed column sizing
* Header row styling
* Light horizontal line styling
* No-border tables
* Cell padding
* Cell text color
* Cell background color
* Cell text alignment
* Column span
* Row span
* Optional borders
* Table positioning
* Maximum table width
* Debug mode for development

The PDF exporter should validate these cases:

* Tables with long Korean text
* Tables with mixed Korean and English text
* Tables with many rows
* Tables with many columns
* Tables near the bottom of a page
* Tables after long paragraphs
* Tables followed by text
* Tables with fixed column widths
* Tables with flexible columns
* Tables with row spans
* Tables with column spans
* Tables with empty, `null`, or `undefined` cells
* Tables with styled header rows

Table rendering logic should preserve readability by default. Use simple, consistent styling unless the template requires more complex table formatting.
