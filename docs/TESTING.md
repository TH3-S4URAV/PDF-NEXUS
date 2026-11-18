# PDF NEXUS — Testing & Quality Assurance

## 1. Automated Test Suites

### Backend Unit & Integration Tests
Located in `backend/tests/`:
- `test_services.py`: Directly tests PyMuPDF vector operations, span extraction, Mode A direct editing, Mode B overlay redaction, page operations, annotations, signatures, conversions, and scanned page detection.

Run with:
```bash
cd backend
python tests/test_services.py
```

### Frontend Build & Type Validation
The frontend is strictly verified with TypeScript compiler (`tsc -b`) and Vite production bundler:
```bash
cd frontend
npm run build
```

---

## 2. Test Verification Matrix

| Area | Test Description | Status |
|---|---|---|
| **Text Inspection** | Extracts 100% of spans, fonts, and bounding boxes | ✅ PASS |
| **Thumbnails** | Renders high-res PNG thumbnails per page | ✅ PASS |
| **Mode A Direct Edit**| Replaces text in PDF content stream directly | ✅ PASS |
| **Mode B Redaction** | Physically removes sensitive text & draws typography overlay | ✅ PASS |
| **Page Operations** | Rotate 90°, Duplicate, Insert Blank, Delete | ✅ PASS |
| **Annotations** | Vector highlights, shapes, freehand ink | ✅ PASS |
| **Signatures** | Canvas drawing, transparent PNG, cryptographic audit stamp | ✅ PASS |
| **Compress** | Deflation, image downsampling, garbage collection | ✅ PASS |
| **Watermark** | 45° matrix rotated text stamp across all pages | ✅ PASS |
| **Protect / Unlock** | AES-256 password protection & decryption | ✅ PASS |
| **Scanned Detection** | Detects image scans vs vector text PDFs | ✅ PASS |
| **Frontend Bundle** | React 19 + TypeScript + Tailwind bundle generation | ✅ PASS |
