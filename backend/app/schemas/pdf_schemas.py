"""
PDF NEXUS - Schemas
Pydantic contracts for PDF Inspection, Direct Editing, Overlay Redaction, Utilities, and OCR.
"""

from typing import List, Optional, Literal, Dict, Any
from pydantic import BaseModel, Field

# --- Authentication Schemas ---
class UserRegister(BaseModel):
    email: str
    password: str
    full_name: Optional[str] = None

class UserLogin(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: Dict[str, Any]

# --- Document Inspection Schemas ---
class TextSpan(BaseModel):
    text: str
    bbox: List[float]  # [x0, y0, x1, y1] in points (72 DPI)
    origin: List[float]  # [x, y] text baseline point
    font: str
    size: float
    color: str  # Hex format '#000000'
    flags: int = 0
    is_bold: bool = False
    is_italic: bool = False
    ascender: float = 0.0
    descender: float = 0.0

class TextLine(BaseModel):
    bbox: List[float]
    spans: List[TextSpan]

class TextBlock(BaseModel):
    id: str
    bbox: List[float]
    lines: List[TextLine]
    text: str

class ImageElement(BaseModel):
    xref: int
    bbox: List[float]  # [x0, y0, x1, y1]
    width: int
    height: int
    extension: str

class PageInspection(BaseModel):
    page_number: int  # 1-indexed
    width: float
    height: float
    rotation: int
    blocks: List[TextBlock]
    images: List[ImageElement]
    embedded_fonts: List[Dict[str, Any]]
    is_scanned: bool = False

class DocumentMetadata(BaseModel):
    id: str
    filename: str
    file_size: int
    page_count: int
    pages: List[PageInspection]
    created_at: str

# --- Editing Schemas ---
class EditTextRequest(BaseModel):
    document_id: str
    page_number: int  # 1-indexed
    mode: Literal["direct", "overlay"] = "direct"
    target_bbox: List[float]  # [x0, y0, x1, y1] to redact/replace
    original_text: str
    new_text: str
    font_family: Optional[str] = None
    font_size: Optional[float] = None
    font_color: Optional[str] = "#000000"
    bold: Optional[bool] = False
    italic: Optional[bool] = False
    alignment: Optional[Literal["left", "center", "right", "justify"]] = "left"
    background_color: Optional[str] = "#ffffff"  # for redaction fill
    apply_redaction: bool = True

class AddTextRequest(BaseModel):
    document_id: str
    page_number: int
    text: str
    position: List[float]  # [x, y]
    font_family: Optional[str] = "Helvetica"
    font_size: float = 12.0
    font_color: str = "#000000"
    bold: bool = False
    italic: bool = False

class ImageOperationRequest(BaseModel):
    document_id: str
    page_number: int
    operation: Literal["add", "replace", "delete", "transform"]
    image_xref: Optional[int] = None
    position: Optional[List[float]] = None  # [x0, y0, x1, y1]
    image_data_base64: Optional[str] = None
    opacity: Optional[float] = 1.0

class AnnotationRequest(BaseModel):
    document_id: str
    page_number: int
    type: Literal["highlight", "underline", "strike", "rect", "circle", "line", "draw", "note"]
    rect: Optional[List[float]] = None
    points: Optional[List[List[float]]] = None  # for freehand drawing/lines
    color: str = "#FFD700"  # default gold highlight
    stroke_width: float = 2.0
    opacity: float = 0.5
    comment: Optional[str] = None

class SignatureRequest(BaseModel):
    document_id: str
    page_number: int
    signature_data_url: str  # Base64 PNG
    rect: List[float]  # [x0, y0, x1, y1]
    is_cryptographic: bool = False

class PageManagementRequest(BaseModel):
    document_id: str
    operation: Literal["rotate", "delete", "duplicate", "reorder", "insert_blank", "crop"]
    page_number: int
    target_index: Optional[int] = None
    rotation_angle: Optional[int] = 90  # 90, 180, 270
    crop_rect: Optional[List[float]] = None

# --- PDF Utilities Schemas ---
class MergeRequest(BaseModel):
    document_ids: List[str]

class SplitRequest(BaseModel):
    document_id: str
    page_ranges: str  # e.g., "1-3, 5, 7-10"

class CompressRequest(BaseModel):
    document_id: str
    level: Literal["low", "medium", "high"] = "medium"

class ProtectRequest(BaseModel):
    document_id: str
    password: str
    permissions_print: bool = True
    permissions_copy: bool = True

class UnlockRequest(BaseModel):
    document_id: str
    password: str

class WatermarkRequest(BaseModel):
    document_id: str
    text: str
    font_size: float = 40.0
    opacity: float = 0.3
    rotation: float = 45.0
    color: str = "#888888"

class PageNumberRequest(BaseModel):
    document_id: str
    position: Literal["bottom-center", "bottom-right", "top-right"] = "bottom-center"
    start_number: int = 1
    format_template: str = "Page {page} of {total}"

# --- OCR Schemas ---
class OCRRequest(BaseModel):
    document_id: str
    languages: List[str] = ["eng", "hin"]
    make_searchable: bool = True

# --- AI Schemas ---
class AISummaryRequest(BaseModel):
    document_id: str
    mode: Literal["summary", "bullet_points", "key_takeaways"] = "summary"

class AIQuestionRequest(BaseModel):
    document_id: str
    question: str

class AITranslateRequest(BaseModel):
    document_id: str
    target_language: str
    selected_text: Optional[str] = None

class ActionResponse(BaseModel):
    success: bool
    message: str
    document_id: Optional[str] = None
    export_url: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
