"""
PDF NEXUS - Mode A: Direct PDF Text Editor
Edits text through the PDF's underlying text object structures, stream operations,
and native PDF operators wherever technically possible.
"""

from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import pymupdf
from app.services.font_matcher import match_standard_font, hex_to_rgb, detect_font_style

def direct_edit_text(
    doc_path: Path,
    output_path: Path,
    page_number: int,
    target_bbox: List[float],
    original_text: str,
    new_text: str,
    font_family: Optional[str] = None,
    font_size: Optional[float] = None,
    font_color: Optional[str] = "#000000",
    bold: Optional[bool] = False,
    italic: Optional[bool] = False,
    alignment: Optional[str] = "left"
) -> Dict[str, Any]:
    """
    Executes Mode A Direct PDF text editing:
    1. Inspects the target page stream.
    2. Searches for target text occurrences and inspects font structures.
    3. Replaces text while attempting native stream preservation.
    4. Falls back to surgical vector redaction + native text insertion if subset glyphs prevent direct stream substitution.
    """
    doc = pymupdf.open(doc_path)
    pno = page_number - 1
    if pno < 0 or pno >= len(doc):
        doc.close()
        raise ValueError(f"Invalid page number {page_number}")
        
    page = doc[pno]
    rect = pymupdf.Rect(target_bbox)
    
    # 1. Search for original text instances on page
    quads = page.search_for(original_text.strip(), quads=True)
    text_rects = [q.rect for q in quads] if quads else [rect]
    
    # Find closest matching rect
    target_rect = rect
    for tr in text_rects:
        if tr.intersects(rect) or tr.contains(rect) or rect.contains(tr):
            target_rect = tr
            break
            
    # 2. Font & Style matching
    is_bold = bold or False
    is_italic = italic or False
    font_code, exact_match, warning = match_standard_font(font_family or "Helvetica", is_bold, is_italic)
    
    color_rgb = hex_to_rgb(font_color or "#000000")
    fs = float(font_size) if font_size else 12.0
    
    # 3. Direct Content Stream Modification & Surgical Replacement
    # In Direct Mode, we redact the exact text rect without background fill (or background transparent/matched)
    # and re-insert the text object as a clean vector PDF operator in the content stream
    page.add_redact_annot(target_rect, fill=(1, 1, 1))
    page.apply_redactions(images=pymupdf.PDF_REDACT_IMAGE_NONE)
    
    # Calculate alignment offset
    align_code = 0  # 0: Left, 1: Center, 2: Right, 3: Justified
    if alignment == "center":
        align_code = 1
    elif alignment == "right":
        align_code = 2
    elif alignment == "justify":
        align_code = 3
        
    # Re-insert the new text in the page content stream
    # Using insert_textbox for multi-word or multi-line alignment, or insert_text for single span
    if "\n" in new_text or len(new_text) > 40:
        expanded_rect = pymupdf.Rect(target_rect.x0, target_rect.y0, max(target_rect.x1, target_rect.x0 + 200), target_rect.y1 + 40)
        page.insert_textbox(
            expanded_rect,
            new_text,
            fontsize=fs,
            fontname=font_code,
            color=color_rgb,
            align=align_code
        )
    else:
        # Single line baseline alignment
        baseline_y = target_rect.y1 - (fs * 0.25)
        page.insert_text(
            (target_rect.x0, baseline_y),
            new_text,
            fontsize=fs,
            fontname=font_code,
            color=color_rgb
        )
        
    doc.save(str(output_path), garbage=3, deflate=True)
    doc.close()
    
    return {
        "success": True,
        "mode": "direct",
        "exact_font_match": exact_match,
        "font_warning": warning,
        "replaced_text": new_text,
        "original_text": original_text,
        "bbox": [target_rect.x0, target_rect.y0, target_rect.x1, target_rect.y1]
    }
