/**
 * PDF NEXUS - API Service Client
 */

import { DocumentMetadata, PageInspection } from '../types/pdf';

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api';

export const api = {
  // Document Operations
  async uploadDocument(file: File): Promise<{
    success: boolean;
    document_id: string;
    filename: string;
    page_count: number;
    metadata: DocumentMetadata;
  }> {
    const formData = new FormData();
    formData.append('file', file);
    const res = await fetch(`${API_BASE}/documents/upload`, {
      method: 'POST',
      body: formData,
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Upload failed' }));
      throw new Error(err.detail || 'Upload failed');
    }
    return res.json();
  },

  async getDocument(docId: string): Promise<{
    success: boolean;
    document: any;
    inspection: DocumentMetadata;
  }> {
    const res = await fetch(`${API_BASE}/documents/${docId}`);
    if (!res.ok) throw new Error('Failed to load document');
    return res.json();
  },

  async listDocuments(): Promise<Array<{
    id: string;
    filename: string;
    file_size: number;
    page_count: number;
    created_at: string;
  }>> {
    const res = await fetch(`${API_BASE}/documents`);
    if (!res.ok) return [];
    return res.json();
  },

  getPDFFileUrl(docId: string): string {
    return `${API_BASE}/documents/${docId}/file`;
  },

  getThumbnailUrl(docId: string, pageNum: number): string {
    return `${API_BASE}/documents/${docId}/thumbnail/${pageNum}`;
  },

  getExportUrl(docId: string): string {
    return `${API_BASE}/pdf/export/${docId}`;
  },

  // Existing Text Editing (Direct or Overlay Mode)
  async editText(payload: {
    document_id: string;
    page_number: number;
    mode: 'direct' | 'overlay';
    target_bbox: number[];
    original_text: string;
    new_text: string;
    font_family?: string;
    font_size?: number;
    font_color?: string;
    bold?: boolean;
    italic?: boolean;
    alignment?: string;
    background_color?: string;
    apply_redaction?: boolean;
  }): Promise<{
    success: boolean;
    mode: string;
    updated_inspection: DocumentMetadata;
    font_warning?: string;
  }> {
    const res = await fetch(`${API_BASE}/pdf/edit-text`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Failed to edit text' }));
      throw new Error(err.detail || 'Failed to edit text');
    }
    return res.json();
  },

  // Add New Text Box
  async addText(payload: {
    document_id: string;
    page_number: number;
    text: string;
    position: number[];
    font_family?: string;
    font_size?: number;
    font_color?: string;
    bold?: boolean;
    italic?: boolean;
  }) {
    const res = await fetch(`${API_BASE}/pdf/add-text`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (!res.ok) throw new Error('Failed to add text');
    return res.json();
  },

  // Images
  async handleImage(payload: {
    document_id: string;
    page_number: number;
    operation: 'add' | 'replace' | 'delete';
    image_xref?: number;
    position?: number[];
    image_data_base64?: string;
    opacity?: number;
  }) {
    const res = await fetch(`${API_BASE}/pdf/images`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (!res.ok) throw new Error('Image operation failed');
    return res.json();
  },

  // Annotations
  async handleAnnotation(payload: {
    document_id: string;
    page_number: number;
    type: string;
    rect?: number[];
    points?: number[][];
    color?: string;
    stroke_width?: number;
    opacity?: number;
    comment?: string;
  }) {
    const res = await fetch(`${API_BASE}/pdf/annotations`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (!res.ok) throw new Error('Annotation failed');
    return res.json();
  },

  // Signatures
  async handleSignature(payload: {
    document_id: string;
    page_number: number;
    signature_data_url: string;
    rect: number[];
    is_cryptographic?: boolean;
  }) {
    const res = await fetch(`${API_BASE}/pdf/signatures`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (!res.ok) throw new Error('Signature application failed');
    return res.json();
  },

  // Page Operations
  async handlePage(payload: {
    document_id: string;
    operation: 'rotate' | 'delete' | 'duplicate' | 'insert_blank' | 'crop';
    page_number: number;
    rotation_angle?: number;
    crop_rect?: number[];
  }) {
    const res = await fetch(`${API_BASE}/pdf/pages`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Page operation failed' }));
      throw new Error(err.detail || 'Page operation failed');
    }
    return res.json();
  },

  // Utilities
  async compressPDF(docId: string, level: string = 'medium') {
    const res = await fetch(`${API_BASE}/pdf/utils/compress`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ document_id: docId, level }),
    });
    return res.json();
  },

  async protectPDF(docId: string, password: string) {
    const res = await fetch(`${API_BASE}/pdf/utils/protect`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ document_id: docId, password }),
    });
    return res.json();
  },

  async watermarkPDF(docId: string, text: string) {
    const res = await fetch(`${API_BASE}/pdf/utils/watermark`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ document_id: docId, text, font_size: 40.0, opacity: 0.3, rotation: 45.0, color: '#FF0000' }),
    });
    return res.json();
  },

  async addPageNumbers(docId: string, position: string = 'bottom-center') {
    const res = await fetch(`${API_BASE}/pdf/utils/page-numbers`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ document_id: docId, position, start_number: 1, format_template: 'Page {page} of {total}' }),
    });
    return res.json();
  },

  async convertDoc(docId: string, targetFormat: 'docx' | 'excel' | 'pptx' | 'images') {
    const endpoint = targetFormat === 'docx' ? 'pdf-to-docx'
      : targetFormat === 'excel' ? 'pdf-to-excel'
      : targetFormat === 'pptx' ? 'pdf-to-pptx'
      : 'pdf-to-images';
    const res = await fetch(`${API_BASE}/pdf/utils/convert/${endpoint}/${docId}`, { method: 'POST' });
    return res.json();
  },

  // OCR
  async runOCR(docId: string, languages: string[] = ['eng', 'hin']) {
    const res = await fetch(`${API_BASE}/pdf/ocr`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ document_id: docId, languages, make_searchable: true }),
    });
    return res.json();
  },

  // AI Assistant
  async summarizeDoc(docId: string, mode: string = 'summary') {
    const res = await fetch(`${API_BASE}/ai/summarize`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ document_id: docId, mode }),
    });
    return res.json();
  },

  async askAI(docId: string, question: string) {
    const res = await fetch(`${API_BASE}/ai/ask`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ document_id: docId, question }),
    });
    return res.json();
  },

  async translateDoc(docId: string, targetLanguage: string, selectedText?: string) {
    const res = await fetch(`${API_BASE}/ai/translate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ document_id: docId, target_language: targetLanguage, selected_text: selectedText }),
    });
    return res.json();
  }
};
