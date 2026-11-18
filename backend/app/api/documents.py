"""
PDF NEXUS - Documents API
Uploads, deep page inspection, PDF streaming, thumbnails, and document deletion.
"""

import uuid
import shutil
from pathlib import Path
from typing import Optional, List
from fastapi import APIRouter, UploadFile, File, HTTPException, status, Depends, Response
from fastapi.responses import FileResponse

from app.core.config import settings
from app.core.database import get_db
from app.core.security import get_current_user_optional, safe_resolve_path
from app.services.text_inspector import inspect_document, render_page_thumbnail
from app.schemas.pdf_schemas import DocumentMetadata

router = APIRouter(prefix="/documents", tags=["Documents"])

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    user_payload: Optional[dict] = Depends(get_current_user_optional)
):
    """
    Validates uploaded file, stores securely, performs deep text/font inspection,
    and returns full document geometry and metadata.
    """
    filename = file.filename or "document.pdf"
    ext = Path(filename).suffix.lower()
    if ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format '{ext}'. Allowed: {list(settings.ALLOWED_EXTENSIONS)}"
        )
        
    doc_id = str(uuid.uuid4())
    stored_name = f"{doc_id}{ext}"
    dest_path = settings.UPLOADS_PATH / stored_name
    
    # Read and validate size & PDF magic bytes
    content = await file.read()
    if len(content) > settings.MAX_UPLOAD_SIZE_BYTES:
        raise HTTPException(status_code=413, detail="File exceeds maximum allowed size of 50MB.")
        
    if ext == ".pdf" and not content.startswith(b"%PDF-"):
        raise HTTPException(status_code=400, detail="Invalid PDF file: Missing %PDF- signature.")
        
    with open(dest_path, "wb") as f:
        f.write(content)
        
    # Inspect document if PDF
    page_count = 1
    inspection_result = None
    if ext == ".pdf":
        try:
            inspection_result = inspect_document(dest_path, doc_id, filename)
            page_count = inspection_result.page_count
        except Exception as e:
            # If inspection fails (e.g. password protected or damaged), note in DB
            page_count = 1
            
    user_id = user_payload.get("sub") if user_payload else None
    
    with get_db() as conn:
        conn.execute(
            """
            INSERT INTO documents (id, user_id, filename, stored_filename, file_size, page_count)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (doc_id, user_id, filename, stored_name, len(content), page_count)
        )
        # Create initial version
        conn.execute(
            """
            INSERT INTO document_versions (id, document_id, version_num, stored_filename, description)
            VALUES (?, ?, 1, ?, 'Original Upload')
            """,
            (str(uuid.uuid4()), doc_id, stored_name)
        )
        
    return {
        "success": True,
        "document_id": doc_id,
        "filename": filename,
        "page_count": page_count,
        "file_size": len(content),
        "metadata": inspection_result
    }

@router.get("")
def list_documents(user_payload: Optional[dict] = Depends(get_current_user_optional)):
    """Lists recent documents for the current user or guest session."""
    user_id = user_payload.get("sub") if user_payload else None
    with get_db() as conn:
        if user_id:
            rows = conn.execute(
                "SELECT id, filename, file_size, page_count, created_at, updated_at FROM documents WHERE user_id = ? AND is_deleted = 0 ORDER BY created_at DESC LIMIT 30",
                (user_id,)
            ).fetchall()
        else:
            # Guest: show recently uploaded documents
            rows = conn.execute(
                "SELECT id, filename, file_size, page_count, created_at, updated_at FROM documents WHERE is_deleted = 0 ORDER BY created_at DESC LIMIT 15"
            ).fetchall()
            
    return [{"id": r["id"], "filename": r["filename"], "file_size": r["file_size"], "page_count": r["page_count"], "created_at": r["created_at"]} for r in rows]

@router.get("/{document_id}")
def get_document(document_id: str):
    """Retrieves document metadata, page geometry, blocks, and fonts."""
    with get_db() as conn:
        row = conn.execute("SELECT * FROM documents WHERE id = ? AND is_deleted = 0", (document_id,)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Document not found.")
            
    file_path = settings.UPLOADS_PATH / row["stored_filename"]
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Document file missing on disk.")
        
    # Re-inspect to ensure fresh geometry
    try:
        inspection = inspect_document(file_path, document_id, row["filename"])
        return {
            "success": True,
            "document": dict(row),
            "inspection": inspection
        }
    except Exception as e:
        return {
            "success": True,
            "document": dict(row),
            "inspection": None,
            "error": str(e)
        }

@router.get("/{document_id}/file")
def get_document_file(document_id: str):
    """Streams the raw PDF file for in-browser rendering via PDF.js."""
    with get_db() as conn:
        row = conn.execute("SELECT stored_filename, filename FROM documents WHERE id = ? AND is_deleted = 0", (document_id,)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Document not found.")
            
    file_path = settings.UPLOADS_PATH / row["stored_filename"]
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Document file missing.")
        
    return FileResponse(
        path=str(file_path),
        media_type="application/pdf",
        filename=row["filename"]
    )

@router.get("/{document_id}/thumbnail/{page_num}")
def get_page_thumbnail(document_id: str, page_num: int):
    """Generates and returns a PNG thumbnail for the specified page."""
    with get_db() as conn:
        row = conn.execute("SELECT stored_filename FROM documents WHERE id = ? AND is_deleted = 0", (document_id,)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Document not found.")
            
    file_path = settings.UPLOADS_PATH / row["stored_filename"]
    try:
        png_bytes = render_page_thumbnail(file_path, page_num)
        return Response(content=png_bytes, media_type="image/png")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate thumbnail: {str(e)}")

@router.delete("/{document_id}")
def delete_document(document_id: str):
    """Marks document as deleted."""
    with get_db() as conn:
        conn.execute("UPDATE documents SET is_deleted = 1 WHERE id = ?", (document_id,))
    return {"success": True, "message": "Document deleted."}
