# PDFKit Layout

## Page Size

PDFKit supports predefined page sizes when creating a new document or adding a new page.

Use the `size` option in the `PDFDocument` constructor to set the default page size for the document.

```js
const PDFDocument = require('pdfkit');

const doc = new PDFDocument({
  size: 'A4'
});
```

Use the `size` option in `addPage()` to set the page size for a specific page.

```js
doc.addPage({
  size: 'A4'
});
```

Implementation requirements:

* Use `A4` as the default page size for report, proposal, official document, and printable PDF exports.
* Set the document size in the `PDFDocument` constructor unless a specific page requires a different size.
* Use `addPage({ size: 'A4' })` only when a new page needs explicit page-size control.
* Avoid mixing different page sizes in the same document unless the template explicitly requires it.

## A4 Dimensions

PDFKit uses PostScript points for page dimensions.

A4 size:

* Width: `595.28 pt`
* Height: `841.89 pt`

```js
const A4_WIDTH = 595.28;
const A4_HEIGHT = 841.89;
```

Implementation requirements:

* Treat A4 portrait pages as `595.28 x 841.89` points.
* Use these values when calculating fixed-position layouts.
* Do not hardcode layout coordinates without considering page margins.
* Use shared constants for page width and height.

## Basic A4 Document Setup

Recommended default setup for A4 PDF exports:

```js
const PDFDocument = require('pdfkit');

const doc = new PDFDocument({
  size: 'A4',
  layout: 'portrait',
  margins: {
    top: 56,
    right: 50,
    bottom: 56,
    left: 50
  }
});
```

Implementation requirements:

* Use portrait A4 as the default layout.
* Use explicit margins for predictable layout behavior.
* Keep layout settings centralized in the PDF exporter configuration.
* Do not duplicate page size and margin values across rendering functions.

## Margin Settings

PDFKit supports margin configuration through the document options.

Use a single `margin` value to apply the same margin to all sides.

```js
const doc = new PDFDocument({
  size: 'A4',
  margin: 50
});
```

Use `margins` when each side needs a different value.

```js
const doc = new PDFDocument({
  size: 'A4',
  margins: {
    top: 56,
    right: 50,
    bottom: 56,
    left: 50
  }
});
```

Implementation requirements:

* Use `margins` instead of a single `margin` when official document layouts require different top, bottom, left, or right spacing.
* Use consistent margins for all standard report-style PDF exports.
* Keep enough bottom margin for page numbers and footer content.
* Keep enough top margin for headers, titles, or institutional branding.
* Do not place content directly at the physical page edge unless generating a full-bleed design.

## Recommended Margin Constants

Use shared constants for margin and content area calculation.

```js
const PAGE = {
  size: 'A4',
  width: 595.28,
  height: 841.89
};

const MARGINS = {
  top: 56,
  right: 50,
  bottom: 56,
  left: 50
};

const CONTENT = {
  x: MARGINS.left,
  y: MARGINS.top,
  width: PAGE.width - MARGINS.left - MARGINS.right,
  height: PAGE.height - MARGINS.top - MARGINS.bottom
};
```

Implementation requirements:

* Use `CONTENT.x` as the default left position for text, tables, and images.
* Use `CONTENT.y` as the default starting position for body content.
* Use `CONTENT.width` as the default wrapping width for paragraphs.
* Use `CONTENT.height` when checking whether content can fit on the current page.
* Use these constants in text, image, and table renderers.

## Content Area Calculation

The printable content area is the page size minus margins.

```js
const contentWidth = PAGE.width - MARGINS.left - MARGINS.right;
const contentHeight = PAGE.height - MARGINS.top - MARGINS.bottom;
```

Example usage:

```js
doc.text('Document title', MARGINS.left, MARGINS.top, {
  width: contentWidth,
  align: 'center'
});
```

Implementation requirements:

* Calculate available content width before rendering paragraphs, tables, and images.
* Use the content width as the default `width` value for long text.
* Use the content width as the default `maxWidth` value for tables.
* Use the content width as the maximum width for report images.
* Prevent text, tables, and images from exceeding the content area.

