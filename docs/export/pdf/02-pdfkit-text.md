# PDFKit Text

## Basic Text Output

Use `doc.text()` to add text to a PDF document.

```js
doc.text('Hello world!');
```

PDFKit tracks the current text position automatically. Additional `doc.text()` calls are placed below the previous text.

To place text at a specific position, pass `x` and `y` coordinates.

```js
doc.text('Hello world!', 100, 100);
```

Use `moveDown()` or `moveUp()` to move the current text position by line units.

```js
doc.moveDown();
doc.moveDown(2);
doc.moveUp();
```

Implementation requirements:

* Use `doc.text()` for headings, paragraphs, captions, labels, and short inline text.
* Use explicit `x` and `y` coordinates only when fixed layout placement is required.
* Use `moveDown()` and `moveUp()` for vertical spacing between text blocks.
* Avoid hardcoding too many coordinates in document-style PDFs unless the layout requires precise positioning.

## Line Wrapping and Alignment

PDFKit supports automatic line wrapping. If no options are provided, text wraps within the page margins and flows below the previous text.

PDFKit can automatically add new pages when long text exceeds the current page.

Use `width` to control the wrapping area.

```js
doc.text('Long paragraph text goes here.', {
  width: 410
});
```

Use `lineBreak: false` to disable automatic line wrapping.

```js
doc.text('This text will not wrap.', {
  lineBreak: false
});
```

Use `height` to clip text to a fixed height.

```js
doc.text('Long text content goes here.', {
  width: 410,
  height: 100
});
```

Supported alignment values:

* `left`
* `center`
* `right`
* `justify`

Example:

```js
const lorem = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit.';

doc.fontSize(8);

doc.text(`This text is left aligned. ${lorem}`, {
  width: 410,
  align: 'left'
});

doc.moveDown();

doc.text(`This text is centered. ${lorem}`, {
  width: 410,
  align: 'center'
});

doc.moveDown();

doc.text(`This text is right aligned. ${lorem}`, {
  width: 410,
  align: 'right'
});

doc.moveDown();

doc.text(`This text is justified. ${lorem}`, {
  width: 410,
  align: 'justify'
});
```

Implementation requirements:

* Use `align: 'center'` for titles and cover-page headings.
* Use `align: 'left'` for normal body text.
* Use `align: 'justify'` only for long report-style paragraphs.
* Always set `width` for controlled layouts.
* Test long Korean paragraphs to confirm wrapping and page breaks.

## Text Styling Options

PDFKit supports multiple text styling options through the `doc.text()` options object.

Important options for this project:

* `lineBreak`: Set to `false` to disable line wrapping.
* `width`: Text wrapping width.
* `height`: Maximum text height before clipping.
* `rotation`: Text rotation in degrees.
* `ellipsis`: Character displayed when text is too long. Set to `true` to use the default ellipsis.
* `columns`: Number of text columns.
* `columnGap`: Gap between columns.
* `indent`: First-line paragraph indentation in PDF points.
* `indentAllLines`: Whether all lines should be indented.
* `paragraphGap`: Gap between paragraphs.
* `lineGap`: Gap between lines.
* `wordSpacing`: Space between words.
* `characterSpacing`: Space between characters.
* `horizontalScaling`: Horizontal text scale percentage.
* `fill`: Whether to fill the text.
* `stroke`: Whether to stroke the text.
* `link`: URL linked to the text.
* `goTo`: Anchor target.
* `destination`: Anchor name for this text.
* `underline`: Whether to underline the text.
* `strike`: Whether to strike through the text.
* `oblique`: Whether to slant the text.
* `baseline`: Vertical alignment of the text relative to the insertion point.
* `continued`: Whether the next text call should continue from the same text flow.
* `features`: OpenType feature tags.

Example with multiple columns:

```js
const lorem = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit.';

doc.text(lorem, {
  columns: 3,
  columnGap: 15,
  height: 100,
  width: 465,
  align: 'justify'
});
```

Implementation requirements:

* Use `lineGap` and `paragraphGap` for readable report-style documents.
* Use `ellipsis` for fixed-size text boxes such as cards, labels, and summaries.
* Use `columns` only for newsletter-style or brochure-style layouts.
* Use `link` for URLs in generated reports and promotional materials.
* Use `continued` for rich text segments with mixed styles.

## Text Measurement

Use text measurement methods when precise layout calculation is required.

Available methods:

* `widthOfString(text, options)`
* `heightOfString(text, options)`
* `boundsOfString(text, options)`
* `boundsOfString(text, x, y, options)`

`widthOfString()` returns the rendered text width.

```js
const width = doc.widthOfString('Hello world');
```

`heightOfString()` returns the rendered text height, including wrapping behavior.

```js
const height = doc.heightOfString('Long paragraph text', {
  width: 300
});
```

`boundsOfString()` returns the text bounding box.

