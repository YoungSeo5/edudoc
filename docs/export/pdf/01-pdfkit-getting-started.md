# PDFKit Getting Started

## Installation

Install PDFKit through npm.

```bash
npm install pdfkit
```

## Basic Document Creation

Create a `PDFDocument` instance before adding content.

```js
const PDFDocument = require('pdfkit');
const doc = new PDFDocument();
```

## Writing and Finalizing a PDF

PDFKit writes PDF output through streams. The document must be piped to a destination before calling `doc.end()`.

```js
const fs = require('fs');
const PDFDocument = require('pdfkit');

const doc = new PDFDocument();

doc.pipe(fs.createWriteStream('/path/to/file.pdf'));

doc.text('PDF content goes here.');

doc.end();
```

To send the generated PDF through an HTTP response:

```js
const PDFDocument = require('pdfkit');

const doc = new PDFDocument();

doc.pipe(res);

doc.text('PDF content goes here.');

doc.end();
```

Implementation requirement:

* Always call `doc.end()` after all content has been added.
* Use file streams when saving PDFs to disk.
* Use the HTTP response stream when returning PDFs from an API endpoint.
* Add all document content before finalizing the PDF.

## Browser Usage

PDFKit can also be used in the browser with `blob-stream`.

```js
const PDFDocument = require('pdfkit');
const blobStream = require('blob-stream');

const doc = new PDFDocument();
const stream = doc.pipe(blobStream());

doc.text('PDF content goes here.');

doc.end();

stream.on('finish', function () {
  const blob = stream.toBlob('application/pdf');
  const url = stream.toBlobURL('application/pdf');

  iframe.src = url;
});
```

Implementation requirement:

* Use `blobStream()` when generating PDFs directly in the browser.
* Use `toBlob()` when the PDF file object is needed.
* Use `toBlobURL()` when the PDF needs to be previewed in an iframe or browser viewer.

## Adding Pages

Use `doc.addPage()` to create a new page.

```js
doc.addPage();
```

A handler can be registered for every newly added page.

```js
doc.on('pageAdded', () => {
  doc.text('Page Title');
});
```

Implementation requirement:

* Use `addPage()` when content must continue on a new page.
* Use the `pageAdded` event for repeated page-level elements such as page titles, headers, or layout markers.
* Do not rely only on manual page creation for long text; test automatic page breaks separately.

## Switching to Previous Pages

Enable `bufferPages` when the exporter needs to modify previously created pages.

```js
const PDFDocument = require('pdfkit');

let i;
let end;

const doc = new PDFDocument({
  bufferPages: true
});

doc.addPage();
doc.addPage();

const range = doc.bufferedPageRange();

for (i = range.start, end = range.start + range.count; i < end; i++) {
  doc.switchToPage(i);
  doc.text(`Page ${i + 1} of ${range.count}`);
}

doc.flushPages();

doc.end();
```

Implementation requirement:

* Use `bufferPages: true` when adding page numbers after all pages are created.
* Use `bufferedPageRange()` to get the available page range.
* Use `switchToPage(index)` to write to a previous page.
* Use `flushPages()` when buffered pages should be written manually.
* `doc.end()` automatically flushes buffered pages if they were not manually flushed.

## Default Font

PDFKit uses `Helvetica` as the default font.

A different default font can be passed when creating the document.

```js
const doc = new PDFDocument({
  font: 'Courier'
});
```

Implementation requirement:

* Do not rely on the default font for Korean text.
* Register and use an embeddable Korean font for Korean PDF output.
* Use `registerFont()` for custom fonts such as TTF or OTF fonts.

Example:

```js
doc.registerFont('Korean', 'fonts/NotoSansKR-Regular.ttf');
doc.font('Korean');
```

## Document Metadata

PDF metadata can be added through document information properties. According to the PDF specification, each metadata property should start with an uppercase letter.

Supported metadata fields:

