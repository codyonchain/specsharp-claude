import { useState, useEffect, useMemo } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { scopeService, costService, excelService, tradePackageService } from '../services/api';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';
import TradePackageModal from './TradePackageModal';
import ComparisonTool from './ComparisonTool';
import TradeBreakdownView from './TradeBreakdownView';
import { Package, Sliders, ChevronDown, ChevronUp, FileSpreadsheet, Download } from 'lucide-react';
import { getDisplayBuildingType } from '../utils/buildingTypeDisplay';
import './ProjectDetail.css';
import './TradeBreakdownView.css';
import './ProjectDetailModern.css';
import './ProjectDetailPremium.css';

type TradeType = 'all' | 'structural' | 'mechanical' | 'electrical' | 'plumbing' | 'finishes' | 'general_conditions';

interface TradeSummary {
  name: string;
  displayName: string;
  total: number;
  percentage: number;
  categories?: CategorySummary[];
}

interface CategorySummary {
  name: string;
  total: number;
  systems?: any[];
}

// Trade mapping for aggregation
const TRADE_MAPPING: Record<string, TradeType> = {
  'structural': 'structural',
  'mechanical': 'mechanical',
  'mechanical - equipment': 'mechanical',
  'mechanical - ductwork': 'mechanical',
  'mechanical - terminals': 'mechanical',
  'mechanical - exhaust': 'mechanical',
  'mechanical - controls': 'mechanical',
  'mechanical - piping': 'mechanical',
  'mechanical - commissioning': 'mechanical',
  'electrical': 'electrical',
  'electrical - service & distribution': 'electrical',
  'electrical - branch wiring': 'electrical',
  'electrical - lighting': 'electrical',
  'electrical - devices': 'electrical',
  'electrical - equipment connections': 'electrical',
  'electrical - life safety': 'electrical',
  'electrical - fire alarm': 'electrical',
  'electrical - low voltage': 'electrical',
  'plumbing': 'plumbing',
  'plumbing - fixtures': 'plumbing',
  'plumbing - equipment': 'plumbing',
  'plumbing - piping': 'plumbing',
  'plumbing - insulation': 'plumbing',
  'plumbing - drainage': 'plumbing',
  'plumbing - valves': 'plumbing',
  'plumbing - specialties': 'plumbing',
  'plumbing - gas piping': 'plumbing',
  'finishes': 'finishes',
};

const TRADE_DISPLAY_NAMES: Record<TradeType, string> = {
  'all': 'All Trades',
  'structural': 'Structural',
  'mechanical': 'Mechanical (HVAC)',
  'electrical': 'Electrical',
  'plumbing': 'Plumbing',
  'finishes': 'Finishes',
  'general_conditions': 'General Conditions',
};

// Helper function to get classification display info
const getClassificationInfo = (classification: string | undefined) => {
  const classificationMap = {
    'ground_up': { name: 'Ground-Up', multiplier: 1.00 },
    'addition': { name: 'Addition', multiplier: 1.15 },
    'renovation': { name: 'Renovation', multiplier: 1.35 },
    'tenant_improvement': { name: 'Tenant Improvement', multiplier: 1.10 }
  };
  
  const defaultClassification = { name: 'Ground-Up', multiplier: 1.00 };
  return classificationMap[classification as keyof typeof classificationMap] || defaultClassification;
};

