import React from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Plus, Building2, ArrowRight, MapPin,
  Trash2, Square, Clock, TrendingUp,
  Home, Heart, School, Package, Building
} from 'lucide-react';
import { formatCurrency, formatNumber } from '../../utils/formatters';
import { formatters } from '../../utils/displayFormatters';
import { useProjects } from '../../hooks/useProjects';

export const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const { projects, loading, error, deleteProject } = useProjects();

  const handleDelete = async (id: string) => {
    try {
      await deleteProject(id);
    } catch (err) {
      console.error('Failed to delete project:', err);
    }
  };

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


  const quickTemplates = [
    { name: 'Hospital', icon: '🏥', color: 'from-red-400 to-pink-500', sqft: 200000, type: 'healthcare' },
    { name: 'School', icon: '🏫', color: 'from-yellow-400 to-orange-500', sqft: 95000, type: 'educational' },
    { name: 'Office Tower', icon: '🏢', color: 'from-blue-400 to-indigo-500', sqft: 150000, type: 'commercial' },
    { name: 'Hotel', icon: '🏨', color: 'from-purple-400 to-pink-500', sqft: 125000, type: 'hospitality' },
    { name: 'Apartments', icon: '🏘️', color: 'from-teal-400 to-cyan-500', sqft: 180000, type: 'residential' }
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Projects Dashboard</h1>
              <p className="text-sm text-gray-500">Manage your construction cost estimates</p>
            </div>
            <button 
              onClick={() => navigate('/new')}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition flex items-center gap-2"
            >
              <Plus className="h-4 w-4" />
              New Project
            </button>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-6 py-8">
        {error && (
          <div className="mb-4 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
            {error.message || 'Failed to load projects'}
          </div>
        )}

        {/* Projects Grid */}
        {loading ? (
          <div className="bg-white rounded-lg p-12 text-center mb-8">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-gray-600">Loading your projects...</p>
          </div>
        ) : projects.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
            {projects.map((project) => {
              const analysis = project.analysis;
              if (!analysis) return null;
              
              const { parsed_input, calculations } = analysis;
              const totals = calculations?.totals || {};
              const construction_costs = calculations?.construction_costs || {};
              const buildingType = parsed_input.building_type || 'office';
              const accentGradient = getAccentColor(buildingType);
              const description = project.description || `Build a ${formatNumber(parsed_input.square_footage)} SF ${parsed_input.building_type} with standard features in ${parsed_input.location}`;
              const projectName = project.name || description.split(' ').slice(0, 8).join(' ') + '...';
              
              return (
                <div
                  key={project.id}
                  className="group relative bg-white rounded-xl shadow-sm hover:shadow-xl transition-all duration-300 cursor-pointer overflow-hidden transform hover:-translate-y-1"
                  onClick={() => navigate(`/project/${project.id}`)}
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
                          {projectName}
                        </h3>
                        <p className="text-xs text-gray-500 mt-1 capitalize">
                          {buildingType.replace('_', ' ')}
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
                          {formatCurrency(totals?.hard_costs || construction_costs?.construction_total || 0)}
                        </span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Total Project
                        </span>
                        <span className="text-lg font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
                          {formatCurrency(totals?.total_project_cost || 0)}
                        </span>
                      </div>
                      <div className="flex items-center gap-1 mt-2">
                        <TrendingUp className="h-3 w-3 text-green-500" />
                        <span className="text-xs text-gray-600">
                          ${Math.round((totals?.total_project_cost / parsed_input?.square_footage) || 0)}/SF
                        </span>
                      </div>
                    </div>
                    
                    {/* Footer with timestamp and actions */}
                    <div className="flex justify-between items-center mt-5 pt-4 border-t border-gray-100">
                      <div className="flex items-center gap-1 text-xs text-gray-400">
                        <Clock className="h-3 w-3" />
                        <span>{formatters.relativeTime(project.updated_at || project.created_at || project.createdAt || Date.now().toString())}</span>
                      </div>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleDelete(project.id);
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
        ) : (
          <div className="bg-white rounded-lg p-12 text-center mb-8">
            <Building2 className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">No projects yet</h3>
            <p className="text-gray-500 mb-6">Start by creating your first construction estimate</p>
            <button 
              onClick={() => navigate('/new')}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition inline-flex items-center gap-2"
            >
              <Plus className="h-5 w-5" />
              Create First Project
            </button>
          </div>
        )}

        {/* Quick Start Templates */}
        <div>
          <h2 className="text-xl font-bold text-gray-900 mb-4">Quick Start Templates</h2>
          <p className="text-sm text-gray-500 mb-6">Start with a pre-configured template</p>
          
          <div className="grid grid-cols-5 gap-4">
            {quickTemplates.map((template) => (
              <button
                key={template.name}
                onClick={() => navigate('/new')}
                className={`relative overflow-hidden rounded-xl p-6 text-white transition-all hover:scale-105 hover:shadow-xl bg-gradient-to-br ${template.color}`}
              >
                <div className="text-4xl mb-3">{template.icon}</div>
                <p className="font-bold">{template.name}</p>
                <p className="text-sm opacity-90">{formatNumber(template.sqft)} SF</p>
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
