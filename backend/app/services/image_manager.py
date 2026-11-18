"""
PDF NEXUS - Image Management Service
Handles adding, replacing, deleting, rotating, and scaling images on PDF pages.
"""

import io
import base64
from pathlib import Path
from typing import List, Optional, Dict, Any
import pymupdf
from PIL import Image

def decode_base64_image(data_url: str) -> bytes:
    """Decodes data:image/...;base64,... into raw image bytes."""
    if "," in data_url:
        data_url = data_url.split(",")[1]
    return base64.b64decode(data_url)

def add_image_to_page(
    doc_path: Path,
    output_path: Path,
    page_number: int,
    image_bytes: bytes,
    position: List[float],  # [x0, y0, x1, y1]
    opacity: float = 1.0,
    rotation: int = 0
) -> Dict[str, Any]:
    """Inserts a new image onto a PDF page at specified coordinates."""
    doc = pymupdf.open(doc_path)
    pno = page_number - 1
    if pno < 0 or pno >= len(doc):
        doc.close()
        raise ValueError(f"Invalid page number {page_number}")
        
    page = doc[pno]
    rect = pymupdf.Rect(position)
    
    # Process image with Pillow if rotation or format conversion is needed
    img = Image.open(io.BytesIO(image_bytes))
    if rotation in (90, 180, 270):
        img = img.rotate(-rotation, expand=True)
        
    out_img_io = io.BytesIO()
    img_format = "PNG" if img.mode in ("RGBA", "LA") else "JPEG"
    img.save(out_img_io, format=img_format, quality=95)
    processed_bytes = out_img_io.getvalue()
    
    # Insert image into PDF page
    page.insert_image(
        rect,
        stream=processed_bytes,
        rotate=0,
        keep_proportion=True
    )
    
    doc.save(str(output_path), garbage=3, deflate=True)
    doc.close()
    
    return {
        "success": True,
        "page_number": page_number,
        "rect": [rect.x0, rect.y0, rect.x1, rect.y1]
    }

def replace_existing_image(
    doc_path: Path,
    output_path: Path,
    page_number: int,
    image_xref: int,
    new_image_bytes: bytes
) -> Dict[str, Any]:
    """Replaces an existing image stream referenced by xref."""
    doc = pymupdf.open(doc_path)
    
    # Replace the image object stream directly
    doc.extract_image(image_xref)  # Verify existence
    doc.update_stream(image_xref, new_image_bytes)
    
    doc.save(str(output_path), garbage=3, deflate=True)
    doc.close()
    
    return {
        "success": True,
        "xref": image_xref,
        "message": "Image replaced successfully."
    }

def delete_image_from_page(
    doc_path: Path,
    output_path: Path,
    page_number: int,
    image_xref: int,
    bbox: Optional[List[float]] = None
) -> Dict[str, Any]:
    """Removes an image from a page by redacting its bounding box."""
    doc = pymupdf.open(doc_path)
    pno = page_number - 1
    page = doc[pno]
    
    if bbox:
        rect = pymupdf.Rect(bbox)
    else:
        rects = page.get_image_rects(image_xref)
        rect = rects[0] if rects else None
        
    if rect:
        page.add_redact_annot(rect, fill=(1, 1, 1))
        page.apply_redactions()
        
    doc.save(str(output_path), garbage=3, deflate=True)
    doc.close()
    
    return {
        "success": True,
        "xref": image_xref,
        "message": "Image deleted."
    }
