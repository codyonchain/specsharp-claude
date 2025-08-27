import React from 'react';
import { Project } from '../../types';
import { formatCurrency, formatDate, getBuildingTypeDisplay } from '../../utils/formatters';
import { 
  Building, Home, Building2, Package, School, Heart,
  MapPin, Square, Calendar, TrendingUp, Clock, Trash2
} from 'lucide-react';

interface Props {
  projects: Project[];
  onProjectClick: (id: string) => void;
  onProjectDelete: (id: string) => void;
}

export const ProjectGrid: React.FC<Props> = ({ projects, onProjectClick, onProjectDelete }) => {
  if (projects.length === 0) {
    return (
      <div className="text-center py-16 bg-gradient-to-br from-gray-50 to-white rounded-xl border border-gray-100">
        <div className="p-8">
          <Building2 className="h-16 w-16 text-gray-300 mx-auto mb-4" />
          <p className="text-gray-500 text-lg">No projects yet</p>
          <p className="text-gray-400 text-sm mt-2">Create your first estimate to get started!</p>
        </div>
      </div>
    );
  }

  // Helper function to get building icon
  const getBuildingIcon = (type: string) => {
    const iconClass = "h-5 w-5";
    switch(type) {
      case 'multifamily': return <Home className={iconClass} />;
      case 'office': return <Building2 className={iconClass} />;
      case 'healthcare': return <Heart className={iconClass} />;
      case 'educational': return <School className={iconClass} />;
      case 'warehouse': return <Package className={iconClass} />;
      default: return <Building className={iconClass} />;
    }
  };

  // Helper function to get accent color based on building type
  const getAccentColor = (type: string) => {
    switch(type) {
      case 'multifamily': return 'from-blue-500 to-indigo-600';
      case 'office': return 'from-purple-500 to-indigo-600';
      case 'healthcare': return 'from-red-500 to-pink-600';
      case 'educational': return 'from-green-500 to-emerald-600';
      case 'warehouse': return 'from-orange-500 to-amber-600';
      default: return 'from-gray-500 to-slate-600';
    }
  };

  // Helper function to format relative time
  const formatRelativeTime = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    const diffMinutes = Math.floor(diffMs / (1000 * 60));

    if (diffMinutes < 60) {
      return `Updated ${diffMinutes} minute${diffMinutes !== 1 ? 's' : ''} ago`;
    } else if (diffHours < 24) {
      return `Updated ${diffHours} hour${diffHours !== 1 ? 's' : ''} ago`;
    } else if (diffDays === 1) {
      return 'Updated yesterday';
    } else if (diffDays < 7) {
      return `Updated ${diffDays} days ago`;
    } else {
      return `Updated ${date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}`;
    }
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {projects.map((project) => {
        const { parsed_input, calculations } = project.analysis;
        const buildingType = parsed_input.building_type || 'office';
        const accentGradient = getAccentColor(buildingType);
        
        return (
          <div
            key={project.id}
            className="group relative bg-white rounded-xl shadow-sm hover:shadow-xl transition-all duration-300 cursor-pointer overflow-hidden transform hover:-translate-y-1"
            onClick={() => onProjectClick(project.id)}
          >
            {/* Gradient accent bar */}
            <div className={`h-1 bg-gradient-to-r ${accentGradient}`}></div>
            
            <div className="p-6">
              {/* Header with icon and title */}
              <div className="flex items-start gap-3 mb-4">
                <div className={`p-2 rounded-lg bg-gradient-to-br ${accentGradient} bg-opacity-10 text-white`}>
                  <div className="opacity-80">
                    {getBuildingIcon(buildingType)}
                  </div>
                </div>
                <div className="flex-1 min-w-0">
                  <h3 className="font-bold text-lg text-gray-900 line-clamp-2 group-hover:text-blue-600 transition-colors">
                    {project.name}
                  </h3>
                  <p className="text-xs text-gray-500 mt-1 capitalize">
                    {getBuildingTypeDisplay(buildingType)}
                  </p>
                </div>
              </div>
              
              {/* Project details */}
              <div className="space-y-3">
                <div className="flex items-center gap-2 text-sm">
                  <MapPin className="h-4 w-4 text-gray-400" />
                  <span className="text-gray-600">{parsed_input.location}</span>
                </div>
                <div className="flex items-center gap-2 text-sm">
                  <Square className="h-4 w-4 text-gray-400" />
                  <span className="text-gray-600">
                    {parsed_input.square_footage.toLocaleString()} SF
                  </span>
                </div>
              </div>

              {/* Cost display */}
              <div className="mt-5 p-4 bg-gradient-to-r from-gray-50 to-blue-50 rounded-lg">
                <div className="flex justify-between items-center mb-2">
                  <span className="text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Construction
                  </span>
                  <span className="text-sm font-semibold text-gray-700">
                    {formatCurrency(calculations.totals.hard_costs || 0)}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Total Project
                  </span>
                  <span className="text-lg font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
                    {formatCurrency(calculations.totals.total_project_cost)}
                  </span>
                </div>
                <div className="flex items-center gap-1 mt-2">
                  <TrendingUp className="h-3 w-3 text-green-500" />
                  <span className="text-xs text-gray-600">
                    ${Math.round((calculations.totals.total_project_cost / parsed_input.square_footage) || 0)}/SF
                  </span>
                </div>
              </div>
              
              {/* Footer with timestamp and actions */}
              <div className="flex justify-between items-center mt-5 pt-4 border-t border-gray-100">
                <div className="flex items-center gap-1 text-xs text-gray-400">
                  <Clock className="h-3 w-3" />
                  <span>{formatRelativeTime(project.updated_at || project.created_at)}</span>
                </div>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    onProjectDelete(project.id);
                  }}
                  className="opacity-0 group-hover:opacity-100 transition-opacity duration-200 p-1.5 hover:bg-red-50 rounded-lg"
                  aria-label="Delete project"
                >
                  <Trash2 className="h-4 w-4 text-red-500 hover:text-red-600" />
                </button>
              </div>
            </div>

            {/* Hover overlay effect */}
            <div className="absolute inset-0 bg-gradient-to-t from-black/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none"></div>
          </div>
        );
      })}
    </div>
  );
};