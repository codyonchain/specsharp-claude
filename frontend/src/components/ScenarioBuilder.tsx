import React, { useState, useEffect, useCallback } from 'react';
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
  ChevronRight,
  Building2,
  Layers,
  Car,
  Sparkles,
  Calculator,
  HardHat
} from 'lucide-react';
import scenarioApi from '../services/scenarioApi';
import scenarioV2Api from '../services/scenarioV2Api';
import api from '../services/api';
import { formatCurrency, formatPercentage } from '../utils/formatters';
import { debugProjectData } from '../utils/debugProjectData';
import debounce from 'lodash/debounce';

interface ScenarioBuilderProps {
  projectId: string;
  projectName: string;
  buildingType: string;
  baseProject: any;
  onClose?: () => void;
}

interface ImpactPreview {
  totalCost: number;
  costDelta: number;
  roi: number;
  roiDelta: number;
  payback: number;
  paybackDelta: number;
  costPerSqft: number;
  costPerSqftDelta: number;
}

const ScenarioBuilder: React.FC<ScenarioBuilderProps> = ({
  projectId,
  projectName,
  buildingType,
  baseProject,
  onClose
}) => {
  // Detect if this is a V2 project (has proj_ prefix or is from localStorage)
  const isV2Project = projectId?.startsWith('proj_') || !baseProject?.user_id;
  const activeApi = isV2Project ? scenarioV2Api : scenarioApi;
  
  // Form state for new scenario
  const [scenarioName, setScenarioName] = useState('');
  const [description, setDescription] = useState('');
  const [isCreating, setIsCreating] = useState(false);
  const [loading, setLoading] = useState(false);
  
  // Modification parameters
  const [squareFootage, setSquareFootage] = useState(baseProject?.square_footage || 5000);
  const [finishLevel, setFinishLevel] = useState(baseProject?.finish_level || 'Standard');
  const [parkingType, setParkingType] = useState(baseProject?.parking_type || 'Surface');
  const [numberOfFloors, setNumberOfFloors] = useState(baseProject?.floors || 1);
  const [constructionType, setConstructionType] = useState(baseProject?.project_classification || 'ground_up');
  
  // Impact preview
  const [impactPreview, setImpactPreview] = useState<ImpactPreview | null>(null);
  const [calculating, setCalculating] = useState(false);
  
  // List of saved scenarios
  const [scenarios, setScenarios] = useState<any[]>([]);
  const [selectedScenarios, setSelectedScenarios] = useState<string[]>([]);
  const [comparison, setComparison] = useState<any>(null);
  const [activeTab, setActiveTab] = useState<'create' | 'scenarios' | 'compare'>('create');

  // Load existing scenarios on mount
  useEffect(() => {
    console.log('ScenarioBuilder mounted with projectId:', projectId, 'isV2:', isV2Project);
    
    // Debug the base project data to see what we're working with
    if (baseProject) {
      debugProjectData(baseProject, 'Base Project in ScenarioBuilder');
    }
    
    if (projectId && projectId !== 'undefined') {
      loadScenarios();
    }
  }, [projectId]);

  const loadScenarios = async () => {
    try {
      // Pass baseProject data for V2 projects
      const data = isV2Project 
        ? await scenarioV2Api.listScenarios(projectId, baseProject)
        : await scenarioApi.listScenarios(projectId);
      setScenarios(data);
      
      // Auto-select first two for comparison if available
      if (data.length >= 2) {
        setSelectedScenarios([data[0].id, data[1].id]);
      }
    } catch (error) {
      console.error('Error loading scenarios:', error);
      // If V1 API fails for a V2 project, initialize with empty array
      if (isV2Project) {
        setScenarios([]);
      }
    }
  };

  // Calculate impact preview when parameters change
  const calculateImpact = useCallback(
    debounce(async () => {
      if (!scenarioName.trim()) {
        setImpactPreview(null);
        return;
      }

      setCalculating(true);
      try {
        // Build modifications object matching backend expectations
        const modifications = {
          square_footage: squareFootage,
          finish_level: finishLevel.toLowerCase(),
          parking_type: parkingType.toLowerCase().replace(' ', '_'),
          floors: numberOfFloors,
          project_classification: constructionType
        };

        let result;
        if (isV2Project) {
          // Use V2 API for localStorage projects
          result = await scenarioV2Api.calculateScenarioImpact(projectId, modifications);
        } else {
          // Use V1 API for database projects
          const response = await api.post(`/projects/${projectId}/calculate-scenario`, {
            modifications
          });
          result = response.data;
        }
        
        // Get base values with fallbacks
        const baseCost = baseProject?.total_cost || baseProject?.total_project_cost || baseProject?.totalCost || 0;
        const baseROI = baseProject?.roi || 0.08;
        const basePayback = baseProject?.payback_period || 5;
        const baseCostPerSqft = baseProject?.cost_per_sqft || baseProject?.costPerSqft || 250;
        
        // Calculate deltas with proper values
        setImpactPreview({
          totalCost: result.total_cost || result.total_project_cost || 0,
          costDelta: (result.total_cost || result.total_project_cost || 0) - baseCost,
          roi: result.roi || 0,
          roiDelta: (result.roi || 0) - baseROI,
          payback: result.payback_period || 0,
          paybackDelta: (result.payback_period || 0) - basePayback,
          costPerSqft: result.cost_per_sqft || 0,
          costPerSqftDelta: (result.cost_per_sqft || 0) - baseCostPerSqft
        });
      } catch (error) {
        console.error('Error calculating impact:', error);
        // Provide fallback calculation if API fails
        const baseCost = baseProject?.total_cost || baseProject?.total_project_cost || 1000000;
        let costMultiplier = 1.0;
        
        // Apply construction type multipliers
        if (constructionType === 'addition') costMultiplier = 1.15;
        if (constructionType === 'renovation') costMultiplier = 1.35;
        
        // Apply finish level adjustments
        if (finishLevel === 'Premium') costMultiplier *= 1.15;
        if (finishLevel === 'Luxury') costMultiplier *= 1.30;
        if (finishLevel === 'Economy') costMultiplier *= 0.85;
        
        // Apply parking adjustments
        if (parkingType === 'None') costMultiplier *= 0.90;
        if (parkingType === 'Garage') costMultiplier *= 1.10;
        if (parkingType === 'Underground') costMultiplier *= 1.20;
        
        // Calculate estimated cost
        const estimatedCost = baseCost * costMultiplier * (squareFootage / (baseProject?.square_footage || 5000));
        
        setImpactPreview({
          totalCost: estimatedCost,
          costDelta: estimatedCost - baseCost,
          roi: 0.08 * (baseCost / estimatedCost),
          roiDelta: 0.08 * (baseCost / estimatedCost) - 0.08,
          payback: 5 * (estimatedCost / baseCost),
          paybackDelta: 5 * (estimatedCost / baseCost) - 5,
          costPerSqft: estimatedCost / squareFootage,
          costPerSqftDelta: (estimatedCost / squareFootage) - (baseCost / (baseProject?.square_footage || 5000))
        });
      } finally {
        setCalculating(false);
      }
    }, 500),
    [scenarioName, squareFootage, finishLevel, parkingType, numberOfFloors, constructionType, projectId, baseProject]
  );

  // Trigger impact calculation when parameters change
  useEffect(() => {
    calculateImpact();
  }, [squareFootage, finishLevel, parkingType, numberOfFloors, constructionType, scenarioName]);

  const handleSaveScenario = async () => {
    if (!scenarioName.trim()) {
      alert('Please enter a scenario name');
      return;
    }

    setLoading(true);
    try {
      // Build modifications object matching backend expectations
      const modifications = {
        square_footage: squareFootage,
        finish_level: finishLevel.toLowerCase(),
        parking_type: parkingType.toLowerCase().replace(' ', '_'),
        floors: numberOfFloors,
        project_classification: constructionType
      };

      console.log('Saving scenario with:', {
        projectId,
        name: scenarioName,
        description,
        modifications,
        isV2Project
      });

      // Create the scenario using the correct API (V2 for localStorage projects, V1 for database projects)
      const response = isV2Project 
        ? await scenarioV2Api.createScenario(
            projectId,
            scenarioName,
            description || `${scenarioName} - Modified scenario for ${projectName}`,
            modifications,
            baseProject  // Pass base project data for V2
          )
        : await scenarioApi.createScenario(
            projectId,
            scenarioName,
            description || `${scenarioName} - Modified scenario for ${projectName}`,
            modifications
          );

      console.log('Scenario saved successfully:', response);

      // Show success message
      const successMessage = `Scenario "${scenarioName}" saved successfully! You can now compare it with other scenarios.`;
      
      // Reset form
      setScenarioName('');
      setDescription('');
      setSquareFootage(baseProject?.square_footage || 5000);
      setFinishLevel(baseProject?.finish_level || 'Standard');
      setParkingType(baseProject?.parking_type || 'Surface');
      setNumberOfFloors(baseProject?.floors || 1);
      setConstructionType(baseProject?.project_classification || 'ground_up');
      setImpactPreview(null);
      
      // Reload scenarios and switch to scenarios tab
      await loadScenarios();
      setActiveTab('scenarios');
      
      // Show brief success notification
      setTimeout(() => {
        if (scenarios.length >= 1) {
          setSelectedScenarios([...selectedScenarios, response.id]);
        }
      }, 100);
      
    } catch (error: any) {
      console.error('Error creating scenario:', error);
      const errorMessage = error.response?.data?.detail || error.message || 'Failed to save scenario';
      alert(`Error: ${errorMessage}`);
    } finally {
      setLoading(false);
    }
  };

  const handleCompareScenarios = async () => {
    if (selectedScenarios.length < 2) {
      alert('Please select at least 2 scenarios to compare');
      return;
    }

    setLoading(true);
    try {
      const comparisonData = await activeApi.compareScenarios(
        projectId,
        selectedScenarios,
        `${projectName} Comparison`
      );
      setComparison(comparisonData);
      setActiveTab('compare');
    } catch (error) {
      console.error('Error comparing scenarios:', error);
      alert('Failed to compare scenarios');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteScenario = async (scenarioId: string) => {
    if (!confirm('Are you sure you want to delete this scenario?')) return;
    
    try {
      await activeApi.deleteScenario(scenarioId);
      await loadScenarios();
      
      // Remove from selected if it was selected
      setSelectedScenarios(prev => prev.filter(id => id !== scenarioId));
    } catch (error) {
      console.error('Error deleting scenario:', error);
    }
  };

  const renderImpactPreview = () => {
    if (!impactPreview && !calculating) {
      return (
        <div className="bg-gray-50 rounded-lg p-4 text-center text-gray-500">
          Enter a scenario name to see impact preview
        </div>
      );
    }

    if (calculating) {
      return (
        <div className="bg-gray-50 rounded-lg p-4 text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-2 text-sm text-gray-600">Calculating impact...</p>
        </div>
      );
    }

    if (!impactPreview) return null;

    return (
      <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-lg p-4 space-y-3">
        <h4 className="font-semibold text-gray-900 flex items-center gap-2">
          <Calculator className="h-4 w-4" />
          Impact Preview
        </h4>
        
        <div className="grid grid-cols-2 gap-3">
          <div className="bg-white rounded p-3">
            <div className="text-xs text-gray-600 mb-1">Total Cost</div>
            <div className="font-semibold text-lg">
              {formatCurrency(impactPreview.totalCost)}
            </div>
            <div className={`text-sm ${impactPreview.costDelta > 0 ? 'text-red-600' : 'text-green-600'}`}>
              {impactPreview.costDelta > 0 ? '+' : ''}{formatCurrency(impactPreview.costDelta)}
            </div>
          </div>
          
          <div className="bg-white rounded p-3">
            <div className="text-xs text-gray-600 mb-1">Cost/SF</div>
            <div className="font-semibold text-lg">
              ${impactPreview.costPerSqft.toFixed(0)}/SF
            </div>
            <div className={`text-sm ${impactPreview.costPerSqftDelta > 0 ? 'text-red-600' : 'text-green-600'}`}>
              {impactPreview.costPerSqftDelta > 0 ? '+' : ''}${impactPreview.costPerSqftDelta.toFixed(0)}/SF
            </div>
          </div>
          
          <div className="bg-white rounded p-3">
            <div className="text-xs text-gray-600 mb-1">ROI</div>
            <div className="font-semibold text-lg">
              {(impactPreview.roi * 100).toFixed(1)}%
            </div>
            <div className={`text-sm ${impactPreview.roiDelta < 0 ? 'text-red-600' : 'text-green-600'}`}>
              {impactPreview.roiDelta > 0 ? '+' : ''}{(impactPreview.roiDelta * 100).toFixed(1)}%
            </div>
          </div>
          
          <div className="bg-white rounded p-3">
            <div className="text-xs text-gray-600 mb-1">Payback</div>
            <div className="font-semibold text-lg">
              {impactPreview.payback.toFixed(1)} yrs
            </div>
            <div className={`text-sm ${impactPreview.paybackDelta > 0 ? 'text-red-600' : 'text-green-600'}`}>
              {impactPreview.paybackDelta > 0 ? '+' : ''}{impactPreview.paybackDelta.toFixed(1)} yrs
            </div>
          </div>
        </div>
      </div>
    );
  };

  // Scenario Templates Component
  const ScenarioTemplates: React.FC = () => (
    <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-6 mb-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
        <Sparkles className="h-5 w-5 text-blue-600" />
        Quick Compare Templates
      </h3>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <button 
          className="bg-white rounded-lg p-4 border-2 border-gray-200 hover:border-blue-500 hover:shadow-md transition-all text-left group"
          onClick={() => {
            setScenarioName("Premium Finishes");
            setFinishLevel("Premium");
            setDescription("Upgraded to premium finishes throughout the building");
            setActiveTab('create');
          }}
        >
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 bg-blue-100 rounded-lg group-hover:bg-blue-200 transition-colors">
              <Sparkles className="h-6 w-6 text-blue-600" />
            </div>
            <div className="font-semibold text-gray-900">Premium Finishes</div>
          </div>
          <p className="text-sm text-gray-600">Compare standard vs premium finish levels</p>
          <p className="text-xs text-blue-600 mt-2">Expected Impact: +15-20% cost</p>
        </button>
        
        <button 
          className="bg-white rounded-lg p-4 border-2 border-gray-200 hover:border-blue-500 hover:shadow-md transition-all text-left group"
          onClick={() => {
            setScenarioName("No Parking");
            setParkingType("None");
            setDescription("Remove parking to reduce construction costs");
            setActiveTab('create');
          }}
        >
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 bg-green-100 rounded-lg group-hover:bg-green-200 transition-colors">
              <Car className="h-6 w-6 text-green-600" />
            </div>
            <div className="font-semibold text-gray-900">No Parking</div>
          </div>
          <p className="text-sm text-gray-600">Assess impact of removing parking</p>
          <p className="text-xs text-green-600 mt-2">Expected Savings: -10-15% cost</p>
        </button>
        
        <button 
          className="bg-white rounded-lg p-4 border-2 border-gray-200 hover:border-blue-500 hover:shadow-md transition-all text-left group"
          onClick={() => {
            const newSize = Math.round(squareFootage * 1.2);
            setScenarioName("20% Larger");
            setSquareFootage(newSize);
            setDescription(`Increase building size to ${newSize.toLocaleString()} SF`);
            setActiveTab('create');
          }}
        >
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 bg-purple-100 rounded-lg group-hover:bg-purple-200 transition-colors">
              <Building2 className="h-6 w-6 text-purple-600" />
            </div>
            <div className="font-semibold text-gray-900">Size Increase</div>
          </div>
          <p className="text-sm text-gray-600">Explore economies of scale with +20% size</p>
          <p className="text-xs text-purple-600 mt-2">Better cost per SF at scale</p>
        </button>

        <button 
          className="bg-white rounded-lg p-4 border-2 border-gray-200 hover:border-blue-500 hover:shadow-md transition-all text-left group"
          onClick={() => {
            setScenarioName("Addition vs Ground-Up");
            setConstructionType("addition");
            setDescription("Compare addition costs with 15% premium");
            setActiveTab('create');
          }}
        >
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 bg-orange-100 rounded-lg group-hover:bg-orange-200 transition-colors">
              <Layers className="h-6 w-6 text-orange-600" />
            </div>
            <div className="font-semibold text-gray-900">Addition</div>
          </div>
          <p className="text-sm text-gray-600">Model as building addition (+15%)</p>
          <p className="text-xs text-orange-600 mt-2">Includes tie-in complexity</p>
        </button>

        <button 
          className="bg-white rounded-lg p-4 border-2 border-gray-200 hover:border-blue-500 hover:shadow-md transition-all text-left group"
          onClick={() => {
            setScenarioName("Renovation Scope");
            setConstructionType("renovation");
            setDescription("Full renovation with 35% cost premium");
            setActiveTab('create');
          }}
        >
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 bg-red-100 rounded-lg group-hover:bg-red-200 transition-colors">
              <HardHat className="h-6 w-6 text-red-600" />
            </div>
            <div className="font-semibold text-gray-900">Renovation</div>
          </div>
          <p className="text-sm text-gray-600">Model as renovation (+35%)</p>
          <p className="text-xs text-red-600 mt-2">Includes demo & unknowns</p>
        </button>

        <button 
          className="bg-white rounded-lg p-4 border-2 border-gray-200 hover:border-blue-500 hover:shadow-md transition-all text-left group"
          onClick={() => {
            setScenarioName("Multi-Story");
            setNumberOfFloors(Math.min(5, numberOfFloors + 2));
            setDescription("Add floors to explore vertical expansion");
            setActiveTab('create');
          }}
        >
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 bg-indigo-100 rounded-lg group-hover:bg-indigo-200 transition-colors">
              <Layers className="h-6 w-6 text-indigo-600" />
            </div>
            <div className="font-semibold text-gray-900">Multi-Story</div>
          </div>
          <p className="text-sm text-gray-600">Add 2 floors for vertical growth</p>
          <p className="text-xs text-indigo-600 mt-2">Structural & MEP impacts</p>
        </button>
      </div>
    </div>
  );

  return (
    <div className="bg-white rounded-lg shadow-xl max-w-7xl mx-auto p-6">
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Scenario Builder</h2>
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
          onClick={() => setActiveTab('create')}
          className={`px-4 py-2 font-medium ${
            activeTab === 'create'
              ? 'text-blue-600 border-b-2 border-blue-600'
              : 'text-gray-500 hover:text-gray-700'
          }`}
        >
          <Plus className="inline h-4 w-4 mr-1" />
          Create Scenario
        </button>
        <button
          onClick={() => setActiveTab('scenarios')}
          className={`px-4 py-2 font-medium ${
            activeTab === 'scenarios'
              ? 'text-blue-600 border-b-2 border-blue-600'
              : 'text-gray-500 hover:text-gray-700'
          }`}
        >
          Saved Scenarios ({scenarios.length})
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
          <BarChart3 className="inline h-4 w-4 mr-1" />
          Compare
        </button>
      </div>

      {/* Create Scenario Tab */}
      {activeTab === 'create' && (
        <div className="space-y-6">
          {/* Show templates when no scenario name is entered */}
          {!scenarioName && <ScenarioTemplates />}
          
          {/* Scenario Name and Description */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Scenario Name *
              </label>
              <input
                type="text"
                value={scenarioName}
                onChange={(e) => setScenarioName(e.target.value)}
                placeholder="e.g., Premium Finishes Option"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Description
              </label>
              <input
                type="text"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Brief description of changes"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
          </div>

          {/* Square Footage Slider */}
          <div className="bg-gray-50 rounded-lg p-4">
            <label className="block text-sm font-medium text-gray-700 mb-3">
              <Building2 className="inline h-4 w-4 mr-1" />
              Square Footage: {squareFootage.toLocaleString()} SF
            </label>
            <div className="flex items-center gap-4">
              <span className="text-sm text-gray-500">1,000</span>
              <input
                type="range"
                min={1000}
                max={50000}
                step={100}
                value={squareFootage}
                onChange={(e) => setSquareFootage(Number(e.target.value))}
                className="flex-1 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer slider"
              />
              <span className="text-sm text-gray-500">50,000</span>
            </div>
          </div>

          {/* Finish Level Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">
              <Sparkles className="inline h-4 w-4 mr-1" />
              Finish Level
            </label>
            <div className="grid grid-cols-4 gap-3">
              {['Economy', 'Standard', 'Premium', 'Luxury'].map((level) => (
                <button
                  key={level}
                  onClick={() => setFinishLevel(level)}
                  className={`px-4 py-3 rounded-lg border-2 font-medium transition-all ${
                    finishLevel === level
                      ? 'border-blue-500 bg-blue-50 text-blue-700'
                      : 'border-gray-200 hover:border-gray-300 text-gray-700'
                  }`}
                >
                  {level}
                </button>
              ))}
            </div>
          </div>

          {/* Parking Type Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">
              <Car className="inline h-4 w-4 mr-1" />
              Parking Configuration
            </label>
            <div className="grid grid-cols-4 gap-3">
              {['None', 'Surface', 'Garage', 'Underground'].map((type) => (
                <button
                  key={type}
                  onClick={() => setParkingType(type)}
                  className={`px-4 py-3 rounded-lg border-2 font-medium transition-all ${
                    parkingType === type
                      ? 'border-blue-500 bg-blue-50 text-blue-700'
                      : 'border-gray-200 hover:border-gray-300 text-gray-700'
                  }`}
                >
                  {type}
                </button>
              ))}
            </div>
          </div>

          {/* Number of Floors */}
          <div className="bg-gray-50 rounded-lg p-4">
            <label className="block text-sm font-medium text-gray-700 mb-3">
              <Layers className="inline h-4 w-4 mr-1" />
              Number of Floors: {numberOfFloors}
            </label>
            <div className="flex items-center gap-4">
              <span className="text-sm text-gray-500">1</span>
              <input
                type="range"
                min={1}
                max={20}
                step={1}
                value={numberOfFloors}
                onChange={(e) => setNumberOfFloors(Number(e.target.value))}
                className="flex-1 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
              />
              <span className="text-sm text-gray-500">20</span>
            </div>
          </div>

          {/* Construction Type */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">
              Construction Type
            </label>
            <div className="grid grid-cols-3 gap-3">
              {[
                { value: 'ground_up', label: 'Ground-Up', desc: 'New construction' },
                { value: 'addition', label: 'Addition', desc: '+15% for tie-ins' },
                { value: 'renovation', label: 'Renovation', desc: '+35% for demo' }
              ].map((type) => (
                <button
                  key={type.value}
                  onClick={() => setConstructionType(type.value)}
                  className={`p-4 rounded-lg border-2 text-left transition-all ${
                    constructionType === type.value
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <div className="font-medium text-gray-900">{type.label}</div>
                  <div className="text-xs text-gray-600 mt-1">{type.desc}</div>
                </button>
              ))}
            </div>
          </div>

          {/* Impact Preview */}
          {renderImpactPreview()}

          {/* Action Buttons */}
          <div className="flex gap-3 pt-4 border-t">
            <button
              onClick={handleSaveScenario}
              disabled={!scenarioName.trim() || loading}
              className="flex-1 bg-blue-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {loading ? 'Saving...' : 'Save Scenario'}
            </button>
            <button
              onClick={() => {
                setScenarioName('');
                setDescription('');
                setSquareFootage(baseProject?.square_footage || 5000);
                setFinishLevel(baseProject?.finish_level || 'Standard');
                setParkingType(baseProject?.parking_type || 'Surface');
                setNumberOfFloors(baseProject?.floors || 1);
                setConstructionType(baseProject?.project_classification || 'ground_up');
                setImpactPreview(null);
              }}
              className="px-6 py-3 border border-gray-300 rounded-lg font-medium hover:bg-gray-50 transition-colors"
            >
              Reset
            </button>
          </div>
        </div>
      )}

      {/* Saved Scenarios Tab */}
      {activeTab === 'scenarios' && (
        <div className="space-y-4">
          {scenarios.length === 0 ? (
            <div className="text-center py-12 bg-gray-50 rounded-lg">
              <Building2 className="h-12 w-12 text-gray-400 mx-auto mb-3" />
              <p className="text-gray-600">No scenarios created yet</p>
              <button
                onClick={() => setActiveTab('create')}
                className="mt-4 text-blue-600 hover:text-blue-700 font-medium"
              >
                Create your first scenario
              </button>
            </div>
          ) : (
            <>
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
                        {(scenario.is_base || scenario.isBase) && (
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
                        className="h-4 w-4 text-blue-600 rounded"
                      />
                    </div>
                    
                    <p className="text-sm text-gray-600 mb-3">{scenario.description || 'No description'}</p>
                    
                    <div className="space-y-1 text-sm">
                      <div className="flex justify-between">
                        <span className="text-gray-500">Total Cost:</span>
                        <span className="font-medium">{formatCurrency(
                          scenario.total_cost || 
                          scenario.results?.total_project_cost || 
                          scenario.results?.totalCost || 0
                        )}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-500">Cost/SF:</span>
                        <span className="font-medium">${
                          scenario.cost_per_sqft || 
                          scenario.results?.cost_per_sqft || 
                          scenario.results?.costPerSqft || 0
                        }/SF</span>
                      </div>
                    </div>
                    
                    {!scenario.is_base && !scenario.isBase && (
                      <button
                        onClick={() => handleDeleteScenario(scenario.id)}
                        className="mt-3 text-red-500 hover:text-red-700 text-sm"
                      >
                        <Trash2 className="inline h-4 w-4 mr-1" />
                        Delete
                      </button>
                    )}
                  </div>
                ))}
              </div>

              {selectedScenarios.length >= 2 && (
                <div className="flex justify-center pt-4">
                  <button
                    onClick={handleCompareScenarios}
                    className="bg-blue-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-blue-700 flex items-center gap-2"
                  >
                    <BarChart3 className="h-5 w-5" />
                    Compare {selectedScenarios.length} Scenarios
                  </button>
                </div>
              )}
            </>
          )}
        </div>
      )}

      {/* Compare Tab */}
      {activeTab === 'compare' && (
        <div className="space-y-6">
          {selectedScenarios.length < 2 ? (
            <div className="text-center py-12 bg-gray-50 rounded-lg">
              <BarChart3 className="h-12 w-12 text-gray-400 mx-auto mb-3" />
              <p className="text-gray-600 mb-4">Select at least 2 scenarios to compare</p>
              <button
                onClick={() => setActiveTab('scenarios')}
                className="text-blue-600 hover:text-blue-700 font-medium"
              >
                Go to Saved Scenarios
              </button>
            </div>
          ) : comparison ? (
            <>
              {/* Summary Cards */}
              <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                  <Target className="h-5 w-5 text-blue-600" />
                  Comparison Insights
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                  <div className="bg-white rounded-lg p-4 border border-green-200">
                    <div className="flex items-center gap-2 mb-2">
                      <TrendingUp className="h-4 w-4 text-green-600" />
                      <div className="text-xs text-gray-600">Best Overall</div>
                    </div>
                    <div className="font-bold text-green-600">{comparison.best_overall_scenario}</div>
                    <div className="text-xs text-gray-500 mt-1">Optimal balance of cost & ROI</div>
                  </div>
                  <div className="bg-white rounded-lg p-4 border border-blue-200">
                    <div className="flex items-center gap-2 mb-2">
                      <DollarSign className="h-4 w-4 text-blue-600" />
                      <div className="text-xs text-gray-600">Lowest Cost</div>
                    </div>
                    <div className="font-bold text-blue-600">{comparison.lowest_cost_scenario}</div>
                    <div className="text-xs text-gray-500 mt-1">Minimum capital required</div>
                  </div>
                  <div className="bg-white rounded-lg p-4 border border-purple-200">
                    <div className="flex items-center gap-2 mb-2">
                      <Target className="h-4 w-4 text-purple-600" />
                      <div className="text-xs text-gray-600">Highest ROI</div>
                    </div>
                    <div className="font-bold text-purple-600">{comparison.best_roi_scenario}</div>
                    <div className="text-xs text-gray-500 mt-1">Maximum return potential</div>
                  </div>
                  <div className="bg-white rounded-lg p-4 border border-orange-200">
                    <div className="flex items-center gap-2 mb-2">
                      <Clock className="h-4 w-4 text-orange-600" />
                      <div className="text-xs text-gray-600">Fastest Payback</div>
                    </div>
                    <div className="font-bold text-orange-600">{comparison.fastest_payback_scenario}</div>
                    <div className="text-xs text-gray-500 mt-1">Quickest capital recovery</div>
                  </div>
                </div>
              </div>

              {/* Detailed Comparison Table */}
              <div className="bg-white rounded-lg shadow overflow-hidden">
                <div className="px-6 py-4 bg-gray-50 border-b">
                  <h3 className="text-lg font-semibold text-gray-900">Detailed Metrics Comparison</h3>
                </div>
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="sticky left-0 bg-gray-50 px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Metric
                        </th>
                        {comparison.scenario_names.map((name: string, idx: number) => (
                          <th key={idx} className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            {name}
                            {idx === 0 && <span className="ml-1 text-gray-400">(Base)</span>}
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {Object.entries(comparison.metrics_comparison).map(([metric, values]: [string, any]) => {
                        const metricValues = values as number[];
                        const bestValue = Math.max(...metricValues);
                        const worstValue = Math.min(...metricValues);
                        
                        return (
                          <tr key={metric} className="hover:bg-gray-50">
                            <td className="sticky left-0 bg-white px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                              {metric.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                            </td>
                            {metricValues.map((value: number, idx: number) => {
                              const isBase = idx === 0;
                              const delta = isBase ? 0 : value - metricValues[0];
                              const percentChange = isBase ? 0 : ((value - metricValues[0]) / metricValues[0]) * 100;
                              const isBest = value === bestValue && metricValues.length > 1;
                              const isWorst = value === worstValue && metricValues.length > 1;
                              
                              return (
                                <td key={idx} className="px-6 py-4 whitespace-nowrap text-sm">
                                  <div className={`${isBest ? 'text-green-600 font-semibold' : isWorst ? 'text-red-600' : 'text-gray-900'}`}>
                                    {metric.includes('cost') ? formatCurrency(value) :
                                     metric.includes('roi') || metric.includes('irr') ? formatPercentage(value) :
                                     metric.includes('payback') ? `${value.toFixed(1)} yrs` :
                                     metric.includes('sqft') ? `${value.toFixed(0)}/SF` :
                                     value.toFixed(2)}
                                  </div>
                                  {!isBase && delta !== 0 && (
                                    <div className={`text-xs ${delta > 0 ? 'text-red-500' : 'text-green-500'}`}>
                                      {delta > 0 ? '+' : ''}{metric.includes('cost') ? formatCurrency(delta) : percentChange.toFixed(1) + '%'}
                                    </div>
                                  )}
                                </td>
                              );
                            })}
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* Export Options */}
              <div className="flex justify-end gap-3 pt-4 border-t">
                <button
                  onClick={() => alert('Board presentation export coming soon!')}
                  className="px-4 py-2 border border-gray-300 rounded-lg font-medium hover:bg-gray-50 flex items-center gap-2"
                >
                  <Download className="h-4 w-4" />
                  Export to PowerPoint
                </button>
                <button
                  onClick={() => alert('Excel export coming soon!')}
                  className="px-4 py-2 border border-gray-300 rounded-lg font-medium hover:bg-gray-50 flex items-center gap-2"
                >
                  <Download className="h-4 w-4" />
                  Export to Excel
                </button>
                <button
                  onClick={() => window.print()}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 flex items-center gap-2"
                >
                  <Download className="h-4 w-4" />
                  Print Report
                </button>
              </div>
            </>
          ) : (
            <div className="text-center py-8">
              <button
                onClick={handleCompareScenarios}
                disabled={loading}
                className="bg-blue-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50"
              >
                {loading ? 'Loading comparison...' : 'Generate Comparison'}
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default ScenarioBuilder;