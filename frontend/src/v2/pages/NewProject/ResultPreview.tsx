import React from 'react';

interface Props {
  result: any;
  onSave: () => void;
  onReset: () => void;
  saving: boolean;
}

export const ResultPreview: React.FC<Props> = ({ result, onSave, onReset, saving }) => {
  if (!result || !result.calculations) {
    return <div>No results to display</div>;
  }
  
  const costs = result.calculations;
  
  return (
    <div className="bg-white rounded-lg shadow-sm p-6">
      <h3 className="text-lg font-semibold mb-4">Project Analysis Results</h3>
      
      <div className="grid grid-cols-2 gap-4 mb-6">
        <div className="bg-gray-50 p-4 rounded">
          <div className="text-sm text-gray-600">Building Type</div>
          <div className="font-semibold capitalize">
            {result.parsed_input?.building_type} - {result.parsed_input?.subtype}
          </div>
        </div>
        
        <div className="bg-gray-50 p-4 rounded">
          <div className="text-sm text-gray-600">Square Footage</div>
          <div className="font-semibold">
            {result.parsed_input?.square_footage?.toLocaleString()} SF
          </div>
        </div>
        
        <div className="bg-gray-50 p-4 rounded">
          <div className="text-sm text-gray-600">Location</div>
          <div className="font-semibold">{result.parsed_input?.location}</div>
        </div>
        
        <div className="bg-gray-50 p-4 rounded">
          <div className="text-sm text-gray-600">Project Class</div>
          <div className="font-semibold capitalize">
            {result.parsed_input?.project_class?.replace('_', ' ')}
          </div>
        </div>
      </div>
      
      <div className="border-t pt-4">
        <h4 className="font-semibold mb-3">Cost Summary</h4>
        
        <div className="space-y-2">
          <div className="flex justify-between">
            <span className="text-gray-600">Hard Costs:</span>
            <span className="font-semibold">
              ${(costs.totals?.hard_costs / 1000000).toFixed(1)}M
            </span>
          </div>
          
          <div className="flex justify-between">
            <span className="text-gray-600">Soft Costs:</span>
            <span className="font-semibold">
              ${(costs.totals?.soft_costs / 1000000).toFixed(1)}M
            </span>
          </div>
          
          <div className="flex justify-between text-lg font-bold border-t pt-2">
            <span>Total Project Cost:</span>
            <span className="text-blue-600">
              ${(costs.totals?.total_project_cost / 1000000).toFixed(1)}M
            </span>
          </div>
          
          <div className="flex justify-between text-sm text-gray-600">
            <span>Cost per SF:</span>
            <span>${costs.totals?.cost_per_sf?.toFixed(0)}/SF</span>
          </div>
        </div>
      </div>
      
      <div className="border-t pt-4 mt-4">
        <h4 className="font-semibold mb-3">Hospital Details</h4>
        <div className="text-sm space-y-1">
          <div>Base Cost: ${costs.construction_costs?.base_cost_per_sf}/SF</div>
          <div>Equipment Cost: ${(costs.construction_costs?.equipment_total / 1000000).toFixed(1)}M</div>
        </div>
      </div>
      
      <div className="flex gap-3 mt-6">
        <button
          onClick={onSave}
          disabled={saving}
          className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300"
        >
          {saving ? 'Saving...' : 'Save Project'}
        </button>
        
        <button
          onClick={onReset}
          className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
        >
          Start Over
        </button>
      </div>
    </div>
  );
};
