# PDFKit Images

## Supported Image Inputs

Use `doc.image()` to add an image to a PDF document.

PDFKit accepts these image sources:

* Image file path
* Image buffer
* Base64 data URI

Supported image formats:

* JPEG
* PNG

```js
doc.image('images/example.jpeg');
```

Implementation requirements:

* Use file paths for local/static image assets.
* Use buffers when images are uploaded or generated dynamically.
* Use data URIs only when the image is already available as encoded data.
* Validate that the image format is JPEG or PNG before rendering.

## Basic Image Placement

If `x` and `y` coordinates are not provided, the image is rendered at the current position in the document flow.

```js
doc.image('images/example.jpeg');
```

Use explicit `x` and `y` coordinates for fixed-position image placement.

```js
doc.image('images/example.jpeg', 50, 100);
```

Implementation requirements:

* Use document flow placement for simple report images.
* Use explicit coordinates for logos, banners, thumbnails, card layouts, and fixed design templates.
* Keep image placement logic separate from content generation logic.

## Image Scaling Behavior

PDFKit scales images based on the options passed to `doc.image()`.

Scaling rules:

* If neither `width` nor `height` is provided, the image is rendered at full size.
* If only `width` is provided, the image is scaled proportionally to match the width.
* If only `height` is provided, the image is scaled proportionally to match the height.
* If both `width` and `height` are provided, the image is stretched to the exact dimensions.
* If `scale` is provided, the image is scaled proportionally by the given factor.
* If `fit` is provided, the image is scaled proportionally to fit inside the given area.
* If `cover` is provided, the image is scaled proportionally to completely cover the given area.

## Proportional Scaling by Width

Use `width` without `height` to preserve the original aspect ratio.

```js
doc.image('images/example.jpeg', 50, 100, {
  width: 300
});
```

Implementation requirements:

* Use this approach for report images, screenshots, and content images.
* Prefer proportional scaling over fixed width and height.
* Avoid distortion by not setting both `width` and `height` unless stretching is intentional.

## Proportional Scaling by Height

Use `height` without `width` to preserve the original aspect ratio.

```js
doc.image('images/example.jpeg', 50, 100, {
  height: 200
});
```

Implementation requirements:

* Use this when the image must fit a fixed vertical space.
* Ensure the resulting width does not exceed the page or layout box.

## Fixed-Size Stretching

When both `width` and `height` are provided, PDFKit stretches the image to those dimensions.

```js
doc.image('images/example.jpeg', 50, 100, {
  width: 200,
  height: 100
});
```

Implementation requirements:

* Avoid this for normal image rendering because it can distort the image.
* Use fixed-size stretching only for intentional design effects or when the source image ratio is already known.

## Scaling by Factor

Use `scale` to resize an image proportionally.

```js
doc.image('images/example.jpeg', 50, 100, {
  scale: 0.25
});
```

Implementation requirements:

* Use `scale` for simple proportional resizing.
* Prefer `width` or `fit` when the target layout area is fixed.

## Fit Image Inside a Box

Use `fit: [width, height]` to preserve aspect ratio while fitting the image inside a fixed box.

```js
doc.image('images/example.jpeg', 50, 100, {
  fit: [300, 200]
});
```

This preserves the image aspect ratio and ensures the image does not exceed the given area.

Implementation requirements:

* Use `fit` for thumbnails, uploaded images, card images, report figures, and preview images.
* Use `fit` when image distortion is not allowed.
* Use this as the default behavior for user-uploaded images.

## Fit Image with Center Alignment

When using `fit`, use `align` and `valign` to control image positioning inside the box.

```js
doc.image('images/example.jpeg', 50, 100, {
  fit: [300, 200],
  align: 'center',
  valign: 'center'
});
```

Supported horizontal alignment values:

* `left`
* `center`
* `right`

Supported vertical alignment values:

* `top`
* `center`
* `bottom`

Implementation requirements:

* Use `align: 'center'` and `valign: 'center'` for balanced image placement.
* Use this for card news layouts, cover images, and promotional templates.
* Draw layout boxes during development to verify positioning.

## Cover Image Area

Use `cover: [width, height]` when the image must completely fill a fixed area.

```js
doc.image('images/example.jpeg', 50, 100, {
  cover: [300, 200],
  align: 'center',
  valign: 'center'
});
```

Implementation requirements:

* Use `cover` for background images, hero images, banners, and card covers.
* Be aware that part of the image may be cropped.
* Use `fit` instead of `cover` when the full image must remain visible.

## Image Links

Use `link` to attach a URL to an image.

```js
doc.image('images/example.jpeg', 50, 100, {
  width: 300,
  link: 'https://example.com'
});
```

Implementation requirements:

* Use image links for logos, QR-related assets, campaign banners, and promotional materials.
* Validate URLs before adding them to generated PDFs.

## Image Anchors and Navigation

PDFKit supports navigation-related image options:

* `goTo`: Link image to an internal anchor.
* `destination`: Create an anchor at the image location.

Implementation requirements:

* Use `goTo` and `destination` only when the PDF requires internal navigation.
* Do not include internal navigation in simple report or card-style PDFs unless required.

## JPEG Orientation

PDFKit handles JPEG EXIF orientation by default.

Use `ignoreOrientation: true` to ignore JPEG EXIF orientation.

```js
const doc = new PDFDocument({
  ignoreOrientation: true
});
```

Or apply it to a specific image:

```js
doc.image('images/example.jpeg', 50, 100, {
  width: 300,
  ignoreOrientation: true
});
```

Implementation requirements:

* Keep default orientation handling unless there is a known image rotation issue.
* Test uploaded JPEG images from mobile devices.
* Use `ignoreOrientation: true` only when automatic EXIF orientation causes incorrect output.

## Development Debugging Example

Draw a rectangle around the target image area to verify placement.

```js
doc
  .rect(50, 100, 300, 200)
  .stroke();

doc.image('images/example.jpeg', 50, 100, {
  fit: [300, 200],
  align: 'center',
  valign: 'center'
});
```

Implementation requirements:

* Use bounding rectangles during layout debugging.
* Remove debug rectangles from production output.
* Use this method to verify image fitting, alignment, and cropping behavior.

## Recommended Image Rendering Defaults

For normal report images:

```js
doc.image('images/example.jpeg', 50, 100, {
  width: 450
});
```

For fixed image boxes where the full image must be visible:

```js
doc.image('images/example.jpeg', 50, 100, {
  fit: [450, 250],
  align: 'center',
  valign: 'center'
});
```

For banner or cover areas that must be fully filled:

```js
doc.image('images/example.jpeg', 50, 100, {
  cover: [450, 250],
  align: 'center',
  valign: 'center'
});
```

## Exporter Requirements

The PDF exporter should support these image features:

* Render image from file path
* Render image from buffer
* Render JPEG images
* Render PNG images
* Fixed-position image placement
* Flow-based image placement
* Proportional scaling by width
* Proportional scaling by height
* Fit image inside fixed box
* Cover fixed image area
* Horizontal alignment
* Vertical alignment
* Image links
* JPEG EXIF orientation handling

The PDF exporter should validate these cases:

* Large images
* Small images
* Wide images
* Tall images
* Transparent PNG images
* Mobile JPEG images with EXIF orientation
* Images inside fixed-size cards
* Images near the bottom of a page
* Images with links
* Missing or invalid image paths

Image rendering logic should preserve aspect ratio by default. Use stretching only when explicitly required by a template.
