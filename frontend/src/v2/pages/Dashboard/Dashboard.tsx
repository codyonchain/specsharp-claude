import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Plus, Building2, ArrowRight, MapPin,
  Trash2, Square
} from 'lucide-react';
import { Project } from '../../types';
import { formatCurrency, formatNumber } from '../../utils/formatters';

export const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const [projects, setProjects] = useState<Project[]>([]);

  useEffect(() => {
    // Load projects from localStorage
    const loadProjects = () => {
      try {
        const stored = localStorage.getItem('specsharp_projects');
        if (stored) {
          const parsed = JSON.parse(stored);
          setProjects(Array.isArray(parsed) ? parsed : []);
        }
      } catch (error) {
        console.error('Error loading projects:', error);
        setProjects([]);
      }
    };
    
    loadProjects();
    
    // Listen for storage events (when projects are added/updated)
    window.addEventListener('storage', loadProjects);
    
    // Check for updates every second (for same-tab updates)
    const interval = setInterval(loadProjects, 1000);
    
    return () => {
      window.removeEventListener('storage', loadProjects);
      clearInterval(interval);
    };
  }, []);

  const handleDelete = (id: string) => {
    const updated = projects.filter(p => p.id !== id);
    setProjects(updated);
    localStorage.setItem('specsharp_projects', JSON.stringify(updated));
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
        {/* Projects Grid */}
        {projects.length > 0 ? (
          <div className="grid grid-cols-3 gap-6 mb-8">
            {projects.map((project) => {
              const analysis = project.analysis;
              if (!analysis) return null;
              
              const { parsed_input, calculations } = analysis;
              const { totals, construction_costs } = calculations;
              const description = project.description || `Build a ${formatNumber(parsed_input.square_footage)} SF ${parsed_input.building_type} with standard features in ${parsed_input.location}`;
              
              return (
                <div
                  key={project.id}
                  className="bg-white rounded-lg shadow-sm border border-gray-200 hover:shadow-lg transition-shadow cursor-pointer"
                  onClick={() => navigate(`/project/${project.id}`)}
                >
                  <div className="p-6">
                    <div className="flex justify-between items-start mb-4">
                      <h3 className="font-semibold text-gray-900 text-lg">
                        {description.split(' ').slice(0, 8).join(' ')}...
                      </h3>
                      <button 
                        onClick={(e) => {
                          e.stopPropagation();
                          handleDelete(project.id);
                        }}
                        className="text-red-500 hover:bg-red-50 p-1 rounded"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </div>
                    
                    <div className="space-y-2 mb-4">
                      <div className="flex items-center gap-2 text-sm text-gray-600">
                        <Building2 className="h-4 w-4" />
                        <span className="font-medium capitalize">{parsed_input.building_type}</span>
                      </div>
                      <div className="flex items-center gap-2 text-sm text-gray-600">
                        <Square className="h-4 w-4" />
                        <span>{formatNumber(parsed_input.square_footage)} SF</span>
                      </div>
                      <div className="flex items-center gap-2 text-sm text-gray-600">
                        <MapPin className="h-4 w-4" />
                        <span>{parsed_input.location}</span>
                      </div>
                    </div>
                    
                    <div className="pt-4 border-t border-gray-100 space-y-2">
                      <div>
                        <span className="text-sm text-gray-500">Construction Cost</span>
                        <p className="text-xl font-bold text-gray-900">
                          {formatCurrency(construction_costs.construction_total)}
                        </p>
                      </div>
                      <div>
                        <span className="text-sm text-gray-500">Total Project Cost</span>
                        <p className="text-2xl font-bold text-blue-600">
                          {formatCurrency(totals.total_project_cost)}
                        </p>
                      </div>
                    </div>
                    
                    <div className="flex items-center justify-between text-xs text-gray-500 mt-4">
                      <span>{new Date(project.createdAt || project.created_at || Date.now()).toLocaleDateString()}</span>
                      <button className="text-blue-600 hover:underline flex items-center gap-1">
                        View Details
                        <ArrowRight className="h-3 w-3" />
                      </button>
                    </div>
                  </div>
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