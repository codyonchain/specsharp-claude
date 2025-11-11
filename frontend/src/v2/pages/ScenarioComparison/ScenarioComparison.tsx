import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  ArrowLeft,
  Plus,
  Download,
  TrendingUp,
  DollarSign,
  Clock,
  BarChart3,
} from 'lucide-react';
import { api } from '../../api/client';
import ScenarioTemplates from './ScenarioTemplates';
import ScenarioBuilder from './ScenarioBuilder';
import ComparisonView from './ComparisonView';
import ExportOptions from './ExportOptions';
import { Project, Scenario, ComparisonResult } from './types';

const ScenarioComparison: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [project, setProject] = useState<Project | null>(null);
  const [scenarios, setScenarios] = useState<Scenario[]>([]);
  const [activeTab, setActiveTab] = useState<'scenarios' | 'compare' | 'export'>('scenarios');
  const [showBuilder, setShowBuilder] = useState(false);
  const [selectedTemplate, setSelectedTemplate] = useState<string | null>(null);
  const [comparisonResult, setComparisonResult] = useState<ComparisonResult | null>(null);
  const canonicalProjectId = project?.id || projectId || '';

  useEffect(() => {
    loadProject();
  }, [projectId]);

  const loadProject = async () => {
    try {
      setLoading(true);
      if (!projectId) {
        setLoading(false);
        return;
      }
      const projectData = await api.getProject(projectId);
      setProject(projectData);
      
      // Extract data from project analysis if available
      const analysis = projectData.analysis;
      const parsed = analysis?.parsed_input || {};
      const calculations = analysis?.calculations || {};
      const totals = calculations?.totals || {};
      
      // Create base scenario from project
      const baseScenario: Scenario = {
        id: 'base',
        name: 'Current Design',
        isBase: true,
        building_type: parsed.building_type || projectData.building_type || 'commercial',
        subtype: parsed.building_subtype || parsed.subtype || projectData.subtype || 'general',
        square_footage: parsed.square_footage || projectData.square_footage || 10000,
        location: parsed.location || projectData.location || 'Nashville',
        project_class: parsed.project_class || projectData.project_class || 'ground_up',
        ownership_type: parsed.ownership_type || projectData.ownership_type || 'for_profit',
        floors: parsed.floors || projectData.floors || 1,
        modifications: {},
        totalCost: totals.total_project_cost || projectData.total_cost || 0,
        costPerSF: totals.cost_per_sf || projectData.cost_per_sqft || 0,
      };
      setScenarios([baseScenario]);
    } catch (error) {
      console.error('Failed to load project:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateScenario = (template?: string) => {
    setSelectedTemplate(template || null);
    setShowBuilder(true);
  };

  const handleSaveScenario = (scenario: Scenario) => {
    setScenarios([...scenarios, scenario]);
    setShowBuilder(false);
    setSelectedTemplate(null);
    // Automatically run comparison when scenario is added
    if (scenarios.length >= 1) {
      runComparison([...scenarios, scenario]);
    }
  };

  const handleDeleteScenario = (id: string) => {
    const updatedScenarios = scenarios.filter(s => s.id !== id);
    setScenarios(updatedScenarios);
    if (updatedScenarios.length > 1) {
      runComparison(updatedScenarios);
    }
  };

  const runComparison = async (scenariosToCompare: Scenario[]) => {
    try {
      // Using the raw axios client for now since this endpoint isn't in the v2 api client yet
      const response = await api.client.post('/api/v2/compare', {
        scenarios: scenariosToCompare.map(s => ({
          name: s.name,
          building_type: s.building_type,
          subtype: s.subtype,
          square_footage: s.square_footage,
          location: s.location,
          project_class: s.project_class,
          ownership_type: s.ownership_type,
          floors: s.floors,
          special_features: s.special_features,
        })),
      });
      setComparisonResult(response.data);
    } catch (error) {
      console.error('Failed to run comparison:', error);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading project data...</p>
        </div>
      </div>
    );
  }

  if (!project) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-600">Project not found</p>
          <button
            onClick={() => navigate('/dashboard')}
            className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Back to Dashboard
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-6 py-6">
        {/* Header */}
        <div className="mb-6 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button
              onClick={() => navigate(canonicalProjectId ? `/project/${canonicalProjectId}` : '/dashboard')}
              className="p-2 hover:bg-gray-100 rounded-lg transition"
            >
              <ArrowLeft className="h-5 w-5" />
            </button>
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                Scenario Comparison
              </h1>
              <p className="text-gray-600">
                {project?.name || 'Project'} - Compare different options
              </p>
            </div>
          </div>
          <div className="flex gap-3">
            <button
              onClick={() => handleCreateScenario()}
              disabled={scenarios.length >= 5}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Plus className="h-4 w-4" />
              Add Scenario
            </button>
            <button
              onClick={() => setActiveTab('export')}
              className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition flex items-center gap-2"
            >
              <Download className="h-4 w-4" />
              Export
            </button>
          </div>
        </div>

        {/* Quick Stats */}
        {scenarios.length > 1 && comparisonResult && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            <div className="bg-white rounded-lg p-4 text-center shadow-sm">
              <DollarSign className="h-8 w-8 text-green-600 mx-auto mb-2" />
              <p className="text-2xl font-bold">
                ${((comparisonResult.summary.cost_range.max - comparisonResult.summary.cost_range.min) / 1000000).toFixed(1)}M
              </p>
              <p className="text-sm text-gray-600">Cost Variance</p>
            </div>
            <div className="bg-white rounded-lg p-4 text-center shadow-sm">
              <TrendingUp className="h-8 w-8 text-blue-600 mx-auto mb-2" />
              <p className="text-2xl font-bold">{scenarios.length}</p>
              <p className="text-sm text-gray-600">Options Compared</p>
            </div>
            <div className="bg-white rounded-lg p-4 text-center shadow-sm">
              <Clock className="h-8 w-8 text-orange-600 mx-auto mb-2" />
              <p className="text-2xl font-bold">
                {comparisonResult.summary.lowest_cost_scenario}
              </p>
              <p className="text-sm text-gray-600">Most Economical</p>
            </div>
            <div className="bg-white rounded-lg p-4 text-center shadow-sm">
              <BarChart3 className="h-8 w-8 text-purple-600 mx-auto mb-2" />
              <p className="text-2xl font-bold">Board Ready</p>
              <p className="text-sm text-gray-600">Export Available</p>
            </div>
          </div>
        )}

        {/* Main Content */}
        <div className="bg-white rounded-lg shadow-sm min-h-[600px]">
          {showBuilder ? (
            <ScenarioBuilder
              baseProject={project!}
              template={selectedTemplate}
              onSave={handleSaveScenario}
              onCancel={() => {
                setShowBuilder(false);
                setSelectedTemplate(null);
              }}
            />
          ) : (
            <>
              {/* Tabs */}
              <div className="border-b border-gray-200">
                <nav className="flex px-6">
                  <button
                    onClick={() => setActiveTab('scenarios')}
                    className={`py-4 px-6 border-b-2 font-medium text-sm transition ${
                      activeTab === 'scenarios'
                        ? 'border-blue-600 text-blue-600'
                        : 'border-transparent text-gray-500 hover:text-gray-700'
                    }`}
                  >
                    Scenarios
                    <span className="ml-2 px-2 py-0.5 bg-gray-100 text-gray-600 rounded-full text-xs">
                      {scenarios.length}
                    </span>
                  </button>
                  <button
                    onClick={() => setActiveTab('compare')}
                    disabled={scenarios.length < 2}
                    className={`py-4 px-6 border-b-2 font-medium text-sm transition ${
                      activeTab === 'compare'
                        ? 'border-blue-600 text-blue-600'
                        : 'border-transparent text-gray-500 hover:text-gray-700'
                    } disabled:opacity-50 disabled:cursor-not-allowed`}
                  >
                    Compare
                  </button>
                  <button
                    onClick={() => setActiveTab('export')}
                    disabled={scenarios.length < 2}
                    className={`py-4 px-6 border-b-2 font-medium text-sm transition ${
                      activeTab === 'export'
                        ? 'border-blue-600 text-blue-600'
                        : 'border-transparent text-gray-500 hover:text-gray-700'
                    } disabled:opacity-50 disabled:cursor-not-allowed`}
                  >
                    Export
                  </button>
                </nav>
              </div>

              {/* Tab Content */}
              <div className="p-6">
                {activeTab === 'scenarios' && (
                  scenarios.length === 1 ? (
                    <ScenarioTemplates onSelectTemplate={handleCreateScenario} />
                  ) : (
                    <div>
                      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        {scenarios.map(scenario => (
                          <div
                            key={scenario.id}
                            className={`p-4 rounded-lg border-2 ${
                              scenario.isBase
                                ? 'border-blue-500 bg-blue-50'
                                : 'border-gray-200 bg-white'
                            } relative`}
                          >
                            {scenario.isBase && (
                              <span className="absolute top-2 right-2 px-2 py-1 bg-blue-600 text-white text-xs font-medium rounded">
                                BASE
                              </span>
                            )}
                            <h3 className="text-lg font-semibold mb-2">
                              {scenario.name}
                            </h3>
                            <div className="mb-3">
                              <p className="text-sm text-gray-600">Total Cost</p>
                              <p className="text-2xl font-bold">
                                ${(scenario.totalCost / 1000000).toFixed(2)}M
                              </p>
                            </div>
                            <div className="mb-3">
                              <p className="text-sm text-gray-600">Cost per SF</p>
                              <p className="text-xl font-semibold">
                                ${scenario.costPerSF}/SF
                              </p>
                            </div>
                            {Object.keys(scenario.modifications || {}).length > 0 && (
                              <div>
                                <p className="text-sm text-gray-600 mb-1">
                                  Modifications
                                </p>
                                <div className="flex flex-wrap gap-1">
                                  {Object.entries(scenario.modifications).map(([key, value]) => (
                                    <span
                                      key={key}
                                      className="px-2 py-1 bg-gray-100 text-xs rounded"
                                    >
                                      {key}: {value}
                                    </span>
                                  ))}
                                </div>
                              </div>
                            )}
                            {!scenario.isBase && (
                              <button
                                onClick={() => handleDeleteScenario(scenario.id)}
                                className="mt-3 text-red-600 text-sm hover:text-red-700"
                              >
                                Remove
                              </button>
                            )}
                          </div>
                        ))}
                        {scenarios.length < 5 && (
                          <button
                            onClick={() => handleCreateScenario()}
                            className="p-4 rounded-lg border-2 border-dashed border-gray-300 hover:border-gray-400 hover:bg-gray-50 transition flex flex-col items-center justify-center min-h-[200px]"
                          >
                            <Plus className="h-12 w-12 text-gray-400 mb-2" />
                            <span className="text-lg font-medium text-gray-600">
                              Add Scenario
                            </span>
                            <span className="text-sm text-gray-500">
                              Compare up to 5 options
                            </span>
                          </button>
                        )}
                      </div>
                    </div>
                  )
                )}

                {activeTab === 'compare' && scenarios.length >= 2 && (
                  <ComparisonView
                    scenarios={scenarios}
                    comparisonResult={comparisonResult}
                    project={project!}
                  />
                )}

                {activeTab === 'export' && scenarios.length >= 2 && (
                  <ExportOptions
                    scenarios={scenarios}
                    comparisonResult={comparisonResult}
                    project={project!}
                  />
                )}
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default ScenarioComparison;
