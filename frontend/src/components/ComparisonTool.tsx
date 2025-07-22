import { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Sliders, Plus, Trash2, Download } from 'lucide-react';
import './ComparisonTool.css';

interface ComparisonToolProps {
  projectData: any;
  onClose: () => void;
}

interface Scenario {
  id: string;
  name: string;
  square_footage: number;
  building_mix: {
    warehouse: number;
    office: number;
  };
  features: {
    bathrooms?: number;
    dock_doors?: number;
    break_room?: boolean;
    loading_bays?: number;
  };
}

function ComparisonTool({ projectData, onClose }: ComparisonToolProps) {
  const [scenarios, setScenarios] = useState<Scenario[]>([]);
  const [comparisonResult, setComparisonResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [activeTemplate, setActiveTemplate] = useState<string>('');

  useEffect(() => {
    // Initialize with base scenario
    initializeBaseScenario();
  }, [projectData]);

  const initializeBaseScenario = () => {
    const baseMix = projectData.request_data.building_mix || { warehouse: 0.7, office: 0.3 };
    
    const baseScenario: Scenario = {
      id: 'base',
      name: 'Current Design',
      square_footage: projectData.request_data.square_footage,
      building_mix: {
        warehouse: baseMix.warehouse || 0.7,
        office: baseMix.office || 0.3
      },
      features: extractFeaturesFromProject(projectData)
    };

    setScenarios([baseScenario]);
  };

  const extractFeaturesFromProject = (project: any) => {
    const specialReqs = project.request_data.special_requirements || '';
    const features: any = {};

    // Extract bathrooms
    const bathroomMatch = specialReqs.match(/(\d+)\s*bathroom/i);
    if (bathroomMatch) {
      features.bathrooms = parseInt(bathroomMatch[1]);
    } else {
      features.bathrooms = 2; // default
    }

    // Extract dock doors
    const dockMatch = specialReqs.match(/(\d+)\s*dock\s*door/i);
    if (dockMatch) {
      features.dock_doors = parseInt(dockMatch[1]);
    } else {
      features.dock_doors = 2; // default
    }

    return features;
  };

  const addScenario = () => {
    if (scenarios.length >= 3) {
      setError('Maximum 3 scenarios allowed');
      return;
    }

    const newScenario: Scenario = {
      id: `scenario_${Date.now()}`,
      name: `Scenario ${scenarios.length + 1}`,
      square_footage: projectData.request_data.square_footage,
      building_mix: {
        warehouse: 0.7,
        office: 0.3
      },
      features: {
        bathrooms: 2,
        dock_doors: 2
      }
    };

    setScenarios([...scenarios, newScenario]);
  };

  const updateScenario = (id: string, updates: Partial<Scenario>) => {
    setScenarios(scenarios.map(s => 
      s.id === id ? { ...s, ...updates } : s
    ));
  };

  const removeScenario = (id: string) => {
    if (id === 'base') return; // Can't remove base scenario
    setScenarios(scenarios.filter(s => s.id !== id));
  };

  const runComparison = async () => {
    try {
      setLoading(true);
      setError('');

      // Prepare scenarios for API
      const apiScenarios = scenarios.slice(1).map(s => ({
        name: s.name,
        square_footage: s.square_footage,
        building_mix: s.building_mix,
        features: s.features
      }));

      const response = await fetch(`http://localhost:8001/api/v1/comparison/compare/${projectData.project_id}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({ scenarios: apiScenarios })
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
        throw new Error(errorData.detail || 'Failed to run comparison');
      }

      const data = await response.json();
      setComparisonResult(data.comparison);
    } catch (err: any) {
      console.error('Comparison error:', err);
      setError(err.message || 'Failed to run comparison');
    } finally {
      setLoading(false);
    }
  };

  const applyTemplate = async (templateName: string) => {
    try {
      const response = await fetch('http://localhost:8001/api/v1/comparison/templates', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (!response.ok) throw new Error('Failed to load templates');

      const data = await response.json();
      const template = data.templates.find((t: any) => t.name === templateName);

      if (template) {
        // Apply template scenarios
        const baseScenario = scenarios[0];
        const newScenarios = [baseScenario];

        template.scenarios.forEach((templateScenario: any, index: number) => {
          const scenario: Scenario = {
            id: `scenario_${Date.now()}_${index}`,
            name: templateScenario.name,
            square_footage: templateScenario.square_footage_multiplier 
              ? baseScenario.square_footage * templateScenario.square_footage_multiplier
              : baseScenario.square_footage,
            building_mix: templateScenario.building_mix || baseScenario.building_mix,
            features: templateScenario.features || baseScenario.features
          };
          newScenarios.push(scenario);
        });

        setScenarios(newScenarios.slice(0, 4)); // Max 3 scenarios + base
        setActiveTemplate(templateName);
      }
    } catch (err: any) {
      setError('Failed to apply template');
    }
  };

  const downloadReport = () => {
    if (!comparisonResult) return;

    const report = {
      project: projectData.project_name,
      generated: new Date().toISOString(),
      scenarios: comparisonResult.scenarios,
      analysis: comparisonResult.analysis,
      summary: comparisonResult.summary
    };

    const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `comparison_report_${projectData.project_id}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="comparison-tool">
      <div className="comparison-header">
        <h2>
          <Sliders size={24} />
          What-If Scenario Comparison
        </h2>
        <button className="close-btn" onClick={onClose}>×</button>
      </div>

      <div className="comparison-body">
        <div className="templates-section">
          <h3>Quick Templates</h3>
          <div className="template-buttons">
            <button 
              className={`template-btn ${activeTemplate === 'Cost Optimization' ? 'active' : ''}`}
              onClick={() => applyTemplate('Cost Optimization')}
            >
              Cost Optimization
            </button>
            <button 
              className={`template-btn ${activeTemplate === 'Size Analysis' ? 'active' : ''}`}
              onClick={() => applyTemplate('Size Analysis')}
            >
              Size Analysis
            </button>
            <button 
              className={`template-btn ${activeTemplate === 'Feature Impact' ? 'active' : ''}`}
              onClick={() => applyTemplate('Feature Impact')}
            >
              Feature Impact
            </button>
          </div>
        </div>

        <div className="scenarios-section">
          <div className="scenarios-header">
            <h3>Scenarios</h3>
            {scenarios.length < 4 && (
              <button className="add-scenario-btn" onClick={addScenario}>
                <Plus size={16} />
                Add Scenario
              </button>
            )}
          </div>

          <div className="scenarios-grid">
            {scenarios.map((scenario) => (
              <div key={scenario.id} className={`scenario-card ${scenario.id === 'base' ? 'base-scenario' : ''}`}>
                <div className="scenario-header">
                  <input
                    type="text"
                    value={scenario.name}
                    onChange={(e) => updateScenario(scenario.id, { name: e.target.value })}
                    className="scenario-name"
                    disabled={scenario.id === 'base'}
                  />
                  {scenario.id !== 'base' && (
                    <button 
                      className="remove-scenario-btn"
                      onClick={() => removeScenario(scenario.id)}
                    >
                      <Trash2 size={16} />
                    </button>
                  )}
                </div>

                <div className="scenario-controls">
                  <div className="control-group">
                    <label>Square Footage</label>
                    <input
                      type="number"
                      value={scenario.square_footage}
                      onChange={(e) => updateScenario(scenario.id, { 
                        square_footage: parseInt(e.target.value) || 0 
                      })}
                      disabled={scenario.id === 'base'}
                    />
                  </div>

                  <div className="control-group">
                    <label>Warehouse %</label>
                    <input
                      type="range"
                      min="0"
                      max="100"
                      value={scenario.building_mix.warehouse * 100}
                      onChange={(e) => {
                        const warehouse = parseInt(e.target.value) / 100;
                        updateScenario(scenario.id, {
                          building_mix: {
                            warehouse,
                            office: 1 - warehouse
                          }
                        });
                      }}
                      disabled={scenario.id === 'base'}
                    />
                    <span>{Math.round(scenario.building_mix.warehouse * 100)}%</span>
                  </div>

                  <div className="control-group">
                    <label>Office %</label>
                    <input
                      type="range"
                      min="0"
                      max="100"
                      value={scenario.building_mix.office * 100}
                      disabled
                    />
                    <span>{Math.round(scenario.building_mix.office * 100)}%</span>
                  </div>

                  <div className="control-group">
                    <label>Bathrooms</label>
                    <input
                      type="number"
                      min="0"
                      max="20"
                      value={scenario.features.bathrooms || 0}
                      onChange={(e) => updateScenario(scenario.id, {
                        features: {
                          ...scenario.features,
                          bathrooms: parseInt(e.target.value) || 0
                        }
                      })}
                      disabled={scenario.id === 'base'}
                    />
                  </div>

                  <div className="control-group">
                    <label>Dock Doors</label>
                    <input
                      type="number"
                      min="0"
                      max="20"
                      value={scenario.features.dock_doors || 0}
                      onChange={(e) => updateScenario(scenario.id, {
                        features: {
                          ...scenario.features,
                          dock_doors: parseInt(e.target.value) || 0
                        }
                      })}
                      disabled={scenario.id === 'base'}
                    />
                  </div>
                </div>
              </div>
            ))}
          </div>

          {scenarios.length > 1 && (
            <button className="compare-btn" onClick={runComparison} disabled={loading}>
              {loading ? 'Comparing...' : 'Run Comparison'}
            </button>
          )}
        </div>

        {error && (
          <div className="error-message">{error}</div>
        )}

        {comparisonResult && (
          <div className="results-section">
            <div className="results-header">
              <h3>Comparison Results</h3>
              <button className="download-btn" onClick={downloadReport}>
                <Download size={16} />
                Download Report
              </button>
            </div>

            <div className="results-summary">
              <div className="summary-card">
                <h4>Cost Comparison</h4>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={comparisonResult.visualization.cost_comparison.datasets[0].data.map((value: number, index: number) => ({
                    name: comparisonResult.visualization.cost_comparison.labels[index],
                    cost: value
                  }))}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis tickFormatter={(value) => `$${(value / 1000).toFixed(0)}k`} />
                    <Tooltip formatter={(value: number) => `$${value.toLocaleString()}`} />
                    <Bar dataKey="cost" fill="#0066cc" />
                  </BarChart>
                </ResponsiveContainer>
              </div>

              <div className="metrics-grid">
                {comparisonResult.analysis.key_metrics.map((metric: any) => (
                  <div key={metric.scenario_id} className="metric-card">
                    <h5>{metric.scenario_name}</h5>
                    <div className="metric-value">${metric.total_cost.toLocaleString()}</div>
                    <div className="metric-label">Total Cost</div>
                    <div className="metric-secondary">
                      ${metric.cost_per_sqft.toFixed(2)}/sq ft
                    </div>
                  </div>
                ))}
              </div>

              <div className="recommendations">
                <h4>Recommendations</h4>
                <ul>
                  {comparisonResult.summary.recommendations.map((rec: string, index: number) => (
                    <li key={index}>{rec}</li>
                  ))}
                </ul>
              </div>

              {comparisonResult.analysis.cost_deltas.length > 0 && (
                <div className="deltas-section">
                  <h4>Cost Differences</h4>
                  {comparisonResult.analysis.cost_deltas.map((delta: any) => (
                    <div key={delta.scenario_id} className="delta-item">
                      <span className="delta-name">{delta.scenario_name}:</span>
                      <span className={`delta-value ${delta.delta_amount > 0 ? 'positive' : 'negative'}`}>
                        {delta.comparison_text}
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default ComparisonTool;