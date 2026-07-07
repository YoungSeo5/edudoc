# PDFKit Fonts Korean

## Purpose

This document defines how the PDF exporter should handle fonts, custom font embedding, and Korean text rendering when using PDFKit.

The PDF exporter must not rely on PDFKit standard fonts for Korean output. Korean text should be rendered with registered embeddable font files such as TTF or OTF.

## Standard PDF Fonts

PDFKit supports standard PDF fonts out of the box.

Standard font labels include:

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

Implementation requirements:

* Do not use standard PDF fonts for Korean text.
* Use standard fonts only for simple English-only test output.
* Use registered custom fonts for all production PDF output that may contain Korean text.

## Custom Font Embedding

PDFKit supports embedding custom fonts directly into PDF documents.

Supported custom font formats:

* `.ttf`
* `.otf`
* `.woff`
* `.woff2`
* `.ttc`
* `.dfont`

Implementation requirements:

* Use embeddable fonts for Korean PDF output.
* Prefer `.ttf` or `.otf` font files for predictable behavior.
* Store font registration logic in a shared font registry module.
* Do not hardcode font file paths in individual rendering functions.
* Verify font license compatibility before bundling fonts with the application.

## Applying a Font

Use `doc.font()` to select the font used for text rendering.

For a standard PDF font:

```js
doc.font('Times-Roman')
  .text('Hello from Times Roman!');
```

For a custom TrueType font:

```js
doc.font('fonts/Example-Regular.ttf')
  .text('This text uses a custom TrueType font.');
```

For a collection font such as `.ttc` or `.dfont`, pass the specific style name.

```js
doc.font('fonts/Example.ttc', 'Example-Bold')
  .text('This text uses a font from a collection.');
```

Implementation requirements:

* Use `doc.font()` before calling `doc.text()`.
* Apply the intended font before rendering each text style.
* Do not assume that a previously selected font is still active across independent rendering functions.
* Use explicit font names for headings, body text, captions, and table text.

## Registering Reusable Fonts

Use `doc.registerFont()` to register a font file under a reusable name.

```js
doc.registerFont('Heading Font', 'fonts/Example-Bold.ttf');

doc.font('Heading Font')
  .text('This is a heading.');
```

Implementation requirements:

* Register fonts once during PDF document setup.
* Use semantic font aliases such as `Korean-Regular`, `Korean-Bold`, and `Korean-Light`.
* Use registered font aliases instead of repeating font file paths.
* Keep font aliases consistent across all PDF templates.

## Korean Font Registration

The exporter should register separate Korean font aliases for regular and bold text.

```js
doc.registerFont('Korean-Regular', 'fonts/NotoSansKR-Regular.ttf');
doc.registerFont('Korean-Bold', 'fonts/NotoSansKR-Bold.ttf');
```

Use the registered font before rendering Korean text.

```js
doc.font('Korean-Regular')
  .fontSize(11)
  .text('한글 PDF 렌더링 테스트입니다.');

doc.font('Korean-Bold')
  .fontSize(16)
  .text('한글 제목 테스트');
```

Implementation requirements:

* Register Korean fonts before rendering any Korean text.
* Use `Korean-Regular` for body text.
* Use `Korean-Bold` for headings and emphasized text.
* Do not render Korean text before font registration is complete.
* Ensure mixed Korean and English text uses the Korean font when both languages appear in the same text block.

## Recommended Font Registry Pattern

Create a shared font registration function for the PDF exporter.

```js
function registerPdfFonts(doc) {
  doc.registerFont('Korean-Regular', 'fonts/NotoSansKR-Regular.ttf');
  doc.registerFont('Korean-Bold', 'fonts/NotoSansKR-Bold.ttf');
}

module.exports = {
  registerPdfFonts
};
```

Use the font registry during PDF document creation.

```js
const PDFDocument = require('pdfkit');
const { registerPdfFonts } = require('./font-registry');

const doc = new PDFDocument({
  size: 'A4'
});

registerPdfFonts(doc);

doc.font('Korean-Regular')
  .fontSize(11)
  .text('한글 PDF 렌더링 테스트입니다.');
```

Implementation requirements:

* Keep font registration separate from text rendering.
* Call the font registry before rendering document content.
* Reuse the same font registry across reports, proposals, official documents, and card-style PDFs.

## Korean Font Rendering Test

Create a test PDF that verifies Korean text rendering.

```js
const fs = require('fs');
const PDFDocument = require('pdfkit');

const doc = new PDFDocument({
  size: 'A4',
  margins: {
    top: 56,
    right: 50,
    bottom: 56,
    left: 50
  }
});

doc.pipe(fs.createWriteStream('output/korean-font-test.pdf'));

doc.registerFont('Korean-Regular', 'fonts/NotoSansKR-Regular.ttf');
doc.registerFont('Korean-Bold', 'fonts/NotoSansKR-Bold.ttf');

doc.font('Korean-Bold')
  .fontSize(18)
  .text('한글 폰트 렌더링 테스트', {
    align: 'center'
  });

doc.moveDown();

doc.font('Korean-Regular')
  .fontSize(11)
  .text('한글 PDF 렌더링 테스트입니다. 가나다라마바사아자차카타파하.', {
    width: 495,
    align: 'left',
    lineGap: 4
  });

doc.moveDown();

doc.text('English and Korean mixed text rendering test: AI 기반 콘텐츠 생성 시스템.', {
  width: 495,
  align: 'left',
  lineGap: 4
});

doc.moveDown();

doc.font('Korean-Bold')
  .fontSize(13)
  .text('Bold Korean text test');

doc.font('Korean-Regular')
  .fontSize(11)
  .text('Regular Korean text test');

doc.end();
```

Implementation requirements:

* Generate a real PDF file with Korean text.
* Verify that Korean characters are visible.
* Verify that Korean characters are not replaced with blank boxes or missing glyphs.
* Verify that mixed Korean and English text renders correctly.
* Verify that regular and bold font styles are visually different.
* Verify that long Korean text wraps correctly within the page content area.

## PDF/A Font Requirement

PDF/A documents require fonts to be embedded.

Implementation requirements:

* Use embedded custom fonts for PDF/A output.
* Do not use PDFKit standard fonts for PDF/A output.
* Do not enable encryption for PDF/A output.
* Validate generated PDF/A files separately when archival compliance is required.

## Exporter Requirements

The PDF exporter should support these font features:

* Custom font registration
* Korean regular font
* Korean bold font
* Font alias usage
* Font switching by text role
* Font file path configuration
* Mixed Korean and English rendering
* Korean text wrapping
* PDF/A-compatible embedded fonts

The PDF exporter should validate these cases:

* Korean title text
* Korean body text
* Korean bold text
* Mixed Korean and English text
* Long Korean paragraphs
* Korean text inside fixed-width text boxes
* Korean text inside tables
* Korean text near the bottom of a page
* Missing font file path
* Invalid font file path
* PDF output with embedded fonts

Font rendering logic should be centralized. Rendering modules should request fonts by semantic aliases instead of using raw font file paths directly.
