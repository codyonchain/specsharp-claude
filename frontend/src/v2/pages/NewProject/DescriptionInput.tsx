import React from 'react';

interface Props {
  value: string;
  onChange: (value: string) => void;
  onAnalyze: () => void;
  analyzing: boolean;
}

const EXAMPLES = [
  {
    category: "Healthcare",
    text: "Build a 200,000 SF hospital with emergency department in Nashville"
  },
  {
    category: "Healthcare",
    text: "Build a 50,000 SF medical office building with imaging center in Nashville"
  },
  {
    category: "Multifamily",
    text: "Build a 300,000 SF luxury apartment complex with 300 units and rooftop amenities in Nashville"
  },
  {
    category: "Multifamily",
    text: "Build a 150,000 SF affordable housing development with 200 units in Memphis"
  },
  {
    category: "Office",
    text: "Build a 50,000 SF Class A office building with 5 floors in downtown Nashville"
  },
  {
    category: "Office", 
    text: "Build a 100,000 SF Class A office tower with 20 floors in New York"
  },
  {
    category: "Retail",
    text: "Build a 25,000 SF shopping center with anchor tenant space in Nashville"
  },
  {
    category: "Industrial",
    text: "Build a 150,000 SF distribution center with 40 foot clear height near Nashville airport"
  },
  {
    category: "Hospitality",
    text: "Build a 100,000 SF full service hotel with 150 rooms and restaurant in Nashville"
  },
  {
    category: "Educational",
    text: "Build a 75,000 SF elementary school for 500 students in Nashville"
  },
  {
    category: "Parking",
    text: "Build a 200,000 SF parking garage with 600 spaces on 5 levels in Nashville"
  },
  {
    category: "Specialty",
    text: "Build a 50,000 SF data center with redundant power systems in Nashville"
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
