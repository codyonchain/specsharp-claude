import React from 'react';
import { Project } from '../../types';
import { formatNumber } from '../../utils/formatters';
import { ArrowLeft, FileSpreadsheet, HardHat, MapPin } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

interface Props {
  project: Project;
  onDelete: () => void;
  activeView: 'executive' | 'construction';
  onViewChange: (view: 'executive' | 'construction') => void;
}

export const ProjectHeader: React.FC<Props> = ({ project, onDelete, activeView, onViewChange }) => {
  const navigate = useNavigate();
  const { parsed_input, calculations } = project.analysis;
  
  return (
    <div className="bg-white border-b">
      <div className="max-w-7xl mx-auto px-4">
        {/* Top bar with navigation */}
        <div className="py-4 flex items-center justify-between">
          <button
            onClick={() => navigate('/dashboard')}
            className="flex items-center gap-2 text-gray-600 hover:text-gray-900"
          >
            <ArrowLeft className="h-4 w-4" />
            Dashboard
          </button>
          
          {/* View Toggle */}
          <div className="flex gap-2 bg-gray-100 p-1 rounded-lg">
            <button
              onClick={() => onViewChange('executive')}
              className={`flex items-center gap-2 px-4 py-2 rounded-md font-medium transition ${
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
              className={`flex items-center gap-2 px-4 py-2 rounded-md font-medium transition ${
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
        
        {/* Project info */}
        <div className="py-6">
          <h1 className="text-2xl font-bold text-gray-900">
            {formatNumber(parsed_input.square_footage)} SF {calculations.project_info.display_name}
          </h1>
          <div className="flex items-center gap-4 mt-2 text-sm text-gray-600">
            <span className="flex items-center gap-1">
              <MapPin className="h-3 w-3" />
              {parsed_input.location}
            </span>
            <span>{parsed_input.floors || calculations.project_info.typical_floors} Floors</span>
            <span className="capitalize">{parsed_input.project_class.replace('_', ' ')}</span>
          </div>
        </div>
      </div>
    </div>
  );
};