## Adding A4 Pages

When adding a new page, preserve the same A4 layout and margins.

```js
doc.addPage({
  size: 'A4',
  layout: 'portrait',
  margins: {
    top: 56,
    right: 50,
    bottom: 56,
    left: 50
  }
});
```

Implementation requirements:

* Use the same layout configuration for all automatically added pages.
* Ensure headers and footers are rendered consistently on new pages.
* Avoid creating pages with default margins accidentally.
* Use a shared helper function when creating new pages.

Recommended helper:

```js
function addA4Page(doc) {
  doc.addPage({
    size: 'A4',
    layout: 'portrait',
    margins: {
      top: 56,
      right: 50,
      bottom: 56,
      left: 50
    }
  });
}
```

## Layout Orientation

Use portrait layout by default.

```js
const doc = new PDFDocument({
  size: 'A4',
  layout: 'portrait'
});
```

Use landscape layout only when the template requires wide content.

```js
const doc = new PDFDocument({
  size: 'A4',
  layout: 'landscape'
});
```

Implementation requirements:

* Use portrait A4 for reports, official documents, proposals, and text-heavy exports.
* Use landscape A4 only for wide tables, comparison charts, or presentation-like PDF pages.
* Do not switch orientation within the same document unless the template explicitly requires it.

## Recommended A4 Layout Presets

Report layout:

```js
const REPORT_LAYOUT = {
  size: 'A4',
  layout: 'portrait',
  margins: {
    top: 56,
    right: 50,
    bottom: 56,
    left: 50
  }
};
```

Official document layout:

```js
const OFFICIAL_DOCUMENT_LAYOUT = {
  size: 'A4',
  layout: 'portrait',
  margins: {
    top: 64,
    right: 56,
    bottom: 64,
    left: 56
  }
};
```

Compact layout:

```js
const COMPACT_LAYOUT = {
  size: 'A4',
  layout: 'portrait',
  margins: {
    top: 40,
    right: 40,
    bottom: 40,
    left: 40
  }
};
```

Wide table layout:

```js
const WIDE_TABLE_LAYOUT = {
  size: 'A4',
  layout: 'landscape',
  margins: {
    top: 40,
    right: 40,
    bottom: 40,
    left: 40
  }
};
```

Implementation requirements:

* Select a layout preset based on the export template type.
* Keep layout presets in a shared configuration file.
* Do not define layout values inside individual rendering functions.
* Use compact margins only when the template requires more content density.

## Page Boundary Validation

The exporter should validate whether rendered content fits inside the available content area.

```js
function isWithinContentArea(x, y, width, height) {
  return (
    x >= MARGINS.left &&
    y >= MARGINS.top &&
    x + width <= PAGE.width - MARGINS.right &&
    y + height <= PAGE.height - MARGINS.bottom
  );
}
```

Implementation requirements:

* Validate fixed-position text boxes, images, and tables.
* Prevent content from overflowing into the page margins.
* Add a new page before rendering content that cannot fit on the current page.
* Test long Korean text, large images, and multi-row tables near the bottom of a page.

## Exporter Requirements

The PDF exporter should support these layout features:

* A4 page size
* Portrait orientation
* Landscape orientation
* Global document margins
* Per-page margin configuration
* Content area calculation
* Shared page layout constants
* Layout presets by document type
* New page creation with consistent size and margins
* Fixed-position content placement
* Flow-based content placement
* Page boundary validation

The PDF exporter should validate these cases:

* A4 report with normal margins
* A4 official document with wider margins
* A4 landscape page with a wide table
* Long text near the bottom of a page
* Image inside the content area
* Table inside the content area
* Header and footer inside the margin-safe area
* Page number placement
* Multiple pages with consistent layout
* Explicit `addPage()` calls preserving layout options

Layout configuration should be centralized. Rendering modules should read page size, margins, and content dimensions from shared layout settings instead of hardcoding coordinates.