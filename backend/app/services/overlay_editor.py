"""
PDF NEXUS - Mode B: Overlay Redaction & Replacement Editor
Provides secure true redaction (excising underlying vector text completely)
and draws matched typography replacement over the exact coordinate bounding box.
"""

from pathlib import Path
from typing import List, Dict, Any, Optional
import pymupdf
from PIL import Image
from app.services.font_matcher import match_standard_font, hex_to_rgb

def sample_background_color(page: pymupdf.Page, rect: pymupdf.Rect) -> tuple[float, float, float]:
    """
    Samples the surrounding background color around a text rect to ensure
    seamless visual blending during overlay redaction.
    """
    try:
        # Sample a 20x20 pixel area just outside the text rect
        sample_x = max(0, rect.x0 - 5)
        sample_y = max(0, rect.y0 - 5)
        sample_rect = pymupdf.Rect(sample_x, sample_y, sample_x + 10, sample_y + 10)
        pix = page.get_pixmap(clip=sample_rect)
        if pix.width > 0 and pix.height > 0:
            # Average color
            color = pix.pixel(0, 0)
            if len(color) >= 3:
                return (color[0] / 255.0, color[1] / 255.0, color[2] / 255.0)
    except Exception:
        pass
    return (1.0, 1.0, 1.0)  # Default clean white

def overlay_edit_text(
    doc_path: Path,
    output_path: Path,
    page_number: int,
    target_bbox: List[float],
    original_text: str,
    new_text: str,
    font_family: Optional[str] = "Helvetica",
    font_size: Optional[float] = 12.0,
    font_color: Optional[str] = "#000000",
    bold: Optional[bool] = False,
    italic: Optional[bool] = False,
    alignment: Optional[str] = "left",
    background_color: Optional[str] = "#ffffff",
    apply_redaction: bool = True
) -> Dict[str, Any]:
    """
    Executes Mode B Overlay Editing:
    1. Redacts the original text rect genuinely removing underlying content.
    2. Blends with background fill color.
    3. Places replacement text precisely matching typography and alignment.
    """
    doc = pymupdf.open(doc_path)
    pno = page_number - 1
    if pno < 0 or pno >= len(doc):
        doc.close()
        raise ValueError(f"Invalid page number {page_number}")
        
    page = doc[pno]
    rect = pymupdf.Rect(target_bbox)
    
    # 1. Determine background fill
    bg_rgb = hex_to_rgb(background_color) if background_color else sample_background_color(page, rect)
    
    # 2. Genuine redaction of underlying text content
    if apply_redaction:
        # Pad rect slightly to ensure full coverage of ascenders/descenders
        padded_rect = pymupdf.Rect(rect.x0 - 1, rect.y0 - 1, rect.x1 + 1, rect.y1 + 1)
        page.add_redact_annot(padded_rect, fill=bg_rgb)
        page.apply_redactions(images=pymupdf.PDF_REDACT_IMAGE_NONE)
        
    # 3. Match font and colors
    is_bold = bold or False
    is_italic = italic or False
    font_code, exact_match, warning = match_standard_font(font_family or "Helvetica", is_bold, is_italic)
    text_color_rgb = hex_to_rgb(font_color or "#000000")
    fs = float(font_size) if font_size else 12.0
    
    # 4. Insert replacement text with alignment
    align_code = 0
    if alignment == "center":
        align_code = 1
    elif alignment == "right":
        align_code = 2
    elif alignment == "justify":
        align_code = 3
        
    # Multi-line vs single line
    if "\n" in new_text or len(new_text) > 40:
        box_width = max(rect.width, 150.0)
        box_height = max(rect.height, fs * 2.0)
        text_rect = pymupdf.Rect(rect.x0, rect.y0, rect.x0 + box_width, rect.y0 + box_height)
        page.insert_textbox(
            text_rect,
            new_text,
            fontsize=fs,
            fontname=font_code,
            color=text_color_rgb,
            align=align_code
        )
    else:
        # Align within single line
        baseline_y = rect.y1 - (fs * 0.25)
        start_x = rect.x0
        if alignment == "center":
            text_len = pymupdf.get_text_length(new_text, fontname=font_code, fontsize=fs)
            start_x = max(rect.x0, rect.x0 + (rect.width - text_len) / 2.0)
        elif alignment == "right":
            text_len = pymupdf.get_text_length(new_text, fontname=font_code, fontsize=fs)
            start_x = max(rect.x0, rect.x1 - text_len)
            
        page.insert_text(
            (start_x, baseline_y),
            new_text,
            fontsize=fs,
            fontname=font_code,
            color=text_color_rgb
        )
        
    doc.save(str(output_path), garbage=3, deflate=True)
    doc.close()
    
    return {
        "success": True,
        "mode": "overlay",
        "redaction_applied": apply_redaction,
        "exact_font_match": exact_match,
        "font_warning": warning,
        "new_text": new_text,
        "bbox": [rect.x0, rect.y0, rect.x1, rect.y1]
    }