```js
const bounds = doc.boundsOfString('Rotated or wrapped text', {
  width: 300
});
```

The returned bounds object has this structure:

```js
{
  x: 0,
  y: 0,
  width: 0,
  height: 0
}
```

Implementation requirements:

* Use `heightOfString()` before rendering long text blocks in fixed-height areas.
* Use `boundsOfString()` when rotated text or multi-line wrapped text must be positioned accurately.
* Use measurement methods to prevent text overflow in cards, tables, captions, and layout boxes.

## Lists

Use `doc.list()` to create bulleted lists.

```js
doc.list([
  'First item',
  'Second item',
  'Third item'
]);
```

Nested arrays can be used for multilevel lists.

```js
doc.list([
  'First item',
  [
    'Nested item 1',
    'Nested item 2'
  ],
  'Second item'
]);
```

Additional list options:

* `bulletRadius`
* `textIndent`
* `bulletIndent`

Implementation requirements:

* Use lists for feature summaries, requirements, benefits, and step-by-step content.
* Use nested lists only when the document type requires hierarchy.
* Keep list indentation consistent across all generated PDFs.

## Rich Text

PDFKit supports simple rich text using the `continued` option.

When `continued: true` is used, the next `doc.text()` call continues from the same text flow.

```js
const lorem = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit.';

doc.fillColor('green')
  .text(lorem.slice(0, 50), {
    width: 465,
    continued: true
  })
  .fillColor('red')
  .text(lorem.slice(50));
```

The first text call can retain options such as `width` for following continued text calls.

To remove a link in continued rich text, set `link: null`.

```js
doc.fillColor('red')
  .text('Normal text ', {
    width: 465,
    continued: true
  })
  .fillColor('blue')
  .text('linked text ', {
    link: 'http://www.example.com',
    continued: true
  })
  .fillColor('green')
  .text('plain text again', {
    link: null
  });
```

Implementation requirements:

* Use `continued` for inline emphasis, colored phrases, mixed font styles, and inline links.
* Reset styles after rich text segments to avoid unintended styling.
* Set `link: null` after linked text when the following text should not be linked.

## Fonts

PDFKit supports the 14 standard PDF fonts.

Standard font labels:

* `Courier`
* `Courier-Bold`
* `Courier-Oblique`
* `Courier-BoldOblique`
* `Helvetica`
* `Helvetica-Bold`
* `Helvetica-Oblique`
* `Helvetica-BoldOblique`
* `Symbol`
* `Times-Roman`
* `Times-Bold`
* `Times-Italic`
* `Times-BoldItalic`
* `ZapfDingbats`

Use `doc.font()` to switch fonts.

```js
doc.fontSize(18);

doc.font('Times-Roman')
  .text('Hello from Times Roman!');
```

PDFKit can embed custom fonts in these formats:

* `.ttf`
* `.otf`
* `.woff`
* `.woff2`
* `.ttc`
* `.dfont`

Use a font file path or buffer to apply a custom font.

```js
doc.font('fonts/GoodDog.ttf')
  .text('This text uses a custom TrueType font.');
```

For collection fonts such as `.ttc` or `.dfont`, pass the specific style name.

```js
doc.font('fonts/Chalkboard.ttc', 'Chalkboard-Bold')
  .text('This text uses a font from a collection.');
```

Register reusable fonts with `registerFont()`.

```js
doc.registerFont('Heading Font', 'fonts/Chalkboard.ttc', 'Chalkboard-Bold');

doc.font('Heading Font')
  .text('This is a heading.');
```

Implementation requirements:

* Do not rely on standard PDF fonts for Korean output.
* Register Korean fonts before rendering Korean text.
* Use separate registered font names for regular, bold, and other text styles.
* Use embeddable fonts for generated documents, especially PDF/A documents.
* Keep font registration in a shared font registry module.

Example Korean font setup:

```js
doc.registerFont('Korean-Regular', 'fonts/NotoSansKR-Regular.ttf');
doc.registerFont('Korean-Bold', 'fonts/NotoSansKR-Bold.ttf');

doc.font('Korean-Regular')
  .text('Korean PDF text example.');
```

## Exporter Requirements

The PDF exporter should support these text features:

* Basic paragraph rendering
* Fixed-position text rendering
* Automatic line wrapping
* Text alignment
* Font size control
* Font family control
* Line spacing
* Paragraph spacing
* Lists
* Rich text segments
* Inline links
* Text measurement
* Korean font rendering

The PDF exporter should validate these cases:

* Long paragraphs
* Multi-page text
* Korean text
* Mixed Korean and English text
* Long titles
* Bulleted lists
* Fixed-width text boxes
* Text with links
* Rich text with multiple styles
* Text near the bottom of a page

Text rendering logic should be implemented separately from content generation logic. The exporter should receive structured content data and convert it into PDFKit rendering calls.
