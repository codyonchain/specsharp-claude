import React, { useState, useEffect, useMemo, useCallback } from 'react';
import { ArrowUpDown, MapPin, Building2, Layers, DollarSign, TrendingUp, TrendingDown } from 'lucide-react';
import { scopeService } from '../services/api';
import './ComparisonToolV2.css';

interface ComparisonToolV2Props {
  projectData: any;
  onClose: () => void;
}

interface ComparisonScenario {
  id: string;
  name: string;
  location: string;
  square_footage: number;
  num_floors: number;
  data?: any;
  loading?: boolean;
  error?: string;
}

const ComparisonToolV2: React.FC<ComparisonToolV2Props> = ({ projectData, onClose }) => {
  const [baseScenario, setBaseScenario] = useState<ComparisonScenario>({
    id: 'base',
    name: 'Current Design',
    location: projectData.request_data.location,
    square_footage: projectData.request_data.square_footage,
    num_floors: projectData.request_data.num_floors || 1,
    data: projectData
  });

  const [compareScenario, setCompareScenario] = useState<ComparisonScenario>({
    id: 'compare',
    name: 'Alternative Design',
    location: projectData.request_data.location,
    square_footage: projectData.request_data.square_footage,
    num_floors: projectData.request_data.num_floors || 1
  });

  const [isGenerating, setIsGenerating] = useState(false);

  // Popular comparison locations
  const popularLocations = [
    'Phoenix, AZ',
    'Austin, TX',
    'Denver, CO',
    'Atlanta, GA',
    'Chicago, IL',
    'Seattle, WA',
    'Miami, FL',
    'Boston, MA',
    'San Francisco, CA',
    'New York, NY'
  ];

  const generateComparison = async (scenario?: ComparisonScenario) => {
    const targetScenario = scenario || compareScenario;
    setIsGenerating(true);
    setCompareScenario(prev => ({ ...prev, loading: true, error: undefined }));

    try {
      // Create a new scope request with the comparison parameters
      const comparisonRequest = {
        ...projectData.request_data,
        project_name: `${projectData.project_name} - Comparison`,
        location: targetScenario.location,
        square_footage: targetScenario.square_footage,
        num_floors: targetScenario.num_floors
      };

      const response = await scopeService.generate(comparisonRequest);
      
      setCompareScenario(prev => ({
        ...prev,
        data: response,
        loading: false
      }));
    } catch (error: any) {
      console.error('Comparison generation error:', error);
      setCompareScenario(prev => ({
        ...prev,
        error: 'Failed to generate comparison',
        loading: false
      }));
    } finally {
      setIsGenerating(false);
    }
  };

  const formatCurrency = useCallback((value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(value);
  }, []);

  const calculateDifference = useCallback((baseValue: number, compareValue: number) => {
    const diff = compareValue - baseValue;
    const percentage = ((diff / baseValue) * 100).toFixed(1);
    return { diff, percentage };
  }, []);

  const getCostDifferenceColor = useCallback((diff: number) => {
    if (diff > 0) return 'cost-increase';
    if (diff < 0) return 'cost-decrease';
    return 'cost-same';
  }, []);

  // Memoize the comparison calculations
  const comparisonData = useMemo(() => {
    if (!baseScenario.data || !compareScenario.data) return null;
    
    const baseCost = baseScenario.data.total_cost;
    const compareCost = compareScenario.data.total_cost;
    const difference = calculateDifference(baseCost, compareCost);
    
    return {
      baseCost,
      compareCost,
      difference,
      color: getCostDifferenceColor(difference.diff)
    };
  }, [baseScenario.data, compareScenario.data, calculateDifference, getCostDifferenceColor]);

  const renderScenarioCard = (scenario: ComparisonScenario, isBase: boolean) => {
    const totalCost = scenario.data?.total_cost || 0;
    const costPerSqFt = scenario.square_footage > 0 ? totalCost / scenario.square_footage : 0;

    return (
      <div className={`scenario-card ${isBase ? 'base-scenario' : 'compare-scenario'}`}>
        <div className="scenario-header">
          <h3>{scenario.name}</h3>
          {!isBase && scenario.data && (
            <div className={`cost-difference ${getCostDifferenceColor(calculateDifference(baseScenario.data.total_cost, totalCost).diff)}`}>
              {calculateDifference(baseScenario.data.total_cost, totalCost).diff > 0 ? (
                <TrendingUp size={20} />
              ) : calculateDifference(baseScenario.data.total_cost, totalCost).diff < 0 ? (
                <TrendingDown size={20} />
              ) : null}
              <span>
                {calculateDifference(baseScenario.data.total_cost, totalCost).diff > 0 ? '+' : ''}
                {formatCurrency(calculateDifference(baseScenario.data.total_cost, totalCost).diff)}
                ({calculateDifference(baseScenario.data.total_cost, totalCost).percentage}%)
              </span>
            </div>
          )}
        </div>

        <div className="scenario-inputs">
          <div className="input-group">
            <label>
              <MapPin size={16} />
              Location
            </label>
            {isBase ? (
              <input type="text" value={scenario.location} disabled />
            ) : (
              <select
                value={scenario.location}
                onChange={(e) => setCompareScenario(prev => ({ ...prev, location: e.target.value }))}
                disabled={isGenerating}
              >
                <option value={scenario.location}>{scenario.location}</option>
                {popularLocations
                  .filter(loc => loc !== scenario.location)
                  .map(loc => (
                    <option key={loc} value={loc}>{loc}</option>
                  ))}
              </select>
            )}
          </div>

          <div className="input-group">
            <label>
              <Building2 size={16} />
              Square Footage
            </label>
            <input
              type="number"
              value={scenario.square_footage}
              onChange={(e) => !isBase && setCompareScenario(prev => ({ 
                ...prev, 
                square_footage: parseInt(e.target.value) || 0 
              }))}
              disabled={isBase || isGenerating}
            />
          </div>

          <div className="input-group">
            <label>
              <Layers size={16} />
              Number of Floors
            </label>
            <input
              type="number"
              value={scenario.num_floors}
              onChange={(e) => !isBase && setCompareScenario(prev => ({ 
                ...prev, 
                num_floors: parseInt(e.target.value) || 1 
              }))}
              min="1"
              max="50"
              disabled={isBase || isGenerating}
            />
          </div>
        </div>

        {scenario.loading && (
          <div className="scenario-loading">
            <div className="loading-spinner"></div>
            <p>Generating comparison estimate...</p>
          </div>
        )}

        {scenario.error && (
          <div className="scenario-error">
            <p>{scenario.error}</p>
          </div>
        )}

        {scenario.data && !scenario.loading && (
          <div className="scenario-results">
            <div className="result-item total-cost">
              <DollarSign size={20} />
              <div>
                <div className="result-value">{formatCurrency(totalCost)}</div>
                <div className="result-label">Total Cost</div>
              </div>
            </div>

            <div className="result-item">
              <div className="result-value">${costPerSqFt.toFixed(2)}</div>
              <div className="result-label">Per Sq Ft</div>
            </div>

            <div className="cost-breakdown">
              <h4>Cost Breakdown</h4>
              {scenario.data.categories?.slice(0, 5).map((category: any) => (
                <div key={category.name} className="breakdown-item">
                  <span className="category-name">{category.name}</span>
                  <span className="category-cost">{formatCurrency(category.subtotal)}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="comparison-tool-v2-overlay">
      <div className="comparison-tool-v2">
        <div className="comparison-header">
          <h2>
            <ArrowUpDown size={24} />
            Project Comparison
          </h2>
          <button className="close-btn" onClick={onClose}>×</button>
        </div>

        <div className="comparison-body">
          <div className="comparison-intro">
            <p>Compare your project across different locations, sizes, or floor counts to find the most cost-effective option.</p>
            
            {!compareScenario.data && (
              <div className="quick-locations">
                <p className="quick-locations-label">Quick compare with:</p>
                <div className="location-buttons">
                  {popularLocations
                    .filter(loc => loc !== baseScenario.location)
                    .slice(0, 5)
                    .map(loc => (
                      <button
                        key={loc}
                        className="location-btn"
                        onClick={() => {
                          setCompareScenario(prev => ({ ...prev, location: loc }));
                          generateComparison({ ...compareScenario, location: loc });
                        }}
                        disabled={isGenerating}
                      >
                        {loc}
                      </button>
                    ))}
                </div>
              </div>
            )}
          </div>

          <div className="scenarios-container">
            {renderScenarioCard(baseScenario, true)}
            
            <div className="vs-divider">
              <span>VS</span>
            </div>

            {renderScenarioCard(compareScenario, false)}
          </div>

          {!compareScenario.data && !compareScenario.loading && (
            <div className="generate-section">
              <button 
                className="generate-btn"
                onClick={generateComparison}
                disabled={isGenerating}
              >
                {isGenerating ? 'Generating Comparison...' : 'Generate Comparison'}
              </button>
            </div>
          )}

          {baseScenario.data && compareScenario.data && (
            <div className="comparison-summary">
              <h3>Summary</h3>
              <div className="summary-content">
                <div className="summary-item">
                  <span className="summary-label">Location Impact:</span>
                  <span className={`summary-value ${getCostDifferenceColor(calculateDifference(baseScenario.data.total_cost, compareScenario.data.total_cost).diff)}`}>
                    Building in {compareScenario.location} instead of {baseScenario.location} would
                    {calculateDifference(baseScenario.data.total_cost, compareScenario.data.total_cost).diff > 0 ? ' increase ' : ' decrease '}
                    costs by {formatCurrency(Math.abs(calculateDifference(baseScenario.data.total_cost, compareScenario.data.total_cost).diff))}
                  </span>
                </div>
                
                {compareScenario.square_footage !== baseScenario.square_footage && (
                  <div className="summary-item">
                    <span className="summary-label">Size Impact:</span>
                    <span className="summary-value">
                      {compareScenario.square_footage > baseScenario.square_footage ? 'Increasing' : 'Decreasing'} to {compareScenario.square_footage.toLocaleString()} sq ft
                    </span>
                  </div>
                )}

                {compareScenario.num_floors !== baseScenario.num_floors && (
                  <div className="summary-item">
                    <span className="summary-label">Height Impact:</span>
                    <span className="summary-value">
                      {compareScenario.num_floors > baseScenario.num_floors ? 'Adding' : 'Removing'} floors affects structural and mechanical costs
                    </span>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ComparisonToolV2;