"""
PDF NEXUS - Page Management Service
Reorder, rotate, delete, duplicate, crop, and insert blank pages.
"""

from pathlib import Path
from typing import List, Optional, Dict, Any
import pymupdf

def rotate_page(doc_path: Path, output_path: Path, page_number: int, angle: int = 90) -> Dict[str, Any]:
    """Rotates a specific page by angle (90, 180, 270)."""
    doc = pymupdf.open(doc_path)
    pno = page_number - 1
    page = doc[pno]
    new_rotation = (page.rotation + angle) % 360
    page.set_rotation(new_rotation)
    doc.save(str(output_path), garbage=3, deflate=True)
    doc.close()
    return {"success": True, "page_number": page_number, "new_rotation": new_rotation}

def delete_page(doc_path: Path, output_path: Path, page_number: int) -> Dict[str, Any]:
    """Deletes a page from the document."""
    doc = pymupdf.open(doc_path)
    if len(doc) <= 1:
        doc.close()
        raise ValueError("Cannot delete the only page in the document.")
    pno = page_number - 1
    doc.delete_page(pno)
    doc.save(str(output_path), garbage=3, deflate=True)
    total_pages = len(doc)
    doc.close()
    return {"success": True, "deleted_page": page_number, "total_pages": total_pages}

def duplicate_page(doc_path: Path, output_path: Path, page_number: int) -> Dict[str, Any]:
    """Duplicates a page immediately after itself."""
    doc = pymupdf.open(doc_path)
    pno = page_number - 1
    doc.copy_page(pno, pno + 1)
    doc.save(str(output_path), garbage=3, deflate=True)
    total_pages = len(doc)
    doc.close()
    return {"success": True, "duplicated_page": page_number, "total_pages": total_pages}

def reorder_pages(doc_path: Path, output_path: Path, page_order: List[int]) -> Dict[str, Any]:
    """
    Reorders pages based on 1-indexed list of page numbers, e.g. [3, 1, 2].
    """
    doc = pymupdf.open(doc_path)
    # 0-indexed order
    zero_indexed = [p - 1 for p in page_order if 1 <= p <= len(doc)]
    if len(zero_indexed) != len(doc):
        doc.close()
        raise ValueError("Page order list must contain all pages exactly once.")
        
    doc.select(zero_indexed)
    doc.save(str(output_path), garbage=3, deflate=True)
    doc.close()
    return {"success": True, "new_page_order": page_order}

def insert_blank_page(
    doc_path: Path,
    output_path: Path,
    position: int,  # 1-indexed insertion index
    width: float = 612.0,  # Standard Letter 8.5 x 11
    height: float = 792.0
) -> Dict[str, Any]:
    """Inserts a blank page at the given index."""
    doc = pymupdf.open(doc_path)
    pno = max(0, min(position - 1, len(doc)))
    doc.new_page(pno, width=width, height=height)
    doc.save(str(output_path), garbage=3, deflate=True)
    total_pages = len(doc)
    doc.close()
    return {"success": True, "inserted_at": position, "total_pages": total_pages}

def crop_page(doc_path: Path, output_path: Path, page_number: int, crop_rect: List[float]) -> Dict[str, Any]:
    """Crops a page to the specified rect [x0, y0, x1, y1]."""
    doc = pymupdf.open(doc_path)
    pno = page_number - 1
    page = doc[pno]
    rect = pymupdf.Rect(crop_rect)
    page.set_cropbox(rect)
    doc.save(str(output_path), garbage=3, deflate=True)
    doc.close()
    return {"success": True, "page_number": page_number, "crop_rect": crop_rect}
