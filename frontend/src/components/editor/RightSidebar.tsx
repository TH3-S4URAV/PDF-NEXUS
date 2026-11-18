import React, { useState, useEffect } from 'react';
import { 
  Type, Bold, Italic, AlignLeft, AlignCenter, AlignRight, AlignJustify, 
  Palette, AlertCircle, Check, X, ShieldAlert, Sparkles, Layers, Sliders
} from 'lucide-react';
import { SelectedTextElement, EditorMode, PageInspection } from '../../types/pdf';

interface RightSidebarProps {
  selectedText: SelectedTextElement | null;
  onUpdateSelectedText: (updated: SelectedTextElement) => void;
  onApplyTextEdit: () => void;
  onCancelSelection: () => void;
  isApplying: boolean;
  editorMode: EditorMode;
  currentPageData: PageInspection | null;
  isCollapsed: boolean;
}

const POPULAR_FONTS = [
  'Helvetica',
  'Arial',
  'Times New Roman',
  'Courier',
  'Calibri',
  'Georgia',
  'Roboto',
  'Open Sans'
];

const PRESET_COLORS = [
  '#000000',
  '#1e293b',
  '#dc2626',
  '#ea580c',
  '#16a34a',
  '#2563eb',
  '#7c3aed',
  '#ffffff'
];

