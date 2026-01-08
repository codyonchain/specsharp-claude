/**
 * BuildingTypeSelector - Type selection component
 * Replaces: Type selection portion of ScopeGenerator
 */

import React from 'react';

interface Props {
  buildingType: string;
  subtype: string;
  onChange: (type: string, subtype: string) => void;
}

// Building types configuration
const BUILDING_TYPES = {
  healthcare: {
    label: 'Healthcare',
    subtypes: ['hospital', 'medical_office', 'urgent_care']
  },
  multifamily: {
    label: 'Multifamily',
    subtypes: ['luxury_apartments', 'market_rate_apartments', 'affordable_housing']
  },
  office: {
    label: 'Office',
    subtypes: ['class_a', 'class_b']
  },
  retail: {
    label: 'Retail',
    subtypes: ['shopping_center', 'big_box']
  },
  industrial: {
    label: 'Industrial',
    subtypes: ['warehouse', 'distribution_center', 'manufacturing', 'flex_space']
  },
  hospitality: {
    label: 'Hospitality',
    subtypes: ['full_service_hotel', 'limited_service_hotel']
  },
  educational: {
    label: 'Educational',
    subtypes: ['elementary_school', 'middle_school', 'high_school', 'university']
  }
};

export const BuildingTypeSelector: React.FC<Props> = ({ 
  buildingType, 
  subtype, 
  onChange 
}) => {
  const formatSubtype = (sub: string) => {
    return sub.split('_').map(word => 
      word.charAt(0).toUpperCase() + word.slice(1)
    ).join(' ');
  };

  return (
    <div className="bg-white rounded-lg shadow-sm p-6">
      <h3 className="text-lg font-semibold mb-4">Building Type</h3>
      
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Type
          </label>
          <select
            value={buildingType}
            onChange={(e) => {
              const newType = e.target.value;
              const firstSubtype = BUILDING_TYPES[newType as keyof typeof BUILDING_TYPES]?.subtypes[0] || '';
              onChange(newType, firstSubtype);
            }}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
          >
            {Object.entries(BUILDING_TYPES).map(([key, config]) => (
              <option key={key} value={key}>
                {config.label}
              </option>
            ))}
          </select>
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Subtype
          </label>
          <select
            value={subtype}
            onChange={(e) => onChange(buildingType, e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
          >
            {BUILDING_TYPES[buildingType as keyof typeof BUILDING_TYPES]?.subtypes.map(sub => (
              <option key={sub} value={sub}>
                {formatSubtype(sub)}
              </option>
            ))}
          </select>
        </div>
      </div>
      
      <div className="mt-4 p-3 bg-blue-50 rounded-lg">
        <p className="text-sm text-blue-700">
          Auto-detected from your description. You can adjust if needed.
        </p>
      </div>
    </div>
  );
};
