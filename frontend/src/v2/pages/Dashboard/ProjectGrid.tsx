import React from 'react';
import { Project } from '../../types';
import { formatCurrency, formatDate, getBuildingTypeDisplay } from '../../utils/formatters';

interface Props {
  projects: Project[];
  onProjectClick: (id: string) => void;
  onProjectDelete: (id: string) => void;
}

export const ProjectGrid: React.FC<Props> = ({ projects, onProjectClick, onProjectDelete }) => {
  if (projects.length === 0) {
    return (
      <div className="text-center py-12 bg-white rounded-lg">
        <p className="text-gray-500">No projects yet. Create your first estimate!</p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {projects.map((project) => {
        const { parsed_input, calculations } = project.analysis;
        
        return (
          <div
            key={project.id}
            className="bg-white rounded-lg shadow-sm hover:shadow-md transition cursor-pointer"
            onClick={() => onProjectClick(project.id)}
          >
            <div className="p-6">
              <h3 className="font-semibold text-lg mb-2 line-clamp-2">
                {project.name}
              </h3>
              
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-500">Type</span>
                  <span>{getBuildingTypeDisplay(parsed_input.building_type)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">Size</span>
                  <span>{parsed_input.square_footage.toLocaleString()} SF</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">Location</span>
                  <span>{parsed_input.location}</span>
                </div>
                <div className="flex justify-between font-semibold">
                  <span>Total Cost</span>
                  <span className="text-blue-600">
                    {formatCurrency(calculations.totals.total_project_cost)}
                  </span>
                </div>
              </div>
              
              <div className="flex justify-between items-center mt-4 pt-4 border-t">
                <span className="text-xs text-gray-500">
                  {formatDate(project.created_at)}
                </span>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    onProjectDelete(project.id);
                  }}
                  className="text-red-600 hover:text-red-700 text-sm"
                >
                  Delete
                </button>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
};