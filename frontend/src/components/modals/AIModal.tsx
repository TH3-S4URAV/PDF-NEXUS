import React, { useState } from 'react';
import { Sparkles, X, Send, BookOpen, Languages, MessageSquare, Bot } from 'lucide-react';
import { api } from '../../services/api';

interface AIModalProps {
  isOpen: boolean;
  onClose: () => void;
  documentId: string;
}

export const AIModal: React.FC<AIModalProps> = ({
  isOpen,
  onClose,
  documentId
}) => {
  const [activeTab, setActiveTab] = useState<'summary' | 'qa' | 'translate'>('summary');
  const [isProcessing, setIsProcessing] = useState(false);

  // Summary state
  const [summaryResult, setSummaryResult] = useState<any>(null);

  // Q&A state
  const [question, setQuestion] = useState('');
  const [chatHistory, setChatHistory] = useState<Array<{ q: string; a: string }>>([]);

  // Translate state
  const [targetLang, setTargetLang] = useState('Spanish');
  const [translationResult, setTranslationResult] = useState<any>(null);

  if (!isOpen) return null;

  const handleGenerateSummary = async () => {
    setIsProcessing(true);
    try {
      const res = await api.summarizeDoc(documentId, 'summary');
      setSummaryResult(res);
    } catch (err: any) {
      setSummaryResult({ success: false, message: err.message });
    } finally {
      setIsProcessing(false);
    }
  };

  const handleAskQuestion = async () => {
    if (!question.trim()) return;
    const currentQ = question;
    setQuestion('');
    setIsProcessing(true);
    try {
      const res = await api.askAI(documentId, currentQ);
      setChatHistory(prev => [...prev, { q: currentQ, a: res.answer || 'No answer available.' }]);
    } catch (err: any) {
      setChatHistory(prev => [...prev, { q: currentQ, a: `Error: ${err.message}` }]);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleTranslate = async () => {
    setIsProcessing(true);
    try {
      const res = await api.translateDoc(documentId, targetLang);
      setTranslationResult(res);
    } catch (err: any) {
      setTranslationResult({ success: false, message: err.message });
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl shadow-2xl max-w-xl w-full h-[580px] flex flex-col overflow-hidden transition-colors">
        {/* Header */}
        <div className="px-6 py-4 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <div className="p-1.5 rounded-lg bg-gradient-to-tr from-indigo-500 to-purple-600 text-white shadow-sm">
              <Sparkles className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-slate-900 dark:text-white">
                PDF NEXUS AI Assistant
              </h3>
              <p className="text-[11px] text-slate-500">Document summaries, questions, and instant translation</p>
            </div>
          </div>
          <button onClick={onClose} className="p-1 rounded-lg text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Tab Navigation */}
        <div className="flex border-b border-slate-200 dark:border-slate-800 px-6 bg-slate-50/50 dark:bg-slate-950/40 text-xs font-semibold">
          <button
            onClick={() => setActiveTab('summary')}
            className={`py-3 px-4 border-b-2 transition flex items-center space-x-1.5 ${
              activeTab === 'summary'
                ? 'border-indigo-500 text-indigo-600 dark:text-indigo-400'
                : 'border-transparent text-slate-500 hover:text-slate-800 dark:hover:text-slate-300'
            }`}
          >
            <BookOpen className="w-3.5 h-3.5" />
            <span>Summary</span>
          </button>
          <button
            onClick={() => setActiveTab('qa')}
            className={`py-3 px-4 border-b-2 transition flex items-center space-x-1.5 ${
              activeTab === 'qa'
                ? 'border-indigo-500 text-indigo-600 dark:text-indigo-400'
                : 'border-transparent text-slate-500 hover:text-slate-800 dark:hover:text-slate-300'
            }`}
          >
            <MessageSquare className="w-3.5 h-3.5" />
            <span>Ask PDF</span>
          </button>
          <button
            onClick={() => setActiveTab('translate')}
            className={`py-3 px-4 border-b-2 transition flex items-center space-x-1.5 ${
              activeTab === 'translate'
                ? 'border-indigo-500 text-indigo-600 dark:text-indigo-400'
                : 'border-transparent text-slate-500 hover:text-slate-800 dark:hover:text-slate-300'
            }`}
          >
            <Languages className="w-3.5 h-3.5" />
            <span>Translate</span>
          </button>
        </div>

        {/* Content Body */}
        <div className="flex-1 overflow-y-auto p-6">
          {activeTab === 'summary' && (
            <div className="space-y-4">
              {!summaryResult ? (
                <div className="text-center py-10 space-y-3">
                  <div className="w-12 h-12 rounded-2xl bg-indigo-50 dark:bg-indigo-950/50 text-indigo-500 flex items-center justify-center mx-auto">
                    <BookOpen className="w-6 h-6" />
                  </div>
                  <h4 className="text-sm font-bold text-slate-800 dark:text-slate-200">
                    Generate Executive Document Summary
                  </h4>
                  <p className="text-xs text-slate-500 max-w-sm mx-auto">
                    Synthesizes key sections, themes, and figures. Works with Gemini AI or built-in extractive analyzer.
                  </p>
                  <button
                    onClick={handleGenerateSummary}
                    disabled={isProcessing}
                    className="mt-2 px-5 py-2 rounded-xl bg-gradient-to-r from-indigo-500 to-purple-600 text-white font-bold text-xs shadow-md shadow-indigo-500/20 hover:opacity-95 transition disabled:opacity-50"
                  >
                    {isProcessing ? 'Analyzing Document...' : 'Generate Summary'}
                  </button>
                </div>
              ) : (
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-slate-700 dark:text-slate-300">
                      Summary ({summaryResult.provider})
                    </span>
                    <button
                      onClick={handleGenerateSummary}
                      className="text-xs text-indigo-500 hover:underline"
                    >
                      Regenerate
                    </button>
                  </div>
                  <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 text-xs text-slate-800 dark:text-slate-200 leading-relaxed whitespace-pre-wrap">
                    {summaryResult.summary || summaryResult.message}
                  </div>
                </div>
              )}
            </div>
          )}

          {activeTab === 'qa' && (
            <div className="flex flex-col h-full space-y-4">
              {/* Chat Scroll Area */}
              <div className="flex-1 overflow-y-auto space-y-3 pr-1">
                {chatHistory.length === 0 ? (
                  <div className="text-center py-12 text-slate-400 space-y-2">
                    <Bot className="w-8 h-8 mx-auto text-slate-300 dark:text-slate-600" />
                    <p className="text-xs">Ask any question about this PDF document.</p>
                  </div>
                ) : (
                  chatHistory.map((item, idx) => (
                    <div key={idx} className="space-y-2 text-xs">
                      {/* User message */}
                      <div className="flex justify-end">
                        <div className="p-2.5 rounded-xl bg-indigo-600 text-white max-w-[80%] rounded-tr-none">
                          {item.q}
                        </div>
                      </div>
                      {/* Assistant message */}
                      <div className="flex justify-start">
                        <div className="p-3 rounded-xl bg-slate-100 dark:bg-slate-800 text-slate-800 dark:text-slate-200 max-w-[85%] rounded-tl-none border border-slate-200 dark:border-slate-700">
                          {item.a}
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>

              {/* Chat Input */}
              <div className="flex items-center space-x-2 pt-2 border-t border-slate-200 dark:border-slate-800">
                <input
                  type="text"
                  value={question}
                  onChange={(e) => setQuestion(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleAskQuestion()}
                  placeholder="e.g. What were the total earnings in Q4?"
                  className="flex-1 text-xs p-2.5 rounded-xl border border-slate-300 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-white focus:outline-none focus:ring-1 focus:ring-indigo-500"
                />
                <button
                  onClick={handleAskQuestion}
                  disabled={isProcessing || !question.trim()}
                  className="p-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white transition disabled:opacity-50"
                >
                  <Send className="w-4 h-4" />
                </button>
              </div>
            </div>
          )}

          {activeTab === 'translate' && (
            <div className="space-y-4">
              <div className="space-y-2">
                <label className="text-xs font-bold text-slate-700 dark:text-slate-300">
                  Target Language:
                </label>
                <select
                  value={targetLang}
                  onChange={(e) => setTargetLang(e.target.value)}
                  className="w-full text-xs p-2.5 rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-800 dark:text-slate-200"
                >
                  {['Hindi', 'Spanish', 'French', 'German', 'Japanese', 'Arabic'].map((l) => (
                    <option key={l} value={l}>{l}</option>
                  ))}
                </select>
              </div>

              <button
                onClick={handleTranslate}
                disabled={isProcessing}
                className="w-full py-2.5 rounded-xl bg-gradient-to-r from-indigo-500 to-purple-600 text-white font-bold text-xs shadow-md shadow-indigo-500/20 hover:opacity-95 transition disabled:opacity-50"
              >
                {isProcessing ? 'Translating...' : `Translate to ${targetLang}`}
              </button>

              {translationResult && (
                <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 text-xs text-slate-800 dark:text-slate-200 whitespace-pre-wrap">
                  {translationResult.translated_text || translationResult.message}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
