import React, { useState } from 'react';
import { Cpu, X, Check, Download, AlertTriangle, FileCheck, Sparkles } from 'lucide-react';
import { api } from '../../services/api';

interface OCRModalProps {
  isOpen: boolean;
  onClose: () => void;
  documentId: string;
}

export const OCRModal: React.FC<OCRModalProps> = ({
  isOpen,
  onClose,
  documentId
}) => {
  const [languages, setLanguages] = useState<string[]>(['eng', 'hin']);
  const [isProcessing, setIsProcessing] = useState(false);
  const [ocrResult, setOcrResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const toggleLanguage = (lang: string) => {
    if (languages.includes(lang)) {
      if (languages.length > 1) {
        setLanguages(languages.filter(l => l !== lang));
      }
    } else {
      setLanguages([...languages, lang]);
    }
  };

  const handleRunOCR = async () => {
    setIsProcessing(true);
    setError(null);
    try {
      const res = await api.runOCR(documentId, languages);
      setOcrResult(res);
    } catch (err: any) {
      setError(err.message || 'OCR processing failed');
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl shadow-2xl max-w-lg w-full overflow-hidden transition-colors">
        {/* Header */}
        <div className="px-6 py-4 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <div className="p-1.5 rounded-lg bg-purple-100 dark:bg-purple-950/60 text-purple-600 dark:text-purple-400">
              <Cpu className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-slate-900 dark:text-white">
                Optical Character Recognition (OCR)
              </h3>
              <p className="text-[11px] text-slate-500">Transform scanned and image-based PDFs into searchable vector text</p>
            </div>
          </div>
          <button onClick={onClose} className="p-1 rounded-lg text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-5">
          {/* Language Selection */}
          <div className="space-y-2">
            <label className="text-xs font-bold text-slate-700 dark:text-slate-300">
              Recognition Languages:
            </label>
            <div className="grid grid-cols-2 gap-2">
              {[
                { id: 'eng', name: 'English (Latin script)' },
                { id: 'hin', name: 'Hindi (Devanagari script)' },
              ].map((lang) => {
                const selected = languages.includes(lang.id);
                return (
                  <div
                    key={lang.id}
                    onClick={() => toggleLanguage(lang.id)}
                    className={`cursor-pointer p-3 rounded-xl border flex items-center justify-between text-xs transition ${
                      selected
                        ? 'border-purple-500 bg-purple-50/50 dark:bg-purple-950/30 text-purple-700 dark:text-purple-300 font-semibold'
                        : 'border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-400 hover:border-slate-300'
                    }`}
                  >
                    <span>{lang.name}</span>
                    {selected && <Check className="w-4 h-4 text-purple-500" />}
                  </div>
                );
              })}
            </div>
          </div>

          {/* Engine Features Info */}
          <div className="p-3.5 rounded-xl bg-slate-50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-700 text-xs text-slate-600 dark:text-slate-400 space-y-1.5">
            <div className="font-bold text-slate-800 dark:text-slate-200 flex items-center">
              <Sparkles className="w-3.5 h-3.5 text-purple-500 mr-1" />
              OCR Capabilities:
            </div>
            <ul className="list-disc pl-4 space-y-1 text-[11px]">
              <li>Produces a 100% pixel-perfect <strong>Searchable PDF</strong> with an invisible text layer overlay.</li>
              <li>Preserves original scan image resolution and document aesthetics.</li>
              <li>Enables text selection, copy-pasting, and search in any PDF reader.</li>
            </ul>
          </div>

          {error && (
            <div className="p-3 bg-red-50 dark:bg-red-950/50 border border-red-200 dark:border-red-800 rounded-xl text-red-600 text-xs">
              {error}
            </div>
          )}

          {/* Success State */}
          {ocrResult && (
            <div className="p-4 rounded-xl bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-800 space-y-3">
              <div className="flex items-center space-x-2 text-emerald-700 dark:text-emerald-300 text-xs font-bold">
                <FileCheck className="w-4 h-4 text-emerald-500" />
                <span>Searchable PDF Ready!</span>
              </div>
              <p className="text-[11px] text-emerald-600 dark:text-emerald-400">
                OCR successfully recognized and embedded text across all {ocrResult.pages?.length || 1} pages.
              </p>
              {ocrResult.download_url && (
                <a
                  href={`http://127.0.0.1:8000${ocrResult.download_url}`}
                  target="_blank"
                  rel="noreferrer"
                  className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-emerald-600 text-white text-xs font-bold hover:bg-emerald-700 shadow-sm"
                >
                  <Download className="w-3.5 h-3.5" />
                  <span>Download Searchable PDF</span>
                </a>
              )}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-3 border-t border-slate-200 dark:border-slate-800 flex items-center justify-end space-x-2 bg-slate-50 dark:bg-slate-900/50">
          <button
            onClick={onClose}
            className="px-4 py-2 text-xs font-semibold rounded-xl border border-slate-300 dark:border-slate-700 hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-300 transition"
          >
            Close
          </button>
          {!ocrResult && (
            <button
              onClick={handleRunOCR}
              disabled={isProcessing}
              className="px-4 py-2 text-xs font-bold rounded-xl bg-purple-600 hover:bg-purple-700 text-white flex items-center space-x-1.5 shadow-md shadow-purple-500/20 transition disabled:opacity-50"
            >
              {isProcessing ? (
                <div className="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin" />
              ) : (
                <Cpu className="w-3.5 h-3.5" />
              )}
              <span>Run OCR Engine</span>
            </button>
          )}
        </div>
      </div>
    </div>
  );
};
