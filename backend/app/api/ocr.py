"""
PDF NEXUS - OCR API
Endpoints for scanned page detection, text recognition, and Searchable PDF generation.
"""

import uuid
from pathlib import Path
from fastapi import APIRouter, HTTPException
from app.core.config import settings
from app.core.database import get_db
from app.schemas.pdf_schemas import OCRRequest
from app.services.ocr_service import detect_scanned_pages, perform_ocr

router = APIRouter(prefix="/pdf/ocr", tags=["OCR Engine"])

@router.post("")
def run_ocr_on_document(req: OCRRequest):
    """
    Executes OCR on document. Identifies text, supports English and Hindi,
    and produces a searchable PDF.
    """
    with get_db() as conn:
        row = conn.execute("SELECT stored_filename, filename FROM documents WHERE id = ? AND is_deleted = 0", (req.document_id,)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Document not found.")
            
    src = settings.UPLOADS_PATH / row["stored_filename"]
    out_name = f"ocr_searchable_{uuid.uuid4().hex[:6]}_{row['filename']}"
    out_path = settings.EXPORTS_PATH / out_name
    
    try:
        res = perform_ocr(
            doc_path=src,
            output_path=out_path,
            languages=req.languages,
            make_searchable=req.make_searchable
        )
        if req.make_searchable and out_path.exists():
            res["download_url"] = f"/api/pdf/utils/download/{out_name}"
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OCR processing failed: {str(e)}")

@router.get("/detect-scanned/{document_id}")
def check_if_scanned(document_id: str):
    """Quickly scans document pages to determine if any page is an image scan."""
    with get_db() as conn:
        row = conn.execute("SELECT stored_filename FROM documents WHERE id = ? AND is_deleted = 0", (document_id,)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Document not found.")
            
    src = settings.UPLOADS_PATH / row["stored_filename"]
    results = detect_scanned_pages(src)
    is_any_scanned = any(r["is_scanned"] for r in results)
    return {
        "success": True,
        "is_scanned_document": is_any_scanned,
        "page_details": results
    }
