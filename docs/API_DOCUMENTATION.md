# PDF NEXUS — REST API Documentation

Base URL: `http://127.0.0.1:8000/api`

Interactive Swagger Docs: `http://127.0.0.1:8000/docs`  
ReDoc: `http://127.0.0.1:8000/redoc`

---

## 1. Authentication Endpoints

### `POST /auth/register`
Creates a new user account.
```json
{
  "email": "user@example.com",
  "password": "StrongPassword123!",
  "full_name": "Jane Doe"
}
```

### `POST /auth/login`
Authenticates a user and returns a signed JWT token.
```json
{
  "email": "user@example.com",
  "password": "StrongPassword123!"
}
```

### `GET /auth/me`
Retrieves current session profile or indicates guest mode.

---

## 2. Document Endpoints

### `POST /documents/upload`
Uploads a document (`multipart/form-data`). Validates `%PDF-` signature and runs deep span-level text geometry inspection.

**Response:**
```json
{
  "success": true,
  "document_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "filename": "annual_report.pdf",
  "page_count": 5,
  "file_size": 248910,
  "metadata": { ... }
}
```

### `GET /documents/{document_id}`
Retrieves document metadata, page dimensions, text blocks, lines, spans, and embedded fonts.

### `GET /documents/{document_id}/file`
Streams the binary PDF file for rendering in PDF.js.

### `GET /documents/{document_id}/thumbnail/{page_num}`
Returns a PNG thumbnail of the requested page.

### `DELETE /documents/{document_id}`
Soft-deletes the document.

---

## 3. PDF Editing Endpoints

### `POST /pdf/edit-text`
Edits existing text in the document.
```json
{
  "document_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "page_number": 1,
  "mode": "direct",
  "target_bbox": [72.0, 130.0, 400.0, 150.0],
  "original_text": "Original text here",
  "new_text": "Replacement text here",
  "font_family": "Helvetica",
  "font_size": 12.0,
  "font_color": "#000000",
  "bold": false,
  "italic": false,
  "alignment": "left",
  "background_color": "#ffffff",
  "apply_redaction": true
}
```

### `POST /pdf/add-text`
Inserts a new text element.
```json
{
  "document_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "page_number": 1,
  "text": "Invoice #4829",
  "position": [100.0, 200.0],
  "font_family": "Helvetica",
  "font_size": 14.0,
  "font_color": "#000000",
  "bold": true,
  "italic": false
}
```

### `POST /pdf/pages`
Performs page operations: `rotate`, `delete`, `duplicate`, `insert_blank`, `crop`.
```json
{
  "document_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "operation": "rotate",
  "page_number": 1,
  "rotation_angle": 90
}
```

### `POST /pdf/annotations`
Adds highlights, shapes, drawings, and notes.

### `POST /pdf/signatures`
Applies a drawn or uploaded signature.

### `GET /pdf/export/{document_id}`
Serves a clean, garbage-collected, and deflated PDF download.

---

## 4. PDF Utilities Endpoints

- `POST /pdf/utils/convert/pdf-to-docx/{document_id}`
- `POST /pdf/utils/convert/pdf-to-excel/{document_id}`
- `POST /pdf/utils/convert/pdf-to-pptx/{document_id}`
- `POST /pdf/utils/convert/pdf-to-images/{document_id}`
- `POST /pdf/utils/compress` (low, medium, high)
- `POST /pdf/utils/protect` (AES-256)
- `POST /pdf/utils/unlock`
- `POST /pdf/utils/watermark`
- `POST /pdf/utils/page-numbers`

---

## 5. OCR & AI Endpoints

- `POST /pdf/ocr` (scanned page recognition, searchable PDF generation)
- `GET /pdf/ocr/detect-scanned/{document_id}`
- `POST /ai/summarize` (executive summaries)
- `POST /ai/ask` (document Q&A)
- `POST /ai/translate` (multilingual translation)
