# PDF NEXUS 📄⚡

> **Professional Online PDF Editor & Document Management Platform**  
> *Precision Vector PDF Text Editing, OCR Intelligence, True Redaction & Document Conversions.*

---

## 🚀 Overview

**PDF NEXUS** is a modern, high-performance online PDF editor and document processing platform engineered to bridge the gap between simple web annotators and full-featured desktop software like Adobe Acrobat.

Unlike basic web tools that merely paint text layers over an existing PDF, **PDF NEXUS** provides **genuine existing PDF text editing**, font matching, true redaction, multi-page manipulation, scanned document OCR, and full document format conversions.

---

## ✨ Core Features

### 1. Advanced Existing PDF Text Editing (The Core Engine)
- **Mode A: Direct Edit Mode**: Rewrites text objects inside the underlying PDF vector stream, preserving native operators, baseline coordinates, and font geometry.
- **Mode B: True Redaction & Overlay Mode**: Physically and permanently excises original vector text and glyphs from the PDF content stream (no ghost or searchable text remains), automatically samples the local background color, and places typography-matched replacement text at exact baseline coordinates.
- **Font Matching & Inspection**:
  - Automatically identifies embedded and subset fonts (`ABCDEF+Calibri`, `Helvetica`, `TimesNewRoman`, etc.).
  - Extracts font style flags (Bold, Italic, Monospace, Serif).
  - Matches fonts to standard PDF vector typography (`helv`, `tiro`, `cour`) with fallback warning detection.
- **Interactive Text Selection Experience**:
  - Click or drag-select any existing text span on the page.
  - Hover highlights bounding boxes and displays font metrics.
  - Double-click to trigger in-place inline editing directly on the canvas.
  - Adjust font family, font size, color, bold, italic, and alignment.

### 2. Comprehensive PDF Toolkit
- **Document Conversions**:
  - PDF to Word (`.docx`)
  - Word (`.docx`) to PDF
  - PDF to Excel (`.xlsx`) table extraction
  - Excel (`.xlsx`) to PDF
  - PDF to PowerPoint (`.pptx`) slides
  - PDF to High-Resolution PNG Images (zipped)
  - Image files to PDF
- **Page Management**:
  - Rotate individual pages (90°, 180°, 270°)
  - Duplicate pages
  - Reorder pages
  - Insert custom blank pages
  - Crop pages to custom bounding rectangles
  - Delete pages
- **Annotations & Markup**:
  - Vector Highlights, Underlines, and Strikethroughs
  - Freehand pencil/ink markup with live SVG preview
  - Geometric shapes: Rectangles, Circles, and Lines
  - Sticky notes and comments
- **Signatures**:
  - Interactive HTML5 canvas signature pad
  - Smooth vector stroke smoothing
  - Distinguishes visual image stamps from **Cryptographic Digital Audit Stamps**
- **PDF Security & Utilities**:
  - **AES-256 PDF Encryption & Password Protection**
  - Instant password decryption & unlocking
  - High-ratio document compression (deflation, image downsampling, garbage collection)
  - Customizable watermarks (arbitrary angles, opacity, font size)
  - Dynamic page numbering ("Page X of Y")

### 3. OCR Engine (English & Hindi)
- Automatically detects scanned and image-only pages.
- Leverages OCR text recognition with multi-language support (English and Hindi).
- Generates **100% Searchable PDFs** using PDF text render mode 3 (invisible selectable text layer), preserving original scan images pixel-perfect while making text selectable and searchable.

### 4. Optional AI Document Assistant
- Document summarization (executive summary, bullet points, key figures).
- Conversational Q&A on PDF contents.
- Language translation.
- Fully resilient: works with Google Gemini AI (`GEMINI_API_KEY`), OpenAI (`OPENAI_API_KEY`), or uses built-in extractive algorithms when no API key is provided.

---

## 🛠️ Technology Stack

| Layer | Technology |
|---|---|
| **Frontend** | React 19, TypeScript, Vite, Tailwind CSS, Lucide Icons, PDF.js |
| **Backend** | Python 3.12+, FastAPI, Uvicorn, Pydantic v2 |
| **PDF Processing** | PyMuPDF (Fitz), pdfplumber, pdfminer.six, Pillow, FontTools, reportlab |
| **Conversions** | pdf2docx, python-docx, python-pptx, openpyxl |
| **Database** | SQLite with WAL mode & foreign keys (Production ready for PostgreSQL) |
| **Testing** | Pytest, Synthetic PDF generators, Automated CI/CD |
| **DevOps** | Docker, Docker Compose, Nginx, GitHub Actions |

---

## ⚡ Quick Start (Local Development)

### Prerequisites
- Python 3.11+
- Node.js 18+ & npm
- Git

### 1. Clone the Repository
```bash
git clone https://github.com/TH3-S4URAV/PDF-NEXUS.git
cd PDF-NEXUS
```

### 2. Run Backend
```bash
cd backend
python -m pip install -r requirements.txt
python run.py
```
*Backend runs on `http://127.0.0.1:8000` (API Docs: `http://127.0.0.1:8000/docs`).*

### 3. Run Frontend
```bash
cd frontend
npm install
npm run dev
```
*Frontend runs on `http://localhost:5173`.*

---

## 🐳 Docker Deployment

Run the entire full-stack application with a single command:
```bash
docker-compose up --build
```
- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:8000/api`
- API Docs: `http://localhost:8000/docs`

---

## 🧪 Testing

PDF NEXUS includes automated test suites covering geometry extraction, text editing modes, page operations, and utilities:
```bash
cd backend
python tests/test_services.py
```

---

## 📖 Documentation

- [Architecture & Design Principles](docs/ARCHITECTURE.md)
- [REST API Documentation](docs/API_DOCUMENTATION.md)
- [Installation Guide](docs/INSTALLATION.md)
- [Production Deployment](docs/DEPLOYMENT.md)
- [Security & Privacy](docs/SECURITY.md)
- [Testing Suite](docs/TESTING.md)
- [Changelog](docs/CHANGELOG.md)

---

## 📄 License
MIT License. Built for modern document management.
