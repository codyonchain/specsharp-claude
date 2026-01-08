import React from 'react';
import { Project } from '../../types';
import { formatCurrency } from '../../utils/formatters';

interface Props {
  projects: Project[];
}

export const DashboardStats: React.FC<Props> = ({ projects }) => {
  const totalValue = projects.reduce(
    (sum, p) => sum + p.analysis.calculations.totals.total_project_cost, 
    0
  );
  
  const totalSF = projects.reduce(
    (sum, p) => sum + p.analysis.parsed_input.square_footage, 
    0
  );
  
  const avgCostPerSF = totalSF > 0 ? totalValue / totalSF : 0;

  return (
    <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
      <div className="bg-white rounded-lg shadow-sm p-6">
        <p className="text-sm text-gray-500">Total Projects</p>
        <p className="text-2xl font-bold mt-1">{projects.length}</p>
      </div>
      
      <div className="bg-white rounded-lg shadow-sm p-6">
        <p className="text-sm text-gray-500">Total Value</p>
        <p className="text-2xl font-bold mt-1">{formatCurrency(totalValue)}</p>
      </div>
      
      <div className="bg-white rounded-lg shadow-sm p-6">
        <p className="text-sm text-gray-500">Total Square Feet</p>
        <p className="text-2xl font-bold mt-1">{totalSF.toLocaleString()} SF</p>
      </div>
      
      <div className="bg-white rounded-lg shadow-sm p-6">
        <p className="text-sm text-gray-500">Avg Cost/SF</p>
        <p className="text-2xl font-bold mt-1">{formatCurrency(avgCostPerSF)}</p>
      </div>
    </div>
  );
};