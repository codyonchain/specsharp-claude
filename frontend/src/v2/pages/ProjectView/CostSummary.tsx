import React from 'react';
import { ConstructionCosts, ProjectTotals } from '../../types';
import { formatCurrency } from '../../utils/formatters';

interface Props {
  costs: ConstructionCosts;
  totals: ProjectTotals;
}

export const CostSummary: React.FC<Props> = ({ costs, totals }) => {
  return (
    <div className="bg-white rounded-lg shadow-sm p-6">
      <h2 className="text-xl font-bold mb-4">Cost Summary</h2>
      
      <div className="space-y-3">
        <div className="flex justify-between items-center">
          <span className="text-gray-600">Base Cost/SF</span>
          <span className="font-medium">{formatCurrency(costs.base_cost_per_sf)}</span>
        </div>
        
        <div className="flex justify-between items-center">
          <span className="text-gray-600">Regional Multiplier</span>
          <span className="font-medium">{(costs.regional_multiplier * 100).toFixed(0)}%</span>
        </div>
        
        <div className="flex justify-between items-center">
          <span className="text-gray-600">Final Cost/SF</span>
          <span className="font-medium">{formatCurrency(costs.final_cost_per_sf)}</span>
        </div>
        
        <div className="border-t pt-3">
          <div className="flex justify-between items-center">
            <span className="text-gray-600">Construction</span>
            <span className="font-medium">{formatCurrency(costs.construction_total)}</span>
          </div>
          
          <div className="flex justify-between items-center mt-2">
            <span className="text-gray-600">Equipment</span>
            <span className="font-medium">{formatCurrency(costs.equipment_total)}</span>
          </div>
          
          <div className="flex justify-between items-center mt-2">
            <span className="text-gray-600">Soft Costs</span>
            <span className="font-medium">{formatCurrency(totals.soft_costs)}</span>
          </div>
        </div>
        
        <div className="border-t pt-3">
          <div className="flex justify-between items-center">
            <span className="text-lg font-semibold">Total Project Cost</span>
            <span className="text-2xl font-bold text-blue-600">
              {formatCurrency(totals.total_project_cost)}
            </span>
          </div>
          <div className="flex justify-between items-center mt-1">
            <span className="text-sm text-gray-500">Total per SF</span>
            <span className="text-sm font-medium">
              {formatCurrency(totals.cost_per_sf)}/SF
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};