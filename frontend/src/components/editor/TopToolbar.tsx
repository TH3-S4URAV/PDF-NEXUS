import React, { useState } from 'react';
import { 
  ArrowLeft, FileText, Download, RotateCw, ZoomIn, ZoomOut, 
  Maximize2, Undo2, Redo2, Type, Image as ImageIcon, Highlighter, 
  PenTool, ShieldCheck, Cpu, Sparkles, Moon, Sun, 
  PlusSquare, Scissors, HelpCircle, Layers, MoreHorizontal, Settings
} from 'lucide-react';
import { ActiveTool, EditorMode } from '../../types/pdf';

interface TopToolbarProps {
  filename: string;
  activeTool: ActiveTool;
  setActiveTool: (tool: ActiveTool) => void;
  editorMode: EditorMode;
  setEditorMode: (mode: EditorMode) => void;
  zoom: number;
  setZoom: (zoom: number | ((prev: number) => number)) => void;
  onBackToDashboard: () => void;
  onExport: () => void;
  isExporting: boolean;
  onOpenOCR: () => void;
  onOpenAI: () => void;
  onOpenSignatures: () => void;
  onOpenUtilities: () => void;
  isDark: boolean;
  onToggleTheme: () => void;
}

export const TopToolbar: React.FC<TopToolbarProps> = ({
  filename,
  activeTool,
  setActiveTool,
  editorMode,
  setEditorMode,
  zoom,
  setZoom,
  onBackToDashboard,
  onExport,
  isExporting,
  onOpenOCR,
  onOpenAI,
  onOpenSignatures,
  onOpenUtilities,
  isDark,
  onToggleTheme
}) => {
  return (
    <header className="h-14 border-b border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 px-4 flex items-center justify-between select-none z-30 transition-colors">
      {/* Left: Back & Document Title */}
      <div className="flex items-center space-x-3 min-w-0">
        <button
          onClick={onBackToDashboard}
          className="p-1.5 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-600 dark:text-slate-300 transition"
          title="Back to Dashboard"
        >
          <ArrowLeft className="w-5 h-5" />
        </button>

        <div className="flex items-center space-x-2 min-w-0">
          <div className="w-7 h-7 rounded-lg bg-nexus-500 text-white flex items-center justify-center flex-shrink-0 shadow-sm">
            <FileText className="w-4 h-4" />
          </div>
          <span className="text-sm font-bold text-slate-800 dark:text-slate-100 truncate max-w-[180px] sm:max-w-xs" title={filename}>
            {filename}
          </span>
        </div>

        {/* Mode Selector Pill */}
        <div className="hidden lg:flex items-center bg-slate-100 dark:bg-slate-800 p-0.5 rounded-lg border border-slate-200 dark:border-slate-700 text-xs font-medium">
          <button
            onClick={() => setEditorMode('direct')}
            className={`px-2.5 py-1 rounded-md transition ${
              editorMode === 'direct'
                ? 'bg-white dark:bg-slate-900 text-nexus-600 dark:text-nexus-400 shadow-sm font-semibold'
                : 'text-slate-500 hover:text-slate-900 dark:hover:text-white'
            }`}
            title="Edit original text through native PDF structures"
          >
            Direct Edit Mode
          </button>
          <button
            onClick={() => setEditorMode('overlay')}
            className={`px-2.5 py-1 rounded-md transition ${
              editorMode === 'overlay'
                ? 'bg-white dark:bg-slate-900 text-nexus-600 dark:text-nexus-400 shadow-sm font-semibold'
                : 'text-slate-500 hover:text-slate-900 dark:hover:text-white'
            }`}
            title="Redacts original text genuinely and overlays matched typography"
          >
            Overlay Redact Mode
          </button>
        </div>
      </div>

      {/* Center: Editing Tools */}
      <div className="flex items-center space-x-1 sm:space-x-1.5">
        <button
          onClick={() => setActiveTool('select')}
          className={`px-2.5 py-1.5 rounded-lg text-xs font-semibold flex items-center space-x-1 transition ${
            activeTool === 'select'
              ? 'bg-nexus-50 dark:bg-nexus-950 text-nexus-600 dark:text-nexus-400 border border-nexus-200 dark:border-nexus-800'
              : 'hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-600 dark:text-slate-300'
          }`}
          title="Select & Inspect Elements (V)"
        >
          <span>Select</span>
        </button>

        <button
          onClick={() => setActiveTool('text_edit')}
          className={`px-2.5 py-1.5 rounded-lg text-xs font-semibold flex items-center space-x-1 transition ${
            activeTool === 'text_edit'
              ? 'bg-nexus-500 text-white shadow-sm'
              : 'hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-600 dark:text-slate-300'
          }`}
          title="Click to edit existing PDF text"
        >
          <Type className="w-3.5 h-3.5" />
          <span className="hidden md:inline">Edit Text</span>
        </button>

        <button
          onClick={() => setActiveTool('add_text')}
          className={`px-2.5 py-1.5 rounded-lg text-xs font-semibold flex items-center space-x-1 transition ${
            activeTool === 'add_text'
              ? 'bg-nexus-500 text-white shadow-sm'
              : 'hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-600 dark:text-slate-300'
          }`}
          title="Add new text box"
        >
          <PlusSquare className="w-3.5 h-3.5" />
          <span className="hidden md:inline">Add Text</span>
        </button>

        <button
          onClick={() => setActiveTool('highlight')}
          className={`p-1.5 rounded-lg transition ${
            activeTool === 'highlight'
              ? 'bg-amber-100 dark:bg-amber-950/60 text-amber-600 dark:text-amber-400 border border-amber-200 dark:border-amber-800'
              : 'hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-600 dark:text-slate-300'
          }`}
          title="Highlight Text"
        >
          <Highlighter className="w-4 h-4" />
        </button>

        <button
          onClick={() => setActiveTool('draw')}
          className={`p-1.5 rounded-lg transition ${
            activeTool === 'draw'
              ? 'bg-purple-100 dark:bg-purple-950/60 text-purple-600 dark:text-purple-400 border border-purple-200 dark:border-purple-800'
              : 'hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-600 dark:text-slate-300'
          }`}
          title="Freehand Pen / Markup"
        >
          <PenTool className="w-4 h-4" />
        </button>

        <div className="h-5 w-px bg-slate-200 dark:bg-slate-800 mx-1 hidden sm:block" />

        {/* Signature Button */}
        <button
          onClick={onOpenSignatures}
          className="px-2 py-1.5 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-600 dark:text-slate-300 text-xs font-semibold flex items-center space-x-1 transition"
          title="Draw or Apply Signatures"
        >
          <ShieldCheck className="w-3.5 h-3.5 text-emerald-500" />
          <span className="hidden lg:inline">Sign</span>
        </button>

        {/* OCR Button */}
        <button
          onClick={onOpenOCR}
          className="px-2 py-1.5 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-600 dark:text-slate-300 text-xs font-semibold flex items-center space-x-1 transition"
          title="OCR Engine (English & Hindi)"
        >
          <Cpu className="w-3.5 h-3.5 text-purple-500" />
          <span className="hidden lg:inline">OCR</span>
        </button>

        {/* AI Assistant Button */}
        <button
          onClick={onOpenAI}
          className="px-2.5 py-1 rounded-lg bg-gradient-to-r from-indigo-500 to-purple-600 text-white text-xs font-semibold flex items-center space-x-1 shadow-sm hover:opacity-90 transition"
          title="AI Document Intelligence"
        >
          <Sparkles className="w-3.5 h-3.5" />
          <span className="hidden lg:inline">AI</span>
        </button>

        {/* PDF Utilities Hub */}
        <button
          onClick={onOpenUtilities}
          className="px-2 py-1.5 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-600 dark:text-slate-300 text-xs font-semibold flex items-center space-x-1 transition"
          title="PDF Conversions & Utilities"
        >
          <Layers className="w-3.5 h-3.5 text-blue-500" />
          <span className="hidden xl:inline">Tools</span>
        </button>
      </div>

      {/* Right: Zoom, Theme & Export */}
      <div className="flex items-center space-x-2">
        {/* Zoom Controls */}
        <div className="hidden sm:flex items-center bg-slate-100 dark:bg-slate-800 rounded-lg p-0.5 border border-slate-200 dark:border-slate-700 text-xs">
          <button
            onClick={() => setZoom((z: number) => Math.max(0.4, Number((z - 0.15).toFixed(2))))}
            className="p-1 hover:bg-white dark:hover:bg-slate-900 rounded text-slate-600 dark:text-slate-300 transition"
            title="Zoom Out (Ctrl -)"
          >
            <ZoomOut className="w-3.5 h-3.5" />
          </button>
          <span className="px-1.5 font-semibold text-slate-700 dark:text-slate-300 min-w-[42px] text-center">
            {Math.round(zoom * 100)}%
          </span>
          <button
            onClick={() => setZoom((z: number) => Math.min(2.5, Number((z + 0.15).toFixed(2))))}
            className="p-1 hover:bg-white dark:hover:bg-slate-900 rounded text-slate-600 dark:text-slate-300 transition"
            title="Zoom In (Ctrl +)"
          >
            <ZoomIn className="w-3.5 h-3.5" />
          </button>
        </div>

        {/* Theme Toggle */}
        <button
          onClick={onToggleTheme}
          className="p-1.5 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-600 dark:text-slate-300 transition"
        >
          {isDark ? <Sun className="w-4 h-4 text-amber-400" /> : <Moon className="w-4 h-4" />}
        </button>

        {/* Save / Export Download Button */}
        <button
          onClick={onExport}
          disabled={isExporting}
          className="px-3.5 py-1.5 rounded-lg bg-nexus-600 hover:bg-nexus-700 text-white text-xs font-bold flex items-center space-x-1.5 shadow-md shadow-nexus-500/20 transition disabled:opacity-50"
        >
          {isExporting ? (
            <div className="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin" />
          ) : (
            <Download className="w-3.5 h-3.5" />
          )}
          <span>Download PDF</span>
        </button>
      </div>
    </header>
  );
};
