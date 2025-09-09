import React from 'react';
import { 
  Calculator, 
  TrendingUp, 
  Target, 
  HelpCircle,
  CheckCircle,
  AlertTriangle,
  XCircle
} from 'lucide-react';
import { FinancialRequirements } from '../../types';

interface Props {
  requirements: FinancialRequirements;
  isVisible?: boolean;
}

export const FinancialRequirementsCard: React.FC<Props> = ({ 
  requirements, 
  isVisible = true 
}) => {
  if (!isVisible || !requirements) return null;

  const getStatusIcon = (status?: string) => {
    switch (status) {
      case 'green':
        return <CheckCircle className="h-4 w-4 text-green-600" />;
      case 'yellow':
        return <AlertTriangle className="h-4 w-4 text-yellow-600" />;
      case 'red':
        return <XCircle className="h-4 w-4 text-red-600" />;
      default:
        return null;
    }
  };

  const getStatusColor = (status?: string) => {
    switch (status) {
      case 'green':
        return 'text-green-700';
      case 'yellow':
        return 'text-yellow-700';
      case 'red':
        return 'text-red-700';
      default:
        return 'text-gray-700';
    }
  };

  const getSectionIcon = (title: string) => {
    if (title.toLowerCase().includes('primary')) return Calculator;
    if (title.toLowerCase().includes('performance')) return Target;
    if (title.toLowerCase().includes('market')) return TrendingUp;
    return Calculator;
  };

  const getSectionClasses = (index: number) => {
    const classes = [
      { bg: 'bg-blue-50', text: 'text-blue-600' },
      { bg: 'bg-green-50', text: 'text-green-600' },
      { bg: 'bg-purple-50', text: 'text-purple-600' }
    ];
    return classes[index % classes.length];
  };

  const sections = [
    requirements.primary_metrics,
    requirements.performance_targets,
    requirements.market_analysis
  ].filter(section => section && section.metrics && section.metrics.length > 0);

  return (
    <div className="bg-white rounded-xl shadow-lg overflow-hidden border border-gray-200">
      <div className="bg-gradient-to-r from-indigo-500 to-purple-600 px-6 py-4">
        <h3 className="text-lg font-bold text-white flex items-center gap-2">
          <Calculator className="h-5 w-5" />
          Hospital Financial Requirements
        </h3>
        <p className="text-sm text-indigo-100">
          Investment metrics required for sustainable operations
        </p>
      </div>

      <div className="p-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {sections.map((section, sectionIndex) => {
            const SectionIcon = getSectionIcon(section.title);
            const colorClasses = getSectionClasses(sectionIndex);
            
            return (
              <div key={sectionIndex} className="space-y-4">
                <div className="flex items-center gap-2 mb-4">
                  <div className={`p-2 ${colorClasses.bg} rounded-lg`}>
                    <SectionIcon className={`h-5 w-5 ${colorClasses.text}`} />
                  </div>
                  <h4 className="font-semibold text-gray-900">{String(section.title || '')}</h4>
                </div>

                <div className="space-y-3">
                  {section.metrics.map((metric, metricIndex) => (
                    <div key={metricIndex} className="bg-gray-50 rounded-lg p-4">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-2">
                            <span className="text-sm font-medium text-gray-600">
                              {String(metric.label || '')}
                            </span>
                            {metric.tooltip && (
                              <div className="group relative">
                                <HelpCircle className="h-3 w-3 text-gray-400 cursor-help" />
                                <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-2 py-1 bg-gray-800 text-white text-xs rounded opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none whitespace-nowrap z-10">
                                  {String(metric.tooltip || '')}
                                </div>
                              </div>
                            )}
                          </div>
                          <p className={`text-lg font-bold mt-1 ${getStatusColor(metric.status)}`}>
                            {String(metric.value || '')}
                          </p>
                        </div>
                        <div className="flex items-center gap-1 ml-2">
                          {getStatusIcon(metric.status)}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            );
          })}
        </div>

        {sections.length === 0 && (
          <div className="text-center py-8 text-gray-500">
            <Calculator className="h-12 w-12 mx-auto mb-4 text-gray-300" />
            <p>Financial requirements data is not available for this project type.</p>
          </div>
        )}
      </div>
    </div>
  );
};