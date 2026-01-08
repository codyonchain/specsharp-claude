import React from 'react';

interface Props {
  onNewProject: () => void;
}

export const DashboardHeader: React.FC<Props> = ({ onNewProject }) => {
  return (
    <div className="bg-white shadow">
      <div className="max-w-7xl mx-auto px-4 py-6">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Projects Dashboard</h1>
            <p className="mt-1 text-gray-600">
              Manage your construction cost estimates
            </p>
          </div>
          <button
            onClick={onNewProject}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium"
          >
            + New Project
          </button>
        </div>
      </div>
    </div>
  );
};