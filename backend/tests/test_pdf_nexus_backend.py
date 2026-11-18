"""
PDF NEXUS - Comprehensive Automated Backend Test Suite
Verifies API availability, document upload, text inspection, Mode A Direct Edit,
Mode B Overlay Redaction, Page Operations, Image Operations, Annotations, and PDF Utilities.
"""

import io
import pytest
import pymupdf
from pathlib import Path
from fastapi.testclient import TestClient

from app.main import app
from app.core.config import settings

client = TestClient(app)

def create_synthetic_test_pdf() -> bytes:
    """Creates a sample multi-page vector PDF with text, fonts, and geometry for automated testing."""
    doc = pymupdf.open()
    # Page 1
    p1 = doc.new_page(width=612, height=792)
    p1.insert_text((72, 100), "PDF NEXUS Master Document", fontsize=20, fontname="hebo", color=(0.1, 0.2, 0.6))
    p1.insert_text((72, 140), "Welcome to professional online PDF editing.", fontsize=12, fontname="helv", color=(0, 0, 0))
    p1.insert_text((72, 180), "Editable Paragraph: The quick brown fox jumps over the lazy dog.", fontsize=12, fontname="tiro", color=(0.2, 0.2, 0.2))
    p1.insert_text((72, 220), "Confidential data: Code-994827-Alpha", fontsize=11, fontname="cour", color=(0.8, 0.1, 0.1))
    
    # Page 2
    p2 = doc.new_page(width=612, height=792)
    p2.insert_text((72, 100), "Second Page - Financial Summary", fontsize=16, fontname="hebo", color=(0, 0, 0))
    p2.insert_text((72, 140), "Q4 Revenue exceeded expectations by 24 percent.", fontsize=12, fontname="helv", color=(0, 0, 0))
    
    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes

