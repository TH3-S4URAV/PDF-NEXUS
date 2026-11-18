import React from 'react';
import { 
  RotateCw, Copy, Trash2, Plus, FileText, ChevronRight, Eye
} from 'lucide-react';
import { PageInspection } from '../../types/pdf';
import { api } from '../../services/api';

interface LeftSidebarProps {
  documentId: string;
  pages: PageInspection[];
  currentPage: number;
  onSelectPage: (pageNum: number) => void;
  onPageOperation: (op: 'rotate' | 'duplicate' | 'delete' | 'insert_blank', pageNum: number) => void;
  isCollapsed: boolean;
  onToggleCollapse: () => void;
}

export const LeftSidebar: React.FC<LeftSidebarProps> = ({
  documentId,
  pages,
  currentPage,
  onSelectPage,
  onPageOperation,
  isCollapsed,
  onToggleCollapse
}) => {
  if (isCollapsed) {
    return (
      <aside className="w-12 border-r border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 flex flex-col items-center py-4 select-none transition-colors">
        <button
          onClick={onToggleCollapse}
          className="p-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-500"
          title="Expand Left Panel"
        >
          <ChevronRight className="w-5 h-5" />
        </button>
      </aside>
    );
  }

  return (
    <aside className="w-64 border-r border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 flex flex-col select-none transition-colors z-20">
      {/* Header */}
      <div className="h-12 border-b border-slate-200 dark:border-slate-800 px-4 flex items-center justify-between">
        <span className="text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider flex items-center">
          <FileText className="w-3.5 h-3.5 mr-1.5 text-nexus-500" />
          Pages ({pages.length})
        </span>
        <button
          onClick={() => onPageOperation('insert_blank', currentPage)}
          className="p-1 rounded hover:bg-slate-100 dark:hover:bg-slate-800 text-nexus-600 dark:text-nexus-400 text-xs flex items-center space-x-1"
          title="Insert Blank Page"
        >
          <Plus className="w-3.5 h-3.5" />
          <span className="font-semibold text-[11px]">Add</span>
        </button>
      </div>

      {/* Thumbnails Scroll Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {pages.map((p) => {
          const isActive = p.page_number === currentPage;
          return (
            <div
              key={p.page_number}
              className={`group relative rounded-xl border-2 transition-all p-2 ${
                isActive
                  ? 'border-nexus-500 bg-nexus-50/40 dark:bg-nexus-950/30 shadow-md ring-2 ring-nexus-500/20'
                  : 'border-slate-200 dark:border-slate-800 hover:border-slate-300 dark:hover:border-slate-700 bg-slate-50/50 dark:bg-slate-800/30'
              }`}
            >
              {/* Thumbnail Card */}
              <div 
                onClick={() => onSelectPage(p.page_number)}
                className="cursor-pointer aspect-[1/1.3] rounded-lg bg-white dark:bg-slate-950 border border-slate-200 dark:border-slate-800 flex items-center justify-center overflow-hidden shadow-sm"
              >
                <img
                  src={api.getThumbnailUrl(documentId, p.page_number)}
                  alt={`Page ${p.page_number}`}
                  className="w-full h-full object-contain pointer-events-none"
                  onError={(e) => {
                    // Fallback to placeholder if thumbnail is still generating
                    (e.target as HTMLElement).style.display = 'none';
                  }}
                />
              </div>

              {/* Page Number & Actions Bar */}
              <div className="mt-2 flex items-center justify-between text-xs">
                <span className={`font-bold text-[11px] ${isActive ? 'text-nexus-600 dark:text-nexus-400' : 'text-slate-500'}`}>
                  Page {p.page_number}
                </span>

                <div className="flex items-center space-x-1 opacity-0 group-hover:opacity-100 transition-opacity">
                  <button
                    onClick={() => onPageOperation('rotate', p.page_number)}
                    className="p-1 hover:bg-slate-200 dark:hover:bg-slate-700 rounded text-slate-500 hover:text-slate-900 dark:hover:text-white"
                    title="Rotate 90°"
                  >
                    <RotateCw className="w-3 h-3" />
                  </button>
                  <button
                    onClick={() => onPageOperation('duplicate', p.page_number)}
                    className="p-1 hover:bg-slate-200 dark:hover:bg-slate-700 rounded text-slate-500 hover:text-slate-900 dark:hover:text-white"
                    title="Duplicate Page"
                  >
                    <Copy className="w-3 h-3" />
                  </button>
                  {pages.length > 1 && (
                    <button
                      onClick={() => onPageOperation('delete', p.page_number)}
                      className="p-1 hover:bg-red-100 dark:hover:bg-red-950/60 rounded text-red-500 hover:text-red-700"
                      title="Delete Page"
                    >
                      <Trash2 className="w-3 h-3" />
                    </button>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </aside>
  );
};
