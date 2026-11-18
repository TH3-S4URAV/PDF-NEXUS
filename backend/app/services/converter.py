"""
PDF NEXUS - Document Conversion & PDF Utilities Engine
Handles high-fidelity conversions between PDF, Word, Excel, PowerPoint, and Images,
plus Compress, Merge, Split, Protect, Unlock, Watermark, and Page Numbering.
"""

import io
import os
import zipfile
from pathlib import Path
from typing import List, Dict, Any, Optional
import pymupdf
from PIL import Image
import openpyxl
from openpyxl.styles import Font, PatternFill
import docx
from pptx import Presentation
from pptx.util import Inches, Pt

from app.services.font_matcher import hex_to_rgb

# 1. CONVERSIONS

def pdf_to_docx(pdf_path: Path, output_path: Path) -> Path:
    """Converts a PDF document to Microsoft Word .docx using pdf2docx."""
    from pdf2docx import Converter
    cv = Converter(str(pdf_path))
    try:
        cv.convert(str(output_path), start=0, end=None)
    finally:
        cv.close()
    return output_path

def docx_to_pdf(docx_path: Path, output_path: Path) -> Path:
    """Converts a .docx document to PDF via python-docx text extraction and PyMuPDF vector rendering."""
    doc_docx = docx.Document(docx_path)
    out_pdf = pymupdf.open()
    
    # Simple flow layout engine
    page = out_pdf.new_page(width=612, height=792)  # Standard Letter
    y = 54.0
    for p in doc_docx.paragraphs:
        txt = p.text.strip()
        if not txt:
            y += 12
            continue
        if y > 738:
            page = out_pdf.new_page(width=612, height=792)
            y = 54.0
            
        is_heading = p.style.name.startswith("Heading")
        font_size = 16.0 if is_heading else 11.0
        font_name = "hebo" if is_heading else "helv"
        
        rect = pymupdf.Rect(54, y, 558, min(738, y + 100))
        rc = page.insert_textbox(rect, txt, fontsize=font_size, fontname=font_name, color=(0, 0, 0))
        y += max(20, rect.height if rc > 0 else 24)
        
    out_pdf.save(str(output_path), garbage=3, deflate=True)
    out_pdf.close()
    return output_path

def pdf_to_excel(pdf_path: Path, output_path: Path) -> Path:
    """Extracts tables and structured text from PDF into an Excel spreadsheet (.xlsx)."""
    import pdfplumber
    wb = openpyxl.Workbook()
    # Remove default sheet
    wb.remove(wb.active)
    
    with pdfplumber.open(pdf_path) as pdf:
        for idx, page in enumerate(pdf.pages):
            sheet = wb.create_sheet(title=f"Page {idx+1}")
            tables = page.extract_tables()
            if tables:
                r_offset = 1
                for table in tables:
                    for row in table:
                        clean_row = [str(c or "") for c in row]
                        sheet.append(clean_row)
                        r_offset += 1
                    sheet.append([])  # empty separator
            else:
                # Fallback to extracting text lines
                text = page.extract_text() or ""
                for line in text.split("\n"):
                    sheet.append([line])
                    
    wb.save(output_path)
    return output_path

def excel_to_pdf(xlsx_path: Path, output_path: Path) -> Path:
    """Converts Excel sheet to PDF table view."""
    wb = openpyxl.load_workbook(xlsx_path, data_only=True)
    out_pdf = pymupdf.open()
    
    for sheet_name in wb.sheetnames:
        sheet = wb[sheet_name]
        page = out_pdf.new_page(width=792, height=612)  # Landscape
        page.insert_text((54, 40), f"Sheet: {sheet_name}", fontsize=14, fontname="hebo")
        
        y = 70.0
        for row in sheet.iter_rows(values_only=True):
            if y > 560:
                page = out_pdf.new_page(width=792, height=612)
                y = 54.0
            row_str = "  |  ".join([str(val) if val is not None else "" for val in row if val is not None])
            if row_str.strip():
                page.insert_text((54, y), row_str[:120], fontsize=9, fontname="cour")
                y += 16.0
                
    out_pdf.save(str(output_path), garbage=3, deflate=True)
    out_pdf.close()
    return output_path

def pdf_to_pptx(pdf_path: Path, output_path: Path) -> Path:
    """Converts PDF pages into PowerPoint slides with page screenshots."""
    doc = pymupdf.open(pdf_path)
    prs = Presentation()
    # Set 16:9 widescreen or 4:3
    prs.slide_width = Inches(10)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]
    
    try:
        for pno in range(len(doc)):
            page = doc[pno]
            pix = page.get_pixmap(dpi=150)
            img_io = io.BytesIO(pix.tobytes(output="png"))
            
            slide = prs.slides.add_slide(blank_layout)
            slide.shapes.add_picture(img_io, Inches(0.5), Inches(0.5), width=Inches(9))
            
        prs.save(str(output_path))
    finally:
        doc.close()
    return output_path

def pdf_to_images(pdf_path: Path, output_dir: Path, format: str = "png") -> List[Path]:
    """Renders every page of a PDF as high-resolution image."""
    doc = pymupdf.open(pdf_path)
    img_paths = []
    try:
        for pno in range(len(doc)):
            page = doc[pno]
            pix = page.get_pixmap(dpi=200)
            out_file = output_dir / f"page_{pno + 1}.{format}"
            pix.save(str(out_file))
            img_paths.append(out_file)
    finally:
        doc.close()
    return img_paths

def images_to_pdf(image_paths: List[Path], output_path: Path) -> Path:
    """Combines one or more images into a single PDF document."""
    out_pdf = pymupdf.open()
    for img_path in image_paths:
        img = Image.open(img_path)
        w, h = img.size
        # Create page matching image aspect ratio
        page = out_pdf.new_page(width=float(w), height=float(h))
        page.insert_image(pymupdf.Rect(0, 0, w, h), filename=str(img_path))
    out_pdf.save(str(output_path), garbage=3, deflate=True)
    out_pdf.close()
    return output_path

