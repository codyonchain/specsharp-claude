import React from 'react';
import { COMMON_SIZES, CommonSize, getCommonSizesByCategory } from '../constants/commonSizes';

interface CommonSizeSelectorProps {
  category?: string;
  onSelect: (size: number) => void;
  className?: string;
}

export const CommonSizeSelector: React.FC<CommonSizeSelectorProps> = ({ 
  category, 
  onSelect,
  className = '' 
}) => {
  const sizes = category ? getCommonSizesByCategory(category) : COMMON_SIZES;
  
  const groupedSizes = sizes.reduce((acc, size) => {
    if (!acc[size.category]) {
      acc[size.category] = [];
    }
    acc[size.category].push(size);
    return acc;
  }, {} as Record<string, CommonSize[]>);

  const categoryDisplayNames: Record<string, string> = {
    office: 'Office Buildings',
    retail: 'Retail',
    restaurant: 'Restaurant',
    healthcare: 'Healthcare',
    educational: 'Educational',
    multi_family: 'Multi-Family Residential',
    warehouse: 'Warehouse',
    industrial: 'Industrial',
    hospitality: 'Hospitality'
  };

  return (
    <div className={`${className}`}>
      <h3 className="text-sm font-medium text-gray-700 mb-2">Quick Size Selection</h3>
      
      {category ? (
        // Single category view
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2">
          {sizes.map((size) => (
            <button
              key={size.label}
              onClick={() => onSelect(size.value)}
              className="text-left px-3 py-2 text-sm border border-gray-300 rounded-md hover:bg-blue-50 hover:border-blue-300 transition-colors"
            >
              <div className="font-medium">{size.label}</div>
              <div className="text-xs text-gray-500">{size.value.toLocaleString()} SF</div>
            </button>
          ))}
        </div>
      ) : (
        // All categories view
        <div className="space-y-4">
          {Object.entries(groupedSizes).map(([cat, catSizes]) => (
            <div key={cat}>
              <h4 className="text-xs font-semibold text-gray-600 uppercase tracking-wider mb-2">
                {categoryDisplayNames[cat] || cat}
              </h4>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-2">
                {catSizes.map((size) => (
                  <button
                    key={size.label}
                    onClick={() => onSelect(size.value)}
                    className="text-left px-3 py-2 text-sm border border-gray-300 rounded-md hover:bg-blue-50 hover:border-blue-300 transition-colors"
                  >
                    <div className="font-medium">{size.label}</div>
                    <div className="text-xs text-gray-500">{size.value.toLocaleString()} SF</div>
                  </button>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

// Inline quick selector for forms
export const InlineCommonSizeSelector: React.FC<{
  onSelect: (size: number) => void;
  currentValue?: number;
}> = ({ onSelect, currentValue }) => {
  const [isOpen, setIsOpen] = React.useState(false);
  
  return (
    <div className="relative">
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className="text-sm text-blue-600 hover:text-blue-800 underline"
      >
        Common sizes
      </button>
      
      {isOpen && (
        <>
          <div
            className="fixed inset-0 z-10"
            onClick={() => setIsOpen(false)}
          />
          <div className="absolute top-full left-0 mt-1 w-64 max-h-96 overflow-y-auto bg-white border border-gray-200 rounded-lg shadow-lg z-20">
            <div className="p-2">
              {COMMON_SIZES.map((size) => (
                <button
                  key={size.label}
                  onClick={() => {
                    onSelect(size.value);
                    setIsOpen(false);
                  }}
                  className={`w-full text-left px-3 py-2 text-sm rounded hover:bg-gray-100 ${
                    currentValue === size.value ? 'bg-blue-50 text-blue-700' : ''
                  }`}
                >
                  <div className="font-medium">{size.label}</div>
                  <div className="text-xs text-gray-500">{size.value.toLocaleString()} SF</div>
                </button>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  );
};