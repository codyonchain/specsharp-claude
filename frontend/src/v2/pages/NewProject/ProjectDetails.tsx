/**
 * ProjectDetails - Detailed project configuration
 * Replaces: Details portion of ScopeGenerator
 */

import React from 'react';

interface Props {
  data: any;
  onChange: (data: any) => void;
}

export const ProjectDetails: React.FC<Props> = ({ data, onChange }) => {
  return (
    <div className="bg-white rounded-lg shadow-sm p-6">
      <h3 className="text-lg font-semibold mb-4">Project Details</h3>
      
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Square Footage
          </label>
          <input
            type="number"
            value={data.square_footage || ''}
            onChange={(e) => onChange({
              ...data,
              square_footage: parseInt(e.target.value) || 0
            })}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
            placeholder="e.g., 50000"
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Location
          </label>
          <input
            type="text"
            value={data.location || ''}
            onChange={(e) => onChange({
              ...data,
              location: e.target.value
            })}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
            placeholder="e.g., Nashville"
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Number of Floors
          </label>
          <input
            type="number"
            value={data.floors || ''}
            onChange={(e) => onChange({
              ...data,
              floors: parseInt(e.target.value) || null
            })}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
            placeholder="Auto-detect"
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Project Classification
          </label>
          <select
            value={data.project_class || 'ground_up'}
            onChange={(e) => onChange({
              ...data,
              project_class: e.target.value
            })}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="ground_up">Ground-Up Construction</option>
            <option value="addition">Addition</option>
            <option value="renovation">Renovation</option>
            <option value="tenant_improvement">Tenant Improvement</option>
          </select>
        </div>
      </div>
      
      <div className="mt-4">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Special Features (Optional)
        </label>
        <div className="flex flex-wrap gap-2">
          {['emergency_department', 'imaging_center', 'surgery_center', 'parking_garage'].map(feature => (
            <button
              key={feature}
              onClick={() => {
                const features = data.special_features || [];
                const newFeatures = features.includes(feature)
                  ? features.filter((f: string) => f !== feature)
                  : [...features, feature];
                onChange({ ...data, special_features: newFeatures });
              }}
              className={`px-3 py-1 rounded-full text-sm ${
                (data.special_features || []).includes(feature)
                  ? 'bg-blue-100 text-blue-700 border-blue-300'
                  : 'bg-gray-100 text-gray-700 border-gray-300'
              } border`}
            >
              {feature.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};