* `Title`: Document title
* `Author`: Document author
* `Subject`: Document subject
* `Keywords`: Keywords related to the document
* `CreationDate`: Document creation date, automatically added by PDFKit
* `ModDate`: Last modified date

Example:

```js
const doc = new PDFDocument();

doc.info.Title = 'AI Content Generation Report';
doc.info.Author = 'Content Exporter';
doc.info.Subject = 'Generated PDF Document';
doc.info.Keywords = 'PDF, PDFKit, content generation, exporter';
```

Implementation requirement:

* Set metadata for generated reports, proposals, and official documents.
* Use meaningful `Title`, `Author`, `Subject`, and `Keywords` values when available.
* Preserve metadata generation in the PDF exporter layer.

## Encryption and Access Privileges

PDFKit supports password protection and permission control.

Main options:

* `userPassword`: Password required to open the PDF
* `ownerPassword`: Password used by the document owner
* `permissions`: Object defining PDF access permissions

Permission fields:

* `printing`: Controls whether printing is allowed. Use `"lowResolution"` or `"highResolution"`.
* `modifying`: Controls whether document modification is allowed.
* `copying`: Controls whether text or graphics copying is allowed.
* `annotating`: Controls whether annotations and form filling are allowed.
* `fillingForms`: Controls whether form filling and signing are allowed.
* `contentAccessibility`: Controls whether copying text for accessibility is allowed.
* `documentAssembly`: Controls whether document assembly is allowed.

Implementation requirement:

* Treat encryption as an optional export setting.
* Do not enable encryption by default unless required by the user or document policy.
* Do not use encryption for PDF/A output because PDF/A documents cannot be encrypted.

## PDF/A

PDF/A is an ISO standard for long-term archival electronic documents.

PDF/A restrictions include:

* The document cannot be encrypted.
* Fonts must be embedded.
* JavaScript is not allowed.
* Audio content is not allowed.
* Video content is not allowed.
* XMP metadata must be included.
* Color spaces must be defined.

PDFKit aims to support the following PDF/A standards:

* `PDF/A-1b`
* `PDF/A-2b`
* `PDF/A-3b`
* `PDF/A-1a`
* `PDF/A-2a`
* `PDF/A-3a`

Use a PDF/A subset when creating the `PDFDocument`.

```js
const doc = new PDFDocument({
  subset: 'PDF/A-1b'
});
```

For PDF/A-1:

* Set `pdfVersion` to at least `1.4`.
* Set `tagged: true` for PDF/A-1a.

For PDF/A-2 and PDF/A-3:

* Set `pdfVersion` to at least `1.7`.
* Set `tagged: true` for level A conformance.

Example:

```js
const doc = new PDFDocument({
  subset: 'PDF/A-2b',
  pdfVersion: '1.7'
});
```

For accessible PDF/A output:

```js
const doc = new PDFDocument({
  subset: 'PDF/A-2a',
  pdfVersion: '1.7',
  tagged: true
});
```

Implementation requirement:

* Use PDF/A only when long-term archiving or official document preservation is required.
* Do not enable encryption for PDF/A documents.
* Always embed fonts for PDF/A documents.
* Do not use PDFKit standard fonts for PDF/A because they are AFM metric fonts and do not include embeddable font data.
* Use `registerFont()` with embeddable fonts such as TTF or OTF.
* Validate generated PDF/A files with a validator such as veraPDF.

## Adding Content

After creating a `PDFDocument` instance, content can be added using PDFKit APIs.

Common content types needed for the exporter:

* Text
* Images
* Tables
* Vector graphics
* Links and annotations
* Page headers
* Page footers
* Page numbers
* Metadata

Implementation requirement:

* Keep PDF creation logic inside a dedicated PDF exporter module.
* Convert structured input data into PDFKit rendering calls.
* Do not mix content generation logic with PDF rendering logic.
* Use a consistent layout system for margins, typography, spacing, and page breaks.
* Test Korean text, long paragraphs, tables, images, and multi-page documents.