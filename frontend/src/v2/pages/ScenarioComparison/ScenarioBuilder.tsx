import React, { useState, useEffect } from 'react';
import {
  TrendingUp,
  TrendingDown,
  AlertCircle,
} from 'lucide-react';
import { Project, Scenario } from './types';
import { api } from '../../api/client';

interface ScenarioBuilderProps {
  baseProject: Project;
  template?: string | null;
  onSave: (scenario: Scenario) => void;
  onCancel: () => void;
}

const ScenarioBuilder: React.FC<ScenarioBuilderProps> = ({
  baseProject,
  template,
  onSave,
  onCancel,
}) => {
  // Extract data from project analysis if available
  const analysis = baseProject.analysis;
  const parsed = analysis?.parsed_input || {};
  const calculations = analysis?.calculations || {};
  const totals = calculations?.totals || {};
  const baseSquareFootage = parsed.square_footage || baseProject.square_footage || 10000;
  const baseFloors = parsed.floors || baseProject.floors || 1;
  const baseProjectClass = parsed.project_class || baseProject.project_class || 'ground_up';
  const baseTotalCost = totals.total_project_cost || baseProject.total_cost || 0;
  
  const [name, setName] = useState('');
  const [squareFootage, setSquareFootage] = useState(baseSquareFootage);
  const [finishLevel, setFinishLevel] = useState('standard');
  const [parkingType, setParkingType] = useState('surface');
  const [floors, setFloors] = useState(baseFloors);
  const [projectClass, setProjectClass] = useState(baseProjectClass);
  const [calculating, setCalculating] = useState(false);
  const [preview, setPreview] = useState<any>(null);

  useEffect(() => {
    // Pre-fill based on template
    if (template) {
      switch (template) {
        case 'finish_level':
          setName('Premium Finishes');
          setFinishLevel('premium');
          break;
        case 'size':
          setName('20% Larger');
          setSquareFootage(Math.round(baseSquareFootage * 1.2));
          break;
        case 'parking':
          setName('Structured Parking');
          setParkingType('garage');
          break;
        case 'phasing':
          setName('Multi-Phase Construction');
          setProjectClass('renovation');
          break;
        case 'floors':
          setName(`${floors + 2} Story Option`);
          setFloors(floors + 2);
          break;
        default:
          setName('Custom Scenario');
      }
    }
    // Calculate initial preview
    calculatePreview();
  }, [template, baseSquareFootage]);

  useEffect(() => {
    // Calculate preview when parameters change
    const timer = setTimeout(() => {
      calculatePreview();
    }, 500);
    return () => clearTimeout(timer);
  }, [squareFootage, finishLevel, parkingType, floors, projectClass]);

  const calculatePreview = async () => {
    try {
      setCalculating(true);
      const response = await api.client.post('/api/v2/calculate', {
        building_type: parsed.building_type || baseProject.building_type || 'commercial',
        subtype: parsed.building_subtype || parsed.subtype || baseProject.subtype || 'general',
        square_footage: squareFootage,
        location: parsed.location || baseProject.location || 'Nashville',
        project_class: projectClass,
        floors: floors,
        ownership_type: parsed.ownership_type || baseProject.ownership_type || 'for_profit',
        special_features: getSpecialFeatures(),
      });
      setPreview(response.data);
    } catch (error: any) {
      console.error('Failed to calculate preview:', error);
      // Fallback calculation if API fails
      const basePerSF = baseTotalCost / baseSquareFootage;
      const sizeMultiplier = squareFootage / baseSquareFootage;
      const finishMultiplier = finishLevel === 'economy' ? 0.85 : 
                               finishLevel === 'premium' ? 1.15 : 
                               finishLevel === 'luxury' ? 1.35 : 1.0;
      const parkingCost = parkingType === 'garage' ? 50000 : 
                         parkingType === 'underground' ? 100000 : 0;
      const estimatedCost = (basePerSF * squareFootage * finishMultiplier) + parkingCost;
      
      setPreview({
        totals: {
          total_project_cost: estimatedCost,
          cost_per_sf: Math.round(estimatedCost / squareFootage)
        }
      });
    } finally {
      setCalculating(false);
    }
  };

  const getSpecialFeatures = () => {
    const features = [];
    if (finishLevel === 'premium') features.push('premium_finishes');
    if (finishLevel === 'luxury') features.push('luxury_finishes');
    if (parkingType === 'garage') features.push('parking_garage');
    if (parkingType === 'underground') features.push('underground_parking');
    return features;
  };

  const handleSave = () => {
    console.log('Save clicked:', { name, preview, calculating });
    if (!name || !preview) return;

    const scenario: Scenario = {
      id: Date.now().toString(),
      name,
      isBase: false,
      building_type: parsed.building_type || baseProject.building_type || 'commercial',
      subtype: parsed.building_subtype || parsed.subtype || baseProject.subtype || 'general',
      square_footage: squareFootage,
      location: parsed.location || baseProject.location || 'Nashville',
      project_class: projectClass,
      ownership_type: parsed.ownership_type || baseProject.ownership_type || 'for_profit',
      floors: floors,
      special_features: getSpecialFeatures(),
      modifications: {
        size_change: `${((squareFootage / baseSquareFootage - 1) * 100).toFixed(0)}%`,
        finish_level: finishLevel,
        parking: parkingType,
      },
      totalCost: preview?.totals?.total_project_cost || 0,
      costPerSF: preview?.totals?.cost_per_sf || 0,
    };

    onSave(scenario);
  };

  const formatCurrency = (value: number) => {
    if (value >= 1000000) return `$${(value / 1000000).toFixed(1)}M`;
    if (value >= 1000) return `$${(value / 1000).toFixed(0)}K`;
    return `$${value.toFixed(0)}`;
  };

  return (
    <div className="p-6">
      <h2 className="text-2xl font-bold text-gray-900 mb-2">
        Create New Scenario
      </h2>
      <p className="text-gray-600 mb-6">
        Adjust parameters to see how changes impact cost and returns
      </p>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column - Inputs */}
        <div className="lg:col-span-2">
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <input
              type="text"
              placeholder="Scenario Name (e.g., Premium Finishes Option)"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 mb-6"
            />

            <hr className="my-6" />

            {/* Square Footage Slider */}
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Square Footage: {squareFootage.toLocaleString()} SF
              </label>
              <input
                type="range"
                min={Math.round(baseSquareFootage * 0.5)}
                max={Math.round(baseSquareFootage * 1.5)}
                step={100}
                value={squareFootage}
                onChange={(e) => setSquareFootage(Number(e.target.value))}
                className="w-full"
              />
              <div className="flex justify-between text-xs text-gray-500 mt-1">
                <span>-50%</span>
                <span>Base: {baseSquareFootage.toLocaleString()} SF</span>
                <span>+50%</span>
              </div>
            </div>

            {/* Finish Level */}
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Finish Level
              </label>
              <div className="grid grid-cols-4 gap-2">
                {['economy', 'standard', 'premium', 'luxury'].map(level => (
                  <button
                    key={level}
                    onClick={() => setFinishLevel(level)}
                    className={`px-3 py-2 rounded-lg border-2 transition capitalize ${
                      finishLevel === level
                        ? 'border-blue-500 bg-blue-50 text-blue-700'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    {level}
                  </button>
                ))}
              </div>
            </div>

            {/* Parking Type */}
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Parking Configuration
              </label>
              <div className="grid grid-cols-4 gap-2">
                {['none', 'surface', 'garage', 'underground'].map(type => (
                  <button
                    key={type}
                    onClick={() => setParkingType(type)}
                    className={`px-3 py-2 rounded-lg border-2 transition capitalize ${
                      parkingType === type
                        ? 'border-blue-500 bg-blue-50 text-blue-700'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    {type}
                  </button>
                ))}
              </div>
            </div>

            {/* Floors */}
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Number of Floors: {floors}
              </label>
              <input
                type="range"
                min={1}
                max={20}
                step={1}
                value={floors}
                onChange={(e) => setFloors(Number(e.target.value))}
                className="w-full"
              />
              <div className="flex justify-between text-xs text-gray-500 mt-1">
                <span>1</span>
                <span>10</span>
                <span>20</span>
              </div>
            </div>

            {/* Project Class */}
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Construction Type
              </label>
              <select
                value={projectClass}
                onChange={(e) => setProjectClass(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="ground_up">Ground-Up Construction</option>
                <option value="addition">Addition to Existing</option>
                <option value="renovation">Renovation</option>
                <option value="tenant_improvement">Tenant Improvement</option>
              </select>
            </div>
          </div>
        </div>

        {/* Right Column - Impact Preview */}
        <div className="lg:col-span-1">
          <div className="bg-white rounded-lg border border-gray-200 p-6 sticky top-6">
            <h3 className="text-lg font-semibold mb-4">Impact Preview</h3>

            {calculating ? (
              <div className="text-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-2"></div>
                <p className="text-gray-600">Calculating...</p>
              </div>
            ) : preview ? (
              <>
                {/* Cost Impact */}
                <div className="mb-4">
                  <p className="text-sm text-gray-600 mb-1">Total Project Cost</p>
                  <div className="flex items-baseline gap-2">
                    <p className="text-3xl font-bold">
                      {formatCurrency(preview.totals.total_project_cost)}
                    </p>
                    {preview.totals.total_project_cost !== baseTotalCost && (
                      <span className={`flex items-center gap-1 text-sm ${
                        preview.totals.total_project_cost > baseTotalCost
                          ? 'text-red-600'
                          : 'text-green-600'
                      }`}>
                        {preview.totals.total_project_cost > baseTotalCost ? (
                          <TrendingUp className="h-4 w-4" />
                        ) : (
                          <TrendingDown className="h-4 w-4" />
                        )}
                        {((preview.totals.total_project_cost / baseTotalCost - 1) * 100).toFixed(1)}%
                      </span>
                    )}
                  </div>
                  <p className="text-sm text-gray-500">
                    vs. {formatCurrency(baseTotalCost)} base
                  </p>
                </div>

                {/* Cost per SF */}
                <div className="mb-4">
                  <p className="text-sm text-gray-600 mb-1">Cost per Square Foot</p>
                  <p className="text-2xl font-bold">
                    ${preview.totals.cost_per_sf}/SF
                  </p>
                </div>

                <hr className="my-4" />

                {/* Financial Metrics */}
                {preview.ownership_analysis && (
                  <>
                    <p className="text-sm font-medium text-gray-700 mb-3">
                      Financial Metrics
                    </p>
                    <div className="grid grid-cols-2 gap-3">
                      <div>
                        <p className="text-xs text-gray-600">ROI</p>
                        <p className="text-lg font-semibold">
                          {(preview.ownership_analysis.estimated_roi * 100).toFixed(1)}%
                        </p>
                      </div>
                      <div>
                        <p className="text-xs text-gray-600">Payback</p>
                        <p className="text-lg font-semibold">
                          {preview.ownership_analysis.payback_years?.toFixed(1) || 'N/A'} yrs
                        </p>
                      </div>
                      <div>
                        <p className="text-xs text-gray-600">DSCR</p>
                        <p className="text-lg font-semibold">
                          {preview.ownership_analysis.dscr?.toFixed(2) || 'N/A'}
                        </p>
                      </div>
                      <div>
                        <p className="text-xs text-gray-600">Cash/Cash</p>
                        <p className="text-lg font-semibold">
                          {(preview.ownership_analysis.cash_on_cash_return * 100).toFixed(1)}%
                        </p>
                      </div>
                    </div>
                  </>
                )}

                <div className="mt-4 p-3 bg-blue-50 rounded-lg">
                  <div className="flex items-start gap-2">
                    <AlertCircle className="h-4 w-4 text-blue-600 mt-0.5" />
                    <p className="text-sm text-blue-900">
                      This scenario {preview.totals.total_project_cost > baseTotalCost ? 'increases' : 'decreases'} your
                      investment by {formatCurrency(Math.abs(preview.totals.total_project_cost - baseTotalCost))}
                    </p>
                  </div>
                </div>
              </>
            ) : (
              <div className="p-4 bg-gray-50 rounded-lg">
                <div className="text-center py-4">
                  <p className="text-sm text-gray-600">
                    Adjust parameters to calculate impact
                  </p>
                </div>
              </div>
            )}
          </div>

          {/* Action Buttons */}
          <div className="mt-4 flex gap-3">
            <button
              onClick={handleSave}
              disabled={!name.trim() || !preview || calculating}
              className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
              title={!name.trim() ? "Enter a scenario name" : !preview ? "Waiting for calculation" : "Save scenario"}
            >
              Save Scenario
            </button>
            <button
              onClick={onCancel}
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition"
            >
              Cancel
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ScenarioBuilder;