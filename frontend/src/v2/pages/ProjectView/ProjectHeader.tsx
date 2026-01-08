import React from 'react';
import { Project } from '../../types';
import { ArrowLeft, FileSpreadsheet, HardHat } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

interface Props {
  project: Project;
  onDelete: () => void;
  activeView: 'executive' | 'construction';
  onViewChange: (view: 'executive' | 'construction') => void;
}

export const ProjectHeader: React.FC<Props> = ({ project: _project, onDelete: _onDelete, activeView, onViewChange }) => {
  const navigate = useNavigate();
  
  return (
    <div className="sticky top-0 z-40 bg-white/95 backdrop-blur supports-[backdrop-filter]:bg-white/80 border-b border-slate-100">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3 flex items-center justify-between gap-4">
        <button
          onClick={() => navigate('/dashboard')}
          className="flex items-center gap-2 text-blue-600 hover:text-blue-700 text-sm font-medium whitespace-nowrap"
        >
          <ArrowLeft className="h-4 w-4" />
          Dashboard
        </button>
        <div className="flex-1">
          <div className="w-full overflow-x-auto">
            <div className="inline-flex bg-gray-100 p-1 rounded-lg min-w-full sm:min-w-0">
              <button
                onClick={() => onViewChange('executive')}
                className={`flex-1 sm:flex-none flex items-center justify-center gap-2 px-4 sm:px-6 py-2.5 rounded-md font-medium transition-all ${
                  activeView === 'executive'
                    ? 'bg-blue-600 text-white shadow-sm'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                <FileSpreadsheet className="h-4 w-4" />
                Executive View
              </button>
              <button
                onClick={() => onViewChange('construction')}
                className={`flex-1 sm:flex-none flex items-center justify-center gap-2 px-4 sm:px-6 py-2.5 rounded-md font-medium transition-all ${
                  activeView === 'construction'
                    ? 'bg-blue-600 text-white shadow-sm'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                <HardHat className="h-4 w-4" />
                Trade Breakdown
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
