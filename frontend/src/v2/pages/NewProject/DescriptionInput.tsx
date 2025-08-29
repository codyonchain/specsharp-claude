import React from 'react';

interface Props {
  value: string;
  onChange: (value: string) => void;
  onAnalyze: () => void;
  analyzing: boolean;
}

const EXAMPLES = [
  // Nashville/Tennessee Area Examples
  {
    category: "Healthcare",
    text: "Build a 200,000 SF hospital with emergency department in Nashville"
  },
  {
    category: "Restaurant",
    text: "Build a 4,200 SF full-service restaurant with bar and patio in Franklin TN"
  },
  {
    category: "Office",
    text: "Build an 85,000 SF Class A office tower with structured parking in Nashville"
  },
  {
    category: "Multifamily",
    text: "Build a 250-unit luxury apartment complex with amenity deck in Brentwood TN"
  },
  // Southern NH Examples
  {
    category: "Medical",
    text: "Build a 45,000 SF medical office building with imaging center in Manchester NH"
  },
  {
    category: "Industrial",
    text: "Build a 120,000 SF distribution warehouse with 24 loading docks in Nashua NH"
  },
  {
    category: "Retail",
    text: "Build a 35,000 SF neighborhood shopping center with grocery anchor in Concord NH"
  },
  {
    category: "Educational",
    text: "Build a 65,000 SF middle school for 800 students in Bedford NH"
  },
  {
    category: "Housing",
    text: "Build a 180-unit workforce housing development with community center in Salem NH"
  }
];

export const DescriptionInput: React.FC<Props> = ({ value, onChange, onAnalyze, analyzing }) => {
  return (
    <div className="bg-white rounded-lg shadow-sm p-6">
      <label className="block text-sm font-medium text-gray-700 mb-2">
        Describe Your Project
      </label>
      
      <textarea
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder="Enter a natural language description of your project..."
        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
        rows={4}
      />
      
      <div className="mt-4">
        <p className="text-sm text-gray-600 mb-2">Try an example:</p>
        <div className="flex flex-wrap gap-2">
          {EXAMPLES.map((example, i) => (
            <button
              key={i}
              onClick={() => onChange(example.text)}
              className="text-xs px-3 py-1.5 bg-gray-100 hover:bg-gray-200 rounded-full transition-colors"
              title={example.text}
            >
              {example.category}: {example.text.substring(0, 40)}...
            </button>
          ))}
        </div>
      </div>
      
      <button
        onClick={onAnalyze}
        disabled={!value.trim() || analyzing}
        className="mt-4 w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 transition-colors flex items-center justify-center"
      >
        {analyzing ? (
          <>
            <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent mr-2"></div>
            Analyzing...
          </>
        ) : (
          'Analyze Project'
        )}
      </button>
    </div>
  );
};