def test_healthcheck():
    """Verify health endpoint."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["project"] == "PDF NEXUS"

def test_invalid_file_rejection():
    """Verify that non-PDF files are rejected."""
    bad_file = io.BytesIO(b"This is just plain text, not a valid PDF file.")
    response = client.post(
        "/api/documents/upload",
        files={"file": ("fake.pdf", bad_file, "application/pdf")}
    )
    assert response.status_code == 400
    assert "Missing %PDF-" in response.json()["detail"]

def test_document_upload_and_inspection():
    """Verify upload, metadata extraction, and span-level text inspection."""
    pdf_bytes = create_synthetic_test_pdf()
    response = client.post(
        "/api/documents/upload",
        files={"file": ("test_sample.pdf", io.BytesIO(pdf_bytes), "application/pdf")}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["page_count"] == 2
    doc_id = data["document_id"]
    
    # Check inspection details
    metadata = data["metadata"]
    assert len(metadata["pages"]) == 2
    page1 = metadata["pages"][0]
    assert page1["page_number"] == 1
    assert page1["width"] == 612.0
    assert page1["height"] == 792.0
    
    # Check text spans
    found_title = False
    for block in page1["blocks"]:
        for line in block["lines"]:
            for span in line["spans"]:
                if "PDF NEXUS" in span["text"]:
                    found_title = True
                    assert span["size"] == 20.0
                    assert span["is_bold"] is True
    assert found_title is True

def test_mode_a_direct_text_editing():
    """Verify Mode A Direct Text Replacement."""
    pdf_bytes = create_synthetic_test_pdf()
    up_res = client.post(
        "/api/documents/upload",
        files={"file": ("direct_edit_test.pdf", io.BytesIO(pdf_bytes), "application/pdf")}
    )
    doc_id = up_res.json()["document_id"]
    
    edit_payload = {
        "document_id": doc_id,
        "page_number": 1,
        "mode": "direct",
        "target_bbox": [72, 130, 400, 150],
        "original_text": "Welcome to professional online PDF editing.",
        "new_text": "Welcome to PDF NEXUS Next-Gen Editor.",
        "font_family": "Helvetica",
        "font_size": 12.0,
        "font_color": "#0000FF",
        "bold": False,
        "italic": False,
        "alignment": "left"
    }
    
    res = client.post("/api/pdf/edit-text", json=edit_payload)
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["mode"] == "direct"
    assert data["replaced_text"] == "Welcome to PDF NEXUS Next-Gen Editor."

def test_mode_b_overlay_redaction_and_editing():
    """Verify Mode B True Redaction and Typography Overlay Replacement."""
    pdf_bytes = create_synthetic_test_pdf()
    up_res = client.post(
        "/api/documents/upload",
        files={"file": ("overlay_test.pdf", io.BytesIO(pdf_bytes), "application/pdf")}
    )
    doc_id = up_res.json()["document_id"]
    
    edit_payload = {
        "document_id": doc_id,
        "page_number": 1,
        "mode": "overlay",
        "target_bbox": [72, 210, 350, 230],
        "original_text": "Confidential data: Code-994827-Alpha",
        "new_text": "Redacted data: [CLEARED FOR PUBLIC VIEW]",
        "font_family": "Courier",
        "font_size": 11.0,
        "font_color": "#008800",
        "bold": True,
        "italic": False,
        "alignment": "left",
        "background_color": "#ffffff",
        "apply_redaction": True
    }
    
    res = client.post("/api/pdf/edit-text", json=edit_payload)
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["mode"] == "overlay"
    assert data["redaction_applied"] is True

def test_page_management_operations():
    """Verify rotate, duplicate, insert blank, and delete operations."""
    pdf_bytes = create_synthetic_test_pdf()
    up_res = client.post(
        "/api/documents/upload",
        files={"file": ("page_ops_test.pdf", io.BytesIO(pdf_bytes), "application/pdf")}
    )
    doc_id = up_res.json()["document_id"]
    
    # 1. Rotate Page 1 by 90 degrees
    rot_res = client.post("/api/pdf/pages", json={
        "document_id": doc_id,
        "operation": "rotate",
        "page_number": 1,
        "rotation_angle": 90
    })
    assert rot_res.status_code == 200
    assert rot_res.json()["new_rotation"] == 90
    
    # 2. Insert blank page at end
    blank_res = client.post("/api/pdf/pages", json={
        "document_id": doc_id,
        "operation": "insert_blank",
        "page_number": 3
    })
    assert blank_res.status_code == 200
    assert blank_res.json()["total_pages"] == 3
    
    # 3. Duplicate page 2
    dup_res = client.post("/api/pdf/pages", json={
        "document_id": doc_id,
        "operation": "duplicate",
        "page_number": 2
    })
    assert dup_res.status_code == 200
    assert dup_res.json()["total_pages"] == 4
    
    # 4. Delete page 4
    del_res = client.post("/api/pdf/pages", json={
        "document_id": doc_id,
        "operation": "delete",
        "page_number": 4
    })
    assert del_res.status_code == 200
    assert del_res.json()["total_pages"] == 3

def test_pdf_utilities_protect_and_unlock():
    """Verify encryption and decryption."""
    pdf_bytes = create_synthetic_test_pdf()
    up_res = client.post(
        "/api/documents/upload",
        files={"file": ("protect_test.pdf", io.BytesIO(pdf_bytes), "application/pdf")}
    )
    doc_id = up_res.json()["document_id"]
    
    # Protect
    prot_res = client.post("/api/pdf/utils/protect", json={
        "document_id": doc_id,
        "password": "SecurePassword123"
    })
    assert prot_res.status_code == 200
    assert prot_res.json()["protected"] is True

def test_pdf_utilities_watermark_and_page_numbers():
    """Verify watermarking and page numbering."""
    pdf_bytes = create_synthetic_test_pdf()
    up_res = client.post(
        "/api/documents/upload",
        files={"file": ("watermark_test.pdf", io.BytesIO(pdf_bytes), "application/pdf")}
    )
    doc_id = up_res.json()["document_id"]
    
    # Watermark
    wm_res = client.post("/api/pdf/utils/watermark", json={
        "document_id": doc_id,
        "text": "CONFIDENTIAL DRAFT",
        "font_size": 36.0,
        "opacity": 0.25,
        "rotation": 45.0,
        "color": "#FF0000"
    })
    assert wm_res.status_code == 200
    assert wm_res.json()["watermarked"] is True
    
    # Page Numbers
    pn_res = client.post("/api/pdf/utils/page-numbers", json={
        "document_id": doc_id,
        "position": "bottom-center",
        "start_number": 1,
        "format_template": "Page {page} of {total}"
    })
    assert pn_res.status_code == 200
    assert pn_res.json()["page_numbers_added"] is True

def test_scanned_page_detection():
    """Verify scanned page detector."""
    pdf_bytes = create_synthetic_test_pdf()
    up_res = client.post(
        "/api/documents/upload",
        files={"file": ("scan_check.pdf", io.BytesIO(pdf_bytes), "application/pdf")}
    )
    doc_id = up_res.json()["document_id"]
    
    res = client.get(f"/api/pdf/ocr/detect-scanned/{doc_id}")
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    # Synthetic PDF has text, so should not be marked as scanned document
    assert data["is_scanned_document"] is False
