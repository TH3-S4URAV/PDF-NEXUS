"""
PDF NEXUS - AI Document Intelligence Service
Optional AI integration for summaries, translation, text explanations, and Q&A.
Operates gracefully with extractive fallback if no API key is provided.
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional
import pymupdf
from app.core.config import settings

def extract_document_text(doc_path: Path, max_pages: int = 20) -> str:
    """Extracts text from the first N pages of the PDF for AI analysis."""
    doc = pymupdf.open(doc_path)
    text_parts = []
    try:
        limit = min(len(doc), max_pages)
        for pno in range(limit):
            page_text = doc[pno].get_text()
            if page_text.strip():
                text_parts.append(f"--- Page {pno + 1} ---\n{page_text}")
    finally:
        doc.close()
    return "\n\n".join(text_parts)

def summarize_pdf(doc_path: Path, mode: str = "summary") -> Dict[str, Any]:
    """Generates an executive summary or key takeaways for the document."""
    text = extract_document_text(doc_path)
    if not text.strip():
        return {
            "success": False,
            "message": "Document contains no readable text (it may be a scanned image). Please run OCR first."
        }
        
    api_key = settings.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY")
    if api_key:
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-1.5-flash")
            prompt = (
                f"You are an expert document analyst in PDF NEXUS. Analyze the following document text and provide a "
                f"structured {mode} highlighting key themes, critical figures, and main conclusions.\n\n"
                f"DOCUMENT TEXT:\n{text[:20000]}"
            )
            response = model.generate_content(prompt)
            return {
                "success": True,
                "provider": "Gemini AI",
                "summary": response.text,
                "mode": mode
            }
        except Exception as e:
            # Fallback to local extractive summary
            pass
            
    # Local Extractive Rule-based Summary Fallback (Zero external dependencies)
    sentences = [s.strip() for s in text.replace("\n", " ").split(".") if len(s.strip()) > 30]
    top_sentences = sentences[:6] if len(sentences) >= 6 else sentences
    fallback_summary = " ".join(top_sentences) + ("." if top_sentences else "")
    
    return {
        "success": True,
        "provider": "Built-in Extractive Engine (AI Key not configured)",
        "summary": fallback_summary or "Document analyzed. Key information extracted from opening sections.",
        "mode": mode,
        "note": "To enable deep generative insights, configure GEMINI_API_KEY in your environment."
    }

def ask_document_question(doc_path: Path, question: str) -> Dict[str, Any]:
    """Answers user questions based on the PDF contents."""
    text = extract_document_text(doc_path)
    if not text.strip():
        return {"success": False, "answer": "Document contains no extractable text."}
        
    api_key = settings.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY")
    if api_key:
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-1.5-flash")
            prompt = (
                f"Based strictly on this document, answer the question accurately and concisely.\n\n"
                f"DOCUMENT:\n{text[:25000]}\n\n"
                f"QUESTION: {question}"
            )
            response = model.generate_content(prompt)
            return {"success": True, "answer": response.text, "provider": "Gemini AI"}
        except Exception:
            pass
            
    # Local Keyword Search Fallback
    keywords = [w.lower() for w in question.split() if len(w) > 3]
    matches = []
    for line in text.split("\n"):
        if any(k in line.lower() for k in keywords):
            matches.append(line.strip())
            if len(matches) >= 3:
                break
                
    local_answer = " ".join(matches) if matches else "No direct passage matched your question in the text."
    return {
        "success": True,
        "answer": local_answer,
        "provider": "Built-in Local Search (Configure GEMINI_API_KEY for conversational AI)"
    }

def translate_document_text(text: str, target_language: str) -> Dict[str, Any]:
    """Translates selected text or document excerpt to target language."""
    api_key = settings.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY")
    if api_key:
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-1.5-flash")
            prompt = f"Translate the following text accurately into {target_language}:\n\n{text}"
            res = model.generate_content(prompt)
            return {"success": True, "translated_text": res.text, "target_language": target_language}
        except Exception:
            pass
            
    return {
        "success": False,
        "message": "AI translation requires GEMINI_API_KEY to be configured in backend environment."
    }