export const RightSidebar: React.FC<RightSidebarProps> = ({
  selectedText,
  onUpdateSelectedText,
  onApplyTextEdit,
  onCancelSelection,
  isApplying,
  editorMode,
  currentPageData,
  isCollapsed
}) => {
  if (isCollapsed) return null;

  return (
    <aside className="w-80 border-l border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 flex flex-col select-none transition-colors z-20">
      {/* Header */}
      <div className="h-12 border-b border-slate-200 dark:border-slate-800 px-4 flex items-center justify-between">
        <span className="text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider flex items-center">
          <Sliders className="w-3.5 h-3.5 mr-1.5 text-nexus-500" />
          Properties Inspector
        </span>
        {selectedText && (
          <button
            onClick={onCancelSelection}
            className="p-1 hover:bg-slate-100 dark:hover:bg-slate-800 rounded text-slate-400 hover:text-slate-600"
            title="Deselect"
          >
            <X className="w-4 h-4" />
          </button>
        )}
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-6">
        {selectedText ? (
          /* Text Properties Section */
          <div className="space-y-5">
            {/* Mode Indicator Banner */}
            <div className={`p-3 rounded-xl border text-xs ${
              editorMode === 'direct'
                ? 'bg-blue-50/60 dark:bg-blue-950/40 border-blue-200 dark:border-blue-800 text-blue-700 dark:text-blue-300'
                : 'bg-purple-50/60 dark:bg-purple-950/40 border-purple-200 dark:border-purple-800 text-purple-700 dark:text-purple-300'
            }`}>
              <div className="flex items-center space-x-1.5 font-bold mb-1">
                <Sparkles className="w-3.5 h-3.5" />
                <span>Editing Mode: {editorMode === 'direct' ? 'Mode A (Direct Stream)' : 'Mode B (True Redact & Overlay)'}</span>
              </div>
              <p className="text-[11px] opacity-90">
                {editorMode === 'direct' 
                  ? 'Rewrites text in the underlying PDF content stream directly.' 
                  : 'Physically excises sensitive text and renders styled typography at exact coordinates.'}
              </p>
            </div>

            {/* Editable Content */}
            <div className="space-y-1.5">
              <label className="text-xs font-bold text-slate-700 dark:text-slate-300">
                Text Content
              </label>
              <textarea
                value={selectedText.currentText}
                onChange={(e) => onUpdateSelectedText({ ...selectedText, currentText: e.target.value })}
                rows={3}
                className="w-full text-sm p-3 rounded-xl border border-slate-300 dark:border-slate-700 bg-slate-50 dark:bg-slate-800/80 text-slate-900 dark:text-white focus:ring-2 focus:ring-nexus-500 focus:outline-none transition resize-none font-mono"
                placeholder="Edit text..."
              />
            </div>

            {/* Typography Controls */}
            <div className="space-y-4 pt-2 border-t border-slate-200 dark:border-slate-800">
              {/* Font Family */}
              <div className="space-y-1">
                <label className="text-xs font-semibold text-slate-600 dark:text-slate-400">
                  Font Family
                </label>
                <select
                  value={selectedText.fontFamily}
                  onChange={(e) => onUpdateSelectedText({ ...selectedText, fontFamily: e.target.value })}
                  className="w-full text-xs p-2 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-800 dark:text-slate-200 focus:ring-1 focus:ring-nexus-500"
                >
                  {POPULAR_FONTS.map((f) => (
                    <option key={f} value={f}>{f}</option>
                  ))}
                </select>
              </div>

              {/* Font Size & Weight Row */}
              <div className="grid grid-cols-2 gap-3 items-center">
                <div className="space-y-1">
                  <label className="text-xs font-semibold text-slate-600 dark:text-slate-400">
                    Font Size ({selectedText.fontSize} pt)
                  </label>
                  <input
                    type="range"
                    min="6"
                    max="72"
                    step="0.5"
                    value={selectedText.fontSize}
                    onChange={(e) => onUpdateSelectedText({ ...selectedText, fontSize: parseFloat(e.target.value) })}
                    className="w-full accent-nexus-500"
                  />
                </div>

                <div className="space-y-1">
                  <label className="text-xs font-semibold text-slate-600 dark:text-slate-400">
                    Styles
                  </label>
                  <div className="flex items-center space-x-1 bg-slate-100 dark:bg-slate-800 p-1 rounded-lg border border-slate-200 dark:border-slate-700">
                    <button
                      onClick={() => onUpdateSelectedText({ ...selectedText, isBold: !selectedText.isBold })}
                      className={`flex-1 py-1 rounded flex items-center justify-center transition ${
                        selectedText.isBold 
                          ? 'bg-white dark:bg-slate-900 text-nexus-600 dark:text-nexus-400 shadow-sm font-bold' 
                          : 'text-slate-500 hover:text-slate-800 dark:hover:text-white'
                      }`}
                      title="Bold"
                    >
                      <Bold className="w-3.5 h-3.5" />
                    </button>
                    <button
                      onClick={() => onUpdateSelectedText({ ...selectedText, isItalic: !selectedText.isItalic })}
                      className={`flex-1 py-1 rounded flex items-center justify-center transition ${
                        selectedText.isItalic 
                          ? 'bg-white dark:bg-slate-900 text-nexus-600 dark:text-nexus-400 shadow-sm italic' 
                          : 'text-slate-500 hover:text-slate-800 dark:hover:text-white'
                      }`}
                      title="Italic"
                    >
                      <Italic className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>
              </div>

              {/* Text Alignment */}
              <div className="space-y-1">
                <label className="text-xs font-semibold text-slate-600 dark:text-slate-400">
                  Alignment
                </label>
                <div className="flex items-center space-x-1 bg-slate-100 dark:bg-slate-800 p-1 rounded-lg border border-slate-200 dark:border-slate-700">
                  {(['left', 'center', 'right', 'justify'] as const).map((align) => (
                    <button
                      key={align}
                      onClick={() => onUpdateSelectedText({ ...selectedText, alignment: align })}
                      className={`flex-1 py-1 rounded flex items-center justify-center transition ${
                        selectedText.alignment === align
                          ? 'bg-white dark:bg-slate-900 text-nexus-600 dark:text-nexus-400 shadow-sm'
                          : 'text-slate-500 hover:text-slate-800 dark:hover:text-white'
                      }`}
                      title={`Align ${align}`}
                    >
                      {align === 'left' && <AlignLeft className="w-3.5 h-3.5" />}
                      {align === 'center' && <AlignCenter className="w-3.5 h-3.5" />}
                      {align === 'right' && <AlignRight className="w-3.5 h-3.5" />}
                      {align === 'justify' && <AlignJustify className="w-3.5 h-3.5" />}
                    </button>
                  ))}
                </div>
              </div>

              {/* Font Color Picker */}
              <div className="space-y-2">
                <label className="text-xs font-semibold text-slate-600 dark:text-slate-400 flex items-center justify-between">
                  <span>Text Color</span>
                  <span className="font-mono text-[11px] text-slate-500">{selectedText.fontColor}</span>
                </label>
                <div className="flex items-center space-x-1.5">
                  <input
                    type="color"
                    value={selectedText.fontColor}
                    onChange={(e) => onUpdateSelectedText({ ...selectedText, fontColor: e.target.value })}
                    className="w-8 h-8 rounded-lg cursor-pointer border border-slate-300 dark:border-slate-700 p-0.5 bg-transparent"
                  />
                  <div className="flex items-center space-x-1 flex-1">
                    {PRESET_COLORS.map((c) => (
                      <button
                        key={c}
                        onClick={() => onUpdateSelectedText({ ...selectedText, fontColor: c })}
                        style={{ backgroundColor: c }}
                        className={`w-5 h-5 rounded-md border transition-transform ${
                          selectedText.fontColor.toLowerCase() === c.toLowerCase()
                            ? 'scale-110 ring-2 ring-nexus-500'
                            : 'border-slate-300 dark:border-slate-600 hover:scale-105'
                        }`}
                      />
                    ))}
                  </div>
                </div>
              </div>

              {/* Background Color for Overlay Mode */}
              {editorMode === 'overlay' && (
                <div className="space-y-1.5 pt-2 border-t border-slate-200 dark:border-slate-800">
                  <label className="text-xs font-semibold text-slate-600 dark:text-slate-400 flex items-center justify-between">
                    <span>Redaction Fill Color</span>
                    <span className="font-mono text-[11px] text-slate-500">{selectedText.backgroundColor}</span>
                  </label>
                  <div className="flex items-center space-x-2">
                    <input
                      type="color"
                      value={selectedText.backgroundColor}
                      onChange={(e) => onUpdateSelectedText({ ...selectedText, backgroundColor: e.target.value })}
                      className="w-8 h-8 rounded-lg cursor-pointer border border-slate-300 dark:border-slate-700 p-0.5 bg-transparent"
                    />
                    <span className="text-xs text-slate-500">
                      Blends over original text
                    </span>
                  </div>
                </div>
              )}
            </div>

            {/* Apply & Cancel Actions */}
            <div className="pt-4 border-t border-slate-200 dark:border-slate-800 flex items-center space-x-2">
              <button
                onClick={onApplyTextEdit}
                disabled={isApplying}
                className="flex-1 py-2 px-3 rounded-xl bg-nexus-600 hover:bg-nexus-700 text-white font-bold text-xs flex items-center justify-center space-x-1.5 shadow-md shadow-nexus-500/20 transition disabled:opacity-50"
              >
                {isApplying ? (
                  <div className="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                ) : (
                  <Check className="w-3.5 h-3.5" />
                )}
                <span>Apply to PDF</span>
              </button>

              <button
                onClick={onCancelSelection}
                className="py-2 px-3 rounded-xl border border-slate-300 dark:border-slate-700 hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-600 dark:text-slate-300 text-xs font-semibold transition"
              >
                Cancel
              </button>
            </div>
          </div>
        ) : (
          /* Empty / Document Summary State */
          <div className="space-y-6">
            <div className="text-center py-6 px-2 space-y-2">
              <div className="w-12 h-12 rounded-2xl bg-slate-100 dark:bg-slate-800 text-slate-400 flex items-center justify-center mx-auto">
                <Type className="w-6 h-6" />
              </div>
              <h4 className="text-xs font-bold text-slate-700 dark:text-slate-300">
                No Text Element Selected
              </h4>
              <p className="text-[11px] text-slate-500 dark:text-slate-400">
                Click any existing text on the PDF to inspect its font, size, weight, and edit it directly.
              </p>
            </div>

            {/* Page Metadata Summary */}
            {currentPageData && (
              <div className="p-3.5 rounded-xl bg-slate-50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-800 space-y-3">
                <span className="text-xs font-bold text-slate-700 dark:text-slate-300 flex items-center">
                  <Layers className="w-3.5 h-3.5 mr-1.5 text-nexus-500" />
                  Active Page Stats
                </span>

                <div className="space-y-2 text-xs">
                  <div className="flex justify-between text-slate-600 dark:text-slate-400">
                    <span>Dimensions:</span>
                    <span className="font-medium text-slate-800 dark:text-slate-200">
                      {currentPageData.width} × {currentPageData.height} pt
                    </span>
                  </div>
                  <div className="flex justify-between text-slate-600 dark:text-slate-400">
                    <span>Text Blocks:</span>
                    <span className="font-medium text-slate-800 dark:text-slate-200">
                      {currentPageData.blocks.length}
                    </span>
                  </div>
                  <div className="flex justify-between text-slate-600 dark:text-slate-400">
                    <span>Images:</span>
                    <span className="font-medium text-slate-800 dark:text-slate-200">
                      {currentPageData.images.length}
                    </span>
                  </div>
                  <div className="flex justify-between text-slate-600 dark:text-slate-400">
                    <span>Detected Fonts:</span>
                    <span className="font-medium text-slate-800 dark:text-slate-200">
                      {currentPageData.embedded_fonts.length}
                    </span>
                  </div>
                  <div className="flex justify-between text-slate-600 dark:text-slate-400">
                    <span>Scanned Page:</span>
                    <span className={`font-semibold ${currentPageData.is_scanned ? 'text-amber-500' : 'text-emerald-500'}`}>
                      {currentPageData.is_scanned ? 'Yes (Image Scan)' : 'No (Vector Text)'}
                    </span>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </aside>
  );
};