# 2. PDF UTILITIES

def compress_pdf(doc_path: Path, output_path: Path, level: str = "medium") -> Dict[str, Any]:
    """Compresses PDF by garbage collection, stream deflation, and image downsampling."""
    doc = pymupdf.open(doc_path)
    orig_size = doc_path.stat().st_size
    
    # Save with full deflation
    garbage_level = 4 if level == "high" else 3
    doc.save(
        str(output_path),
        garbage=garbage_level,
        deflate=True,
        clean=True,
        deflate_images=True,
        deflate_fonts=True
    )
    doc.close()
    new_size = output_path.stat().st_size
    saving_pct = round(max(0, (1.0 - (new_size / orig_size))) * 100, 1) if orig_size > 0 else 0
    return {
        "success": True,
        "original_size": orig_size,
        "compressed_size": new_size,
        "savings_percentage": saving_pct
    }

def merge_pdfs(doc_paths: List[Path], output_path: Path) -> Dict[str, Any]:
    """Merges multiple PDF documents in given order."""
    merged = pymupdf.open()
    for p in doc_paths:
        with pymupdf.open(p) as src:
            merged.insert_pdf(src)
    merged.save(str(output_path), garbage=3, deflate=True)
    total_pages = len(merged)
    merged.close()
    return {"success": True, "total_pages": total_pages}

def split_pdf(doc_path: Path, output_dir: Path, page_ranges: str) -> List[Path]:
    """Splits PDF by ranges, e.g. '1-2, 3, 4-5'."""
    doc = pymupdf.open(doc_path)
    max_pages = len(doc)
    created_files = []
    
    parts = [p.strip() for p in page_ranges.split(",") if p.strip()]
    try:
        for idx, part in enumerate(parts):
            if "-" in part:
                start_s, end_s = part.split("-")
                start = max(1, min(int(start_s), max_pages))
                end = max(1, min(int(end_s), max_pages))
            else:
                start = end = max(1, min(int(part), max_pages))
                
            split_doc = pymupdf.open()
            split_doc.insert_pdf(doc, from_page=start - 1, to_page=end - 1)
            out_file = output_dir / f"split_part_{idx+1}_pages_{start}_{end}.pdf"
            split_doc.save(str(out_file), garbage=3, deflate=True)
            split_doc.close()
            created_files.append(out_file)
    finally:
        doc.close()
    return created_files

def protect_pdf(doc_path: Path, output_path: Path, password: str) -> Dict[str, Any]:
    """Encrypts and password-protects a PDF document."""
    doc = pymupdf.open(doc_path)
    perm = pymupdf.PDF_PERM_PRINT | pymupdf.PDF_PERM_COPY
    doc.save(
        str(output_path),
        encryption=pymupdf.PDF_ENCRYPT_AES_256,
        owner_pw=password,
        user_pw=password,
        permissions=perm
    )
    doc.close()
    return {"success": True, "protected": True}

def unlock_pdf(doc_path: Path, output_path: Path, password: str) -> Dict[str, Any]:
    """Decrypts a password-protected PDF document."""
    doc = pymupdf.open(doc_path)
    if doc.is_encrypted:
        auth_success = doc.authenticate(password)
        if not auth_success:
            doc.close()
            raise ValueError("Incorrect password provided.")
    doc.save(str(output_path), encryption=pymupdf.PDF_ENCRYPT_NONE)
    doc.close()
    return {"success": True, "unlocked": True}

def watermark_pdf(
    doc_path: Path,
    output_path: Path,
    text: str,
    font_size: float = 40.0,
    opacity: float = 0.3,
    rotation: float = 45.0,
    color: str = "#888888"
) -> Dict[str, Any]:
    """Adds a semi-transparent diagonal watermark across all pages."""
    doc = pymupdf.open(doc_path)
    color_rgb = hex_to_rgb(color)
    
    for page in doc:
        rect = page.rect
        center_x = rect.width / 2.0
        center_y = rect.height / 2.0
        
        # Insert rotated watermark text using matrix morphing
        pt = pymupdf.Point(center_x - 100, center_y)
        mat = pymupdf.Matrix(rotation)
        page.insert_text(
            pt,
            text,
            fontsize=font_size,
            fontname="hebo",
            color=color_rgb,
            morph=(pt, mat),
            fill_opacity=opacity
        )
        
    doc.save(str(output_path), garbage=3, deflate=True)
    doc.close()
    return {"success": True, "watermarked": True}

def add_page_numbers(
    doc_path: Path,
    output_path: Path,
    position: str = "bottom-center",
    start_number: int = 1,
    format_template: str = "Page {page} of {total}"
) -> Dict[str, Any]:
    """Adds customizable page numbers to each page."""
    doc = pymupdf.open(doc_path)
    total_pages = len(doc)
    
    for idx, page in enumerate(doc):
        cur_num = start_number + idx
        label = format_template.format(page=cur_num, total=total_pages)
        rect = page.rect
        
        if position == "bottom-center":
            pos = (rect.width / 2.0 - 40, rect.height - 30)
        elif position == "bottom-right":
            pos = (rect.width - 120, rect.height - 30)
        elif position == "top-right":
            pos = (rect.width - 120, 30)
        else:
            pos = (rect.width / 2.0 - 40, rect.height - 30)
            
        page.insert_text(pos, label, fontsize=10, fontname="helv", color=(0.3, 0.3, 0.3))
        
    doc.save(str(output_path), garbage=3, deflate=True)
    doc.close()
    return {"success": True, "page_numbers_added": True}
