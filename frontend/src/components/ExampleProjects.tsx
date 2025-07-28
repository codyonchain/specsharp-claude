import React from 'react';
import { EXAMPLE_PROJECTS, ExampleProject, getRandomExamples, getFeaturedExamples } from '../constants/exampleProjects';

interface ExampleProjectsProps {
  onSelect: (project: ExampleProject) => void;
  variant?: 'random' | 'featured' | 'all';
  count?: number;
  className?: string;
}

export const ExampleProjects: React.FC<ExampleProjectsProps> = ({ 
  onSelect, 
  variant = 'random',
  count = 4,
  className = '' 
}) => {
  let projects: ExampleProject[] = [];
  
  switch (variant) {
    case 'random':
      projects = getRandomExamples(count);
      break;
    case 'featured':
      projects = getFeaturedExamples();
      break;
    case 'all':
      projects = EXAMPLE_PROJECTS;
      break;
  }

  return (
    <div className={`${className}`}>
      <h3 className="text-lg font-semibold text-gray-800 mb-4">
        Example Projects
      </h3>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {projects.map((project, index) => (
          <ExampleProjectCard
            key={`${project.description}-${index}`}
            project={project}
            onSelect={onSelect}
          />
        ))}
      </div>
    </div>
  );
};

interface ExampleProjectCardProps {
  project: ExampleProject;
  onSelect: (project: ExampleProject) => void;
}

const ExampleProjectCard: React.FC<ExampleProjectCardProps> = ({ project, onSelect }) => {
  const categoryColors: Record<string, string> = {
    'Healthcare': 'bg-red-100 text-red-800',
    'Educational': 'bg-blue-100 text-blue-800',
    'Hospitality': 'bg-purple-100 text-purple-800',
    'Retail': 'bg-green-100 text-green-800',
    'Office': 'bg-gray-100 text-gray-800',
    'Restaurant': 'bg-orange-100 text-orange-800',
    'Multi-Family': 'bg-indigo-100 text-indigo-800',
    'Industrial': 'bg-yellow-100 text-yellow-800'
  };

  return (
    <button
      onClick={() => onSelect(project)}
      className="text-left p-4 border border-gray-200 rounded-lg hover:border-blue-300 hover:shadow-md transition-all duration-200 bg-white"
    >
      <div className="flex items-start justify-between mb-2">
        <span className={`inline-block px-2 py-1 text-xs font-semibold rounded-full ${categoryColors[project.category] || 'bg-gray-100 text-gray-800'}`}>
          {project.category}
        </span>
        <span className="text-sm text-gray-500">
          {project.location}
        </span>
      </div>
      <p className="text-sm text-gray-700 mb-2 line-clamp-2">
        {project.description}
      </p>
      <div className="flex items-center gap-4 text-xs text-gray-500">
        <span>{project.squareFootage.toLocaleString()} SF</span>
        <span>{project.floors} {project.floors === 1 ? 'Floor' : 'Floors'}</span>
      </div>
    </button>
  );
};

// Compact version for homepage
export const ExampleProjectsList: React.FC<{
  onSelect: (description: string) => void;
  className?: string;
}> = ({ onSelect, className = '' }) => {
  const examples = getRandomExamples(4);
  
  return (
    <div className={`${className}`}>
      <p className="text-sm text-gray-600 mb-2">Try an example:</p>
      <div className="space-y-2">
        {examples.map((project, index) => (
          <button
            key={`${project.description}-${index}`}
            onClick={() => onSelect(project.description)}
            className="block w-full text-left text-sm text-blue-600 hover:text-blue-800 hover:underline p-2 rounded hover:bg-blue-50 transition-colors"
          >
            {project.description}
          </button>
        ))}
      </div>
    </div>
  );
};

// Inline example selector for forms
export const InlineExampleSelector: React.FC<{
  onSelect: (description: string) => void;
  currentValue?: string;
}> = ({ onSelect, currentValue }) => {
  const [isOpen, setIsOpen] = React.useState(false);
  
  return (
    <div className="relative">
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className="text-sm text-blue-600 hover:text-blue-800 underline"
      >
        Try an example
      </button>
      
      {isOpen && (
        <>
          <div
            className="fixed inset-0 z-10"
            onClick={() => setIsOpen(false)}
          />
          <div className="absolute top-full left-0 mt-1 w-96 max-h-96 overflow-y-auto bg-white border border-gray-200 rounded-lg shadow-lg z-20">
            <div className="p-3">
              <h4 className="font-medium text-gray-700 mb-2">Example Projects</h4>
              {EXAMPLE_PROJECTS.map((project, index) => (
                <button
                  key={`${project.description}-${index}`}
                  onClick={() => {
                    onSelect(project.description);
                    setIsOpen(false);
                  }}
                  className={`w-full text-left p-2 text-sm rounded hover:bg-gray-100 ${
                    currentValue === project.description ? 'bg-blue-50 text-blue-700' : ''
                  }`}
                >
                  <div className="font-medium">{project.category}</div>
                  <div className="text-gray-600 line-clamp-2">{project.description}</div>
                </button>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  );
};