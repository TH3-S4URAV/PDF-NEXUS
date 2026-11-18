"""
PDF NEXUS - AI Document Assistant API
Endpoints for document summarization, Q&A, and translation.
"""

from fastapi import APIRouter, HTTPException
from app.core.config import settings
from app.core.database import get_db
from app.schemas.pdf_schemas import AISummaryRequest, AIQuestionRequest, AITranslateRequest
from app.services.ai_service import summarize_pdf, ask_document_question, translate_document_text

router = APIRouter(prefix="/ai", tags=["AI Assistant"])

def get_file(doc_id: str):
    with get_db() as conn:
        row = conn.execute("SELECT stored_filename FROM documents WHERE id = ? AND is_deleted = 0", (doc_id,)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Document not found.")
    p = settings.UPLOADS_PATH / row["stored_filename"]
    if not p.exists():
        raise HTTPException(status_code=404, detail="File missing.")
    return p

@router.post("/summarize")
def summarize(req: AISummaryRequest):
    """Generates executive summary or bullet points."""
    src = get_file(req.document_id)
    return summarize_pdf(src, mode=req.mode)

@router.post("/ask")
def ask_question(req: AIQuestionRequest):
    """Answers questions based on document text."""
    src = get_file(req.document_id)
    return ask_document_question(src, req.question)

@router.post("/translate")
def translate(req: AITranslateRequest):
    """Translates selected excerpt or document text."""
    if not req.selected_text:
        src = get_file(req.document_id)
        from app.services.ai_service import extract_document_text
        text_to_translate = extract_document_text(src, max_pages=3)
    else:
        text_to_translate = req.selected_text
        
    return translate_document_text(text_to_translate, req.target_language)
