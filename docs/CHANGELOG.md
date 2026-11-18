# Changelog — PDF NEXUS

All notable changes to the PDF NEXUS platform will be documented in this file.

## [1.0.0] - 2026-11-18
### Added
- **Core Text Editing Engine**:
  - Implemented Mode A (Direct PDF stream rewrite).
  - Implemented Mode B (True redaction with font-matched overlay).
  - Font matching & identification engine with fallback warnings.
  - Interactive canvas bounding box text selection and in-line editing.
- **Page Management**:
  - Rotate, delete, duplicate, insert blank, crop, reorder pages.
- **Annotations & Signatures**:
  - Vector highlights, shapes (rect, circle, line), freehand pencil ink.
  - Signature drawing canvas with transparent alpha and cryptographic stamping.
- **PDF Utilities**:
  - PDF to Word (.docx), Excel (.xlsx), PowerPoint (.pptx), PNG images.
  - Document compression, AES-256 password protection & unlock.
  - Watermarking and dynamic page numbering.
- **OCR Engine**:
  - Scanned page detector.
  - Optical character recognition with English and Hindi support.
  - Searchable PDF generation with PDF render mode 3 invisible text layer.
- **AI Document Assistant**:
  - Summarize document, Q&A on PDF, and text translation.
- **UI/UX**:
  - Complete 3-panel professional layout with dark/light mode.
  - High-DPI canvas rendering with PDF.js.
  - Dashboard with drag-and-drop and recent documents history.
- **DevOps & QA**:
  - Comprehensive automated test suite (`tests/test_services.py`).
  - Docker Compose and Nginx multi-stage build.
  - GitHub Actions CI/CD pipeline.
