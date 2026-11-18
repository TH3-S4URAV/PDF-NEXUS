"""
PDF NEXUS - Text & Page Inspector Service
Extracts span-level text geometry, font attributes, images, and scans detection from PDF pages.
"""

import uuid
from pathlib import Path
from typing import List, Dict, Any, Tuple
import pymupdf
from PIL import Image

from app.schemas.pdf_schemas import (
    PageInspection, TextBlock, TextLine, TextSpan, ImageElement, DocumentMetadata
)
from app.services.font_matcher import clean_font_name, detect_font_style, color_to_hex
from app.core.config import settings

def inspect_document(doc_path: Path, doc_id: str, original_filename: str) -> DocumentMetadata:
    """
    Performs full deep inspection of a PDF document: pages, text spans,
    fonts, images, and generates thumbnail previews.
    """
    doc = pymupdf.open(doc_path)
    pages_data: List[PageInspection] = []
    
    try:
        page_count = len(doc)
        for pno in range(page_count):
            page = doc[pno]
            page_num = pno + 1
            rect = page.rect
            width = float(rect.width)
            height = float(rect.height)
            rotation = page.rotation
            
            # 1. Text blocks extraction (deep dictionary)
            text_dict = page.get_text("dict")
            blocks: List[TextBlock] = []
            total_text_length = 0
            
            for b_idx, block in enumerate(text_dict.get("blocks", [])):
                if block.get("type") == 0:  # text block
                    lines: List[TextLine] = []
                    block_text_parts = []
                    for line in block.get("lines", []):
                        spans: List[TextSpan] = []
                        for span in line.get("spans", []):
                            txt = span.get("text", "")
                            if not txt.strip():
                                continue
                            total_text_length += len(txt)
                            block_text_parts.append(txt)
                            
                            font_name = span.get("font", "Helvetica")
                            flags = span.get("flags", 0)
                            is_bold, is_italic = detect_font_style(font_name, flags)
                            
                            bbox = [round(float(c), 2) for c in span.get("bbox", [0, 0, 0, 0])]
                            origin = [round(float(c), 2) for c in span.get("origin", [bbox[0], bbox[3]])]
                            
                            spans.append(TextSpan(
                                text=txt,
                                bbox=bbox,
                                origin=origin,
                                font=clean_font_name(font_name),
                                size=round(float(span.get("size", 12.0)), 2),
                                color=color_to_hex(span.get("color", 0)),
                                flags=flags,
                                is_bold=is_bold,
                                is_italic=is_italic,
                                ascender=float(span.get("ascender", 0.0)),
                                descender=float(span.get("descender", 0.0))
                            ))
                        if spans:
                            lines.append(TextLine(
                                bbox=[round(float(c), 2) for c in line.get("bbox", [0, 0, 0, 0])],
                                spans=spans
                            ))
                    if lines:
                        block_id = f"p{page_num}_b{b_idx}_{uuid.uuid4().hex[:6]}"
                        blocks.append(TextBlock(
                            id=block_id,
                            bbox=[round(float(c), 2) for c in block.get("bbox", [0, 0, 0, 0])],
                            lines=lines,
                            text=" ".join(block_text_parts)
                        ))
            
            # 2. Extract Images on page
            images_list: List[ImageElement] = []
            raw_images = page.get_images(full=True)
            for img_info in raw_images:
                xref = img_info[0]
                # Try to get image bbox on page
                img_rects = page.get_image_rects(xref)
                for irect in img_rects:
                    images_list.append(ImageElement(
                        xref=xref,
                        bbox=[round(float(c), 2) for c in irect],
                        width=img_info[2],
                        height=img_info[3],
                        extension=img_info[8] or "png"
                    ))
            
            # 3. Detect Scanned Page
            # A page is considered scanned if it has very little or no extracted text (< 40 chars)
            # but has image(s) covering substantial area of the page.
            is_scanned = False
            if total_text_length < 40 and len(images_list) > 0:
                is_scanned = True
                
            # 4. Embedded Fonts
            page_fonts = []
            for f in doc.get_page_fonts(pno):
                page_fonts.append({
                    "xref": f[0],
                    "ext": f[1],
                    "type": f[2],
                    "basefont": f[3],
                    "name": f[4],
                    "encoding": f[5]
                })
                
            pages_data.append(PageInspection(
                page_number=page_num,
                width=width,
                height=height,
                rotation=rotation,
                blocks=blocks,
                images=images_list,
                embedded_fonts=page_fonts,
                is_scanned=is_scanned
            ))
            
        file_size = doc_path.stat().st_size
        return DocumentMetadata(
            id=doc_id,
            filename=original_filename,
            file_size=file_size,
            page_count=page_count,
            pages=pages_data,
            created_at=""
        )
    finally:
        doc.close()

def render_page_thumbnail(doc_path: Path, page_number: int, scale: float = 0.3) -> bytes:
    """Renders a single page as a PNG thumbnail byte buffer."""
    doc = pymupdf.open(doc_path)
    try:
        pno = max(0, min(page_number - 1, len(doc) - 1))
        page = doc[pno]
        matrix = pymupdf.Matrix(scale, scale)
        pix = page.get_pixmap(matrix=matrix, alpha=False)
        return pix.tobytes(output="png")
    finally:
        doc.close()
