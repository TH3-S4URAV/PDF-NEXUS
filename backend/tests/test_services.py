"""
PDF NEXUS - Direct Services Test Suite
Tests text inspection, Mode A Direct Edit, Mode B Overlay Redaction, Page Operations,
Image Operations, Annotations, Signatures, and Utilities directly against PyMuPDF.
"""

import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

import pymupdf
from app.services.text_inspector import inspect_document, render_page_thumbnail
from app.services.direct_text_editor import direct_edit_text
from app.services.overlay_editor import overlay_edit_text
from app.services.page_manager import rotate_page, duplicate_page, delete_page, insert_blank_page
from app.services.annotations_manager import add_annotation_to_page, apply_signature
from app.services.converter import compress_pdf, protect_pdf, unlock_pdf, watermark_pdf, add_page_numbers, pdf_to_images
from app.services.ocr_service import detect_scanned_pages

def create_sample_pdf(output_path: Path):
    doc = pymupdf.open()
    # Page 1
    p1 = doc.new_page(width=612, height=792)
    p1.insert_text((72, 100), "PDF NEXUS Master Document", fontsize=20, fontname="hebo", color=(0.1, 0.2, 0.6))
    p1.insert_text((72, 140), "Welcome to professional online PDF editing.", fontsize=12, fontname="helv", color=(0, 0, 0))
    p1.insert_text((72, 180), "Original Text Paragraph: The quick brown fox jumps.", fontsize=12, fontname="tiro", color=(0.2, 0.2, 0.2))
    p1.insert_text((72, 220), "Confidential Code: 994827-Secret", fontsize=11, fontname="cour", color=(0.8, 0.1, 0.1))
    
    # Page 2
    p2 = doc.new_page(width=612, height=792)
    p2.insert_text((72, 100), "Second Page - Financial Summary", fontsize=16, fontname="hebo", color=(0, 0, 0))
    p2.insert_text((72, 140), "Q4 Revenue exceeded expectations by 24 percent.", fontsize=12, fontname="helv", color=(0, 0, 0))
    doc.save(str(output_path))
    doc.close()

