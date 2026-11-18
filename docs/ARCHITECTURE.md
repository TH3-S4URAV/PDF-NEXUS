# PDF NEXUS — System Architecture & Design

## 1. Architectural Philosophy
PDF NEXUS is engineered with clear separation of concerns, high throughput, and strict respect for document geometry and typography.

```
+-------------------------------------------------------------+
|                      Client Browser                         |
|  React 19 + TypeScript + Tailwind CSS + PDF.js + Canvas     |
+------------------------------+------------------------------+
                               | REST API (JSON / Blobs)
                               v
+-------------------------------------------------------------+
|                     FastAPI Gateway                         |
|   - CORS Validation       - Request Schemas (Pydantic v2)   |
|   - Authentication (JWT)  - Safe Path Resolution            |
+------------------------------+------------------------------+
                               |
         +---------------------+---------------------+
         |                                           |
         v                                           v
+-----------------------------+             +-----------------------------+
|   PDF Processing Engine     |             |       Persistence Layer     |
| - Text & Span Inspector     |             | - SQLite (WAL mode)         |
| - Mode A: Direct Edit       |             | - Document Versions History |
| - Mode B: Overlay Redaction |             | - Local/Cloud Object Store  |
| - Font Matching & Fallbacks |             +-----------------------------+
| - Page & Image Managers     |
| - Document Converter        |
| - Searchable OCR Engine     |
+-----------------------------+
```

## 2. Coordinate Spaces & Geometric Precision
PDF documents define page dimensions in **Points (72 points per inch)**, with the origin `(0, 0)` traditionally at the bottom-left or top-left depending on transformation matrices.

1. **Backend Normalization**:
   - PyMuPDF normalizes all rects to top-left origin `[x0, y0, x1, y1]`.
   - Every text span extracted provides both its bounding box and exact baseline `origin` `(x, y)`.
2. **Frontend Viewport Scaling**:
   - The interactive canvas renders PDF pages at a variable user zoom level ($Z$).
   - The scaling ratio is calculated dynamically:
     $$\text{Scale} = \frac{\text{Rendered Canvas Width}}{\text{Page Width (points)}}$$
   - Every bounding box is projected into screen coordinates:
     $$\text{left} = x_0 \times \text{Scale}, \quad \text{top} = y_0 \times \text{Scale}$$
     $$\text{width} = (x_1 - x_0) \times \text{Scale}, \quad \text{height} = (y_1 - y_0) \times \text{Scale}$$

## 3. The Two Text Editing Modes

### Mode A: Direct PDF Stream Edit
- Locates target text strings in the page stream.
- Re-encodes the replacement text using the matched font or replaces the stream contents.
- Preserves native vector PDF operators (`BT`, `Tf`, `Tm`, `Tj`, `ET`).
- Where embedded subset fonts lack glyphs, falls back to surgical vector redaction with standard vector typography injection.

### Mode B: True Redaction & Typography Overlay
- Uses PyMuPDF's C-level `add_redact_annot` and `apply_redactions`.
- **True Redaction**: Excises the underlying vector glyphs permanently from the PDF file, leaving zero hidden or ghost text.
- Samples the surrounding background color for seamless visual continuity.
- Re-inserts the newly styled text with exact font family, size, weight, color, and alignment (`align_code`: 0 = Left, 1 = Center, 2 = Right, 3 = Justified).

## 4. Searchable OCR Engine
Scanned documents (image-only pages with `< 40` characters of text) are recognized by the OCR engine.
Rather than destroying or altering the original scan image:
- The original scanned bitmap is preserved at full resolution.
- An invisible text layer is rendered over the exact coordinates using PDF Text Render Mode 3 (`render_mode=3`: "Neither fill nor stroke text").
- Result: The user sees the original document, but can now select, highlight, search, and copy text effortlessly.
