# PDF NEXUS — Installation & Setup Guide

This guide covers running PDF NEXUS on Windows, Linux, or macOS.

## 1. System Requirements
- **Python**: 3.11 or higher
- **Node.js**: 18.0 or higher
- **RAM**: 4GB minimum (8GB recommended for large multi-page PDF processing)
- **Tesseract OCR**: Optional (integrated inside PyMuPDF, or system package for additional language dictionaries)

---

## 2. Step-by-Step Setup

### Step 1: Clone Repository
```bash
git clone https://github.com/TH3-S4URAV/PDF-NEXUS.git
cd PDF-NEXUS
```

### Step 2: Backend Setup
Open a terminal in the project root:
```bash
cd backend
python -m venv venv

# On Windows (PowerShell):
venv\Scripts\Activate.ps1

# On Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
python run.py
```
Backend will be listening on `http://127.0.0.1:8000`.

### Step 3: Frontend Setup
Open a second terminal in the project root:
```bash
cd frontend
npm install
npm run dev
```
Frontend will be accessible on `http://localhost:5173`.

---

## 3. Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

| Variable | Description | Default |
|---|---|---|
| `PORT` | Backend listening port | `8000` |
| `SECRET_KEY` | JWT encryption secret | Auto-generated in dev |
| `DATABASE_URL` | SQLite / PostgreSQL URL | `sqlite:///./pdf_nexus.db` |
| `GEMINI_API_KEY` | Optional Google Gemini Key | `""` |