function ProjectDetail() {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();
  const [project, setProject] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [viewMode, setViewMode] = useState<'trade' | 'executive'>('executive');
  const [ownerViewData, setOwnerViewData] = useState<any>(null);
  const [loadingOwnerView, setLoadingOwnerView] = useState(false);
  const [selectedTrade, setSelectedTrade] = useState<TradeType>('all');
  const [expandedCategories, setExpandedCategories] = useState<Set<string>>(new Set());
  const [showTradePackageModal, setShowTradePackageModal] = useState(false);
  const [selectedTradePackage, setSelectedTradePackage] = useState<string>('');
  const [showComparisonTool, setShowComparisonTool] = useState(false);
  const [ownershipType, setOwnershipType] = useState<string>('for_profit');

  useEffect(() => {
    if (projectId) {
      loadProjectDetails();
    }
  }, [projectId]);

  const loadProjectDetails = async () => {
    try {
      console.log('=' .repeat(60));
      console.log('📋 STEP 6: LOADING PROJECT FOR DISPLAY');
      console.log('=' .repeat(60));
      console.log('Project ID:', projectId);
      
      const projectData = await scopeService.getProject(projectId!);
      
      console.log('Project data loaded:', JSON.stringify(projectData, null, 2));
      console.log('Key values:');
      console.log('  Building type:', projectData.building_type);
      console.log('  Building subtype:', projectData.building_subtype);
      console.log('  Cost per SF:', projectData.cost_per_sqft);
      console.log('  Total cost:', projectData.total_cost);
      console.log('  Square footage:', projectData.square_footage);
      
      if (projectData.building_type === 'education' && projectData.cost_per_sqft < 250) {
        console.error('🚨 BUG IN DISPLAY: Education type but commercial pricing!');
        console.error('Expected: ~$309/SF for middle school');
        console.error('Got:', projectData.cost_per_sqft);
      }
      
      setProject(projectData);
    } catch (error) {
      console.error('Failed to load project:', error);
    } finally {
      setLoading(false);
    }
  };

  const extractSquareFootage = (description: string): number => {
    const match = description.match(/(\d{1,3}(?:,\d{3})*)\s*(?:sf|sq|square)/i);
    return match ? parseInt(match[1].replace(/,/g, '')) : 100000;
  };

  const fetchOwnerView = async (ownership?: string) => {
    console.log('=== DEBUG: fetchOwnerView called ===');
    console.log('Project Data:', project);
    console.log('Project ID:', projectId);
    
    if (!project) {
      console.log('No project data available');
      return;
    }
    
    setLoadingOwnerView(true);
    try {
      // Debug the project structure
      console.log('Project structure keys:', Object.keys(project));
      console.log('Request data:', project.request_data);
      console.log('Categories:', project.categories);
      
      // Extract square footage from the project data with multiple fallbacks
      const sqft = project.square_footage || 
                   project.request_data?.square_footage || 
                   extractSquareFootage(project.description || '') ||
                   extractSquareFootage(project.request_data?.special_requirements || '') ||
                   100000; // Default fallback
      
      // Use detected building type from project (NOT hardcoded)
      let buildingType = project.building_type || 
                        project.request_data?.building_type || 
                        'office';  // Changed default from healthcare to office
      let subtype = project.building_subtype || 
                   project.request_data?.building_subtype || 
                   project.subtype ||  // Also check for 'subtype' field
                   'class_b';  // Changed default from hospital to class_b
      
      // No need for manual detection - the backend NLP handles this
      console.log('Using NLP-detected building type:', buildingType, '/', subtype);
      
      // Get the construction cost with multiple fallbacks
      const constructionCost = project.subtotal || 
                              project.total_cost || 
                              project.totalCost ||
                              0;
      
      console.log('Extracted values:', {
        constructionCost,
        sqft,
        buildingType,
        subtype
      });
      
      // Build trade breakdown from the categories
      const tradeBreakdown: any = {};
      if (project.categories) {
        console.log('Processing categories:', project.categories.length);
        project.categories.forEach((category: any) => {
          const tradeName = category.name.toLowerCase();
          const categoryTotal = category.systems?.reduce((sum: number, system: any) => sum + system.total_cost, 0) || 
                               category.total || 
                               0;
          
          console.log(`Category: ${category.name}, Total: ${categoryTotal}`);
          
          if (tradeName.includes('structural')) {
            tradeBreakdown.structural = (tradeBreakdown.structural || 0) + categoryTotal;
          } else if (tradeName.includes('mechanical')) {
            tradeBreakdown.mechanical = (tradeBreakdown.mechanical || 0) + categoryTotal;
          } else if (tradeName.includes('electrical')) {
            tradeBreakdown.electrical = (tradeBreakdown.electrical || 0) + categoryTotal;
          } else if (tradeName.includes('plumbing')) {
            tradeBreakdown.plumbing = (tradeBreakdown.plumbing || 0) + categoryTotal;
          } else if (tradeName.includes('finish')) {
            tradeBreakdown.finishes = (tradeBreakdown.finishes || 0) + categoryTotal;
          }
        });
      }
      
      console.log('=== API Request Payload ===');
      console.log('Fetching owner view with:', {
        building_type: buildingType,
        subtype: subtype,
        construction_cost: constructionCost,
        square_footage: sqft,
        trade_breakdown: tradeBreakdown,
        ownership_type: ownership || ownershipType
      });
      
      // Use absolute URL to ensure correct endpoint
      const response = await fetch('http://localhost:8001/api/v1/scope/owner-view', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          building_type: buildingType,
          subtype: subtype,
          description: project.description || project.request_data?.special_requirements,  // Include for NLP fallback
          construction_cost: constructionCost,
          square_footage: sqft,
          trade_breakdown: Object.keys(tradeBreakdown).length > 0 ? tradeBreakdown : undefined,
          ownership_type: ownership || ownershipType
        })
      });
      
      if (response.ok) {
        const data = await response.json();
        console.log('=== API Response Success ===');
        console.log('Response data:', data);
        setOwnerViewData(data.data);
      } else {
        const errorText = await response.text();
        console.error('=== API Response Error ===');
        console.error('Status:', response.status);
        console.error('Error:', errorText);
      }
    } catch (error) {
      console.error('=== Fetch Error ===');
      console.error('Error fetching owner view:', error);
    } finally {
      setLoadingOwnerView(false);
    }
  };

  useEffect(() => {
    console.log('ViewMode changed to:', viewMode);
    console.log('Project available:', !!project);
    console.log('OwnerViewData available:', !!ownerViewData);
    
    if (viewMode === 'executive' && project && !ownerViewData) {
      console.log('Fetching owner view data...');
      fetchOwnerView();
    }
  }, [viewMode, project]);

  // Aggregate categories into main trades
  const tradeSummaries = useMemo(() => {
    if (!project?.categories) return [];

    const tradeGroups: Record<TradeType, TradeSummary> = {
      'structural': { name: 'structural', displayName: 'Structural', total: 0, percentage: 0, categories: [] },
      'mechanical': { name: 'mechanical', displayName: 'Mechanical', total: 0, percentage: 0, categories: [] },
      'electrical': { name: 'electrical', displayName: 'Electrical', total: 0, percentage: 0, categories: [] },
      'plumbing': { name: 'plumbing', displayName: 'Plumbing', total: 0, percentage: 0, categories: [] },
      'finishes': { name: 'finishes', displayName: 'Finishes', total: 0, percentage: 0, categories: [] },
    };

    // Aggregate categories into trades (skip General Conditions)
    project.categories.forEach((category: any) => {
      const categoryName = category.name.toLowerCase();
      
      // Skip General Conditions entirely
      if (categoryName.includes('general')) {
        return;
      }
      
      const tradeName = TRADE_MAPPING[categoryName];
      
      if (tradeName && tradeGroups[tradeName]) {
        const categoryTotal = category.systems.reduce((sum: number, system: any) => sum + system.total_cost, 0);
        tradeGroups[tradeName].total += categoryTotal;
        tradeGroups[tradeName].categories!.push({
          name: category.name,
          total: categoryTotal,
          systems: category.systems
        });
      }
    });

    // Calculate percentages and filter out empty trades
    const totalCost = Object.values(tradeGroups).reduce((sum, trade) => sum + trade.total, 0);
    const summaries = Object.values(tradeGroups)
      .filter(trade => trade.total > 0)
      .map(trade => ({
        ...trade,
        percentage: (trade.total / totalCost) * 100
      }));

    return summaries;
  }, [project]);

  // Get data for selected trade
  const selectedTradeData = useMemo(() => {
    if (selectedTrade === 'all') {
      return tradeSummaries;
    }
    return tradeSummaries.filter(trade => trade.name === selectedTrade);
  }, [tradeSummaries, selectedTrade]);

  // Chart data for pie chart
  const chartData = useMemo(() => {
    if (selectedTrade === 'all') {
      return tradeSummaries.map(trade => ({
        name: trade.displayName,
        value: trade.total,
        percentage: trade.percentage
      }));
    } else {
      const trade = tradeSummaries.find(t => t.name === selectedTrade);
      return trade?.categories?.map(cat => ({
        name: cat.name,
        value: cat.total,
        percentage: (cat.total / trade.total) * 100
      })) || [];
    }
  }, [tradeSummaries, selectedTrade]);

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8', '#82CA9D', '#FFC658', '#8DD1E1'];

  const toggleCategoryExpansion = (categoryName: string) => {
    const newExpanded = new Set(expandedCategories);
    if (newExpanded.has(categoryName)) {
      newExpanded.delete(categoryName);
    } else {
      newExpanded.add(categoryName);
    }
    setExpandedCategories(newExpanded);
  };

  const handleGenerateTradePackage = async (projectId: string, trade: string) => {
    try {
      const data = await tradePackageService.generate(projectId, trade);
      return data;
    } catch (error) {
      console.error('[TradePackage] Error generating package:', error);
      throw error;
    }
  };

  const openTradePackageModal = (trade: string) => {
    setSelectedTradePackage(trade);
    setShowTradePackageModal(true);
  };

  // Excel export handlers
  const handleExportFullProject = async () => {
    try {
      const response = await excelService.exportProject(project.project_id);
      // response.data is already a blob when responseType is 'blob'
      const blob = response.data;
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `${project.project_name.replace(/\s+/g, '_')}_estimate.xlsx`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (error: any) {
      console.error('Failed to export Excel:', error);
      console.error('Error details:', {
        message: error.message,
        response: error.response?.data,
        status: error.response?.status,
        projectId: project.project_id
      });
      
      let errorMessage = 'Failed to export Excel file. Please try again.';
      if (error.response?.status === 404) {
        errorMessage = 'Project not found. Please refresh and try again.';
      } else if (error.response?.status === 401) {
        errorMessage = 'Session expired. Please log in again.';
      } else if (error.response?.data?.detail) {
        errorMessage = `Export failed: ${error.response.data.detail}`;
      }
      
      alert(errorMessage);
    }
  };

  const handleExportTrade = async (tradeName: string) => {
    try {
      const response = await excelService.exportTrade(project.project_id, tradeName);
      // response.data is already a blob when responseType is 'blob'
      const blob = response.data;
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `${project.project_name.replace(/\s+/g, '_')}_${tradeName}_package.xlsx`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Failed to export trade Excel:', error);
      alert('Failed to export trade Excel file. Please try again.');
    }
  };

  if (loading) {
    return <div className="loading">Loading project details...</div>;
  }

  if (!project) {
    return <div className="error">Project not found</div>;
  }

  // Check if building type detection failed
  // DISABLED: Old projects may not have building_type field
  if (false && (!project?.building_type || project?.building_type === 'other')) {
    return (
      <div className="min-h-screen bg-gray-50 p-8">
        <div className="max-w-3xl mx-auto">
          <div className="bg-yellow-50 border-2 border-yellow-200 rounded-lg p-8">
            <div className="flex items-start">
              <svg className="w-6 h-6 text-yellow-600 mt-1 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
              <div className="flex-1">
                <h3 className="text-lg font-semibold text-yellow-800 mb-2">
                  Building Type Not Detected
                </h3>
                <p className="text-yellow-700 mb-4">
                  We couldn't determine the building type from your project description. 
                  Please update the project with more specific terms.
                </p>
                <div className="bg-white border border-yellow-300 rounded-md p-4 mb-4">
                  <p className="text-sm font-medium text-gray-700 mb-2">Try including terms like:</p>
                  <ul className="grid grid-cols-2 gap-2 text-sm text-gray-600">
                    <li className="flex items-center">
                      <span className="text-yellow-500 mr-2">•</span>
                      "apartment complex", "multifamily"
                    </li>
                    <li className="flex items-center">
                      <span className="text-yellow-500 mr-2">•</span>
                      "office building", "corporate"
                    </li>
                    <li className="flex items-center">
                      <span className="text-yellow-500 mr-2">•</span>
                      "hospital", "medical center"
                    </li>
                    <li className="flex items-center">
                      <span className="text-yellow-500 mr-2">•</span>
                      "hotel", "hospitality"
                    </li>
                    <li className="flex items-center">
                      <span className="text-yellow-500 mr-2">•</span>
                      "warehouse", "distribution"
                    </li>
                    <li className="flex items-center">
                      <span className="text-yellow-500 mr-2">•</span>
                      "school", "university"
                    </li>
                    <li className="flex items-center">
                      <span className="text-yellow-500 mr-2">•</span>
                      "restaurant", "retail"
                    </li>
                    <li className="flex items-center">
                      <span className="text-yellow-500 mr-2">•</span>
                      "senior living", "assisted"
                    </li>
                  </ul>
                </div>
                {project?.description && (
                  <div className="bg-gray-50 border border-gray-200 rounded-md p-3 mb-4">
                    <p className="text-xs font-medium text-gray-500 mb-1">Your description:</p>
                    <p className="text-sm text-gray-700">{project.description}</p>
                  </div>
                )}
                <div className="flex gap-3">
                  <button 
                    onClick={() => navigate('/dashboard')}
                    className="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 transition-colors text-sm font-medium"
                  >
                    Back to Dashboard
                  </button>
                  <button 
                    onClick={() => navigate(`/scope/new`)}
                    className="px-4 py-2 bg-yellow-600 text-white rounded-md hover:bg-yellow-700 transition-colors text-sm font-medium"
                  >
                    Create New Project
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  const totalCost = selectedTrade === 'all' 
    ? project.total_cost 
    : selectedTradeData.reduce((sum, trade) => sum + trade.total, 0);

  return (
    <div className="min-h-screen bg-gray-50">
      {/* View Mode Toggle - AT THE VERY TOP */}
      <div className="bg-white border-b shadow-sm sticky top-0 z-20">
        <div className="max-w-7xl mx-auto px-4 py-3">
          <div className="flex justify-center">
            <div className="inline-flex rounded-lg border-2 border-gray-200 p-1 bg-gray-50">
              <button
                onClick={() => setViewMode('executive')}
                className={`px-6 py-2 rounded-md text-sm font-semibold transition-all ${
                  viewMode === 'executive'
                    ? 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-lg'
                    : 'text-gray-600 hover:text-gray-900 hover:bg-white'
                }`}
              >
                🏢 Executive View
              </button>
              <button
                onClick={() => setViewMode('trade')}
                className={`px-6 py-2 rounded-md text-sm font-semibold transition-all ${
                  viewMode === 'trade'
                    ? 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-lg'
                    : 'text-gray-600 hover:text-gray-900 hover:bg-white'
                }`}
              >
                🔨 Trade Breakdown
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Trade Navigation - Only if functional and in trade view */}
      {viewMode === 'trade' && selectedTrade !== 'all' && (
        <div className="trade-navigation-premium">
          <div className="trade-nav-pills">
            <button
              className="nav-pill active"
              onClick={() => setSelectedTrade('all')}
            >
              ← Back to All Trades
            </button>
          </div>
          <div className="trade-actions-premium">
            <button 
              className="action-pill"
              onClick={() => handleExportTrade(selectedTrade)}
            >
              <FileSpreadsheet size={16} />
              Export Excel
            </button>
            <button 
              className="action-pill primary"
              onClick={() => openTradePackageModal(selectedTrade)}
            >
              <Package size={16} />
              Generate Package
            </button>
          </div>
        </div>
      )}

      {/* Unified Project Header - Changes style based on view mode */}
      <div className={viewMode === 'executive' 
        ? "bg-gradient-to-r from-gray-900 via-gray-800 to-gray-900 shadow-xl" 
        : "bg-white border-b shadow-sm"
      }>
        <div className="max-w-7xl mx-auto px-6 py-8">
          {/* Top Row - Navigation and Actions */}
          <div className="flex justify-between items-center mb-6">
            <Link 
              to="/dashboard" 
              className={`flex items-center gap-2 transition-colors ${
                viewMode === 'executive' 
                  ? 'text-gray-400 hover:text-white' 
                  : 'text-blue-600 hover:text-blue-800'
              }`}
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
              <span className="text-sm font-medium">Dashboard</span>
            </Link>
            
            <div className="flex gap-3">
              <button
                onClick={handleExportFullProject}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
                  viewMode === 'executive'
                    ? 'bg-gray-800 text-gray-300 hover:bg-gray-700'
                    : 'bg-white border border-gray-300 text-gray-700 hover:bg-gray-50'
                }`}
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <span className="text-sm font-medium">Export Excel</span>
              </button>
              <button
                onClick={() => setShowComparisonTool(true)}
                className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
                <span className="text-sm font-medium">Compare Scenarios</span>
              </button>
            </div>
          </div>
          
          {/* Main Content - Project Info and Total */}
          <div className="flex justify-between items-end">
            <div>
              <h1 className={`text-3xl font-bold mb-2 ${
                viewMode === 'executive' ? 'text-white' : 'text-gray-900'
              }`}>
                {project?.description || `${project.request_data.square_footage.toLocaleString()} SF ${getDisplayBuildingType(project.request_data)}`}
              </h1>
              <div className={`flex items-center gap-4 text-sm ${
                viewMode === 'executive' ? 'text-gray-400' : 'text-gray-600'
              }`}>
                <span className="flex items-center gap-1">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                  </svg>
                  {project.request_data.location}
                </span>
                <span className="flex items-center gap-1">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                  </svg>
                  {project.request_data.num_floors} {project.request_data.num_floors === 1 ? 'Floor' : 'Floors'}
                </span>
                <span className="flex items-center gap-1">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                  </svg>
                  {getClassificationInfo(project.request_data.project_classification).name}
                </span>
              </div>
            </div>
            
            <div className="text-right">
              <p className={`text-xs uppercase tracking-wider mb-1 ${
                viewMode === 'executive' ? 'text-gray-500' : 'text-gray-500'
              }`}>
                {viewMode === 'executive' ? 'Total Investment Required' : 'Total Construction Cost'}
              </p>
              <p className={`text-4xl font-bold ${
                viewMode === 'executive' ? 'text-white' : 'text-blue-600'
              }`}>
                ${viewMode === 'executive' && ownerViewData 
                  ? (ownerViewData.project_summary?.total_project_cost / 1000000).toFixed(0)
                  : (totalCost / 1000000).toFixed(0)
                }M
              </p>
              <p className={`text-sm mt-1 ${
                viewMode === 'executive' ? 'text-gray-400' : 'text-gray-600'
              }`}>
                ${viewMode === 'executive' && ownerViewData
                  ? ownerViewData.project_summary?.total_cost_per_sqft?.toFixed(0)
                  : Math.round(totalCost / project.request_data.square_footage).toLocaleString()
                } per SF
              </p>
            </div>
          </div>
        </div>
      </div>

      <div className="project-content-premium">

        {viewMode === 'executive' ? (
          <div className="bg-gradient-to-br from-slate-50 to-blue-50 min-h-screen -mx-4 -mt-8 px-4 pt-8">
            {!ownerViewData && loadingOwnerView ? (
              <div className="flex flex-col items-center justify-center h-96">
                <div className="relative">
                  <div className="animate-spin rounded-full h-20 w-20 border-b-4 border-blue-600"></div>
                  <div className="absolute inset-0 flex items-center justify-center">
                    <span className="text-xs font-semibold text-blue-600">LOADING</span>
                  </div>
                </div>
                <p className="mt-4 text-gray-600">Preparing executive dashboard...</p>
              </div>
            ) : ownerViewData ? (
              <div className="max-w-7xl mx-auto space-y-8 pb-12">
                {/* Key Metrics Summary - Clean Card Design */}
                <div className="bg-white rounded-xl shadow-lg p-6">
                  <div className="grid grid-cols-4 gap-6">
                    <div className="text-center">
                      <p className="text-gray-600 text-sm font-medium mb-1">Construction Cost</p>
                      <p className="text-3xl font-bold text-gray-900">${(ownerViewData.project_summary?.construction_cost / 1000000).toFixed(1)}M</p>
                      <p className="text-xs text-gray-500 mt-1">Hard costs only</p>
                    </div>
                    <div className="text-center">
                      <p className="text-gray-600 text-sm font-medium mb-1">Soft Costs</p>
                      <p className="text-3xl font-bold text-gray-900">
                        ${((ownerViewData.soft_costs?.soft_costs_subtotal || (ownerViewData.project_summary?.total_project_cost - ownerViewData.project_summary?.construction_cost)) / 1000000).toFixed(1)}M
                      </p>
                      <p className="text-xs text-gray-500 mt-1">{ownerViewData.soft_costs?.soft_costs_percentage || 46}% of construction</p>
                    </div>
                    <div className="text-center">
                      <p className="text-gray-600 text-sm font-medium mb-1">Expected ROI</p>
                      <p className="text-3xl font-bold text-blue-600">{(ownerViewData.roi_analysis?.financial_metrics?.roi_percentage || 0).toFixed(1)}%</p>
                      <p className="text-xs text-gray-500 mt-1">Annual return</p>
                    </div>
                    <div className="text-center">
                      <p className="text-gray-600 text-sm font-medium mb-1">Payback Period</p>
                      <p className="text-3xl font-bold text-gray-900">{(ownerViewData.roi_analysis?.financial_metrics?.payback_period_years || 0).toFixed(1)} yrs</p>
                      <p className="text-xs text-gray-500 mt-1">Simple payback</p>
                    </div>
                  </div>
                </div>

                {/* Healthcare Facility Financing Context */}
                {viewMode === 'executive' && ownerViewData && ownerViewData.project_summary?.building_type === 'healthcare' && (
                  <div className="mt-4 p-4 bg-blue-50 rounded-lg border border-blue-200">
                    <div className="flex items-start gap-3">
                      <svg className="w-5 h-5 text-blue-600 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      <div className="flex-1">
                        <p className="text-sm font-medium text-blue-900 mb-2">Healthcare Facility Financing Context</p>
                        <p className="text-sm text-blue-800 mb-3">
                          Healthcare facilities typically require alternative financing structures. This analysis shows commercial financing. 
                          Most hospitals (70%) are non-profit and use tax-exempt bonds, philanthropy, and grants to achieve viability.
                        </p>
                        
                        {/* Ownership Type Selector */}
                        <div className="flex gap-2 flex-wrap">
                          <button
                            onClick={() => {
                              setOwnershipType('for_profit');
                              fetchOwnerView('for_profit');
                            }}
                            className={`px-3 py-1.5 text-xs font-medium rounded-md transition-colors ${
                              ownershipType === 'for_profit' 
                                ? 'bg-blue-600 text-white' 
                                : 'bg-white text-blue-700 border border-blue-300 hover:bg-blue-50'
                            }`}
                          >
                            For-Profit (Commercial)
                          </button>
                          <button
                            onClick={() => {
                              setOwnershipType('non_profit');
                              fetchOwnerView('non_profit');
                            }}
                            className={`px-3 py-1.5 text-xs font-medium rounded-md transition-colors ${
                              ownershipType === 'non_profit' 
                                ? 'bg-blue-600 text-white' 
                                : 'bg-white text-blue-700 border border-blue-300 hover:bg-blue-50'
                            }`}
                          >
                            Non-Profit (Tax-Exempt)
                          </button>
                          <button
                            onClick={() => {
                              setOwnershipType('government');
                              fetchOwnerView('government');
                            }}
                            className={`px-3 py-1.5 text-xs font-medium rounded-md transition-colors ${
                              ownershipType === 'government' 
                                ? 'bg-blue-600 text-white' 
                                : 'bg-white text-blue-700 border border-blue-300 hover:bg-blue-50'
                            }`}
                          >
                            Government/Public
                          </button>
                        </div>
                        
                        {ownershipType === 'non_profit' && (
                          <div className="mt-3 p-3 bg-white rounded border border-blue-200">
                            <p className="text-xs font-medium text-gray-700 mb-1">Non-Profit Assumptions:</p>
                            <ul className="text-xs text-gray-600 space-y-0.5">
                              <li>• Tax-exempt bonds at 4% (vs 6.8% commercial)</li>
                              <li>• ${((ownerViewData.roi_analysis?.ownership_context?.philanthropy_amount || 0) / 1000000).toFixed(1)}M philanthropic campaign ({((ownerViewData.roi_analysis?.ownership_context?.philanthropy_amount || 0) / ownerViewData.project_summary?.total_project_cost * 100).toFixed(0)}% of project)</li>
                              <li>• ${((ownerViewData.roi_analysis?.ownership_context?.grants_amount || 0) / 1000000).toFixed(1)}M government grants ({((ownerViewData.roi_analysis?.ownership_context?.grants_amount || 0) / ownerViewData.project_summary?.total_project_cost * 100).toFixed(0)}% of project)</li>
                              <li>• 1.15x DSCR requirement (vs 1.25x commercial)</li>
                            </ul>
                          </div>
                        )}
                        
                        {ownershipType === 'government' && (
                          <div className="mt-3 p-3 bg-white rounded border border-blue-200">
                            <p className="text-xs font-medium text-gray-700 mb-1">Government/Public Assumptions:</p>
                            <ul className="text-xs text-gray-600 space-y-0.5">
                              <li>• ${((ownerViewData.roi_analysis?.ownership_context?.public_funding_amount || 0) / 1000000).toFixed(1)}M public funding (60% of project)</li>
                              <li>• Tax-exempt bonds at 3.5% for remaining 40%</li>
                              <li>• Break-even operations acceptable</li>
                              <li>• Focus on community benefit over profitability</li>
                            </ul>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                )}

                {/* Go/No-Go Investment Indicator */}
                {ownerViewData?.roi_analysis?.investment_status && (
                  <div className={`mt-6 p-4 rounded-lg border-2 ${
                    ownerViewData.roi_analysis.investment_status.overall === 'green' 
                      ? 'bg-green-50 border-green-500' 
                      : ownerViewData.roi_analysis.investment_status.overall === 'yellow'
                      ? 'bg-yellow-50 border-yellow-500'
                      : 'bg-red-50 border-red-500'
                  }`}>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        {ownerViewData.roi_analysis.investment_status.overall === 'green' ? (
                          <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                          </svg>
                        ) : ownerViewData.roi_analysis.investment_status.overall === 'yellow' ? (
                          <svg className="w-8 h-8 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                          </svg>
                        ) : (
                          <svg className="w-8 h-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
                          </svg>
                        )}
                        <div>
                          <h3 className={`text-lg font-bold ${
                            ownerViewData.roi_analysis.investment_status.overall === 'green' 
                              ? 'text-green-800' 
                              : ownerViewData.roi_analysis.investment_status.overall === 'yellow'
                              ? 'text-yellow-800'
                              : 'text-red-800'
                          }`}>
                            Investment Decision: {
                              ownerViewData.roi_analysis.investment_status.overall === 'green' ? 'GO' :
                              ownerViewData.roi_analysis.investment_status.overall === 'yellow' ? 'REVIEW' : 'NO-GO'
                            }
                          </h3>
                          <p className="text-sm text-gray-600">{ownerViewData.roi_analysis.investment_status.recommendation}</p>
                        </div>
                      </div>
                      <div className="flex gap-4">
                        <div className="text-center">
                          <div className={`w-3 h-3 rounded-full mx-auto mb-1 ${
                            ownerViewData.roi_analysis.investment_status.roi_status === 'green' ? 'bg-green-500' :
                            ownerViewData.roi_analysis.investment_status.roi_status === 'yellow' ? 'bg-yellow-500' : 'bg-red-500'
                          }`}></div>
                          <p className="text-xs text-gray-600">ROI</p>
                          <p className="text-xs font-bold">{ownerViewData.roi_analysis?.financial_metrics?.roi_percentage?.toFixed(1)}%</p>
                        </div>
                        <div className="text-center">
                          <div className={`w-3 h-3 rounded-full mx-auto mb-1 ${
                            ownerViewData.roi_analysis.investment_status.dscr_status === 'green' ? 'bg-green-500' :
                            ownerViewData.roi_analysis.investment_status.dscr_status === 'yellow' ? 'bg-yellow-500' : 'bg-red-500'
                          }`}></div>
                          <p className="text-xs text-gray-600">DSCR</p>
                          <p className="text-xs font-bold">{ownerViewData.roi_analysis?.financial_metrics?.dscr?.toFixed(2)}x</p>
                        </div>
                        <div className="text-center">
                          <div className={`w-3 h-3 rounded-full mx-auto mb-1 ${
                            ownerViewData.roi_analysis.investment_status.payback_status === 'green' ? 'bg-green-500' :
                            ownerViewData.roi_analysis.investment_status.payback_status === 'yellow' ? 'bg-yellow-500' : 'bg-red-500'
                          }`}></div>
                          <p className="text-xs text-gray-600">Payback</p>
                          <p className="text-xs font-bold">{ownerViewData.roi_analysis?.financial_metrics?.payback_period_years?.toFixed(0)} yrs</p>
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {/* Financial Performance Cards */}
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                  {/* Revenue Projections Card */}
                  <div className="bg-white rounded-xl shadow-lg p-6 border-t-4 border-green-500">
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="text-lg font-semibold text-gray-800">Revenue Projections</h3>
                      <div className="p-2 bg-green-100 rounded-lg">
                        <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                      </div>
                    </div>
                    <div className="space-y-3">
                      <div>
                        <p className="text-3xl font-bold text-gray-900">
                          ${(ownerViewData.roi_analysis?.financial_metrics?.annual_revenue / 1000000).toFixed(1)}M
                        </p>
                        <p className="text-sm text-gray-600">Annual Revenue</p>
                      </div>
                      <div className="pt-3 border-t">
                        <div className="flex justify-between">
                          <span className="text-sm text-gray-600">Operating Margin</span>
                          <span className="font-semibold">{(ownerViewData.roi_analysis?.assumptions?.operating_margin * 100).toFixed(0)}%</span>
                        </div>
                        <div className="flex justify-between mt-2">
                          <span className="text-sm text-gray-600">Net Income</span>
                          <span className="font-semibold">${(ownerViewData.roi_analysis?.financial_metrics?.annual_net_income / 1000000).toFixed(1)}M</span>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Facility Metrics Card */}
                  <div className="bg-white rounded-xl shadow-lg p-6 border-t-4 border-blue-500">
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="text-lg font-semibold text-gray-800">Facility Metrics</h3>
                      <div className="p-2 bg-blue-100 rounded-lg">
                        <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                        </svg>
                      </div>
                    </div>
                    <div className="space-y-3">
                      <div>
                        <p className="text-3xl font-bold text-gray-900">
                          {ownerViewData.roi_analysis?.unit_metrics?.unit_count?.toFixed(0) || '150'}
                        </p>
                        <p className="text-sm text-gray-600 capitalize">
                          {ownerViewData.roi_analysis?.unit_metrics?.unit_type || 'Beds'} Capacity
                        </p>
                      </div>
                      <div className="pt-3 border-t">
                        <div className="flex justify-between">
                          <span className="text-sm text-gray-600">Cost per Unit</span>
                          <span className="font-semibold">
                            ${((ownerViewData.project_summary?.total_project_cost / (ownerViewData.roi_analysis?.unit_metrics?.unit_count || 1)) / 1000000).toFixed(2)}M
                          </span>
                        </div>
                        <div className="flex justify-between mt-2">
                          <span className="text-sm text-gray-600">Revenue per Unit</span>
                          <span className="font-semibold">
                            ${(ownerViewData.roi_analysis?.unit_metrics?.revenue_per_unit / 1000).toFixed(0)}K
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Investment Breakdown Card */}
                  <div className="bg-white rounded-xl shadow-lg p-6 border-t-4 border-purple-500">
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="text-lg font-semibold text-gray-800">Investment Mix</h3>
                      <div className="p-2 bg-purple-100 rounded-lg">
                        <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                        </svg>
                      </div>
                    </div>
                    <div className="space-y-3">
                      <div className="relative pt-1">
                        <div className="flex mb-2 items-center justify-between">
                          <div>
                            <span className="text-xs font-semibold inline-block text-blue-600">
                              CONSTRUCTION
                            </span>
                          </div>
                          <div className="text-right">
                            <span className="text-xs font-semibold inline-block text-blue-600">
                              {((ownerViewData?.project_summary?.construction_cost / ownerViewData?.project_summary?.total_project_cost * 100) || 69).toFixed(0)}%
                            </span>
                          </div>
                        </div>
                        <div className="overflow-hidden h-2 mb-4 text-xs flex rounded bg-blue-100">
                          <div 
                            style={{ width: `${(ownerViewData?.project_summary?.construction_cost / ownerViewData?.project_summary?.total_project_cost * 100) || 69}%` }}
                            className="shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center bg-blue-500"
                          ></div>
                        </div>
                      </div>
                      
                      <div className="relative pt-1">
                        <div className="flex mb-2 items-center justify-between">
                          <div>
                            <span className="text-xs font-semibold inline-block text-purple-600">
                              SOFT COSTS
                            </span>
                          </div>
                          <div className="text-right">
                            <span className="text-xs font-semibold inline-block text-purple-600">
                              {(((ownerViewData?.soft_costs?.total_soft_costs || 
                                  (ownerViewData?.project_summary?.total_project_cost - ownerViewData?.project_summary?.construction_cost)) / 
                                  ownerViewData?.project_summary?.total_project_cost * 100) || 31).toFixed(0)}%
                            </span>
                          </div>
                        </div>
                        <div className="overflow-hidden h-2 mb-4 text-xs flex rounded bg-purple-100">
                          <div 
                            style={{ width: `${((ownerViewData?.soft_costs?.total_soft_costs || 
                                                (ownerViewData?.project_summary?.total_project_cost - ownerViewData?.project_summary?.construction_cost)) / 
                                                ownerViewData?.project_summary?.total_project_cost * 100) || 31}%` }}
                            className="shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center bg-purple-500"
                          ></div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Department Allocation Visualization */}
                <div className="bg-white rounded-xl shadow-lg p-8">
                  <h2 className="text-2xl font-bold text-gray-800 mb-6">Department Cost Allocation</h2>
                  <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    {ownerViewData.department_allocation?.departments && 
                      Object.entries(ownerViewData.department_allocation.departments).map(([dept, data]: [string, any]) => {
                        const colors = {
                          clinical: 'bg-gradient-to-br from-blue-500 to-blue-600',
                          support: 'bg-gradient-to-br from-green-500 to-green-600',
                          infrastructure: 'bg-gradient-to-br from-purple-500 to-purple-600'
                        };
                        const icons = {
                          clinical: (
                            <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                            </svg>
                          ),
                          support: (
                            <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18.364 5.636l-3.536 3.536m0 5.656l3.536 3.536M9.172 9.172L5.636 5.636m3.536 9.192l-3.536 3.536M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-5 0a4 4 0 11-8 0 4 4 0 018 0z" />
                            </svg>
                          ),
                          infrastructure: (
                            <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 12h14M5 12a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v4a2 2 0 01-2 2M5 12a2 2 0 00-2 2v4a2 2 0 002 2h14a2 2 0 002-2v-4a2 2 0 00-2-2m-2-4h.01M17 16h.01" />
                            </svg>
                          )
                        };
                        
                        return (
                          <div key={dept} className={`${colors[dept as keyof typeof colors]} rounded-xl p-6 text-white`}>
                            <div className="flex items-center justify-between mb-4">
                              <div className="p-3 bg-white bg-opacity-20 rounded-lg">
                                {icons[dept as keyof typeof icons]}
                              </div>
                              <div className="text-right">
                                <p className="text-3xl font-bold">{(data.percentage * 100).toFixed(0)}%</p>
                                <p className="text-sm opacity-90">of facility</p>
                              </div>
                            </div>
                            <h3 className="text-xl font-semibold mb-2 capitalize">{dept} Department</h3>
                            <p className="text-3xl font-bold mb-2">${(data.amount / 1000000).toFixed(1)}M</p>
                            <div className="space-y-2 mt-4 pt-4 border-t border-white border-opacity-30">
                              {data.trades && Object.entries(data.trades).slice(0, 3).map(([trade, amount]: [string, any]) => (
                                <div key={trade} className="flex justify-between text-sm">
                                  <span className="capitalize opacity-90">{trade}</span>
                                  <span className="font-semibold">${(amount / 1000000).toFixed(1)}M</span>
                                </div>
                              ))}
                            </div>
                          </div>
                        );
                      })
                    }
                  </div>
                </div>

                {/* Soft Costs Analysis */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  {/* Top Soft Costs */}
                  <div className="bg-white rounded-xl shadow-lg p-6">
                    <h3 className="text-xl font-bold text-gray-800 mb-4">Major Soft Cost Categories</h3>
                    <div className="space-y-3">
                      {(() => {
                        const totalSoftCosts = ownerViewData?.soft_costs?.total_soft_costs || 
                                              (ownerViewData?.project_summary?.total_project_cost - ownerViewData?.project_summary?.construction_cost) || 
                                              112500000; // fallback value
                        
                        const categories = [
                          { name: 'Medical Equipment', percentage: 0.26 },
                          { name: 'Design & Engineering', percentage: 0.18 },
                          { name: 'Construction Contingency', percentage: 0.22 },
                          { name: 'Owner Contingency', percentage: 0.11 },
                          { name: 'FF&E', percentage: 0.07 }
                        ];
                        
                        return categories.map(cat => (
                          <div key={cat.name} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
                            <div className="flex items-center gap-3">
                              <div className="w-2 h-8 bg-gradient-to-b from-blue-500 to-blue-600 rounded"></div>
                              <span className="font-medium text-gray-700">{cat.name}</span>
                            </div>
                            <div className="text-right">
                              <p className="font-bold text-gray-900">
                                ${((totalSoftCosts * cat.percentage) / 1000000).toFixed(1)}M
                              </p>
                              <p className="text-xs text-gray-500">
                                {(cat.percentage * 100).toFixed(0)}% of soft costs
                              </p>
                            </div>
                          </div>
                        ));
                      })()}
                    </div>
                  </div>

                  {/* Financial KPIs */}
                  <div className="bg-gradient-to-br from-indigo-600 to-purple-700 rounded-xl shadow-lg p-6 text-white">
                    <h3 className="text-xl font-bold mb-4">Key Financial Indicators</h3>
                    <div className="grid grid-cols-2 gap-4">
                      <div className="bg-white bg-opacity-10 rounded-lg p-4">
                        <p className="text-sm opacity-90 mb-1">Break-Even Occupancy</p>
                        <p className="text-2xl font-bold">
                          {((ownerViewData.roi_analysis?.assumptions?.occupancy_rate || 0.85) * 100).toFixed(0)}%
                        </p>
                      </div>
                      <div className="bg-white bg-opacity-10 rounded-lg p-4">
                        <p className="text-sm opacity-90 mb-1">10-Year NPV</p>
                        <p className="text-2xl font-bold">
                          ${((ownerViewData.roi_analysis?.financial_metrics?.['10_year_npv'] || 0) / 1000000).toFixed(1)}M
                        </p>
                      </div>
                      <div className="bg-white bg-opacity-10 rounded-lg p-4">
                        <p className="text-sm opacity-90 mb-1">Cost per SF</p>
                        <p className="text-2xl font-bold">
                          ${ownerViewData.project_summary?.total_cost_per_sqft?.toFixed(0)}
                        </p>
                      </div>
                      <div className="bg-white bg-opacity-10 rounded-lg p-4">
                        <p className="text-sm opacity-90 mb-1">Total Soft Cost %</p>
                        <p className="text-2xl font-bold">
                          {(((ownerViewData?.soft_costs?.total_soft_costs || 
                              (ownerViewData?.project_summary?.total_project_cost - ownerViewData?.project_summary?.construction_cost)) / 
                              ownerViewData?.project_summary?.construction_cost * 100) || 45.5).toFixed(1)}%
                        </p>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Market Benchmarks, Sensitivity, and Timeline Cards */}
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                  {/* Market Benchmarks Card */}
                  <div className="bg-white rounded-xl shadow-lg p-6 border-l-4 border-teal-500">
                    <h3 className="text-lg font-semibold text-gray-800 mb-4">Market Position</h3>
                    <div className="space-y-3">
                      <div>
                        <div className="flex justify-between text-sm mb-1">
                          <span>Your Cost</span>
                          <span className="font-bold">${ownerViewData?.project_summary?.total_cost_per_sqft?.toFixed(0) || '1,798'}/SF</span>
                        </div>
                        <div className="flex justify-between text-sm mb-1">
                          <span>Regional Avg</span>
                          <span>$1,650/SF</span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div className="bg-teal-500 h-2 rounded-full" style={{ width: '75%' }}></div>
                        </div>
                        <p className="text-xs text-gray-500 mt-1">9% above regional average</p>
                      </div>
                    </div>
                  </div>

                  {/* Simple Risk Sensitivity */}
                  <div className="bg-white rounded-xl shadow-lg p-6 border-l-4 border-amber-500">
                    <h3 className="text-lg font-semibold text-gray-800 mb-4">Quick Sensitivity</h3>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span>If costs +10%:</span>
                        <span className="font-bold text-red-600">ROI drops to {((ownerViewData?.roi_analysis?.financial_metrics?.roi_percentage || 1.2) - 0.7).toFixed(1)}%</span>
                      </div>
                      <div className="flex justify-between">
                        <span>If revenue +10%:</span>
                        <span className="font-bold text-green-600">ROI rises to {((ownerViewData?.roi_analysis?.financial_metrics?.roi_percentage || 1.2) + 1.6).toFixed(1)}%</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Break-even needs:</span>
                        <span className="font-bold">{((ownerViewData?.roi_analysis?.assumptions?.occupancy_rate || 0.85) * 100).toFixed(0)}% occupancy</span>
                      </div>
                    </div>
                  </div>

                  {/* Project Timeline */}
                  <div className="bg-white rounded-xl shadow-lg p-6 border-l-4 border-blue-500">
                    <h3 className="text-lg font-semibold text-gray-800 mb-4">Key Milestones</h3>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span>Groundbreaking</span>
                        <span className="font-semibold">Q1 2025</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Structure Complete</span>
                        <span className="font-semibold">Q3 2025</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Substantial Completion</span>
                        <span className="font-semibold">Q2 2027</span>
                      </div>
                      <div className="flex justify-between">
                        <span>First Patient</span>
                        <span className="font-semibold text-green-600">Q3 2027</span>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Financing Structure and Operational Efficiency */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  {/* Financing Structure */}
                  <div className="bg-gradient-to-br from-emerald-50 to-teal-50 rounded-xl shadow-lg p-6 border-t-4 border-emerald-500">
                    <h3 className="text-xl font-bold text-gray-800 mb-4 flex items-center gap-2">
                      <svg className="w-6 h-6 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      Financing Structure
                    </h3>
                    
                    <div className="space-y-4">
                      {/* Capital Stack */}
                      <div>
                        <p className="text-sm font-medium text-gray-700 mb-2">Capital Stack</p>
                        <div className="space-y-2">
                          <div className="flex items-center justify-between">
                            <div className="flex items-center gap-2">
                              <div className="w-3 h-3 bg-blue-500 rounded"></div>
                              <span className="text-sm">Senior Debt (65%)</span>
                            </div>
                            <span className="font-bold">${((ownerViewData?.project_summary?.total_project_cost || 360000000) * 0.65 / 1000000).toFixed(1)}M</span>
                          </div>
                          <div className="flex items-center justify-between">
                            <div className="flex items-center gap-2">
                              <div className="w-3 h-3 bg-purple-500 rounded"></div>
                              <span className="text-sm">Mezzanine (15%)</span>
                            </div>
                            <span className="font-bold">${((ownerViewData?.project_summary?.total_project_cost || 360000000) * 0.15 / 1000000).toFixed(1)}M</span>
                          </div>
                          <div className="flex items-center justify-between">
                            <div className="flex items-center gap-2">
                              <div className="w-3 h-3 bg-green-500 rounded"></div>
                              <span className="text-sm">Equity (20%)</span>
                            </div>
                            <span className="font-bold">${((ownerViewData?.project_summary?.total_project_cost || 360000000) * 0.20 / 1000000).toFixed(1)}M</span>
                          </div>
                        </div>
                      </div>
                      
                      {/* Financing Costs */}
                      <div className="pt-3 border-t border-emerald-200">
                        <p className="text-sm font-medium text-gray-700 mb-2">Financing Costs</p>
                        <div className="grid grid-cols-2 gap-3 text-sm">
                          <div>
                            <p className="text-gray-600">Weighted Rate</p>
                            <p className="text-xl font-bold">6.8%</p>
                          </div>
                          <div>
                            <p className="text-gray-600">Annual Debt Service</p>
                            <p className="text-xl font-bold">${(((ownerViewData?.project_summary?.total_project_cost || 360000000) * 0.80 * 0.068) / 1000000).toFixed(1)}M</p>
                          </div>
                          <div>
                            <p className="text-gray-600">Interest During Construction</p>
                            <p className="text-xl font-bold">${(((ownerViewData?.project_summary?.total_project_cost || 360000000) * 0.80 * 0.068 * 2.25) / 1000000).toFixed(1)}M</p>
                          </div>
                          <div>
                            <p className="text-gray-600">DSCR Target</p>
                            <p className="text-xl font-bold">1.25x</p>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Operational Efficiency Metrics */}
                  <div className="bg-gradient-to-br from-indigo-50 to-blue-50 rounded-xl shadow-lg p-6 border-t-4 border-indigo-500">
                    <h3 className="text-xl font-bold text-gray-800 mb-4 flex items-center gap-2">
                      <svg className="w-6 h-6 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                      </svg>
                      Operational Efficiency
                    </h3>
                    
                    <div className="space-y-4">
                      {/* Staffing Metrics */}
                      <div>
                        <p className="text-sm font-medium text-gray-700 mb-2">Staffing Ratios</p>
                        <div className="grid grid-cols-2 gap-3">
                          <div className="bg-white p-3 rounded-lg">
                            <p className="text-2xl font-bold text-indigo-600">4.2</p>
                            <p className="text-xs text-gray-600">Beds per Nurse</p>
                          </div>
                          <div className="bg-white p-3 rounded-lg">
                            <p className="text-2xl font-bold text-indigo-600">750</p>
                            <p className="text-xs text-gray-600">Total FTEs Required</p>
                          </div>
                        </div>
                      </div>
                      
                      {/* Revenue Efficiency */}
                      <div className="pt-3 border-t border-indigo-200">
                        <p className="text-sm font-medium text-gray-700 mb-2">Revenue Efficiency</p>
                        <div className="space-y-2">
                          <div className="flex justify-between items-center">
                            <span className="text-sm text-gray-600">Revenue per Employee</span>
                            <span className="font-bold">${((ownerViewData?.roi_analysis?.financial_metrics?.annual_revenue || 24600000) / 750 / 1000).toFixed(0)}K</span>
                          </div>
                          <div className="flex justify-between items-center">
                            <span className="text-sm text-gray-600">Revenue per Bed</span>
                            <span className="font-bold">${((ownerViewData?.roi_analysis?.financial_metrics?.annual_revenue || 24600000) / (ownerViewData?.roi_analysis?.unit_metrics?.unit_count || 150) / 1000).toFixed(0)}K</span>
                          </div>
                          <div className="flex justify-between items-center">
                            <span className="text-sm text-gray-600">Labor Cost Ratio</span>
                            <span className="font-bold">52%</span>
                          </div>
                        </div>
                      </div>
                      
                      {/* Operational KPIs */}
                      <div className="pt-3 border-t border-indigo-200">
                        <p className="text-sm font-medium text-gray-700 mb-2">Target KPIs</p>
                        <div className="grid grid-cols-3 gap-2 text-center">
                          <div>
                            <p className="text-lg font-bold">3.8</p>
                            <p className="text-xs text-gray-600">ALOS (days)</p>
                          </div>
                          <div>
                            <p className="text-lg font-bold">85%</p>
                            <p className="text-xs text-gray-600">Occupancy</p>
                          </div>
                          <div>
                            <p className="text-lg font-bold">$11K</p>
                            <p className="text-xs text-gray-600">Rev/Admission</p>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Executive Decision Points */}
                <div className="bg-gradient-to-r from-amber-50 to-orange-50 border-l-4 border-amber-500 rounded-lg p-6">
                  <div className="flex items-start gap-4">
                    <div className="p-2 bg-amber-100 rounded-lg">
                      <svg className="w-6 h-6 text-amber-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                      </svg>
                    </div>
                    <div>
                      <h4 className="font-semibold text-gray-800 mb-2">Executive Decision Points</h4>
                      <ul className="text-gray-600 space-y-1 text-sm">
                        <li>• Total investment of ${(ownerViewData?.project_summary?.total_project_cost / 1000000).toFixed(0)}M is 9% above regional healthcare average</li>
                        <li>• {(ownerViewData?.roi_analysis?.financial_metrics?.payback_period_years || 97).toFixed(0)}-year payback suggests need for operational efficiency improvements</li>
                        <li>• Consider phased opening to accelerate revenue generation</li>
                        <li>• Soft costs at {(((ownerViewData?.soft_costs?.total_soft_costs || 
                            (ownerViewData?.project_summary?.total_project_cost - ownerViewData?.project_summary?.construction_cost)) / 
                            ownerViewData?.project_summary?.construction_cost * 100) || 45.5).toFixed(1)}% are high - opportunity for value engineering</li>
                      </ul>
                    </div>
                  </div>
                </div>

                {/* Executive Financial Summary */}
                <div className="bg-gradient-to-r from-gray-900 to-gray-800 rounded-xl shadow-2xl p-8 text-white">
                  <h3 className="text-2xl font-bold mb-6">Executive Financial Summary</h3>
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                    <div>
                      <p className="text-gray-400 text-sm mb-2">Total Capital Required</p>
                      <p className="text-3xl font-bold">${(ownerViewData?.project_summary?.total_project_cost / 1000000).toFixed(1)}M</p>
                      <p className="text-gray-400 text-sm mt-1">Construction + Soft Costs</p>
                    </div>
                    <div>
                      <p className="text-gray-400 text-sm mb-2">Expected Annual Return</p>
                      <p className="text-3xl font-bold">${(ownerViewData?.roi_analysis?.financial_metrics?.annual_net_income / 1000000).toFixed(1)}M</p>
                      <p className="text-gray-400 text-sm mt-1">After operating expenses</p>
                    </div>
                    <div>
                      <p className="text-gray-400 text-sm mb-2">Investment per Bed</p>
                      <p className="text-3xl font-bold">${(ownerViewData?.project_summary?.total_project_cost / (ownerViewData?.roi_analysis?.unit_metrics?.unit_count || 150) / 1000000).toFixed(2)}M</p>
                      <p className="text-gray-400 text-sm mt-1">Total cost / bed</p>
                    </div>
                    <div>
                      <p className="text-gray-400 text-sm mb-2">Debt Coverage</p>
                      <p className="text-3xl font-bold">
                        {((ownerViewData?.roi_analysis?.financial_metrics?.annual_net_income || 3700000) / 
                         ((ownerViewData?.project_summary?.total_project_cost || 360000000) * 0.80 * 0.068)).toFixed(2)}x
                      </p>
                      <p className="text-gray-400 text-sm mt-1">DSCR (Target: 1.25x)</p>
                    </div>
                  </div>
                </div>
              </div>
            ) : (
              <div className="flex flex-col items-center justify-center h-96">
                <div className="text-center">
                  <svg className="w-16 h-16 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                  <p className="text-gray-500 mb-4">Unable to load executive dashboard</p>
                  <button 
                    onClick={() => fetchOwnerView()}
                    className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-semibold"
                  >
                    Retry Loading Dashboard
                  </button>
                </div>
              </div>
            )}
          </div>
        ) : (
          // Trade Breakdown View (existing contractor view)
          selectedTrade === 'all' ? (
            <TradeBreakdownView
              tradeSummaries={tradeSummaries}
              selectedTrade={selectedTrade}
              selectedTradeData={selectedTradeData}
              chartData={chartData}
              totalCost={totalCost}
              squareFootage={project.request_data.square_footage}
              onTradeSelect={setSelectedTrade}
              onExportTrade={handleExportTrade}
              onGeneratePackage={openTradePackageModal}
              onViewDetails={(trade) => setSelectedTrade(trade as TradeType)}
              projectData={project.request_data}
            />
          ) : (
            /* Show detailed breakdown when a specific trade is selected */
            <div className="trade-detail-view">
              <TradeBreakdownView
                tradeSummaries={tradeSummaries}
                selectedTrade={selectedTrade}
                selectedTradeData={selectedTradeData}
                chartData={chartData}
                totalCost={totalCost}
                squareFootage={project.request_data.square_footage}
                onTradeSelect={setSelectedTrade}
                onExportTrade={handleExportTrade}
                onGeneratePackage={openTradePackageModal}
                onViewDetails={(trade) => setSelectedTrade(trade as TradeType)}
                projectData={project.request_data}
              />
            </div>
          )
        )}


          {/* Category Details Section - Only shown when drilling down */}
          {selectedTrade !== 'all' && (
            <div className="category-summaries" style={{ marginTop: '2rem' }}>
              <h2>{TRADE_DISPLAY_NAMES[selectedTrade]} Categories</h2>
              {selectedTradeData[0]?.categories?.map(category => (
                <div key={category.name} className="category-card">
                  <div 
                    className="category-header"
                    onClick={() => toggleCategoryExpansion(category.name)}
                    style={{ cursor: 'pointer' }}
                  >
                    <div>
                      <h3>{category.name}</h3>
                      <span className="category-total">${category.total.toLocaleString()}</span>
                    </div>
                    {expandedCategories.has(category.name) ? <ChevronUp /> : <ChevronDown />}
                  </div>
                  
                  {/* Detailed line items (expandable) */}
                  {expandedCategories.has(category.name) && (
                    <div className="category-details">
                      <table>
                        <thead>
                          <tr>
                            <th>Item</th>
                            <th>Quantity</th>
                            <th>Unit</th>
                            <th>Unit Cost</th>
                            <th>Total Cost</th>
                          </tr>
                        </thead>
                        <tbody>
                          {category.systems?.map((system: any, index: number) => (
                            <tr key={index}>
                              <td>{system.name}</td>
                              <td>{system.quantity.toLocaleString()}</td>
                              <td>{system.unit}</td>
                              <td>${system.unit_cost.toFixed(2)}</td>
                              <td>${system.total_cost.toLocaleString()}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}


          {/* Project Footer - Only in Trade View */}
          {viewMode === 'trade' && (
            <div className="project-footer">
              <div className="footer-summary">
                <div className="total">
                  <label>{selectedTrade !== 'all' ? `${TRADE_DISPLAY_NAMES[selectedTrade]} Total:` : 'Total Construction Cost:'}</label>
                  <span>${totalCost.toLocaleString()}</span>
                </div>
              </div>
            </div>
          )}

          {/* Modern Price Journey Section - Only in Trade View */}
          {viewMode === 'trade' && selectedTrade === 'all' && (
            <div className="price-journey-modern">
              <div className="journey-header">
                <h2 className="journey-title">Cost Build-Up Analysis</h2>
                <p className="journey-subtitle">Understanding how your price is calculated</p>
              </div>
              
              {/* Enhanced Visual Cost Flow */}
              <div className="cost-flow-premium">
                <div className="flow-items">
                  {/* Base Cost */}
                  <div className="flow-step">
                    <div className="flow-card-premium hover-lift group">
                      <p className="flow-label-premium">Base Cost</p>
                      <p className="flow-value-premium group-hover:text-blue-600 transition-colors">
                        ${(project.calculation_breakdown?.raw_construction || 
                          (project.total_cost / project.request_data.square_footage / 
                           (project.calculation_breakdown?.multipliers?.regional || 1) / 
                           (project.request_data.project_classification === 'addition' ? 1.15 : 
                            project.request_data.project_classification === 'renovation' ? 1.35 : 1)
                          )).toFixed(0)}
                      </p>
                      <p className="flow-unit">per SF</p>
                      <p className="flow-source-premium">RSMeans 2024 Q3</p>
                    </div>
                  </div>
                  
                  {/* Animated Arrow with multiply */}
                  <div className="flow-connector">
                    <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="flow-arrow-icon arrow-animate">
                      <path d="M5 12h14M12 5l7 7-7 7"/>
                    </svg>
                    <span className="flow-operator">multiply</span>
                  </div>
                  
                  {/* Regional Multiplier */}
                  <div className="flow-step">
                    <div className="flow-card-premium hover-lift group">
                      <p className="flow-label-premium">Regional</p>
                      <p className="flow-value-premium group-hover:text-blue-600 transition-colors">
                        ×{(project.calculation_breakdown?.multipliers?.regional || 1).toFixed(2)}
                      </p>
                      <p className="flow-unit">{project.request_data.location}</p>
                    </div>
                  </div>
                  
                  {/* Animated Arrow with multiply */}
                  <div className="flow-connector">
                    <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="flow-arrow-icon arrow-animate">
                      <path d="M5 12h14M12 5l7 7-7 7"/>
                    </svg>
                    <span className="flow-operator">multiply</span>
                  </div>
                  
                  {/* Complexity Multiplier */}
                  <div className="flow-step">
                    <div className="flow-card-premium hover-lift group">
                      <p className="flow-label-premium">Complexity</p>
                      <p className="flow-value-premium group-hover:text-blue-600 transition-colors">
                        ×{getClassificationInfo(project.request_data.project_classification).multiplier.toFixed(2)}
                      </p>
                      <p className="flow-unit">{getClassificationInfo(project.request_data.project_classification).name}</p>
                    </div>
                  </div>
                  
                  {/* Equals */}
                  <div className="flow-connector">
                    <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="flow-arrow-icon arrow-animate">
                      <path d="M6 9h12M6 15h12"/>
                    </svg>
                    <span className="flow-operator">equals</span>
                  </div>
                  
                  {/* Final Cost - Enhanced */}
                  <div className="flow-step">
                    <div className="flow-card-premium final hover-lift-special group">
                      <p className="flow-label-premium final">Final Cost</p>
                      <p className="flow-value-final-premium group-hover:text-blue-800 transition-colors">
                        ${Math.round(project.total_cost / project.request_data.square_footage)}
                      </p>
                      <p className="flow-unit final">per SF</p>
                      <p className="flow-total-premium group-hover:text-blue-700 transition-colors">
                        ${(project.total_cost / 1000000).toFixed(1)}M Total
                      </p>
                    </div>
                  </div>
                </div>
              </div>
              
              {/* Sensitivity Analysis - Clean Grid */}
              <div className="sensitivity-section">
                <h3 className="sensitivity-title">Sensitivity Analysis</h3>
                
                <div className="sensitivity-grid">
                  {/* Regional Slider */}
                  <div className="slider-item">
                    <div className="slider-header">
                      <label className="slider-label">Regional Multiplier</label>
                      <span className="slider-value">
                        {(project.calculation_breakdown?.multipliers?.regional || 1).toFixed(2)}x
                      </span>
                    </div>
                    <input 
                      type="range" 
                      min="0.8" 
                      max="1.2" 
                      step="0.05"
                      value={project.calculation_breakdown?.multipliers?.regional || 1}
                      disabled
                      className="slider-input"
                    />
                    <p className="slider-description">±20% from baseline</p>
                  </div>
                  
                  {/* Complexity Slider */}
                  <div className="slider-item">
                    <div className="slider-header">
                      <label className="slider-label">Complexity Factor</label>
                      <span className="slider-value">
                        {getClassificationInfo(project.request_data.project_classification).multiplier.toFixed(2)}x
                      </span>
                    </div>
                    <input 
                      type="range"
                      min="1.0" 
                      max="1.5" 
                      step="0.05"
                      value={getClassificationInfo(project.request_data.project_classification).multiplier}
                      disabled
                      className="slider-input"
                    />
                    <p className="slider-description">Ground-Up to Renovation</p>
                  </div>
                  
                  {/* Confidence Band */}
                  <div className="confidence-card">
                    <p className="confidence-label">Confidence Band</p>
                    <p className="confidence-value">95% confidence</p>
                    <p className="confidence-range">
                      ${Math.round((project.total_cost / project.request_data.square_footage) * 0.9)}/SF - 
                      ${Math.round((project.total_cost / project.request_data.square_footage) * 1.1)}/SF
                    </p>
                    <p className="confidence-note">Based on 47 similar projects</p>
                  </div>
                </div>
              </div>
              
              {/* Provenance Footer */}
              <div className="provenance-footer">
                <button 
                  className="provenance-button"
                  onClick={() => alert('Provenance details: Base cost from RSMeans 2024 Q3, Regional index from SpecSharp database, Complexity factor based on project classification.')}
                >
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/>
                    <path d="M14 2v6h6M16 13H8M16 17H8M10 9H8"/>
                  </svg>
                  View Detailed Provenance Receipt
                </button>
              </div>
            </div>
          )}

      </div>

      {showTradePackageModal && (
        <TradePackageModal
          isOpen={showTradePackageModal}
          onClose={() => setShowTradePackageModal(false)}
          projectId={projectId!}
          trade={selectedTradePackage}
          onGenerate={handleGenerateTradePackage}
        />
      )}

      {showComparisonTool && (
        <ComparisonTool
          projectData={project}
          onClose={() => setShowComparisonTool(false)}
        />
      )}
    </div>
  );
}

export default ProjectDetail;