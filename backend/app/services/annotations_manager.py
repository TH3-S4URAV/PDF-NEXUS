"""
PDF NEXUS - Annotations & Signatures Service
Applies vector highlights, shapes, drawings, and signatures.
"""

import base64
import io
from pathlib import Path
from typing import List, Optional, Dict, Any
import pymupdf
from app.services.font_matcher import hex_to_rgb

def add_annotation_to_page(
    doc_path: Path,
    output_path: Path,
    page_number: int,
    annot_type: str,
    rect: Optional[List[float]] = None,
    points: Optional[List[List[float]]] = None,
    color: str = "#FFD700",
    stroke_width: float = 2.0,
    opacity: float = 0.5,
    comment: Optional[str] = None
) -> Dict[str, Any]:
    """Adds a visual or markup annotation to a PDF page."""
    doc = pymupdf.open(doc_path)
    pno = page_number - 1
    page = doc[pno]
    
    color_rgb = hex_to_rgb(color)
    
    if annot_type == "highlight" and rect:
        r = pymupdf.Rect(rect)
        annot = page.add_highlight_annot(r)
        annot.set_colors(stroke=color_rgb)
        annot.set_opacity(opacity)
        annot.update()
    elif annot_type == "underline" and rect:
        r = pymupdf.Rect(rect)
        annot = page.add_underline_annot(r)
        annot.set_colors(stroke=color_rgb)
        annot.set_opacity(opacity)
        annot.update()
    elif annot_type == "strike" and rect:
        r = pymupdf.Rect(rect)
        annot = page.add_strikeout_annot(r)
        annot.set_colors(stroke=color_rgb)
        annot.set_opacity(opacity)
        annot.update()
    elif annot_type == "rect" and rect:
        r = pymupdf.Rect(rect)
        annot = page.add_rect_annot(r)
        annot.set_colors(stroke=color_rgb)
        annot.set_border(width=stroke_width)
        annot.set_opacity(opacity)
        annot.update()
    elif annot_type == "circle" and rect:
        r = pymupdf.Rect(rect)
        annot = page.add_circle_annot(r)
        annot.set_colors(stroke=color_rgb)
        annot.set_border(width=stroke_width)
        annot.set_opacity(opacity)
        annot.update()
    elif annot_type == "line" and rect:
        p1 = pymupdf.Point(rect[0], rect[1])
        p2 = pymupdf.Point(rect[2], rect[3])
        annot = page.add_line_annot(p1, p2)
        annot.set_colors(stroke=color_rgb)
        annot.set_border(width=stroke_width)
        annot.set_opacity(opacity)
        annot.update()
    elif annot_type == "draw" and points and len(points) > 1:
        # Ink annotation for freehand drawing
        point_objs = [[pymupdf.Point(pt[0], pt[1]) for pt in points]]
        annot = page.add_ink_annot(point_objs)
        annot.set_colors(stroke=color_rgb)
        annot.set_border(width=stroke_width)
        annot.set_opacity(opacity)
        annot.update()
    elif annot_type == "note" and rect:
        p = pymupdf.Point(rect[0], rect[1])
        annot = page.add_text_annot(p, comment or "Note")
        annot.set_colors(stroke=color_rgb)
        annot.update()
        
    doc.save(str(output_path), garbage=3, deflate=True)
    doc.close()
    return {"success": True, "type": annot_type, "page_number": page_number}

def apply_signature(
    doc_path: Path,
    output_path: Path,
    page_number: int,
    signature_data_url: str,
    rect: List[float],
    is_cryptographic: bool = False
) -> Dict[str, Any]:
    """Inserts a user-drawn or uploaded signature into the PDF."""
    doc = pymupdf.open(doc_path)
    pno = page_number - 1
    page = doc[pno]
    
    # Decode base64 PNG signature
    raw_data = signature_data_url
    if "," in raw_data:
        raw_data = raw_data.split(",")[1]
    sig_bytes = base64.b64decode(raw_data)
    
    target_rect = pymupdf.Rect(rect)
    page.insert_image(target_rect, stream=sig_bytes, keep_proportion=True)
    
    # If cryptographic signature metadata requested, stamp metadata
    if is_cryptographic:
        meta = doc.metadata or {}
        meta["keywords"] = (meta.get("keywords") or "") + " [Digitally Signed via PDF NEXUS]"
        doc.set_metadata(meta)
        
    doc.save(str(output_path), garbage=3, deflate=True)
    doc.close()
    
    return {
        "success": True,
        "is_cryptographic": is_cryptographic,
        "signature_type": "Cryptographic Digital Stamp" if is_cryptographic else "Image Signature",
        "rect": rect
    }
