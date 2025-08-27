import React, { useState } from 'react';
import { Project } from '../../types';
import { ArrowLeft, FileSpreadsheet, HardHat, GitBranch } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import ScenarioBuilder from '../../../components/ScenarioBuilder';

interface Props {
  project: Project;
  onDelete: () => void;
  activeView: 'executive' | 'construction';
  onViewChange: (view: 'executive' | 'construction') => void;
}

export const ProjectHeader: React.FC<Props> = ({ project, onDelete, activeView, onViewChange }) => {
  const navigate = useNavigate();
  const [showScenarios, setShowScenarios] = useState(false);
  
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
        
        {/* Scenarios Button - Positioned absolutely */}
        <button
          onClick={() => setShowScenarios(true)}
          className="absolute top-4 right-4 flex items-center gap-2 bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 text-sm font-medium"
        >
          <GitBranch className="h-4 w-4" />
          Scenarios
        </button>
      </div>
      
      {/* Scenario Builder Modal */}
      {showScenarios && (
        <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-lg max-w-7xl w-full max-h-[90vh] overflow-y-auto">
            <ScenarioBuilder
              projectId={project.id}
              projectName={project.name}
              buildingType={project.analysis?.parsed_input?.building_type || 'restaurant'}
              baseProject={{
                // Pass the actual cost data from analysis
                id: project.id,
                name: project.name,
                building_type: project.analysis?.parsed_input?.building_type || 'restaurant',
                square_footage: project.analysis?.parsed_input?.square_footage || 4200,
                location: project.analysis?.parsed_input?.location || 'Nashville',
                
                // Financial data from calculations
                total_project_cost: project.analysis?.calculations?.totals?.total_project_cost || 0,
                totalCost: project.analysis?.calculations?.totals?.total_project_cost || 0,
                construction_cost: project.analysis?.calculations?.totals?.hard_costs || 0,
                constructionCost: project.analysis?.calculations?.totals?.hard_costs || 0,
                soft_costs: project.analysis?.calculations?.totals?.soft_costs || 0,
                softCosts: project.analysis?.calculations?.totals?.soft_costs || 0,
                contingency: project.analysis?.calculations?.totals?.contingency || 0,
                
                // Cost per SF
                cost_per_sqft: project.analysis?.calculations?.totals?.cost_per_sqft || 
                               (project.analysis?.calculations?.totals?.total_project_cost || 0) / 
                               (project.analysis?.parsed_input?.square_footage || 1),
                costPerSqft: project.analysis?.calculations?.totals?.cost_per_sqft || 
                             (project.analysis?.calculations?.totals?.total_project_cost || 0) / 
                             (project.analysis?.parsed_input?.square_footage || 1),
                
                // Financial metrics
                roi: project.analysis?.calculations?.ownership_analysis?.return_metrics?.roi || 0.087,
                payback_period: project.analysis?.calculations?.ownership_analysis?.return_metrics?.payback_period || 8.3,
                
                // Additional fields for scenario calculations
                finish_level: project.analysis?.parsed_input?.finish_level || 'standard',
                parking_type: project.analysis?.parsed_input?.parking_type || 'surface',
                floors: project.analysis?.parsed_input?.floors || 1,
                project_classification: project.analysis?.parsed_input?.project_classification || 'ground_up'
              }}
              onClose={() => setShowScenarios(false)}
            />
          </div>
        </div>
      )}
    </>
  );
};