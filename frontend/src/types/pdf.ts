/**
 * PDF NEXUS - Frontend TypeScript Interfaces
 */

export interface TextSpan {
  text: string;
  bbox: [number, number, number, number]; // [x0, y0, x1, y1] in PDF points
  origin: [number, number];
  font: string;
  size: number;
  color: string;
  flags: number;
  is_bold: boolean;
  is_italic: boolean;
  ascender?: number;
  descender?: number;
}

export interface TextLine {
  bbox: [number, number, number, number];
  spans: TextSpan[];
}

export interface TextBlock {
  id: string;
  bbox: [number, number, number, number];
  lines: TextLine[];
  text: string;
}

export interface ImageElement {
  xref: number;
  bbox: [number, number, number, number];
  width: number;
  height: number;
  extension: string;
}

export interface PageInspection {
  page_number: number;
  width: number;
  height: number;
  rotation: number;
  blocks: TextBlock[];
  images: ImageElement[];
  embedded_fonts: Array<{
    xref: number;
    basefont: string;
    type: string;
    encoding: string;
  }>;
  is_scanned: boolean;
}

export interface DocumentMetadata {
  id: string;
  filename: string;
  file_size: number;
  page_count: number;
  pages: PageInspection[];
  created_at: string;
}

export type EditorMode = 'direct' | 'overlay';

export type ActiveTool = 
  | 'select' 
  | 'text_edit' 
  | 'add_text' 
  | 'highlight' 
  | 'draw' 
  | 'shape' 
  | 'image' 
  | 'signature' 
  | 'eraser';

export type ShapeType = 'rect' | 'circle' | 'line';

export interface SelectedTextElement {
  pageNumber: number;
  blockId: string;
  spanIndex: number;
  lineIndex: number;
  span: TextSpan;
  currentText: string;
  fontFamily: string;
  fontSize: number;
  fontColor: string;
  isBold: boolean;
  isItalic: boolean;
  alignment: 'left' | 'center' | 'right' | 'justify';
  backgroundColor: string;
}

export interface UserProfile {
  id: string;
  email: string;
  full_name?: string;
}
