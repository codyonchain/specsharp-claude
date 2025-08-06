import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { scopeService, costService, tradePackageService } from '../services/api';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';
import ArchitecturalFloorPlan from './ArchitecturalFloorPlan';
import FloorPlanViewer from './FloorPlanViewer';
import ProfessionalFloorPlan from './ProfessionalFloorPlan';
import TradePackageModal from './TradePackageModal';
import ComparisonTool from './ComparisonTool';
import ComparisonToolV2 from './ComparisonToolV2';
import TradeSummary from './TradeSummary';
import TimeSavedDisplay from './TimeSavedDisplay';
import { Package, Sliders, FileSpreadsheet, Download, FileText, Share2, ArrowLeft } from 'lucide-react';
import { getDisplayBuildingType as getDisplayBuildingTypeUtil } from '../utils/buildingTypeDisplay';
import { formatCurrency, formatNumber } from '../utils/formatters';
import { calculateDeveloperMetrics, formatMetricValue } from '../utils/developerMetrics';
import { excelService, pdfService, shareService } from '../services/api';
import './ProjectDetail.css';

type TradeType = 'electrical' | 'plumbing' | 'hvac' | 'structural' | 'general';

const TRADE_CATEGORY_MAP: Record<TradeType, string | null> = {
  general: null,
  electrical: 'Electrical',
  plumbing: 'Plumbing',
  hvac: 'Mechanical',
  structural: 'Structural',
};

