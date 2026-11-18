import React, { useState, useRef } from 'react';
import { 
  FileText, UploadCloud, Sparkles, Layers, Shield, FileCheck, 
  ArrowRight, Clock, Trash2, Download, Zap, Moon, Sun, 
  Cpu, FileOutput, FileSpreadsheet, Presentation, Lock, Eye
} from 'lucide-react';
import { api } from '../../services/api';

interface DashboardProps {
  onOpenDocument: (docId: string) => void;
  isDark: boolean;
  onToggleTheme: () => void;
}

export const Dashboard: React.FC<DashboardProps> = ({ onOpenDocument, isDark, onToggleTheme }) => {
  const [isUploading, setIsUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [recentDocs, setRecentDocs] = useState<any[]>([]);
  const [isDragOver, setIsDragOver] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Load recent documents on mount
  React.useEffect(() => {
    api.listDocuments().then(setRecentDocs).catch(() => {});
  }, []);

  const handleFileUpload = async (file: File) => {
    if (!file.name.toLowerCase().endsWith('.pdf')) {
      setUploadError('Please upload a valid PDF document (.pdf).');
      return;
    }
    setUploadError(null);
    setIsUploading(true);

    try {
      const res = await api.uploadDocument(file);
      if (res.success && res.document_id) {
        onOpenDocument(res.document_id);
      }
    } catch (err: any) {
      setUploadError(err.message || 'Failed to upload document');
    } finally {
      setIsUploading(false);
    }
  };

  const onDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileUpload(e.dataTransfer.files[0]);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-50 via-white to-slate-100 dark:from-slate-950 dark:via-slate-900 dark:to-slate-950 transition-colors">
      {/* Top Navbar */}
      <header className="border-b border-slate-200 dark:border-slate-800 bg-white/80 dark:bg-slate-900/80 backdrop-blur sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-nexus-600 to-indigo-500 flex items-center justify-center text-white shadow-lg shadow-nexus-500/30">
              <FileText className="w-6 h-6" />
            </div>
            <div>
              <span className="text-xl font-black tracking-tight text-slate-900 dark:text-white">
                PDF <span className="text-nexus-500">NEXUS</span>
              </span>
              <span className="ml-2 text-[10px] font-semibold px-2 py-0.5 rounded-full bg-nexus-100 dark:bg-nexus-900/50 text-nexus-600 dark:text-nexus-400 border border-nexus-200 dark:border-nexus-800 uppercase tracking-widest">
                v1.0 Pro
              </span>
            </div>
          </div>

          <div className="flex items-center space-x-3">
            <button
              onClick={onToggleTheme}
              className="p-2 rounded-lg bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700 transition"
              title="Toggle Theme"
            >
              {isDark ? <Sun className="w-5 h-5 text-amber-400" /> : <Moon className="w-5 h-5 text-slate-600" />}
            </button>
            <div className="flex items-center space-x-2 text-xs font-medium px-3 py-1.5 rounded-lg bg-emerald-50 dark:bg-emerald-950/50 text-emerald-600 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-800">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
              <span>Engine Ready</span>
            </div>
          </div>
        </div>
      </header>

      {/* Hero & Upload Section */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-12">
        <div className="text-center max-w-3xl mx-auto space-y-4">
          <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-nexus-50 dark:bg-nexus-950/80 border border-nexus-200 dark:border-nexus-800 text-nexus-600 dark:text-nexus-400 text-xs font-semibold">
            <Zap className="w-3.5 h-3.5 text-nexus-500" />
            <span>Precision Vector PDF Editing & Typography Matching</span>
          </div>
          <h1 className="text-4xl sm:text-5xl font-extrabold text-slate-900 dark:text-white tracking-tight">
            The Professional Online <br />
            <span className="bg-gradient-to-r from-nexus-500 via-indigo-500 to-purple-500 bg-clip-text text-transparent">
              PDF Text & Document Editor
            </span>
          </h1>
          <p className="text-slate-600 dark:text-slate-400 text-base sm:text-lg">
            Directly edit existing PDF text, fonts, images, and pages with true vector redaction, OCR intelligence, and format conversions.
          </p>
        </div>

        {/* Upload Zone */}
        <div className="max-w-2xl mx-auto">
          <div
            onDragOver={(e) => { e.preventDefault(); setIsDragOver(true); }}
            onDragLeave={() => setIsDragOver(false)}
            onDrop={onDrop}
            onClick={() => fileInputRef.current?.click()}
            className={`cursor-pointer relative overflow-hidden rounded-2xl border-2 border-dashed p-10 text-center transition-all duration-300 shadow-xl ${
              isDragOver 
                ? 'border-nexus-500 bg-nexus-50/50 dark:bg-nexus-950/30 scale-[1.01]' 
                : 'border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 hover:border-nexus-400 hover:bg-slate-50/50 dark:hover:bg-slate-800/50'
            }`}
          >
            <input
              type="file"
              ref={fileInputRef}
              onChange={(e) => e.target.files?.[0] && handleFileUpload(e.target.files[0])}
              accept=".pdf"
              className="hidden"
            />
            <div className="flex flex-col items-center justify-center space-y-4">
              <div className="w-16 h-16 rounded-2xl bg-nexus-50 dark:bg-nexus-950 text-nexus-600 dark:text-nexus-400 flex items-center justify-center ring-8 ring-nexus-50/50 dark:ring-nexus-950/50">
                {isUploading ? (
                  <div className="w-8 h-8 border-3 border-nexus-500 border-t-transparent rounded-full animate-spin" />
                ) : (
                  <UploadCloud className="w-8 h-8" />
                )}
              </div>
              <div>
                <h3 className="text-lg font-bold text-slate-900 dark:text-white">
                  {isUploading ? 'Inspecting & Parsing PDF Geometry...' : 'Drop your PDF here, or click to browse'}
                </h3>
                <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
                  Supports multi-page documents, embedded fonts, scans & images (up to 50MB)
                </p>
              </div>
              <div className="flex items-center space-x-4 text-xs font-medium text-slate-500 dark:text-slate-400">
                <span className="flex items-center"><Shield className="w-3.5 h-3.5 text-emerald-500 mr-1" /> Client & Server Encrypted</span>
                <span className="flex items-center"><Sparkles className="w-3.5 h-3.5 text-nexus-500 mr-1" /> Direct Text Mode</span>
              </div>
            </div>
          </div>

          {uploadError && (
            <div className="mt-4 p-3 bg-red-50 dark:bg-red-950/50 border border-red-200 dark:border-red-800 rounded-xl text-red-600 dark:text-red-400 text-sm flex items-center justify-center">
              {uploadError}
            </div>
          )}
        </div>

        {/* Feature Tools Grid */}
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-bold text-slate-900 dark:text-white flex items-center">
              <Layers className="w-5 h-5 text-nexus-500 mr-2" />
              Integrated PDF Toolkit
            </h2>
            <span className="text-xs text-slate-500">10+ Professional Document Engines</span>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4">
            {[
              { title: 'Direct Text Edit', icon: FileText, color: 'text-blue-500', desc: 'Edit original words' },
              { title: 'PDF to Word', icon: FileOutput, color: 'text-indigo-500', desc: 'DOCX conversion' },
              { title: 'PDF to Excel', icon: FileSpreadsheet, color: 'text-emerald-500', desc: 'Extract tables' },
              { title: 'OCR Engine', icon: Cpu, color: 'text-purple-500', desc: 'English & Hindi' },
              { title: 'Compress PDF', icon: Zap, color: 'text-amber-500', desc: 'Reduce file size' },
              { title: 'Protect & Sign', icon: Lock, color: 'text-rose-500', desc: 'AES-256 encryption' },
            ].map((tool, idx) => (
              <div 
                key={idx}
                onClick={() => fileInputRef.current?.click()}
                className="group cursor-pointer p-4 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 hover:border-nexus-500 hover:shadow-lg dark:hover:border-nexus-500 transition-all"
              >
                <tool.icon className={`w-6 h-6 ${tool.color} mb-2 group-hover:scale-110 transition-transform`} />
                <h4 className="text-xs font-bold text-slate-900 dark:text-white">{tool.title}</h4>
                <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-0.5">{tool.desc}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Recent Documents Section */}
        {recentDocs.length > 0 && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-xl font-bold text-slate-900 dark:text-white flex items-center">
                <Clock className="w-5 h-5 text-nexus-500 mr-2" />
                Recent Documents
              </h2>
              <span className="text-xs text-slate-500">{recentDocs.length} files available</span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {recentDocs.map((doc) => (
                <div
                  key={doc.id}
                  onClick={() => onOpenDocument(doc.id)}
                  className="cursor-pointer group p-4 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 hover:border-nexus-500 hover:shadow-md transition-all flex items-center space-x-4"
                >
                  <div className="w-12 h-16 rounded bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 flex items-center justify-center text-slate-400 group-hover:text-nexus-500 transition-colors flex-shrink-0">
                    <FileText className="w-6 h-6" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <h4 className="text-sm font-semibold text-slate-900 dark:text-white truncate group-hover:text-nexus-500 transition-colors">
                      {doc.filename}
                    </h4>
                    <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
                      {doc.page_count} page{doc.page_count > 1 ? 's' : ''} • {(doc.file_size / 1024).toFixed(1)} KB
                    </p>
                    <span className="text-[10px] text-slate-400 dark:text-slate-500 block mt-0.5">
                      {new Date(doc.created_at).toLocaleDateString()}
                    </span>
                  </div>
                  <ArrowRight className="w-5 h-5 text-slate-300 dark:text-slate-600 group-hover:text-nexus-500 group-hover:translate-x-1 transition-all" />
                </div>
              ))}
            </div>
          </div>
        )}
      </main>
    </div>
  );
};
