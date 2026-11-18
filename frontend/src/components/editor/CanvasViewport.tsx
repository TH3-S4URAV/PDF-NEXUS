import React, { useEffect, useRef, useState, useCallback } from 'react';
import * as pdfjsLib from 'pdfjs-dist';
import { 
  PageInspection, SelectedTextElement, ActiveTool, EditorMode, TextSpan, TextBlock 
} from '../../types/pdf';
import { api } from '../../services/api';

// Configure PDF.js worker
pdfjsLib.GlobalWorkerOptions.workerSrc = new URL(
  'pdfjs-dist/build/pdf.worker.min.mjs',
  import.meta.url
).toString();

interface CanvasViewportProps {
  documentId: string;
  currentPage: number;
  zoom: number;
  pageData: PageInspection | null;
  activeTool: ActiveTool;
  editorMode: EditorMode;
  selectedText: SelectedTextElement | null;
  onSelectText: (element: SelectedTextElement) => void;
  onAddNewText: (x: number, y: number) => void;
  onAddAnnotation: (type: string, rect?: number[], points?: number[][]) => void;
  onApplyQuickEdit: (newText: string) => void;
}

export const CanvasViewport: React.FC<CanvasViewportProps> = ({
  documentId,
  currentPage,
  zoom,
  pageData,
  activeTool,
  editorMode,
  selectedText,
  onSelectText,
  onAddNewText,
  onAddAnnotation,
  onApplyQuickEdit
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [pdfDoc, setPdfDoc] = useState<any>(null);
  const [isRendering, setIsRendering] = useState(false);
  const [viewportDims, setViewportDims] = useState<{ width: number; height: number }>({ width: 612, height: 792 });
  const [hoveredSpan, setHoveredSpan] = useState<TextSpan | null>(null);
  const [hoveredBlockId, setHoveredBlockId] = useState<string | null>(null);
  const [inlineEditing, setInlineEditing] = useState(false);
  const [inlineEditText, setInlineEditText] = useState('');

  // Freehand drawing state
  const [isDrawing, setIsDrawing] = useState(false);
  const [currentStroke, setCurrentStroke] = useState<number[][]>([]);

  // Load PDF Document
  useEffect(() => {
    let isCancelled = false;
    const loadPdf = async () => {
      try {
        const fileUrl = api.getPDFFileUrl(documentId);
        const loadingTask = pdfjsLib.getDocument({
          url: fileUrl,
          cMapUrl: 'https://cdn.jsdelivr.net/npm/pdfjs-dist@4.10.38/cmaps/',
          cMapPacked: true,
        });
        const doc = await loadingTask.promise;
        if (!isCancelled) {
          setPdfDoc(doc);
        }
      } catch (err) {
        console.error('Error loading PDF document:', err);
      }
    };
    loadPdf();
    return () => { isCancelled = true; };
  }, [documentId]);

  // Render Page to Canvas
  useEffect(() => {
    if (!pdfDoc || !canvasRef.current) return;
    let renderTask: any = null;

    const render = async () => {
      try {
        setIsRendering(true);
        const page = await pdfDoc.getPage(currentPage);
        const viewport = page.getViewport({ scale: zoom });

        const canvas = canvasRef.current;
        if (!canvas) return;
        const ctx = canvas.getContext('2d', { alpha: false });
        if (!ctx) return;

        // Support High-DPI screens
        const dpr = window.devicePixelRatio || 1;
        canvas.width = Math.floor(viewport.width * dpr);
        canvas.height = Math.floor(viewport.height * dpr);
        canvas.style.width = `${Math.floor(viewport.width)}px`;
        canvas.style.height = `${Math.floor(viewport.height)}px`;

        ctx.setTransform(dpr, 0, 0, dpr, 0, 0);

        setViewportDims({ width: viewport.width, height: viewport.height });

        renderTask = page.render({
          canvasContext: ctx,
          viewport: viewport,
        });
        await renderTask.promise;
      } catch (err: any) {
        if (err?.name !== 'RenderingCancelledException') {
          console.error('Render error:', err);
        }
      } finally {
        setIsRendering(false);
      }
    };

    render();
    return () => {
      if (renderTask) {
        renderTask.cancel();
      }
    };
  }, [pdfDoc, currentPage, zoom]);

  // Scale factor from PDF coordinate points to rendered screen pixels
  const pdfToScreenScale = pageData ? viewportDims.width / pageData.width : zoom;

  // Handle canvas click for add_text or annotations
  const handleCanvasContainerClick = (e: React.MouseEvent<HTMLDivElement>) => {
    if (activeTool === 'add_text') {
      const rect = e.currentTarget.getBoundingClientRect();
      const clickX = (e.clientX - rect.left) / pdfToScreenScale;
      const clickY = (e.clientY - rect.top) / pdfToScreenScale;
      onAddNewText(clickX, clickY);
    }
  };

  // Freehand Drawing Event Handlers
  const handleMouseDown = (e: React.MouseEvent<HTMLDivElement>) => {
    if (activeTool !== 'draw') return;
    const rect = e.currentTarget.getBoundingClientRect();
    const x = (e.clientX - rect.left) / pdfToScreenScale;
    const y = (e.clientY - rect.top) / pdfToScreenScale;
    setIsDrawing(true);
    setCurrentStroke([[x, y]]);
  };

  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!isDrawing || activeTool !== 'draw') return;
    const rect = e.currentTarget.getBoundingClientRect();
    const x = (e.clientX - rect.left) / pdfToScreenScale;
    const y = (e.clientY - rect.top) / pdfToScreenScale;
    setCurrentStroke(prev => [...prev, [x, y]]);
  };

  const handleMouseUp = () => {
    if (!isDrawing || activeTool !== 'draw') return;
    setIsDrawing(false);
    if (currentStroke.length > 1) {
      onAddAnnotation('draw', undefined, currentStroke);
    }
    setCurrentStroke([]);
  };

  return (
    <div 
      ref={containerRef}
      className="flex-1 overflow-auto bg-slate-100 dark:bg-slate-950 p-6 flex justify-center items-start transition-colors select-none"
    >
      <div 
        onClick={handleCanvasContainerClick}
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        style={{ width: viewportDims.width, height: viewportDims.height }}
        className="relative bg-white shadow-2xl rounded-sm transition-all flex-shrink-0 cursor-default"
      >
        {/* PDF Canvas Rendering Layer */}
        <canvas ref={canvasRef} className="block w-full h-full" />

        {/* Loading Spinner Indicator */}
        {isRendering && (
          <div className="absolute top-3 right-3 px-2 py-1 bg-black/60 backdrop-blur rounded text-[11px] text-white flex items-center space-x-1.5 z-30">
            <div className="w-2.5 h-2.5 border-2 border-white border-t-transparent rounded-full animate-spin" />
            <span>Rendering</span>
          </div>
        )}

        {/* Freehand Drawing Preview SVG */}
        {isDrawing && currentStroke.length > 1 && (
          <svg className="absolute inset-0 w-full h-full pointer-events-none z-20">
            <polyline
              points={currentStroke.map(p => `${p[0] * pdfToScreenScale},${p[1] * pdfToScreenScale}`).join(' ')}
              fill="none"
              stroke="#7c3aed"
              strokeWidth={3 * zoom}
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        )}

        {/* Vector Text Selection & Interactive Overlay Layer */}
        {pageData && (
          <div className="absolute inset-0 pointer-events-none z-10">
            {pageData.blocks.map((block) => (
              <React.Fragment key={block.id}>
                {block.lines.map((line, lineIdx) => (
                  <React.Fragment key={`${block.id}_l${lineIdx}`}>
                    {line.spans.map((span, spanIdx) => {
                      const isHovered = hoveredSpan === span;
                      const isSelected = selectedText?.span === span;

                      const left = span.bbox[0] * pdfToScreenScale;
                      const top = span.bbox[1] * pdfToScreenScale;
                      const width = Math.max(12, (span.bbox[2] - span.bbox[0]) * pdfToScreenScale);
                      const height = Math.max(10, (span.bbox[3] - span.bbox[1]) * pdfToScreenScale);

                      return (
                        <div
                          key={`${block.id}_s${spanIdx}`}
                          style={{
                            left: `${left}px`,
                            top: `${top}px`,
                            width: `${width}px`,
                            height: `${height}px`,
                          }}
                          onMouseEnter={() => {
                            setHoveredSpan(span);
                            setHoveredBlockId(block.id);
                          }}
                          onMouseLeave={() => {
                            if (hoveredSpan === span) setHoveredSpan(null);
                          }}
                          onClick={(e) => {
                            e.stopPropagation();
                            onSelectText({
                              pageNumber: currentPage,
                              blockId: block.id,
                              spanIndex: spanIdx,
                              lineIndex: lineIdx,
                              span: span,
                              currentText: span.text,
                              fontFamily: span.font,
                              fontSize: span.size,
                              fontColor: span.color,
                              isBold: span.is_bold,
                              isItalic: span.is_italic,
                              alignment: 'left',
                              backgroundColor: '#ffffff'
                            });
                          }}
                          onDoubleClick={(e) => {
                            e.stopPropagation();
                            setInlineEditing(true);
                            setInlineEditText(span.text);
                          }}
                          className={`absolute pointer-events-auto cursor-text rounded-[2px] transition-all duration-75 group ${
                            isSelected
                              ? 'ring-2 ring-nexus-500 bg-nexus-500/20 shadow-sm'
                              : isHovered
                              ? 'ring-1 ring-nexus-400 bg-nexus-400/10'
                              : activeTool === 'text_edit'
                              ? 'hover:ring-1 hover:ring-nexus-400/70 hover:bg-nexus-400/5'
                              : ''
                          }`}
                          title={`Click to edit: "${span.text}" (${span.font}, ${span.size}pt)`}
                        >
                          {/* Inline Double-Click Quick Editor */}
                          {isSelected && inlineEditing && (
                            <div className="absolute -top-1 -left-1 z-50 flex items-center shadow-xl rounded-lg bg-white dark:bg-slate-900 border border-nexus-500 p-1 min-w-[200px]">
                              <input
                                autoFocus
                                type="text"
                                value={inlineEditText}
                                onChange={(e) => setInlineEditText(e.target.value)}
                                onKeyDown={(e) => {
                                  if (e.key === 'Enter') {
                                    onApplyQuickEdit(inlineEditText);
                                    setInlineEditing(false);
                                  } else if (e.key === 'Escape') {
                                    setInlineEditing(false);
                                  }
                                }}
                                className="flex-1 text-xs px-2 py-1 rounded bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-white border-none focus:outline-none font-mono"
                              />
                              <button
                                onClick={() => {
                                  onApplyQuickEdit(inlineEditText);
                                  setInlineEditing(false);
                                }}
                                className="ml-1 px-2 py-1 bg-nexus-600 text-white rounded text-[11px] font-bold hover:bg-nexus-700"
                              >
                                Save
                              </button>
                            </div>
                          )}

                          {/* Hover Tooltip showing Font Name and Size */}
                          {isHovered && !isSelected && (
                            <div className="absolute -top-6 left-0 bg-slate-900 text-white text-[10px] font-sans px-1.5 py-0.5 rounded shadow whitespace-nowrap pointer-events-none z-30">
                              {span.font} • {span.size}pt
                            </div>
                          )}
                        </div>
                      );
                    })}
                  </React.Fragment>
                ))}
              </React.Fragment>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