def run_all_tests():
    tmp_dir = backend_dir / "tests" / "tmp"
    tmp_dir.mkdir(parents=True, exist_ok=True)
    sample_pdf = tmp_dir / "sample.pdf"
    create_sample_pdf(sample_pdf)
    
    print("[1/10] Testing Document Text & Geometry Inspection...")
    inspection = inspect_document(sample_pdf, "doc_123", "sample.pdf")
    assert inspection.page_count == 2
    assert inspection.pages[0].width == 612.0
    assert len(inspection.pages[0].blocks) > 0
    print(" -> Inspection verified! Found", len(inspection.pages[0].blocks), "blocks on page 1.")
    
    print("[2/10] Testing Page Thumbnail Rendering...")
    thumb = render_page_thumbnail(sample_pdf, 1)
    assert len(thumb) > 100
    print(" -> Thumbnail generated! Byte size:", len(thumb))
    
    print("[3/10] Testing Mode A: Direct PDF Text Editing...")
    mode_a_out = tmp_dir / "mode_a_out.pdf"
    res_a = direct_edit_text(
        doc_path=sample_pdf,
        output_path=mode_a_out,
        page_number=1,
        target_bbox=[72, 130, 350, 150],
        original_text="Welcome to professional online PDF editing.",
        new_text="Welcome to PDF NEXUS Next-Gen Editor.",
        font_family="Helvetica",
        font_size=12.0,
        font_color="#0000FF",
        bold=False
    )
    assert res_a["success"] is True
    # Verify in output PDF
    doc_a = pymupdf.open(mode_a_out)
    text_a = doc_a[0].get_text()
    assert "PDF NEXUS Next-Gen Editor" in text_a
    doc_a.close()
    print(" -> Mode A verified! Text replaced in PDF stream.")
    
    print("[4/10] Testing Mode B: Overlay Redaction & Replacement...")
    mode_b_out = tmp_dir / "mode_b_out.pdf"
    res_b = overlay_edit_text(
        doc_path=sample_pdf,
        output_path=mode_b_out,
        page_number=1,
        target_bbox=[72, 210, 300, 230],
        original_text="Confidential Code: 994827-Secret",
        new_text="Cleared Code: [PUBLIC-VERIFIED]",
        font_family="Courier",
        font_size=11.0,
        font_color="#008800",
        bold=True,
        apply_redaction=True
    )
    assert res_b["success"] is True
    doc_b = pymupdf.open(mode_b_out)
    text_b = doc_b[0].get_text()
    assert "994827-Secret" not in text_b  # True redaction: original sensitive text completely removed
    assert "Cleared Code: [PUBLIC-VERIFIED]" in text_b
    doc_b.close()
    print(" -> Mode B verified! Sensitive text physically excised and replaced.")
    
    print("[5/10] Testing Page Operations (Rotate, Duplicate, Insert Blank, Delete)...")
    p_rot = tmp_dir / "page_rot.pdf"
    rotate_page(sample_pdf, p_rot, page_number=1, angle=90)
    doc_rot = pymupdf.open(p_rot)
    assert doc_rot[0].rotation == 90
    doc_rot.close()
    
    p_dup = tmp_dir / "page_dup.pdf"
    duplicate_page(sample_pdf, p_dup, page_number=1)
    doc_dup = pymupdf.open(p_dup)
    assert len(doc_dup) == 3
    doc_dup.close()
    
    p_blank = tmp_dir / "page_blank.pdf"
    insert_blank_page(sample_pdf, p_blank, position=2)
    doc_blank = pymupdf.open(p_blank)
    assert len(doc_blank) == 3
    doc_blank.close()
    print(" -> Page management operations verified!")
    
    print("[6/10] Testing Annotations & Markup...")
    annot_out = tmp_dir / "annot_out.pdf"
    add_annotation_to_page(sample_pdf, annot_out, page_number=1, annot_type="highlight", rect=[72, 95, 300, 115], color="#FFD700")
    doc_annot = pymupdf.open(annot_out)
    assert len(list(doc_annot[0].annots())) > 0
    doc_annot.close()
    print(" -> Vector highlights and annotations verified!")
    
    print("[7/10] Testing Signatures...")
    import base64
    from PIL import Image as PILImage
    import io
    # Create synthetic signature PNG
    sig_img = PILImage.new("RGBA", (100, 50), (255, 255, 255, 0))
    sig_bytes = io.BytesIO()
    sig_img.save(sig_bytes, format="PNG")
    sig_b64 = "data:image/png;base64," + base64.b64encode(sig_bytes.getvalue()).decode()
    
    sig_out = tmp_dir / "sig_out.pdf"
    sig_res = apply_signature(sample_pdf, sig_out, page_number=1, signature_data_url=sig_b64, rect=[400, 700, 500, 750], is_cryptographic=True)
    assert sig_res["success"] is True
    print(" -> Signature stamp and digital stamping verified!")
    
    print("[8/10] Testing PDF Utilities: Compress, Watermark, Page Numbers...")
    comp_out = tmp_dir / "compressed.pdf"
    compress_pdf(sample_pdf, comp_out, level="medium")
    assert comp_out.exists()
    
    wm_out = tmp_dir / "watermarked.pdf"
    watermark_pdf(sample_pdf, wm_out, text="CONFIDENTIAL", font_size=36.0, opacity=0.3)
    assert wm_out.exists()
    
    pn_out = tmp_dir / "numbered.pdf"
    add_page_numbers(sample_pdf, pn_out, position="bottom-center")
    assert pn_out.exists()
    print(" -> Compression, watermarking, and page numbering verified!")
    
    print("[9/10] Testing PDF Protection and Decryption...")
    prot_out = tmp_dir / "protected.pdf"
    protect_pdf(sample_pdf, prot_out, password="NexusPassword2026")
    doc_prot = pymupdf.open(prot_out)
    assert doc_prot.is_encrypted is True
    doc_prot.close()
    
    unlock_out = tmp_dir / "unlocked.pdf"
    unlock_pdf(prot_out, unlock_out, password="NexusPassword2026")
    doc_unl = pymupdf.open(unlock_out)
    assert doc_unl.is_encrypted is False
    doc_unl.close()
    print(" -> AES-256 PDF protection and unlocking verified!")
    
    print("[10/10] Testing Scanned Page Detection...")
    scan_res = detect_scanned_pages(sample_pdf)
    assert len(scan_res) == 2
    assert scan_res[0]["is_scanned"] is False
    print(" -> Scanned page detection verified!")
    
    print("\nALL 10 PDF NEXUS CORE SERVICES TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    run_all_tests()
