import React, { useState, useEffect, useCallback } from 'react';
import { Dashboard } from './components/dashboard/Dashboard';
import { TopToolbar } from './components/editor/TopToolbar';
import { LeftSidebar } from './components/editor/LeftSidebar';
import { RightSidebar } from './components/editor/RightSidebar';
import { CanvasViewport } from './components/editor/CanvasViewport';
import { SignatureModal } from './components/modals/SignatureModal';
import { OCRModal } from './components/modals/OCRModal';
import { AIModal } from './components/modals/AIModal';
import { UtilitiesModal } from './components/modals/UtilitiesModal';

import { 
  DocumentMetadata, PageInspection, ActiveTool, EditorMode, SelectedTextElement 
} from './types/pdf';
import { api } from './services/api';

export const App: React.FC = () => {
  // Theme state
  const [isDark, setIsDark] = useState<boolean>(() => {
    return localStorage.getItem('theme') === 'dark' || 
      window.matchMedia('(prefers-color-scheme: dark)').matches;
  });

  useEffect(() => {
    if (isDark) {
      document.documentElement.classList.add('dark');
      localStorage.setItem('theme', 'dark');
    } else {
      document.documentElement.classList.remove('dark');
      localStorage.setItem('theme', 'light');
    }
  }, [isDark]);

  const toggleTheme = () => setIsDark(prev => !prev);

  // View state: 'dashboard' or 'editor'
  const [view, setView] = useState<'dashboard' | 'editor'>('dashboard');
  const [documentId, setDocumentId] = useState<string | null>(null);
  const [docMetadata, setDocMetadata] = useState<DocumentMetadata | null>(null);

  // Editor states
  const [currentPage, setCurrentPage] = useState<number>(1);
  const [zoom, setZoom] = useState<number>(1.0);
  const [activeTool, setActiveTool] = useState<ActiveTool>('select');
  const [editorMode, setEditorMode] = useState<EditorMode>('direct');
  const [selectedText, setSelectedText] = useState<SelectedTextElement | null>(null);
  const [isApplyingText, setIsApplyingText] = useState<boolean>(false);
  const [isExporting, setIsExporting] = useState<boolean>(false);
  const [leftSidebarCollapsed, setLeftSidebarCollapsed] = useState<boolean>(false);
  const [rightSidebarCollapsed, setRightSidebarCollapsed] = useState<boolean>(false);

  // Modals state
  const [isSignaturesOpen, setIsSignaturesOpen] = useState(false);
  const [isOCROpen, setIsOCROpen] = useState(false);
  const [isAIOpen, setIsAIOpen] = useState(false);
  const [isUtilitiesOpen, setIsUtilitiesOpen] = useState(false);
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  const showToast = (msg: string) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 4000);
  };

  // Open Document from Dashboard
  const handleOpenDocument = async (docId: string) => {
    try {
      const res = await api.getDocument(docId);
      if (res.success && res.inspection) {
        setDocumentId(docId);
        setDocMetadata(res.inspection);
        setCurrentPage(1);
        setView('editor');
      }
    } catch (err: any) {
      showToast(`Failed to open document: ${err.message}`);
    }
  };

  // Reload document metadata from server after edits
  const reloadDocumentMetadata = async () => {
    if (!documentId) return;
    try {
      const res = await api.getDocument(documentId);
      if (res.success && res.inspection) {
        setDocMetadata(res.inspection);
      }
    } catch (err) {
      console.error(err);
    }
  };

  // Text Editing Apply
  const handleApplyTextEdit = async () => {
    if (!selectedText || !documentId) return;
    setIsApplyingText(true);

    try {
      const res = await api.editText({
        document_id: documentId,
        page_number: currentPage,
        mode: editorMode,
        target_bbox: selectedText.span.bbox,
        original_text: selectedText.span.text,
        new_text: selectedText.currentText,
        font_family: selectedText.fontFamily,
        font_size: selectedText.fontSize,
        font_color: selectedText.fontColor,
        bold: selectedText.isBold,
        italic: selectedText.isItalic,
        alignment: selectedText.alignment,
        background_color: selectedText.backgroundColor,
        apply_redaction: true,
      });

      if (res.success) {
        if (res.updated_inspection) {
          setDocMetadata(res.updated_inspection);
        }
        if (res.font_warning) {
          showToast(`Warning: ${res.font_warning}`);
        } else {
          showToast(`Text updated successfully via ${editorMode === 'direct' ? 'Mode A (Direct)' : 'Mode B (Overlay)'}!`);
        }
        setSelectedText(null);
      }
    } catch (err: any) {
      showToast(`Error: ${err.message}`);
    } finally {
      setIsApplyingText(false);
    }
  };

  // In-line Quick Text Edit (double click on canvas)
  const handleApplyQuickEdit = async (newText: string) => {
    if (!selectedText || !documentId) return;
    try {
      const res = await api.editText({
        document_id: documentId,
        page_number: currentPage,
        mode: editorMode,
        target_bbox: selectedText.span.bbox,
        original_text: selectedText.span.text,
        new_text: newText,
        font_family: selectedText.fontFamily,
        font_size: selectedText.fontSize,
        font_color: selectedText.fontColor,
        bold: selectedText.isBold,
        italic: selectedText.isItalic,
        alignment: selectedText.alignment,
        background_color: selectedText.backgroundColor,
        apply_redaction: true,
      });
      if (res.success && res.updated_inspection) {
        setDocMetadata(res.updated_inspection);
        showToast('Text updated!');
      }
    } catch (err: any) {
      showToast(`Edit failed: ${err.message}`);
    }
  };

  // Add New Text Box
  const handleAddNewText = async (x: number, y: number) => {
    if (!documentId) return;
    try {
      const res = await api.addText({
        document_id: documentId,
        page_number: currentPage,
        text: 'New Text',
        position: [x, y],
        font_family: 'Helvetica',
        font_size: 14.0,
        font_color: '#000000',
        bold: false,
        italic: false,
      });
      if (res.success && res.updated_inspection) {
        setDocMetadata(res.updated_inspection);
        showToast('New text element added!');
      }
    } catch (err: any) {
      showToast(`Add text failed: ${err.message}`);
    }
  };

  // Page Operations
  const handlePageOperation = async (
    op: 'rotate' | 'duplicate' | 'delete' | 'insert_blank',
    pageNum: number
  ) => {
    if (!documentId) return;
    try {
      const res = await api.handlePage({
        document_id: documentId,
        operation: op,
        page_number: pageNum,
        rotation_angle: 90,
      });
      if (res.success && res.updated_inspection) {
        setDocMetadata(res.updated_inspection);
        if (op === 'delete' && currentPage > res.updated_inspection.pages.length) {
          setCurrentPage(res.updated_inspection.pages.length);
        }
        showToast(`Page operation '${op}' executed!`);
      }
    } catch (err: any) {
      showToast(`Page operation failed: ${err.message}`);
    }
  };

  // Freehand drawing / vector annotations
  const handleAddAnnotation = async (
    type: string,
    rect?: number[],
    points?: number[][]
  ) => {
    if (!documentId) return;
    try {
      await api.handleAnnotation({
        document_id: documentId,
        page_number: currentPage,
        type: type,
        rect: rect,
        points: points,
        color: '#7c3aed',
        stroke_width: 2.5,
      });
      await reloadDocumentMetadata();
      showToast('Annotation saved!');
    } catch (err: any) {
      showToast(`Annotation failed: ${err.message}`);
    }
  };

  // Signature Apply
  const handleApplySignature = async (dataUrl: string, isCryptographic: boolean) => {
    if (!documentId) return;
    try {
      await api.handleSignature({
        document_id: documentId,
        page_number: currentPage,
        signature_data_url: dataUrl,
        rect: [200, 650, 350, 720],
        is_cryptographic: isCryptographic,
      });
      await reloadDocumentMetadata();
      showToast(isCryptographic ? 'Cryptographic digital signature applied!' : 'Signature stamped!');
    } catch (err: any) {
      showToast(`Signature failed: ${err.message}`);
    }
  };

  // Export & Download Edited PDF
  const handleExport = () => {
    if (!documentId) return;
    setIsExporting(true);
    const exportUrl = api.getExportUrl(documentId);
    const a = document.createElement('a');
    a.href = exportUrl;
    a.download = `PDF_NEXUS_Edited_${docMetadata?.filename || 'document.pdf'}`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    setTimeout(() => setIsExporting(false), 1000);
    showToast('Download initiated!');
  };

  // Keyboard Shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 's') {
        e.preventDefault();
        handleExport();
      }
      if (e.key === 'Escape') {
        setSelectedText(null);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [documentId, docMetadata]);

  const currentPageData = docMetadata?.pages.find(p => p.page_number === currentPage) || null;

  return (
    <div className="h-screen w-screen flex flex-col overflow-hidden bg-slate-50 dark:bg-slate-950 text-slate-800 dark:text-slate-100 font-sans transition-colors">
      {/* Toast Notification */}
      {toastMessage && (
        <div className="fixed bottom-6 right-6 z-50 px-4 py-2.5 rounded-xl bg-slate-900 text-white text-xs font-semibold shadow-2xl border border-slate-700 animate-bounce">
          {toastMessage}
        </div>
      )}

      {view === 'dashboard' ? (
        <Dashboard
          onOpenDocument={handleOpenDocument}
          isDark={isDark}
          onToggleTheme={toggleTheme}
        />
      ) : (
        /* 3-Panel Editor Workspace Layout */
        <div className="flex-1 flex flex-col h-full overflow-hidden">
          {/* Top Bar */}
          <TopToolbar
            filename={docMetadata?.filename || 'Document.pdf'}
            activeTool={activeTool}
            setActiveTool={setActiveTool}
            editorMode={editorMode}
            setEditorMode={setEditorMode}
            zoom={zoom}
            setZoom={setZoom}
            onBackToDashboard={() => setView('dashboard')}
            onExport={handleExport}
            isExporting={isExporting}
            onOpenOCR={() => setIsOCROpen(true)}
            onOpenAI={() => setIsAIOpen(true)}
            onOpenSignatures={() => setIsSignaturesOpen(true)}
            onOpenUtilities={() => setIsUtilitiesOpen(true)}
            isDark={isDark}
            onToggleTheme={toggleTheme}
          />

          {/* Center + Left + Right Panes */}
          <div className="flex-1 flex overflow-hidden">
            {/* Left Sidebar: Pages & Thumbnails */}
            {documentId && docMetadata && (
              <LeftSidebar
                documentId={documentId}
                pages={docMetadata.pages}
                currentPage={currentPage}
                onSelectPage={setCurrentPage}
                onPageOperation={handlePageOperation}
                isCollapsed={leftSidebarCollapsed}
                onToggleCollapse={() => setLeftSidebarCollapsed(!leftSidebarCollapsed)}
              />
            )}

            {/* Center Canvas Viewport */}
            {documentId && (
              <CanvasViewport
                documentId={documentId}
                currentPage={currentPage}
                zoom={zoom}
                pageData={currentPageData}
                activeTool={activeTool}
                editorMode={editorMode}
                selectedText={selectedText}
                onSelectText={(el) => {
                  setSelectedText(el);
                  setRightSidebarCollapsed(false);
                }}
                onAddNewText={handleAddNewText}
                onAddAnnotation={handleAddAnnotation}
                onApplyQuickEdit={handleApplyQuickEdit}
              />
            )}

            {/* Right Sidebar: Properties & Inspector */}
            <RightSidebar
              selectedText={selectedText}
              onUpdateSelectedText={setSelectedText}
              onApplyTextEdit={handleApplyTextEdit}
              onCancelSelection={() => setSelectedText(null)}
              isApplying={isApplyingText}
              editorMode={editorMode}
              currentPageData={currentPageData}
              isCollapsed={rightSidebarCollapsed}
            />
          </div>
        </div>
      )}

      {/* Interactive Modals */}
      <SignatureModal
        isOpen={isSignaturesOpen}
        onClose={() => setIsSignaturesOpen(false)}
        onApplySignature={handleApplySignature}
      />

      {documentId && (
        <>
          <OCRModal
            isOpen={isOCROpen}
            onClose={() => setIsOCROpen(false)}
            documentId={documentId}
          />
          <AIModal
            isOpen={isAIOpen}
            onClose={() => setIsAIOpen(false)}
            documentId={documentId}
          />
          <UtilitiesModal
            isOpen={isUtilitiesOpen}
            onClose={() => setIsUtilitiesOpen(false)}
            documentId={documentId}
          />
        </>
      )}
    </div>
  );
};

export default App;
