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
    <>
      <div className="bg-white relative">
        {/* View Toggle - Centered */}
        <div className="flex justify-center py-4 border-b">
          <div className="inline-flex bg-gray-100 p-1 rounded-lg">
            <button
              onClick={() => onViewChange('executive')}
              className={`flex items-center gap-2 px-6 py-2.5 rounded-md font-medium transition-all ${
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
              className={`flex items-center gap-2 px-6 py-2.5 rounded-md font-medium transition-all ${
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
        
        {/* Back to Dashboard - Positioned absolutely */}
        <button
          onClick={() => navigate('/dashboard')}
          className="absolute top-4 left-4 flex items-center gap-2 text-blue-600 hover:text-blue-700 text-sm font-medium"
        >
          <ArrowLeft className="h-4 w-4" />
          Dashboard
        </button>
      </div>
    </>
  );
};
