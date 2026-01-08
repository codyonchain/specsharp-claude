import React from 'react';
import {
  Sparkles,
  Square,
  Car,
  Calendar,
  Building,
  DollarSign,
  Wrench,
  TreePine,
} from 'lucide-react';

interface ScenarioTemplatesProps {
  onSelectTemplate: (template: string) => void;
}

const templates = [
  {
    id: 'finish_level',
    icon: Sparkles,
    title: 'Finish Level',
    description: 'Compare standard vs premium finishes',
    color: 'purple',
  },
  {
    id: 'size',
    icon: Square,
    title: 'Project Size',
    description: 'Analyze ±20% square footage',
    color: 'blue',
  },
  {
    id: 'parking',
    icon: Car,
    title: 'Parking Options',
    description: 'Surface vs garage vs none',
    color: 'green',
  },
  {
    id: 'phasing',
    icon: Calendar,
    title: 'Phasing Strategy',
    description: 'Single vs multi-phase construction',
    color: 'orange',
  },
  {
    id: 'floors',
    icon: Building,
    title: 'Building Height',
    description: 'Compare different floor counts',
    color: 'cyan',
  },
  {
    id: 'value_engineering',
    icon: DollarSign,
    title: 'Value Engineering',
    description: 'Optimize cost without sacrificing quality',
    color: 'lime',
  },
  {
    id: 'sustainability',
    icon: TreePine,
    title: 'Sustainability',
    description: 'Standard vs LEED Silver/Gold',
    color: 'emerald',
  },
  {
    id: 'amenities',
    icon: Wrench,
    title: 'Amenities',
    description: 'Basic vs enhanced amenity packages',
    color: 'pink',
  },
];

const getColorClasses = (color: string) => {
  const colors: Record<string, { bg: string; text: string; hover: string }> = {
    purple: { bg: 'bg-purple-100', text: 'text-purple-600', hover: 'hover:border-purple-500' },
    blue: { bg: 'bg-blue-100', text: 'text-blue-600', hover: 'hover:border-blue-500' },
    green: { bg: 'bg-green-100', text: 'text-green-600', hover: 'hover:border-green-500' },
    orange: { bg: 'bg-orange-100', text: 'text-orange-600', hover: 'hover:border-orange-500' },
    cyan: { bg: 'bg-cyan-100', text: 'text-cyan-600', hover: 'hover:border-cyan-500' },
    lime: { bg: 'bg-lime-100', text: 'text-lime-600', hover: 'hover:border-lime-500' },
    emerald: { bg: 'bg-emerald-100', text: 'text-emerald-600', hover: 'hover:border-emerald-500' },
    pink: { bg: 'bg-pink-100', text: 'text-pink-600', hover: 'hover:border-pink-500' },
  };
  return colors[color] || colors.blue;
};

const ScenarioTemplates: React.FC<ScenarioTemplatesProps> = ({ onSelectTemplate }) => {
  return (
    <div>
      <div className="text-center mb-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          What would you like to compare?
        </h2>
        <p className="text-gray-600">
          Choose a template to quickly create scenarios, or start from scratch
        </p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4">
        {templates.map(template => {
          const colorClasses = getColorClasses(template.color);
          const Icon = template.icon;
          
          return (
            <button
              key={template.id}
              onClick={() => onSelectTemplate(template.id)}
              className={`p-4 rounded-lg border-2 border-transparent hover:shadow-lg transform hover:-translate-y-1 transition-all duration-200 text-left ${colorClasses.hover}`}
            >
              <div className={`w-12 h-12 rounded-lg ${colorClasses.bg} flex items-center justify-center mb-3`}>
                <Icon className={`h-6 w-6 ${colorClasses.text}`} />
              </div>
              <h3 className="font-semibold text-gray-900 mb-1">
                {template.title}
              </h3>
              <p className="text-sm text-gray-600">
                {template.description}
              </p>
            </button>
          );
        })}
      </div>

      <div className="mt-8 text-center">
        <p className="text-sm text-gray-600 mb-3">
          Or create your own custom scenario
        </p>
        <button
          onClick={() => onSelectTemplate('custom')}
          className="px-6 py-3 border-2 border-gray-300 rounded-lg hover:bg-gray-50 transition font-medium"
        >
          + Create Custom Scenario
        </button>
      </div>
    </div>
  );
};

export default ScenarioTemplates;