function ProjectDetail() {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();
  const [project, setProject] = useState<any>(null);
  const [costBreakdown, setCostBreakdown] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'details' | 'floorplan'>('details');
  const [showTradePackageModal, setShowTradePackageModal] = useState(false);
  const [selectedTradePackage, setSelectedTradePackage] = useState<TradeType>('general');
  const [showComparisonTool, setShowComparisonTool] = useState(false);
  const [selectedTrade, setSelectedTrade] = useState<TradeType>('general');
  const [exportingExcel, setExportingExcel] = useState(false);
  const [exportingPDF, setExportingPDF] = useState(false);
  const [showExportMenu, setShowExportMenu] = useState(false);
  const [projectFinishLevel, setProjectFinishLevel] = useState<'basic' | 'standard' | 'premium'>('standard');
  const [tradeFinishOverrides, setTradeFinishOverrides] = useState<Record<string, 'basic' | 'standard' | 'premium'>>({});
  const [showFinishImpact, setShowFinishImpact] = useState(false);
  const [showShareModal, setShowShareModal] = useState(false);
  const [shareLink, setShareLink] = useState<string>('');
  const [isGeneratingShare, setIsGeneratingShare] = useState(false);
  const [shareCopied, setShareCopied] = useState(false);

  useEffect(() => {
    if (projectId) {
      loadProjectDetails();
    }
  }, [projectId]);

  const loadProjectDetails = async () => {
    try {
      const projectData = await scopeService.getProject(projectId!);
      console.log('Project data loaded:', projectData);
      console.log('Project name:', projectData.project_name);
      console.log('Trade summaries:', projectData.trade_summaries);
      setProject(projectData);
      
      // Set finish level from project data
      if (projectData.request_data?.finish_level) {
        setProjectFinishLevel(projectData.request_data.finish_level);
      }
      
      const breakdown = await costService.calculateBreakdown(projectData);
      setCostBreakdown(breakdown);
    } catch (error) {
      console.error('Failed to load project:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateTradePackage = async (projectId: string, trade: string) => {
    console.log(`[TradePackage] Starting generation for trade: ${trade}, project: ${projectId}`);
    
    try {
      const data = await tradePackageService.generate(projectId, trade);
      console.log('[TradePackage] Successfully generated package:', data);
      return data;
    } catch (error) {
      console.error('[TradePackage] Error generating package:', error);
      throw error;
    }
  };

  const openTradePackageModal = (trade: TradeType) => {
    setSelectedTradePackage(trade);
    setShowTradePackageModal(true);
  };

  // Calculate cost impact of finish level changes
  const calculateFinishImpact = (finishLevel: 'basic' | 'standard' | 'premium') => {
    const multipliers = {
      basic: 0.85,
      standard: 1.0,
      premium: 1.25
    };
    
    const currentMultiplier = multipliers[projectFinishLevel];
    const newMultiplier = multipliers[finishLevel];
    const impactPercentage = ((newMultiplier / currentMultiplier) - 1) * 100;
    
    return {
      percentage: impactPercentage,
      newTotal: project?.total_cost ? project.total_cost * (newMultiplier / currentMultiplier) : 0
    };
  };

  // Excel export handlers
  const handleExportFullProject = async () => {
    try {
      setExportingExcel(true);
      setShowExportMenu(false); // Close menu immediately
      console.log('Starting Excel export for project:', project.project_id);
      console.log('Excel service:', excelService);
      console.log('Export function:', excelService.exportProject);
      const response = await excelService.exportProject(project.project_id);
      
      // Check if response has data
      if (!response.data) {
        throw new Error('No data received from server');
      }
      
      // Check blob size
      console.log('Received blob size:', response.data.size);
      
      if (response.data.size === 0) {
        throw new Error('Received empty file from server');
      }
      
      // response.data is already a blob when responseType is 'blob'
      const blob = response.data;
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `${project.project_name}_estimate.xlsx`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      
      console.log('Excel export completed successfully');
    } catch (error: any) {
      console.error('Failed to export Excel:', error);
      console.error('Error response:', error.response);
      
      let errorMessage = 'Failed to export Excel file. Please try again.';
      
      if (error.response) {
        // The request was made and the server responded with a status code
        // that falls out of the range of 2xx
        if (error.response.status === 401) {
          errorMessage = 'Authentication failed. Please log in again.';
          // Optionally redirect to login
          // navigate('/login');
        } else if (error.response.status === 404) {
          errorMessage = 'Project not found or you do not have access to it.';
        } else if (error.response.status === 500) {
          errorMessage = 'Server error. Please try again later.';
        } else if (error.response.data?.detail) {
          errorMessage = error.response.data.detail;
        }
      } else if (error.request) {
        // The request was made but no response was received
        errorMessage = 'No response from server. Please check your connection.';
      }
      
      alert(`Export Error: ${errorMessage}`);
    } finally {
      setExportingExcel(false);
    }
  };

  // PDF export handler
  const handleExportPDF = async (clientName?: string) => {
    try {
      setExportingPDF(true);
      console.log('Starting PDF export for project:', project.project_id);
      const response = await pdfService.exportProject(project.project_id, clientName);
      
      // Check if response has data
      if (!response.data) {
        throw new Error('No data received from server');
      }
      
      // response.data is already a blob when responseType is 'blob'
      const blob = response.data;
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `${project.project_name}_professional_estimate.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      
      console.log('PDF export completed successfully');
    } catch (error: any) {
      console.error('Failed to export PDF:', error);
      const errorMessage = error.response?.data?.detail || error.message || 'Failed to export PDF file';
      alert(`Export Error: ${errorMessage}`);
    } finally {
      setExportingPDF(false);
      setShowExportMenu(false);
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
      link.setAttribute('download', `${project.project_name}_${tradeName}_package.xlsx`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Failed to export trade Excel:', error);
      alert('Failed to export trade Excel file. Please try again.');
    }
  };

  const handleExtractTrade = async (tradeName: string) => {
    try {
      setExportingExcel(true);
      console.log('Extracting trade for subs:', tradeName);
      
      const response = await excelService.extractForSubs(project.project_id, tradeName);
      console.log('Extract response:', response);
      
      // Create blob and download
      const blob = response.data;
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${project.project_name}_${tradeName}_Scope_for_Subs.xlsx`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error: any) {
      console.error('Failed to extract trade for subs:', error);
      const errorMessage = error.response?.data?.detail || error.message || 'Failed to extract trade data';
      alert(`Extract Error: ${errorMessage}`);
    } finally {
      setExportingExcel(false);
    }
  };

  const handleShareProject = async () => {
    try {
      setIsGeneratingShare(true);
      const response = await shareService.createShareLink(project.project_id);
      setShareLink(response.share_url);
      setShowShareModal(true);
    } catch (error: any) {
      console.error('Failed to create share link:', error);
      alert('Failed to create share link. Please try again.');
    } finally {
      setIsGeneratingShare(false);
    }
  };

  const handleCopyShareLink = async () => {
    try {
      await navigator.clipboard.writeText(shareLink);
      setShareCopied(true);
      setTimeout(() => setShareCopied(false), 2000);
    } catch (error) {
      console.error('Failed to copy to clipboard:', error);
      // Fallback for older browsers
      const textArea = document.createElement('textarea');
      textArea.value = shareLink;
      document.body.appendChild(textArea);
      textArea.select();
      document.execCommand('copy');
      document.body.removeChild(textArea);
      setShareCopied(true);
      setTimeout(() => setShareCopied(false), 2000);
    }
  };

  if (loading) {
    return <div className="loading">Loading project details...</div>;
  }

  if (!project) {
    return <div className="error">Project not found</div>;
  }

  // Get display-friendly building type
  const getDisplayBuildingType = () => {
    return getDisplayBuildingTypeUtil(project.request_data);
  };

  // Filter categories based on selected trade
  const getFilteredCategories = () => {
    if (selectedTrade === 'general') {
      return project.categories;
    }
    
    const targetCategory = TRADE_CATEGORY_MAP[selectedTrade];
    return project.categories.filter((cat: any) => 
      cat.name.toLowerCase() === targetCategory?.toLowerCase()
    );
  };

  const filteredCategories = getFilteredCategories();
  
  // Calculate filtered totals
  const calculateFilteredTotals = () => {
    const categories = getFilteredCategories();
    const subtotal = categories.reduce((sum: number, cat: any) => sum + cat.subtotal, 0);
    const contingencyAmount = subtotal * (project.contingency_percentage / 100);
    const total = subtotal + contingencyAmount;
    
    return { subtotal, contingencyAmount, total };
  };

  const filteredTotals = selectedTrade !== 'general' 
    ? calculateFilteredTotals() 
    : { 
        subtotal: project.subtotal, 
        contingencyAmount: project.contingency_amount, 
        total: project.total_cost 
      };

  // Filter cost breakdown for chart
  const filteredCostBreakdown = selectedTrade !== 'general'
    ? costBreakdown.filter(item => 
        item.category.toLowerCase() === TRADE_CATEGORY_MAP[selectedTrade]?.toLowerCase()
      )
    : costBreakdown;

  const chartData = filteredCostBreakdown.map(item => ({
    name: item.category,
    value: item.subtotal,
    percentage: selectedTrade !== 'general' ? 100 : item.percentage_of_total,
  }));

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

  return (
    <div className="project-detail">
      
      <header className="page-header">
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <button
            onClick={() => navigate('/dashboard')}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
              padding: '0.75rem 1.25rem',
              background: '#667eea',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              cursor: 'pointer',
              fontSize: '16px',
              fontWeight: '600',
              transition: 'all 0.2s'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = '#5a67d8';
              e.currentTarget.style.transform = 'translateY(-2px)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = '#667eea';
              e.currentTarget.style.transform = 'translateY(0)';
            }}
          >
            <ArrowLeft size={20} />
            Dashboard
          </button>
          <h1 style={{ margin: 0, fontSize: '1.5rem', color: '#333' }}>
            {project.project_name || 'Project Details'}
          </h1>
        </div>
        <div className="header-actions">
          <div className="export-menu-container">
            <button 
              className="export-btn"
              onClick={() => setShowExportMenu(!showExportMenu)}
              disabled={exportingExcel || exportingPDF}
              title="Export options"
            >
              <Download size={18} />
              Export
              <span className="dropdown-arrow">▼</span>
            </button>
            
            {showExportMenu && (
              <div className="export-dropdown">
                <button 
                  className="export-option"
                  onClick={(e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    console.log('Excel button clicked!');
                    handleExportFullProject();
                  }}
                  disabled={exportingExcel}
                >
                  <FileSpreadsheet size={16} />
                  Standard Excel
                  {exportingExcel && <span> (Loading...)</span>}
                </button>
                <button 
                  className="export-option premium"
                  onClick={() => {
                    const clientName = prompt('Enter client name (optional):');
                    handleExportPDF(clientName || undefined);
                  }}
                  disabled={exportingPDF}
                >
                  <FileText size={16} />
                  Professional PDF
                  <span className="premium-badge">Premium</span>
                </button>
                <button 
                  className="export-option premium"
                  onClick={() => {
                    const clientName = prompt('Enter client name (optional):');
                    excelService.exportProfessional(project.project_id, clientName || undefined)
                      .then(response => {
                        const blob = response.data;
                        const url = window.URL.createObjectURL(blob);
                        const link = document.createElement('a');
                        link.href = url;
                        link.setAttribute('download', `${project.project_name}_professional.xlsx`);
                        document.body.appendChild(link);
                        link.click();
                        link.remove();
                        window.URL.revokeObjectURL(url);
                      })
                      .catch(error => {
                        console.error('Failed to export professional Excel:', error);
                        alert('Failed to export professional Excel file');
                      })
                      .finally(() => setShowExportMenu(false));
                  }}
                  disabled={exportingExcel}
                >
                  <FileSpreadsheet size={16} />
                  Professional Excel
                  <span className="premium-badge">Premium</span>
                </button>
              </div>
            )}
          </div>
          
          <button 
            className="compare-scenarios-btn"
            onClick={() => setShowComparisonTool(true)}
          >
            <Sliders size={18} />
            Compare Scenarios
          </button>
          
          <button 
            className="share-btn"
            onClick={handleShareProject}
            disabled={isGeneratingShare}
          >
            <Share2 size={18} />
            Share
          </button>
        </div>
      </header>

      {project.floor_plan && (
        <div className="project-tabs">
          <button 
            className={`tab ${activeTab === 'details' ? 'active' : ''}`}
            onClick={() => setActiveTab('details')}
          >
            Project Details
          </button>
          <button 
            className={`tab ${activeTab === 'floorplan' ? 'active' : ''}`}
            onClick={() => setActiveTab('floorplan')}
          >
            Floor Plan
          </button>
        </div>
      )}

      {activeTab === 'details' && (
        <div className="trade-filters">
          <div className="filter-tabs">
            <button
              className={`filter-tab ${selectedTrade === 'general' ? 'active' : ''}`}
              onClick={() => setSelectedTrade('general')}
            >
              All Trades
            </button>
            <button
              className={`filter-tab ${selectedTrade === 'electrical' ? 'active' : ''}`}
              onClick={() => setSelectedTrade('electrical')}
            >
              Electrical
            </button>
            <button
              className={`filter-tab ${selectedTrade === 'plumbing' ? 'active' : ''}`}
              onClick={() => setSelectedTrade('plumbing')}
            >
              Plumbing
            </button>
            <button
              className={`filter-tab ${selectedTrade === 'hvac' ? 'active' : ''}`}
              onClick={() => setSelectedTrade('hvac')}
            >
              HVAC
            </button>
            <button
              className={`filter-tab ${selectedTrade === 'structural' ? 'active' : ''}`}
              onClick={() => setSelectedTrade('structural')}
            >
              Structural
            </button>
          </div>
          {selectedTrade !== 'general' && (
            <div className="trade-actions">
              <button 
                className="trade-excel-btn"
                onClick={() => handleExportTrade(selectedTrade)}
                title="Export to Excel"
              >
                <FileSpreadsheet size={16} />
                Excel
              </button>
              <button 
                className="trade-package-btn"
                onClick={() => openTradePackageModal(selectedTrade)}
              >
                <Package size={16} />
                Generate {TRADE_CATEGORY_MAP[selectedTrade]} Package
              </button>
            </div>
          )}
        </div>
      )}

      {activeTab === 'details' ? (
      <div className="project-content">
        <div className="project-summary">
          <h2>Project Summary</h2>
          <div className="summary-grid">
            <div className="summary-item">
              <label>Location</label>
              <span>{project.request_data.location}</span>
            </div>
            <div className="summary-item">
              <label>Type</label>
              <span>{getDisplayBuildingType()}</span>
            </div>
            <div className="summary-item">
              <label>Project Classification</label>
              <span className="classification-badge">
                {project.request_data.project_classification === 'ground_up' && '🏗️ Ground-Up'}
                {project.request_data.project_classification === 'addition' && '🏠➕ Addition'}
                {project.request_data.project_classification === 'renovation' && '🔨 Renovation'}
                {!project.request_data.project_classification && '🏗️ Ground-Up'}
              </span>
            </div>
            <div className="summary-item">
              <label>Square Footage</label>
              <span>{project.request_data.square_footage.toLocaleString()} sq ft</span>
            </div>
            <div className="summary-item">
              <label>Floors</label>
              <span>{project.request_data.num_floors}</span>
            </div>
            <div className="summary-item">
              <label>Project Finish Level</label>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <select 
                  value={projectFinishLevel} 
                  onChange={(e) => {
                    const newLevel = e.target.value as 'basic' | 'standard' | 'premium';
                    setProjectFinishLevel(newLevel);
                    setShowFinishImpact(true);
                    setTimeout(() => setShowFinishImpact(false), 3000);
                  }}
                  onFocus={() => setShowFinishImpact(true)}
                  onBlur={() => setTimeout(() => setShowFinishImpact(false), 300)}
                  style={{ padding: '4px 8px', borderRadius: '4px', border: '1px solid #ddd' }}
                >
                  <option value="basic">Basic (-15%)</option>
                  <option value="standard">Standard</option>
                  <option value="premium">Premium (+25%)</option>
                </select>
                {showFinishImpact && projectFinishLevel !== 'standard' && (
                  <span style={{ 
                    fontSize: '0.85em', 
                    color: projectFinishLevel === 'basic' ? '#dc3545' : '#28a745',
                    fontWeight: 'bold'
                  }}>
                    {projectFinishLevel === 'basic' ? '-15%' : '+25%'} impact
                  </span>
                )}
              </div>
            </div>
            <div className="summary-item">
              <label>{selectedTrade !== 'general' ? `${TRADE_CATEGORY_MAP[selectedTrade]} Cost` : 'Total Cost'}</label>
              <span className="highlight">{formatCurrency(filteredTotals.total)}</span>
            </div>
            <div className="summary-item">
              <label>Cost per Sq Ft</label>
              <span>${(filteredTotals.total / project.request_data.square_footage).toFixed(2)}</span>
            </div>
          </div>
        </div>

        {/* Developer Metrics */}
        <div className="developer-metrics-section">
          <h3>Key Developer Metrics</h3>
          <div className="metrics-grid">
            {calculateDeveloperMetrics(project).map((metric, index) => (
              <div key={index} className="metric-card">
                <div className="metric-label">{metric.label}</div>
                <div className="metric-value">
                  {formatMetricValue(metric.value)}{metric.unit}
                </div>
                {metric.description && (
                  <div className="metric-description">{metric.description}</div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Time Saved Display */}
        <TimeSavedDisplay 
          generationTimeSeconds={project.generation_time_seconds}
          hourlyRate={75}
        />

        {/* Alert for multi-story buildings without elevators */}
        {project.request_data.num_floors > 1 && 
         project.request_data.occupancy_type === 'healthcare' &&
         !project.categories.some((cat: any) => 
           cat.name === 'Mechanical' && 
           cat.systems.some((sys: any) => sys.name.toLowerCase().includes('elevator'))
         ) && (
          <div className="info-message" style={{ marginBottom: '20px', padding: '15px', backgroundColor: '#fff3cd', border: '1px solid #ffeaa7', borderRadius: '4px' }}>
            <strong>Note:</strong> This project was generated before elevator calculations were added. 
            Consider regenerating the scope for updated mechanical systems including elevators.
          </div>
        )}

        <div className="cost-breakdown">
          <h2>Cost Breakdown</h2>
          <div className="breakdown-content">
            <div className="chart-container">
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={chartData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ percentage }) => `${percentage.toFixed(0)}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {chartData.map((_, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(value: number) => formatCurrency(value)} />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </div>

            <div className="breakdown-table">
              <table>
                <thead>
                  <tr>
                    <th>Category</th>
                    <th>Amount</th>
                    <th>Percentage</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredCostBreakdown.map((item, index) => (
                    <tr key={index}>
                      <td>{item.category}</td>
                      <td>{formatCurrency(item.subtotal)}</td>
                      <td>{(selectedTrade !== 'general' ? 100 : item.percentage_of_total).toFixed(1)}%</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        {selectedTrade === 'general' && project.trade_summaries ? (
          <TradeSummary 
            tradeSummaries={project.trade_summaries}
            onGeneratePackage={(trade) => openTradePackageModal(trade as TradeType)}
          />
        ) : selectedTrade !== 'general' ? (
          <div className="systems-detail">
            <h2>{TRADE_CATEGORY_MAP[selectedTrade]} Details</h2>
            {filteredCategories.map((category: any) => (
              <div key={category.name} className="category-section">
                <div className="category-header">
                  <h3>{category.name}</h3>
                  <button
                    className="extract-btn"
                    onClick={() => handleExtractTrade(category.name)}
                    title="Download scope for subcontractor"
                  >
                    <Download size={16} />
                    Extract for Subs
                  </button>
                </div>
                <table>
                  <thead>
                    <tr>
                      <th>System</th>
                      <th>Quantity</th>
                      <th>Unit</th>
                      <th>Unit Cost</th>
                      <th>Total Cost</th>
                      <th>Finish Level</th>
                      <th>Confidence</th>
                    </tr>
                  </thead>
                  <tbody>
                    {category.systems.map((system: any, index: number) => {
                      const systemKey = `${category.name}-${system.name}`;
                      const finishLevel = tradeFinishOverrides[systemKey] || projectFinishLevel;
                      return (
                        <tr key={index}>
                          <td>{system.name}</td>
                          <td>{system.quantity.toLocaleString()}</td>
                          <td>{system.unit}</td>
                          <td>${system.unit_cost.toFixed(2)}</td>
                          <td>{formatCurrency(system.total_cost)}</td>
                          <td>
                            <select
                              value={finishLevel}
                              onChange={(e) => {
                                const newOverrides = { ...tradeFinishOverrides };
                                if (e.target.value === projectFinishLevel) {
                                  delete newOverrides[systemKey];
                                } else {
                                  newOverrides[systemKey] = e.target.value as 'basic' | 'standard' | 'premium';
                                }
                                setTradeFinishOverrides(newOverrides);
                              }}
                              style={{ 
                                padding: '2px 4px', 
                                fontSize: '0.9em',
                                backgroundColor: finishLevel !== 'standard' ? 
                                  (finishLevel === 'basic' ? '#ffe6e6' : '#e6ffe6') : 'white',
                                border: `1px solid ${finishLevel !== 'standard' ? 
                                  (finishLevel === 'basic' ? '#ffcccc' : '#ccffcc') : '#ddd'}`
                              }}
                            >
                              <option value="basic">Basic</option>
                              <option value="standard">Standard</option>
                              <option value="premium">Premium</option>
                            </select>
                          </td>
                          <td>
                            <span 
                              className={`confidence-badge confidence-${system.confidence_label?.toLowerCase() || 'high'}`}
                              title={`Confidence Score: ${system.confidence_score || 95}%`}
                            >
                              {system.confidence_label || 'High'}
                            </span>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            ))}
          </div>
        ) : (
          <div className="systems-detail">
            <h2>System Details</h2>
            <p className="info-message">Trade summaries are being generated...</p>
            {project.categories && project.categories.map((category: any) => (
              <div key={category.name} className="category-section">
                <div className="category-header">
                  <h3>{category.name}</h3>
                  <button
                    className="extract-btn"
                    onClick={() => handleExtractTrade(category.name)}
                    title="Download scope for subcontractor"
                  >
                    <Download size={16} />
                    Extract for Subs
                  </button>
                </div>
                <table>
                  <thead>
                    <tr>
                      <th>System</th>
                      <th>Quantity</th>
                      <th>Unit</th>
                      <th>Unit Cost</th>
                      <th>Total Cost</th>
                      <th>Finish Level</th>
                      <th>Confidence</th>
                    </tr>
                  </thead>
                  <tbody>
                    {category.systems.map((system: any, index: number) => {
                      const systemKey = `${category.name}-${system.name}`;
                      const finishLevel = tradeFinishOverrides[systemKey] || projectFinishLevel;
                      return (
                        <tr key={index}>
                          <td>{system.name}</td>
                          <td>{system.quantity.toLocaleString()}</td>
                          <td>{system.unit}</td>
                          <td>${system.unit_cost.toFixed(2)}</td>
                          <td>{formatCurrency(system.total_cost)}</td>
                          <td>
                            <select
                              value={finishLevel}
                              onChange={(e) => {
                                const newOverrides = { ...tradeFinishOverrides };
                                if (e.target.value === projectFinishLevel) {
                                  delete newOverrides[systemKey];
                                } else {
                                  newOverrides[systemKey] = e.target.value as 'basic' | 'standard' | 'premium';
                                }
                                setTradeFinishOverrides(newOverrides);
                              }}
                              style={{ 
                                padding: '2px 4px', 
                                fontSize: '0.9em',
                                backgroundColor: finishLevel !== 'standard' ? 
                                  (finishLevel === 'basic' ? '#ffe6e6' : '#e6ffe6') : 'white',
                                border: `1px solid ${finishLevel !== 'standard' ? 
                                  (finishLevel === 'basic' ? '#ffcccc' : '#ccffcc') : '#ddd'}`
                              }}
                            >
                              <option value="basic">Basic</option>
                              <option value="standard">Standard</option>
                              <option value="premium">Premium</option>
                            </select>
                          </td>
                          <td>
                            <span 
                              className={`confidence-badge confidence-${system.confidence_label?.toLowerCase() || 'high'}`}
                              title={`Confidence Score: ${system.confidence_score || 95}%`}
                            >
                              {system.confidence_label || 'High'}
                            </span>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            ))}
          </div>
        )}

        <div className="project-footer">
          <div className="footer-summary">
            {project.markup_summary && (
              <>
                <div>
                  <label>Base Cost:</label>
                  <span>{formatCurrency(project.markup_summary.total_base_cost || project.base_subtotal || filteredTotals.subtotal)}</span>
                </div>
                <div>
                  <label>Markup ({project.markup_summary.average_markup_percent?.toFixed(1) || 0}%):</label>
                  <span>{formatCurrency(project.markup_summary.total_markup || 0)}</span>
                </div>
              </>
            )}
            <div>
              <label>Subtotal:</label>
              <span>{formatCurrency(filteredTotals.subtotal)}</span>
            </div>
            <div>
              <label>Contingency ({project.contingency_percentage}%):</label>
              <span>{formatCurrency(filteredTotals.contingencyAmount)}</span>
            </div>
            <div className="total">
              <label>{selectedTrade !== 'general' ? `${TRADE_CATEGORY_MAP[selectedTrade]} Total Cost:` : 'Total Project Cost:'}</label>
              <span>{formatCurrency(filteredTotals.total)}</span>
            </div>
          </div>
        </div>
      </div>
      ) : (
        // DEBUG: Check what's happening with floor plan rendering
        console.log('🏗️ FLOOR PLAN TAB ACTIVE!'),
        console.log('📊 Floor plan data:', project.floor_plan),
        console.log('🏛️ Has walls?', project.floor_plan && project.floor_plan.walls),
        
        project.floor_plan && project.floor_plan.walls ? (
          <ArchitecturalFloorPlan 
            floorPlan={project.floor_plan} 
            projectName={project.project_name}
          />
        ) : (
          <ProfessionalFloorPlan 
            floorPlan={project.floor_plan} 
            projectName={project.project_name}
          />
        )
      )}

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
        <ComparisonToolV2
          projectData={project}
          onClose={() => setShowComparisonTool(false)}
        />
      )}

      {/* Share Modal */}
      {showShareModal && (
        <div className="modal-overlay" onClick={() => setShowShareModal(false)}>
          <div className="modal-content share-modal" onClick={(e) => e.stopPropagation()}>
            <h3>Share Project</h3>
            <p>Share this read-only view with clients or partners:</p>
            
            <div className="share-link-container">
              <input 
                type="text" 
                value={shareLink} 
                readOnly 
                className="share-link-input"
              />
              <button 
                className="copy-btn"
                onClick={handleCopyShareLink}
              >
                {shareCopied ? '✓ Copied!' : 'Copy Link'}
              </button>
            </div>
            
            <p className="share-info">
              <span className="info-icon">ℹ️</span>
              This link will expire in 30 days
            </p>
            
            <div className="modal-actions">
              <button 
                onClick={() => setShowShareModal(false)} 
                className="close-btn"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default ProjectDetail;