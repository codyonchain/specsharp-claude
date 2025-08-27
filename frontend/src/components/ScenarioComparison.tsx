import React, { useState, useEffect } from 'react';
import {
  Plus,
  Copy,
  Trash2,
  Edit2,
  Check,
  X,
  Download,
  BarChart3,
  TrendingUp,
  DollarSign,
  Clock,
  Target,
  AlertCircle,
  ChevronDown,
  ChevronRight
} from 'lucide-react';
import scenarioApi, { ProjectScenario, ScenarioComparison, ModificationOptions } from '../services/scenarioApi';
import { formatCurrency, formatPercentage } from '../utils/formatters';

interface ScenarioComparisonProps {
  projectId: string;
  projectName: string;
  buildingType: string;
  onClose?: () => void;
}

const ScenarioComparisonComponent: React.FC<ScenarioComparisonProps> = ({
  projectId,
  projectName,
  buildingType,
  onClose
}) => {
  const [scenarios, setScenarios] = useState<ProjectScenario[]>([]);
  const [selectedScenarios, setSelectedScenarios] = useState<string[]>([]);
  const [comparison, setComparison] = useState<ScenarioComparison | null>(null);
  const [modificationOptions, setModificationOptions] = useState<ModificationOptions | null>(null);
  const [activeTab, setActiveTab] = useState<'scenarios' | 'compare' | 'export'>('scenarios');
  const [isCreating, setIsCreating] = useState(false);
  const [editingScenario, setEditingScenario] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  
  // New scenario form
  const [newScenario, setNewScenario] = useState({
    name: '',
    description: '',
    modifications: {} as Record<string, any>
  });
  
  useEffect(() => {
    loadScenarios();
    loadModificationOptions();
  }, [projectId]);
  
  const loadScenarios = async () => {
    try {
      const data = await scenarioApi.listScenarios(projectId);
      setScenarios(data);
      
      // Auto-select first two scenarios for comparison
      if (data.length >= 2) {
        setSelectedScenarios([data[0].id, data[1].id]);
      }
    } catch (error) {
      console.error('Error loading scenarios:', error);
    }
  };
  
  const loadModificationOptions = async () => {
    try {
      const options = await scenarioApi.getModificationOptions(projectId);
      setModificationOptions(options);
    } catch (error) {
      console.error('Error loading modification options:', error);
    }
  };
  
  const handleCreateScenario = async () => {
    if (!newScenario.name) return;
    
    setLoading(true);
    try {
      await scenarioApi.createScenario(
        projectId,
        newScenario.name,
        newScenario.description,
        newScenario.modifications
      );
      
      // Reset form
      setNewScenario({ name: '', description: '', modifications: {} });
      setIsCreating(false);
      
      // Reload scenarios
      await loadScenarios();
    } catch (error) {
      console.error('Error creating scenario:', error);
    }
    setLoading(false);
  };
  
  const handleDeleteScenario = async (scenarioId: string) => {
    if (!confirm('Are you sure you want to delete this scenario?')) return;
    
    try {
      await scenarioApi.deleteScenario(scenarioId);
      await loadScenarios();
    } catch (error) {
      console.error('Error deleting scenario:', error);
    }
  };
  
  const handleCompare = async () => {
    if (selectedScenarios.length < 2) return;
    
    setLoading(true);
    try {
      const comparisonData = await scenarioApi.compareScenarios(
        projectId,
        selectedScenarios,
        `${projectName} Comparison`
      );
      setComparison(comparisonData);
      setActiveTab('compare');
    } catch (error) {
      console.error('Error comparing scenarios:', error);
    }
    setLoading(false);
  };
  
  const handleExport = async (format: 'pdf' | 'excel' | 'pptx') => {
    if (selectedScenarios.length < 1) return;
    
    setLoading(true);
    try {
      const result = await scenarioApi.exportComparison(
        projectId,
        selectedScenarios,
        format,
        true,
        true
      );
      
      // Create download link
      const blob = new Blob([result.data], { type: result.content_type });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = result.filename;
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Error exporting comparison:', error);
    }
    setLoading(false);
  };
  
  const renderModificationForm = () => {
    if (!modificationOptions) return null;
    
    return (
      <div className="space-y-4">
        {Object.entries(modificationOptions.modification_options).map(([param, config]) => (
          <div key={param} className="border rounded-lg p-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              {param.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
            </label>
            
            {config.options ? (
              <select
                className="w-full border rounded px-3 py-2"
                value={newScenario.modifications[param] || ''}
                onChange={(e) => setNewScenario({
                  ...newScenario,
                  modifications: {
                    ...newScenario.modifications,
                    [param]: e.target.value
                  }
                })}
              >
                <option value="">-- Select --</option>
                {config.options.map((opt: any) => (
                  <option key={opt} value={opt}>
                    {typeof opt === 'boolean' ? (opt ? 'Yes' : 'No') : opt}
                  </option>
                ))}
              </select>
            ) : config.min !== undefined ? (
              <div className="flex items-center gap-2">
                <input
                  type="range"
                  min={config.min}
                  max={config.max}
                  step={config.step || 1}
                  value={newScenario.modifications[param] || config.min}
                  onChange={(e) => setNewScenario({
                    ...newScenario,
                    modifications: {
                      ...newScenario.modifications,
                      [param]: Number(e.target.value)
                    }
                  })}
                  className="flex-1"
                />
                <span className="w-16 text-right">
                  {newScenario.modifications[param] || config.min}
                </span>
              </div>
            ) : null}
            
            {/* Show impact preview */}
            {config.impact && newScenario.modifications[param] && (
              <div className="mt-2 text-sm text-gray-600">
                Impact: {JSON.stringify(config.impact[newScenario.modifications[param]] || {})}
              </div>
            )}
          </div>
        ))}
      </div>
    );
  };
  
  const renderComparisonTable = () => {
    if (!comparison) return null;
    
    const metrics = [
      { key: 'total_cost', label: 'Total Cost', format: 'currency', lowerBetter: true },
      { key: 'roi', label: 'ROI', format: 'percentage', lowerBetter: false },
      { key: 'npv', label: 'NPV (10yr)', format: 'currency', lowerBetter: false },
      { key: 'payback_period', label: 'Payback', format: 'years', lowerBetter: true },
      { key: 'dscr', label: 'DSCR', format: 'multiplier', lowerBetter: false },
      { key: 'annual_revenue', label: 'Annual Revenue', format: 'currency', lowerBetter: false },
      { key: 'cost_per_sqft', label: 'Cost/SF', format: 'currency', lowerBetter: true }
    ];
    
    return (
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Metric
              </th>
              {comparison.scenario_names.map((name, idx) => (
                <th key={idx} className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  {name}
                  {idx === 0 && <span className="ml-2 text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">Base</span>}
                </th>
              ))}
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Best
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {metrics.map((metric) => {
              const values = comparison.metrics_comparison[metric.key] || [];
              const winner = comparison.winner_by_metric[metric.key];
              const bestValue = metric.lowerBetter ? Math.min(...values) : Math.max(...values);
              
              return (
                <tr key={metric.key}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {metric.label}
                  </td>
                  {values.map((value, idx) => {
                    const isWinner = comparison.scenario_names[idx] === winner;
                    const deltaFromBase = idx > 0 ? value - values[0] : 0;
                    
                    return (
                      <td key={idx} className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        <div className={isWinner ? 'font-bold text-green-600' : ''}>
                          {metric.format === 'currency' ? formatCurrency(value) :
                           metric.format === 'percentage' ? formatPercentage(value) :
                           metric.format === 'years' ? `${value.toFixed(1)} yrs` :
                           metric.format === 'multiplier' ? `${value.toFixed(2)}x` :
                           value.toFixed(2)}
                        </div>
                        {idx > 0 && deltaFromBase !== 0 && (
                          <div className={`text-xs ${deltaFromBase > 0 ? 
                            (metric.lowerBetter ? 'text-red-500' : 'text-green-500') : 
                            (metric.lowerBetter ? 'text-green-500' : 'text-red-500')}`}>
                            {deltaFromBase > 0 ? '+' : ''}{metric.format === 'currency' ? 
                              formatCurrency(deltaFromBase) : 
                              metric.format === 'percentage' ? 
                              `${(deltaFromBase * 100).toFixed(1)}%` : 
                              deltaFromBase.toFixed(2)}
                          </div>
                        )}
                      </td>
                    );
                  })}
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-bold text-green-600">
                    {winner}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    );
  };
  
  return (
    <div className="bg-white rounded-lg shadow-xl max-w-7xl mx-auto p-6">
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Scenario Comparison</h2>
          <p className="text-gray-600">{projectName} - {buildingType}</p>
        </div>
        {onClose && (
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-500"
          >
            <X className="h-6 w-6" />
          </button>
        )}
      </div>
      
      {/* Tabs */}
      <div className="flex gap-1 mb-6 border-b">
        <button
          onClick={() => setActiveTab('scenarios')}
          className={`px-4 py-2 font-medium ${
            activeTab === 'scenarios'
              ? 'text-blue-600 border-b-2 border-blue-600'
              : 'text-gray-500 hover:text-gray-700'
          }`}
        >
          Scenarios ({scenarios.length})
        </button>
        <button
          onClick={() => setActiveTab('compare')}
          className={`px-4 py-2 font-medium ${
            activeTab === 'compare'
              ? 'text-blue-600 border-b-2 border-blue-600'
              : 'text-gray-500 hover:text-gray-700'
          }`}
          disabled={selectedScenarios.length < 2}
        >
          Compare
        </button>
        <button
          onClick={() => setActiveTab('export')}
          className={`px-4 py-2 font-medium ${
            activeTab === 'export'
              ? 'text-blue-600 border-b-2 border-blue-600'
              : 'text-gray-500 hover:text-gray-700'
          }`}
          disabled={selectedScenarios.length < 1}
        >
          Export
        </button>
      </div>
      
      {/* Content */}
      {activeTab === 'scenarios' && (
        <div className="space-y-4">
          {/* Scenario list */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {scenarios.map((scenario) => (
              <div
                key={scenario.id}
                className={`border rounded-lg p-4 ${
                  selectedScenarios.includes(scenario.id)
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200'
                }`}
              >
                <div className="flex justify-between items-start mb-2">
                  <div>
                    <h3 className="font-semibold text-gray-900">{scenario.name}</h3>
                    {scenario.is_base && (
                      <span className="text-xs bg-gray-100 text-gray-800 px-2 py-1 rounded">Base</span>
                    )}
                  </div>
                  <input
                    type="checkbox"
                    checked={selectedScenarios.includes(scenario.id)}
                    onChange={(e) => {
                      if (e.target.checked) {
                        setSelectedScenarios([...selectedScenarios, scenario.id]);
                      } else {
                        setSelectedScenarios(selectedScenarios.filter(id => id !== scenario.id));
                      }
                    }}
                    className="h-4 w-4 text-blue-600"
                  />
                </div>
                
                <p className="text-sm text-gray-600 mb-3">{scenario.description}</p>
                
                <div className="space-y-1 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-500">Total Cost:</span>
                    <span className="font-medium">{formatCurrency(scenario.total_cost)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500">ROI:</span>
                    <span className="font-medium">{formatPercentage(scenario.roi)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500">Payback:</span>
                    <span className="font-medium">{scenario.payback_period.toFixed(1)} yrs</span>
                  </div>
                </div>
                
                {!scenario.is_base && (
                  <div className="flex gap-2 mt-3">
                    <button
                      onClick={() => handleDeleteScenario(scenario.id)}
                      className="text-red-500 hover:text-red-700"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </div>
                )}
              </div>
            ))}
            
            {/* Add new scenario card */}
            {!isCreating ? (
              <div
                onClick={() => setIsCreating(true)}
                className="border-2 border-dashed border-gray-300 rounded-lg p-4 flex items-center justify-center cursor-pointer hover:border-gray-400"
              >
                <div className="text-center">
                  <Plus className="h-12 w-12 text-gray-400 mx-auto mb-2" />
                  <span className="text-gray-600">Create Scenario</span>
                </div>
              </div>
            ) : (
              <div className="border rounded-lg p-4 col-span-full">
                <h3 className="font-semibold mb-3">New Scenario</h3>
                <div className="space-y-3">
                  <input
                    type="text"
                    placeholder="Scenario name"
                    value={newScenario.name}
                    onChange={(e) => setNewScenario({ ...newScenario, name: e.target.value })}
                    className="w-full border rounded px-3 py-2"
                  />
                  <textarea
                    placeholder="Description"
                    value={newScenario.description}
                    onChange={(e) => setNewScenario({ ...newScenario, description: e.target.value })}
                    className="w-full border rounded px-3 py-2"
                    rows={2}
                  />
                  
                  {renderModificationForm()}
                  
                  <div className="flex gap-2">
                    <button
                      onClick={handleCreateScenario}
                      disabled={!newScenario.name || loading}
                      className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 disabled:opacity-50"
                    >
                      Create
                    </button>
                    <button
                      onClick={() => {
                        setIsCreating(false);
                        setNewScenario({ name: '', description: '', modifications: {} });
                      }}
                      className="bg-gray-200 text-gray-700 px-4 py-2 rounded hover:bg-gray-300"
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>
          
          {/* Compare button */}
          {selectedScenarios.length >= 2 && (
            <div className="flex justify-center">
              <button
                onClick={handleCompare}
                className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 flex items-center gap-2"
              >
                <BarChart3 className="h-5 w-5" />
                Compare {selectedScenarios.length} Scenarios
              </button>
            </div>
          )}
        </div>
      )}
      
      {activeTab === 'compare' && comparison && (
        <div className="space-y-6">
          {/* Summary cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-green-50 border border-green-200 rounded-lg p-4">
              <div className="flex items-center gap-2 mb-2">
                <Target className="h-5 w-5 text-green-600" />
                <span className="text-sm font-medium text-green-900">Best Overall</span>
              </div>
              <p className="text-lg font-bold text-green-900">{comparison.best_overall_scenario}</p>
            </div>
            
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <div className="flex items-center gap-2 mb-2">
                <TrendingUp className="h-5 w-5 text-blue-600" />
                <span className="text-sm font-medium text-blue-900">Highest ROI</span>
              </div>
              <p className="text-lg font-bold text-blue-900">{comparison.best_roi_scenario}</p>
            </div>
            
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
              <div className="flex items-center gap-2 mb-2">
                <DollarSign className="h-5 w-5 text-yellow-600" />
                <span className="text-sm font-medium text-yellow-900">Lowest Cost</span>
              </div>
              <p className="text-lg font-bold text-yellow-900">{comparison.lowest_cost_scenario}</p>
            </div>
            
            <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
              <div className="flex items-center gap-2 mb-2">
                <Clock className="h-5 w-5 text-purple-600" />
                <span className="text-sm font-medium text-purple-900">Fastest Payback</span>
              </div>
              <p className="text-lg font-bold text-purple-900">{comparison.fastest_payback_scenario}</p>
            </div>
          </div>
          
          {/* Comparison table */}
          {renderComparisonTable()}
          
          {/* Impact analysis */}
          <div className="bg-gray-50 rounded-lg p-4">
            <h3 className="font-semibold text-gray-900 mb-3">Key Insights</h3>
            <ul className="space-y-2">
              {Object.entries(comparison.cost_deltas).map(([scenarioId, delta]) => {
                const scenario = scenarios.find(s => s.id === scenarioId);
                if (!scenario) return null;
                
                return (
                  <li key={scenarioId} className="flex items-start gap-2">
                    <AlertCircle className="h-4 w-4 text-blue-500 mt-0.5" />
                    <span className="text-sm text-gray-700">
                      <strong>{scenario.name}:</strong> {delta > 0 ? '+' : ''}{formatCurrency(delta)} cost impact,
                      {' '}{comparison.roi_deltas[scenarioId] > 0 ? '+' : ''}{(comparison.roi_deltas[scenarioId] * 100).toFixed(1)}% ROI change,
                      {' '}{comparison.timeline_deltas[scenarioId] > 0 ? '+' : ''}{comparison.timeline_deltas[scenarioId].toFixed(1)} years payback change
                    </span>
                  </li>
                );
              })}
            </ul>
          </div>
        </div>
      )}
      
      {activeTab === 'export' && (
        <div className="space-y-6">
          <p className="text-gray-600">Export your scenario comparison for presentations and reports.</p>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <button
              onClick={() => handleExport('pdf')}
              disabled={loading}
              className="border-2 border-gray-300 rounded-lg p-6 hover:border-blue-500 hover:bg-blue-50 transition-colors"
            >
              <Download className="h-8 w-8 text-gray-600 mx-auto mb-3" />
              <h3 className="font-semibold text-gray-900">PDF Report</h3>
              <p className="text-sm text-gray-600 mt-1">Professional report with charts</p>
            </button>
            
            <button
              onClick={() => handleExport('excel')}
              disabled={loading}
              className="border-2 border-gray-300 rounded-lg p-6 hover:border-green-500 hover:bg-green-50 transition-colors"
            >
              <Download className="h-8 w-8 text-gray-600 mx-auto mb-3" />
              <h3 className="font-semibold text-gray-900">Excel Workbook</h3>
              <p className="text-sm text-gray-600 mt-1">Detailed data with multiple sheets</p>
            </button>
            
            <button
              onClick={() => handleExport('pptx')}
              disabled={loading}
              className="border-2 border-gray-300 rounded-lg p-6 hover:border-purple-500 hover:bg-purple-50 transition-colors"
            >
              <Download className="h-8 w-8 text-gray-600 mx-auto mb-3" />
              <h3 className="font-semibold text-gray-900">PowerPoint</h3>
              <p className="text-sm text-gray-600 mt-1">Board-ready presentation slides</p>
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default ScenarioComparisonComponent;