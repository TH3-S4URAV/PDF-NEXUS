"""
PDF NEXUS - PDF Editing API
Endpoints for Direct Edit, Overlay Redaction, Text Addition, Images, Annotations, Signatures, and Export.
"""

import uuid
import shutil
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import FileResponse

from app.core.config import settings
from app.core.database import get_db
from app.schemas.pdf_schemas import (
    EditTextRequest, AddTextRequest, ImageOperationRequest,
    AnnotationRequest, SignatureRequest, PageManagementRequest
)
from app.services.direct_text_editor import direct_edit_text
from app.services.overlay_editor import overlay_edit_text
from app.services.image_manager import add_image_to_page, replace_existing_image, delete_image_from_page, decode_base64_image
from app.services.page_manager import rotate_page, delete_page, duplicate_page, reorder_pages, insert_blank_page, crop_page
from app.services.annotations_manager import add_annotation_to_page, apply_signature
from app.services.text_inspector import inspect_document
import pymupdf

router = APIRouter(prefix="/pdf", tags=["PDF Editing"])

def get_doc_file_path(document_id: str) -> tuple[Path, str]:
    with get_db() as conn:
        row = conn.execute("SELECT stored_filename, filename FROM documents WHERE id = ? AND is_deleted = 0", (document_id,)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Document not found.")
    file_path = settings.UPLOADS_PATH / row["stored_filename"]
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Document file missing.")
    return file_path, row["filename"]

def create_new_version(document_id: str, current_file: Path, description: str) -> Path:
    """Creates a new version file to preserve history and support undo."""
    version_id = str(uuid.uuid4())
    new_filename = f"{document_id}_v_{version_id[:8]}.pdf"
    new_path = settings.UPLOADS_PATH / new_filename
    
    with get_db() as conn:
        cur_v = conn.execute(
            "SELECT COUNT(*) as count FROM document_versions WHERE document_id = ?",
            (document_id,)
        ).fetchone()
        next_ver = (cur_v["count"] or 1) + 1
        
        conn.execute(
            "INSERT INTO document_versions (id, document_id, version_num, stored_filename, description) VALUES (?, ?, ?, ?, ?)",
            (version_id, document_id, next_ver, new_filename, description)
        )
        conn.execute(
            "UPDATE documents SET stored_filename = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (new_filename, document_id)
        )
    return new_path

@router.post("/edit-text")
def edit_existing_text(req: EditTextRequest):
    """
    Core Feature: Edits existing PDF text via Direct Edit Mode (Mode A)
    or Overlay Redaction & Replacement Mode (Mode B).
    """
    file_path, orig_name = get_doc_file_path(req.document_id)
    new_version_path = create_new_version(
        req.document_id,
        file_path,
        f"Edit Text: '{req.original_text}' -> '{req.new_text}'"
    )
    
    try:
        if req.mode == "direct":
            result = direct_edit_text(
                doc_path=file_path,
                output_path=new_version_path,
                page_number=req.page_number,
                target_bbox=req.target_bbox,
                original_text=req.original_text,
                new_text=req.new_text,
                font_family=req.font_family,
                font_size=req.font_size,
                font_color=req.font_color,
                bold=req.bold,
                italic=req.italic,
                alignment=req.alignment
            )
        else:
            result = overlay_edit_text(
                doc_path=file_path,
                output_path=new_version_path,
                page_number=req.page_number,
                target_bbox=req.target_bbox,
                original_text=req.original_text,
                new_text=req.new_text,
                font_family=req.font_family,
                font_size=req.font_size,
                font_color=req.font_color,
                bold=req.bold,
                italic=req.italic,
                alignment=req.alignment,
                background_color=req.background_color,
                apply_redaction=req.apply_redaction
            )
            
        # Re-inspect page to return fresh geometry to frontend
        inspection = inspect_document(new_version_path, req.document_id, orig_name)
        result["updated_inspection"] = inspection
        return result
        
    except Exception as e:
        if new_version_path.exists():
            new_version_path.unlink()
        raise HTTPException(status_code=500, detail=f"Text editing failed: {str(e)}")

@router.post("/add-text")
def add_new_text(req: AddTextRequest):
    """Adds a new text element to the specified coordinates on the page."""
    file_path, orig_name = get_doc_file_path(req.document_id)
    new_version_path = create_new_version(req.document_id, file_path, f"Add Text: '{req.text}'")
    
    # We can use overlay_edit_text with apply_redaction=False
    try:
        bbox = [req.position[0], req.position[1], req.position[0] + 200, req.position[1] + 30]
        result = overlay_edit_text(
            doc_path=file_path,
            output_path=new_version_path,
            page_number=req.page_number,
            target_bbox=bbox,
            original_text="",
            new_text=req.text,
            font_family=req.font_family,
            font_size=req.font_size,
            font_color=req.font_color,
            bold=req.bold,
            italic=req.italic,
            apply_redaction=False
        )
        inspection = inspect_document(new_version_path, req.document_id, orig_name)
        result["updated_inspection"] = inspection
        return result
    except Exception as e:
        if new_version_path.exists():
            new_version_path.unlink()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/images")
def handle_image_operation(req: ImageOperationRequest):
    """Adds, replaces, or deletes images on a page."""
    file_path, orig_name = get_doc_file_path(req.document_id)
    new_version_path = create_new_version(req.document_id, file_path, f"Image Op: {req.operation}")
    
    try:
        if req.operation == "add":
            if not req.image_data_base64 or not req.position:
                raise HTTPException(status_code=400, detail="Missing image data or position.")
            img_bytes = decode_base64_image(req.image_data_base64)
            res = add_image_to_page(
                doc_path=file_path,
                output_path=new_version_path,
                page_number=req.page_number,
                image_bytes=img_bytes,
                position=req.position,
                opacity=req.opacity or 1.0
            )
        elif req.operation == "replace":
            if not req.image_data_base64 or not req.image_xref:
                raise HTTPException(status_code=400, detail="Missing new image or xref.")
            img_bytes = decode_base64_image(req.image_data_base64)
            res = replace_existing_image(
                doc_path=file_path,
                output_path=new_version_path,
                page_number=req.page_number,
                image_xref=req.image_xref,
                new_image_bytes=img_bytes
            )
        elif req.operation == "delete":
            res = delete_image_from_page(
                doc_path=file_path,
                output_path=new_version_path,
                page_number=req.page_number,
                image_xref=req.image_xref or 0,
                bbox=req.position
            )
        else:
            raise HTTPException(status_code=400, detail="Unknown image operation.")
            
        inspection = inspect_document(new_version_path, req.document_id, orig_name)
        res["updated_inspection"] = inspection
        return res
    except Exception as e:
        if new_version_path.exists():
            new_version_path.unlink()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/annotations")
def handle_annotation(req: AnnotationRequest):
    """Applies highlights, shapes, freehand ink drawings, or notes."""
    file_path, orig_name = get_doc_file_path(req.document_id)
    new_version_path = create_new_version(req.document_id, file_path, f"Annotate: {req.type}")
    
    try:
        res = add_annotation_to_page(
            doc_path=file_path,
            output_path=new_version_path,
            page_number=req.page_number,
            annot_type=req.type,
            rect=req.rect,
            points=req.points,
            color=req.color,
            stroke_width=req.stroke_width,
            opacity=req.opacity,
            comment=req.comment
        )
        return res
    except Exception as e:
        if new_version_path.exists():
            new_version_path.unlink()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/signatures")
def handle_signature(req: SignatureRequest):
    """Stamps user signature."""
    file_path, orig_name = get_doc_file_path(req.document_id)
    new_version_path = create_new_version(req.document_id, file_path, "Applied Signature")
    
    try:
        res = apply_signature(
            doc_path=file_path,
            output_path=new_version_path,
            page_number=req.page_number,
            signature_data_url=req.signature_data_url,
            rect=req.rect,
            is_cryptographic=req.is_cryptographic
        )
        return res
    except Exception as e:
        if new_version_path.exists():
            new_version_path.unlink()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/pages")
def handle_page_management(req: PageManagementRequest):
    """Executes rotate, delete, duplicate, reorder, insert blank, or crop."""
    file_path, orig_name = get_doc_file_path(req.document_id)
    new_version_path = create_new_version(req.document_id, file_path, f"Page Op: {req.operation}")
    
    try:
        if req.operation == "rotate":
            res = rotate_page(file_path, new_version_path, req.page_number, req.rotation_angle or 90)
        elif req.operation == "delete":
            res = delete_page(file_path, new_version_path, req.page_number)
        elif req.operation == "duplicate":
            res = duplicate_page(file_path, new_version_path, req.page_number)
        elif req.operation == "insert_blank":
            res = insert_blank_page(file_path, new_version_path, req.page_number)
        elif req.operation == "crop":
            if not req.crop_rect:
                raise HTTPException(status_code=400, detail="Missing crop rect coordinates.")
            res = crop_page(file_path, new_version_path, req.page_number, req.crop_rect)
        else:
            raise HTTPException(status_code=400, detail="Unsupported page operation.")
            
        inspection = inspect_document(new_version_path, req.document_id, orig_name)
        res["updated_inspection"] = inspection
        return res
    except Exception as e:
        if new_version_path.exists():
            new_version_path.unlink()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/export/{document_id}")
def export_pdf(document_id: str):
    """Generates and serves a clean, optimized download of the edited PDF."""
    file_path, orig_name = get_doc_file_path(document_id)
    export_name = f"PDF_NEXUS_Edited_{orig_name}"
    export_path = settings.EXPORTS_PATH / f"{uuid.uuid4().hex[:8]}_{export_name}"
    
    # Save optimized copy
    doc = pymupdf.open(file_path)
    doc.save(str(export_path), garbage=4, deflate=True, clean=True)
    doc.close()
    
    return FileResponse(
        path=str(export_path),
        media_type="application/pdf",
        filename=export_name
    )
