import React, { useState } from 'react';
import {
  FileText,
  FileSpreadsheet,
  Presentation,
  Mail,
  Cloud,
  File,
} from 'lucide-react';
import { api } from '../../api/client';
import { Project, Scenario, ComparisonResult } from './types';

interface ExportOptionsProps {
  scenarios: Scenario[];
  comparisonResult: ComparisonResult | null;
  project: Project;
}

const ExportOptions: React.FC<ExportOptionsProps> = ({
  scenarios,
  comparisonResult,
  project,
}) => {
  const [exporting, setExporting] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const handleExport = async (format: string) => {
    try {
      setExporting(format);
      setSuccess(null);

      const exportData = {
        project_id: project.id,
        project_name: project.name,
        scenarios: scenarios,
        comparison_result: comparisonResult,
        format: format,
      };

      const response = await api.client.post('/api/v2/export/comparison', exportData, {
        responseType: format === 'email' ? 'json' : 'blob',
      });

      if (format === 'email') {
        setSuccess('Report sent to your email successfully!');
      } else {
        // Create download link
        const blob = new Blob([response.data]);
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        
        const extension = format === 'powerpoint' ? 'pptx' : 
                        format === 'pdf' ? 'pdf' : 
                        format === 'excel' ? 'xlsx' : 'pdf';
        
        link.download = `${project.name}_scenario_comparison.${extension}`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
        
        setSuccess(`${format.charAt(0).toUpperCase() + format.slice(1)} exported successfully!`);
      }
    } catch (error) {
      console.error('Export failed:', error);
      setSuccess(null);
    } finally {
      setExporting(null);
    }
  };

  const exportOptions = [
    {
      id: 'powerpoint',
      icon: Presentation,
      title: 'PowerPoint Presentation',
      description: 'Board-ready slides with charts and recommendations',
      color: 'orange',
    },
    {
      id: 'pdf',
      icon: FileText,
      title: 'Executive Summary PDF',
      description: '2-page comparison with key metrics and charts',
      color: 'red',
    },
    {
      id: 'excel',
      icon: FileSpreadsheet,
      title: 'Detailed Excel Analysis',
      description: 'Full workbook with all calculations and data',
      color: 'green',
    },
    {
      id: 'word',
      icon: File,
      title: 'Word Report',
      description: 'Comprehensive narrative report with analysis',
      color: 'blue',
    },
    {
      id: 'email',
      icon: Mail,
      title: 'Email to Stakeholders',
      description: 'Send summary directly to team members',
      color: 'purple',
    },
    {
      id: 'cloud',
      icon: Cloud,
      title: 'Save to Cloud',
      description: 'Store comparison for future reference',
      color: 'cyan',
    },
  ];

  const getColorClasses = (color: string) => {
    const colors: Record<string, { bg: string; text: string; border: string }> = {
      orange: { bg: 'bg-orange-50', text: 'text-orange-600', border: 'hover:border-orange-500' },
      red: { bg: 'bg-red-50', text: 'text-red-600', border: 'hover:border-red-500' },
      green: { bg: 'bg-green-50', text: 'text-green-600', border: 'hover:border-green-500' },
      blue: { bg: 'bg-blue-50', text: 'text-blue-600', border: 'hover:border-blue-500' },
      purple: { bg: 'bg-purple-50', text: 'text-purple-600', border: 'hover:border-purple-500' },
      cyan: { bg: 'bg-cyan-50', text: 'text-cyan-600', border: 'hover:border-cyan-500' },
    };
    return colors[color] || colors.blue;
  };

  return (
    <div>
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          Export Comparison Results
        </h2>
        <p className="text-gray-600">
          Choose how you'd like to share or save this scenario comparison
        </p>
      </div>

      {success && (
        <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg">
          <div className="flex items-center justify-between">
            <p className="text-green-800">{success}</p>
            <button
              onClick={() => setSuccess(null)}
              className="text-green-600 hover:text-green-700"
            >
              ×
            </button>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {exportOptions.map(option => {
          const colorClasses = getColorClasses(option.color);
          const Icon = option.icon;
          
          return (
            <button
              key={option.id}
              onClick={() => !exporting && handleExport(option.id)}
              disabled={!!exporting}
              className={`p-6 rounded-lg border-2 border-transparent hover:shadow-lg transform hover:-translate-y-1 transition-all duration-200 text-left ${
                colorClasses.border
              } ${exporting === option.id ? 'opacity-50' : ''} ${
                exporting && exporting !== option.id ? 'opacity-30' : ''
              } disabled:cursor-not-allowed`}
            >
              <div className={`w-16 h-16 rounded-lg ${colorClasses.bg} flex items-center justify-center mb-4 mx-auto`}>
                {exporting === option.id ? (
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-current" />
                ) : (
                  <Icon className={`h-8 w-8 ${colorClasses.text}`} />
                )}
              </div>
              <h3 className="font-semibold text-gray-900 text-center mb-2">
                {option.title}
              </h3>
              <p className="text-sm text-gray-600 text-center">
                {option.description}
              </p>
            </button>
          );
        })}
      </div>

      <div className="mt-8 p-6 bg-gray-50 rounded-lg">
        <h3 className="text-lg font-semibold mb-4">What's Included in Each Export:</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h4 className="font-medium text-gray-900 mb-2">PowerPoint Presentation</h4>
            <ul className="text-sm text-gray-600 space-y-1">
              <li>• Executive summary slide</li>
              <li>• Cost comparison charts</li>
              <li>• Financial metrics table</li>
              <li>• Radar chart for performance</li>
              <li>• Recommendation slide</li>
              <li>• Detailed appendix</li>
            </ul>
          </div>
          <div>
            <h4 className="font-medium text-gray-900 mb-2">Excel Workbook</h4>
            <ul className="text-sm text-gray-600 space-y-1">
              <li>• Summary dashboard</li>
              <li>• Detailed calculations</li>
              <li>• Sensitivity analysis</li>
              <li>• Cash flow projections</li>
              <li>• NPV/IRR calculations</li>
              <li>• Custom charts</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ExportOptions;