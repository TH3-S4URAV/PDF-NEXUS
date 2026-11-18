import React, { useState } from 'react';
import { 
  Layers, X, FileOutput, FileSpreadsheet, Presentation, Image as ImageIcon, 
  Zap, Lock, Stamp, Hash, Download, Check
} from 'lucide-react';
import { api } from '../../services/api';

interface UtilitiesModalProps {
  isOpen: boolean;
  onClose: () => void;
  documentId: string;
}

export const UtilitiesModal: React.FC<UtilitiesModalProps> = ({
  isOpen,
  onClose,
  documentId
}) => {
  const [activeTool, setActiveTool] = useState<string>('convert');
  const [isProcessing, setIsProcessing] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  // Tool specific inputs
  const [compressLevel, setCompressLevel] = useState<'low' | 'medium' | 'high'>('medium');
  const [protectPassword, setProtectPassword] = useState('');
  const [watermarkText, setWatermarkText] = useState('CONFIDENTIAL');

  if (!isOpen) return null;

  const handleConvert = async (format: 'docx' | 'excel' | 'pptx' | 'images') => {
    setIsProcessing(true);
    setError(null);
    setResult(null);
    try {
      const res = await api.convertDoc(documentId, format);
      setResult(res);
    } catch (err: any) {
      setError(err.message || 'Conversion failed');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleCompress = async () => {
    setIsProcessing(true);
    setError(null);
    setResult(null);
    try {
      const res = await api.compressPDF(documentId, compressLevel);
      setResult(res);
    } catch (err: any) {
      setError(err.message || 'Compression failed');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleProtect = async () => {
    if (!protectPassword) return;
    setIsProcessing(true);
    setError(null);
    setResult(null);
    try {
      const res = await api.protectPDF(documentId, protectPassword);
      setResult(res);
    } catch (err: any) {
      setError(err.message || 'Protection failed');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleWatermark = async () => {
    if (!watermarkText) return;
    setIsProcessing(true);
    setError(null);
    setResult(null);
    try {
      const res = await api.watermarkPDF(documentId, watermarkText);
      setResult(res);
    } catch (err: any) {
      setError(err.message || 'Watermarking failed');
    } finally {
      setIsProcessing(false);
    }
  };

  const handlePageNumbers = async () => {
    setIsProcessing(true);
    setError(null);
    setResult(null);
    try {
      const res = await api.addPageNumbers(documentId, 'bottom-center');
      setResult(res);
    } catch (err: any) {
      setError(err.message || 'Adding page numbers failed');
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl shadow-2xl max-w-xl w-full h-[520px] flex flex-col overflow-hidden transition-colors">
        {/* Header */}
        <div className="px-6 py-4 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <div className="p-1.5 rounded-lg bg-blue-100 dark:bg-blue-950/60 text-blue-600 dark:text-blue-400">
              <Layers className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-slate-900 dark:text-white">
                PDF Utilities & Conversions
              </h3>
              <p className="text-[11px] text-slate-500">Transform, optimize, protect, and brand your PDF</p>
            </div>
          </div>
          <button onClick={onClose} className="p-1 rounded-lg text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Tab Nav */}
        <div className="flex border-b border-slate-200 dark:border-slate-800 px-6 bg-slate-50/50 dark:bg-slate-950/40 text-xs font-semibold">
          {[
            { id: 'convert', name: 'Convert', icon: FileOutput },
            { id: 'compress', name: 'Compress', icon: Zap },
            { id: 'protect', name: 'Protect', icon: Lock },
            { id: 'watermark', name: 'Watermark', icon: Stamp },
            { id: 'pages', name: 'Numbers', icon: Hash }
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => { setActiveTool(tab.id); setResult(null); setError(null); }}
              className={`py-3 px-3.5 border-b-2 transition flex items-center space-x-1.5 ${
                activeTool === tab.id
                  ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                  : 'border-transparent text-slate-500 hover:text-slate-800 dark:hover:text-slate-300'
              }`}
            >
              <tab.icon className="w-3.5 h-3.5" />
              <span>{tab.name}</span>
            </button>
          ))}
        </div>

        {/* Body */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {activeTool === 'convert' && (
            <div className="space-y-4">
              <label className="text-xs font-bold text-slate-700 dark:text-slate-300">
                Choose Target Export Format:
              </label>
              <div className="grid grid-cols-2 gap-3">
                {[
                  { id: 'docx', name: 'PDF to Word (.docx)', desc: 'Editable text & tables', icon: FileOutput, color: 'text-indigo-500' },
                  { id: 'excel', name: 'PDF to Excel (.xlsx)', desc: 'Extract data spreadsheets', icon: FileSpreadsheet, color: 'text-emerald-500' },
                  { id: 'pptx', name: 'PDF to PowerPoint (.pptx)', desc: 'Slide presentations', icon: Presentation, color: 'text-orange-500' },
                  { id: 'images', name: 'PDF to PNG Images', desc: 'High-res pages zip', icon: ImageIcon, color: 'text-cyan-500' },
                ].map(item => (
                  <div
                    key={item.id}
                    onClick={() => handleConvert(item.id as any)}
                    className="cursor-pointer p-4 rounded-xl border border-slate-200 dark:border-slate-800 hover:border-blue-500 hover:shadow-md transition bg-slate-50/50 dark:bg-slate-800/40"
                  >
                    <item.icon className={`w-6 h-6 ${item.color} mb-2`} />
                    <h4 className="text-xs font-bold text-slate-900 dark:text-white">{item.name}</h4>
                    <p className="text-[11px] text-slate-500 mt-0.5">{item.desc}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeTool === 'compress' && (
            <div className="space-y-4">
              <div className="space-y-2">
                <label className="text-xs font-bold text-slate-700 dark:text-slate-300">
                  Compression Level:
                </label>
                <div className="grid grid-cols-3 gap-2">
                  {(['low', 'medium', 'high'] as const).map(lvl => (
                    <button
                      key={lvl}
                      onClick={() => setCompressLevel(lvl)}
                      className={`p-3 rounded-xl border text-xs capitalize font-bold transition ${
                        compressLevel === lvl
                          ? 'border-blue-500 bg-blue-50/50 dark:bg-blue-950/40 text-blue-600 dark:text-blue-400'
                          : 'border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-400'
                      }`}
                    >
                      {lvl} Quality
                    </button>
                  ))}
                </div>
              </div>
              <button
                onClick={handleCompress}
                disabled={isProcessing}
                className="w-full py-2.5 rounded-xl bg-blue-600 text-white font-bold text-xs hover:bg-blue-700 transition"
              >
                {isProcessing ? 'Compressing PDF...' : 'Compress Document'}
              </button>
            </div>
          )}

          {activeTool === 'protect' && (
            <div className="space-y-4">
              <div className="space-y-1.5">
                <label className="text-xs font-bold text-slate-700 dark:text-slate-300">
                  Document Password (AES-256):
                </label>
                <input
                  type="password"
                  value={protectPassword}
                  onChange={(e) => setProtectPassword(e.target.value)}
                  placeholder="Enter strong password..."
                  className="w-full text-xs p-2.5 rounded-xl border border-slate-300 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-white"
                />
              </div>
              <button
                onClick={handleProtect}
                disabled={isProcessing || !protectPassword}
                className="w-full py-2.5 rounded-xl bg-blue-600 text-white font-bold text-xs hover:bg-blue-700 transition disabled:opacity-50"
              >
                {isProcessing ? 'Encrypting...' : 'Protect Document'}
              </button>
            </div>
          )}

          {activeTool === 'watermark' && (
            <div className="space-y-4">
              <div className="space-y-1.5">
                <label className="text-xs font-bold text-slate-700 dark:text-slate-300">
                  Watermark Text:
                </label>
                <input
                  type="text"
                  value={watermarkText}
                  onChange={(e) => setWatermarkText(e.target.value)}
                  placeholder="e.g. CONFIDENTIAL / DRAFT"
                  className="w-full text-xs p-2.5 rounded-xl border border-slate-300 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-white uppercase font-bold"
                />
              </div>
              <button
                onClick={handleWatermark}
                disabled={isProcessing || !watermarkText}
                className="w-full py-2.5 rounded-xl bg-blue-600 text-white font-bold text-xs hover:bg-blue-700 transition"
              >
                {isProcessing ? 'Watermarking...' : 'Stamp Watermark'}
              </button>
            </div>
          )}

          {activeTool === 'pages' && (
            <div className="space-y-4 text-center py-6">
              <Hash className="w-10 h-10 text-blue-500 mx-auto" />
              <h4 className="text-xs font-bold text-slate-800 dark:text-slate-200">
                Number All Pages
              </h4>
              <p className="text-[11px] text-slate-500 max-w-xs mx-auto">
                Appends clean "Page X of Y" counters centered on the bottom of every page.
              </p>
              <button
                onClick={handlePageNumbers}
                disabled={isProcessing}
                className="px-6 py-2 rounded-xl bg-blue-600 text-white font-bold text-xs hover:bg-blue-700 transition"
              >
                {isProcessing ? 'Adding Numbers...' : 'Add Page Numbers'}
              </button>
            </div>
          )}

          {/* Download result link */}
          {result?.download_url && (
            <div className="p-4 rounded-xl bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-800 space-y-2">
              <div className="flex items-center space-x-1.5 text-emerald-700 dark:text-emerald-300 text-xs font-bold">
                <Check className="w-4 h-4" />
                <span>Task Completed Successfully!</span>
              </div>
              {result.savings_percentage && (
                <p className="text-xs text-emerald-600">
                  Reduced file size by {result.savings_percentage}%
                </p>
              )}
              <a
                href={`http://127.0.0.1:8000${result.download_url}`}
                target="_blank"
                rel="noreferrer"
                className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-emerald-600 text-white text-xs font-bold hover:bg-emerald-700 shadow-sm"
              >
                <Download className="w-3.5 h-3.5" />
                <span>Download Generated File</span>
              </a>
            </div>
          )}

          {error && (
            <div className="p-3 rounded-xl bg-red-50 dark:bg-red-950/50 border border-red-200 dark:border-red-800 text-red-600 text-xs">
              {error}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
