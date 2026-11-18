"""
PDF NEXUS - Utilities API
Endpoints for conversions (Word, Excel, PPT, Images), Compress, Merge, Split, Protect, Watermark, and Page Numbering.
"""

import uuid
import zipfile
from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, HTTPException, status, UploadFile, File
from fastapi.responses import FileResponse

from app.core.config import settings
from app.core.database import get_db
from app.schemas.pdf_schemas import (
    MergeRequest, SplitRequest, CompressRequest,
    ProtectRequest, UnlockRequest, WatermarkRequest, PageNumberRequest
)
from app.services.converter import (
    pdf_to_docx, docx_to_pdf, pdf_to_excel, excel_to_pdf,
    pdf_to_pptx, pdf_to_images, images_to_pdf,
    compress_pdf, merge_pdfs, split_pdf,
    protect_pdf, unlock_pdf, watermark_pdf, add_page_numbers
)

router = APIRouter(prefix="/pdf/utils", tags=["PDF Utilities"])

def get_file(doc_id: str) -> tuple[Path, str]:
    with get_db() as conn:
        row = conn.execute("SELECT stored_filename, filename FROM documents WHERE id = ? AND is_deleted = 0", (doc_id,)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Document not found.")
    p = settings.UPLOADS_PATH / row["stored_filename"]
    if not p.exists():
        raise HTTPException(status_code=404, detail="File missing.")
    return p, row["filename"]

@router.post("/compress")
def compress_document(req: CompressRequest):
    """Compresses PDF document and returns download link."""
    src, orig_name = get_file(req.document_id)
    out_name = f"compressed_{uuid.uuid4().hex[:6]}_{orig_name}"
    out_path = settings.EXPORTS_PATH / out_name
    
    res = compress_pdf(src, out_path, level=req.level)
    res["download_url"] = f"/api/pdf/utils/download/{out_name}"
    return res

@router.post("/merge")
def merge_documents(req: MergeRequest):
    """Merges multiple uploaded documents into one."""
    if len(req.document_ids) < 2:
        raise HTTPException(status_code=400, detail="At least 2 documents required to merge.")
        
    doc_paths = []
    for d_id in req.document_ids:
        p, _ = get_file(d_id)
        doc_paths.append(p)
        
    merged_name = f"merged_{uuid.uuid4().hex[:8]}.pdf"
    out_path = settings.EXPORTS_PATH / merged_name
    res = merge_pdfs(doc_paths, out_path)
    res["download_url"] = f"/api/pdf/utils/download/{merged_name}"
    return res

@router.post("/split")
def split_document(req: SplitRequest):
    """Splits PDF by page ranges and bundles into a zip archive."""
    src, orig_name = get_file(req.document_id)
    temp_dir = settings.EXPORTS_PATH / f"split_{uuid.uuid4().hex[:8]}"
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    parts = split_pdf(src, temp_dir, req.page_ranges)
    
    # Zip up split files
    zip_name = f"split_{Path(orig_name).stem}.zip"
    zip_path = settings.EXPORTS_PATH / zip_name
    with zipfile.ZipFile(zip_path, "w") as zf:
        for p in parts:
            zf.write(p, arcname=p.name)
            
    return {
        "success": True,
        "parts_count": len(parts),
        "download_url": f"/api/pdf/utils/download/{zip_name}"
    }

@router.post("/convert/pdf-to-docx/{document_id}")
def convert_to_word(document_id: str):
    """Converts PDF to Microsoft Word .docx document."""
    src, orig_name = get_file(document_id)
    stem = Path(orig_name).stem
    out_name = f"{stem}_{uuid.uuid4().hex[:6]}.docx"
    out_path = settings.EXPORTS_PATH / out_name
    
    try:
        pdf_to_docx(src, out_path)
        return {"success": True, "download_url": f"/api/pdf/utils/download/{out_name}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Word conversion failed: {str(e)}")

@router.post("/convert/pdf-to-excel/{document_id}")
def convert_to_excel(document_id: str):
    """Extracts tables from PDF into an Excel spreadsheet (.xlsx)."""
    src, orig_name = get_file(document_id)
    stem = Path(orig_name).stem
    out_name = f"{stem}_{uuid.uuid4().hex[:6]}.xlsx"
    out_path = settings.EXPORTS_PATH / out_name
    
    try:
        pdf_to_excel(src, out_path)
        return {"success": True, "download_url": f"/api/pdf/utils/download/{out_name}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Excel conversion failed: {str(e)}")

@router.post("/convert/pdf-to-pptx/{document_id}")
def convert_to_pptx(document_id: str):
    """Converts PDF pages into PowerPoint slides (.pptx)."""
    src, orig_name = get_file(document_id)
    stem = Path(orig_name).stem
    out_name = f"{stem}_{uuid.uuid4().hex[:6]}.pptx"
    out_path = settings.EXPORTS_PATH / out_name
    
    try:
        pdf_to_pptx(src, out_path)
        return {"success": True, "download_url": f"/api/pdf/utils/download/{out_name}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PowerPoint conversion failed: {str(e)}")

@router.post("/convert/pdf-to-images/{document_id}")
def convert_to_images(document_id: str):
    """Converts PDF pages into high-res PNG images bundled in a zip."""
    src, orig_name = get_file(document_id)
    temp_dir = settings.EXPORTS_PATH / f"imgs_{uuid.uuid4().hex[:8]}"
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    img_paths = pdf_to_images(src, temp_dir)
    zip_name = f"images_{Path(orig_name).stem}.zip"
    zip_path = settings.EXPORTS_PATH / zip_name
    with zipfile.ZipFile(zip_path, "w") as zf:
        for p in img_paths:
            zf.write(p, arcname=p.name)
            
    return {"success": True, "images_count": len(img_paths), "download_url": f"/api/pdf/utils/download/{zip_name}"}

@router.post("/protect")
def protect_document(req: ProtectRequest):
    """Encrypts document with password."""
    src, orig_name = get_file(req.document_id)
    out_name = f"protected_{uuid.uuid4().hex[:6]}_{orig_name}"
    out_path = settings.EXPORTS_PATH / out_name
    
    res = protect_pdf(src, out_path, req.password)
    res["download_url"] = f"/api/pdf/utils/download/{out_name}"
    return res

@router.post("/unlock")
def unlock_document(req: UnlockRequest):
    """Decrypts document."""
    src, orig_name = get_file(req.document_id)
    out_name = f"unlocked_{uuid.uuid4().hex[:6]}_{orig_name}"
    out_path = settings.EXPORTS_PATH / out_name
    
    try:
        res = unlock_pdf(src, out_path, req.password)
        res["download_url"] = f"/api/pdf/utils/download/{out_name}"
        return res
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/watermark")
def watermark_document(req: WatermarkRequest):
    """Stamps semi-transparent watermark across all pages."""
    src, orig_name = get_file(req.document_id)
    out_name = f"watermarked_{uuid.uuid4().hex[:6]}_{orig_name}"
    out_path = settings.EXPORTS_PATH / out_name
    
    res = watermark_pdf(src, out_path, req.text, req.font_size, req.opacity, req.rotation, req.color)
    res["download_url"] = f"/api/pdf/utils/download/{out_name}"
    return res

@router.post("/page-numbers")
def page_numbers_document(req: PageNumberRequest):
    """Adds styled page numbers across all pages."""
    src, orig_name = get_file(req.document_id)
    out_name = f"numbered_{uuid.uuid4().hex[:6]}_{orig_name}"
    out_path = settings.EXPORTS_PATH / out_name
    
    res = add_page_numbers(src, out_path, req.position, req.start_number, req.format_template)
    res["download_url"] = f"/api/pdf/utils/download/{out_name}"
    return res

@router.get("/download/{filename}")
def download_utility_export(filename: str):
    """Serves generated utility output."""
    file_path = settings.EXPORTS_PATH / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Exported file not found.")
    return FileResponse(path=str(file_path), filename=filename)
