import { useState, useEffect, useMemo } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { scopeService, costService, excelService } from '../services/api';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';
import ArchitecturalFloorPlan from './ArchitecturalFloorPlan';
import ProfessionalFloorPlan from './ProfessionalFloorPlan';
import TradePackageModal from './TradePackageModal';
import ComparisonTool from './ComparisonTool';
import { Package, Sliders, ChevronDown, ChevronUp, FileSpreadsheet, Download } from 'lucide-react';
import { getDisplayBuildingType } from '../utils/buildingTypeDisplay';
import './ProjectDetail.css';

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

function ProgressiveProjectDetail() {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();
  const [project, setProject] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'details' | 'floorplan'>('details');
  const [selectedTrade, setSelectedTrade] = useState<TradeType>('all');
  const [expandedCategories, setExpandedCategories] = useState<Set<string>>(new Set());
  const [showTradePackageModal, setShowTradePackageModal] = useState(false);
  const [selectedTradePackage, setSelectedTradePackage] = useState<string>('');
  const [showComparisonTool, setShowComparisonTool] = useState(false);

  useEffect(() => {
    if (projectId) {
      loadProjectDetails();
    }
  }, [projectId]);

  const loadProjectDetails = async () => {
    try {
      const projectData = await scopeService.getProject(projectId!);
      console.log('Project data loaded:', projectData);
      setProject(projectData);
    } catch (error) {
      console.error('Failed to load project:', error);
    } finally {
      setLoading(false);
    }
  };

  // Aggregate categories into main trades
  const tradeSummaries = useMemo(() => {
    if (!project?.categories) return [];

    const tradeGroups: Record<TradeType, TradeSummary> = {
      'structural': { name: 'structural', displayName: 'Structural', total: 0, percentage: 0, categories: [] },
      'mechanical': { name: 'mechanical', displayName: 'Mechanical', total: 0, percentage: 0, categories: [] },
      'electrical': { name: 'electrical', displayName: 'Electrical', total: 0, percentage: 0, categories: [] },
      'plumbing': { name: 'plumbing', displayName: 'Plumbing', total: 0, percentage: 0, categories: [] },
      'finishes': { name: 'finishes', displayName: 'Finishes', total: 0, percentage: 0, categories: [] },
      'general_conditions': { name: 'general_conditions', displayName: 'General Conditions', total: 0, percentage: 0, categories: [] },
    };

    // Aggregate categories into trades
    project.categories.forEach((category: any) => {
      const categoryName = category.name.toLowerCase();
      const tradeName = TRADE_MAPPING[categoryName] || (categoryName.includes('general') ? 'general_conditions' : 'general_conditions');
      
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
    const response = await fetch(`http://localhost:8001/api/v1/trade-package/generate/${projectId}/${trade}`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    });
    
    if (!response.ok) throw new Error('Failed to generate trade package');
    
    const data = await response.json();
    return data;
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

  const totalCost = selectedTrade === 'all' 
    ? project.total_cost 
    : selectedTradeData.reduce((sum, trade) => sum + trade.total, 0);

  return (
    <div className="project-detail">
      <header className="page-header">
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', flex: 1 }}>
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
              transition: 'all 0.2s',
              boxShadow: '0 2px 4px rgba(102, 126, 234, 0.2)'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = '#5a67d8';
              e.currentTarget.style.transform = 'translateY(-2px)';
              e.currentTarget.style.boxShadow = '0 4px 8px rgba(102, 126, 234, 0.3)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = '#667eea';
              e.currentTarget.style.transform = 'translateY(0)';
              e.currentTarget.style.boxShadow = '0 2px 4px rgba(102, 126, 234, 0.2)';
            }}
          >
            <span style={{ fontSize: '20px' }}>←</span>
            Dashboard
          </button>
          <h1 style={{ margin: 0, fontSize: '1.5rem', color: '#333' }}>
            {project.project_name}
          </h1>
        </div>
        <div className="header-actions">
          <button 
            className="export-excel-btn"
            onClick={handleExportFullProject}
            title="Export full project to Excel"
          >
            <FileSpreadsheet size={18} />
            Export Excel
          </button>
          <button 
            className="compare-scenarios-btn"
            onClick={() => setShowComparisonTool(true)}
          >
            <Sliders size={18} />
            Compare Scenarios
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
              className={`filter-tab ${selectedTrade === 'all' ? 'active' : ''}`}
              onClick={() => setSelectedTrade('all')}
            >
              All Trades
            </button>
            {tradeSummaries.map(trade => (
              <button
                key={trade.name}
                className={`filter-tab ${selectedTrade === trade.name ? 'active' : ''}`}
                onClick={() => setSelectedTrade(trade.name as TradeType)}
              >
                {trade.displayName}
              </button>
            ))}
          </div>
          {selectedTrade !== 'all' && (
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
                Generate {TRADE_DISPLAY_NAMES[selectedTrade]} Package
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
                <span>{getDisplayBuildingType(project.request_data)}</span>
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
                <label>{selectedTrade !== 'all' ? `${TRADE_DISPLAY_NAMES[selectedTrade]} Cost` : 'Total Cost'}</label>
                <span className="highlight">${totalCost.toLocaleString()}</span>
              </div>
              <div className="summary-item">
                <label>Cost per Sq Ft</label>
                <span>${(totalCost / project.request_data.square_footage).toFixed(2)}</span>
              </div>
            </div>
          </div>

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
                    <Tooltip formatter={(value: number) => `$${value.toLocaleString()}`} />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              </div>

              <div className="breakdown-table">
                <table>
                  <thead>
                    <tr>
                      <th>{selectedTrade === 'all' ? 'Trade' : 'Category'}</th>
                      <th>Amount</th>
                      <th>Percentage</th>
                    </tr>
                  </thead>
                  <tbody>
                    {chartData.map((item, index) => (
                      <tr key={index}>
                        <td>{item.name}</td>
                        <td>${item.value.toLocaleString()}</td>
                        <td>{item.percentage.toFixed(1)}%</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          {/* Progressive Disclosure Section */}
          <div className="progressive-disclosure">
            {selectedTrade === 'all' ? (
              // Level 1: Show all trades summary
              <div className="trade-summaries">
                <h2>Trade Summaries</h2>
                {tradeSummaries.map(trade => (
                  <div key={trade.name} className="trade-summary-card">
                    <div className="trade-header">
                      <h3>{trade.displayName}</h3>
                      <span className="trade-total">${trade.total.toLocaleString()} ({trade.percentage.toFixed(1)}%)</span>
                    </div>
                    <button 
                      className="view-details-btn"
                      onClick={() => setSelectedTrade(trade.name as TradeType)}
                    >
                      View Details →
                    </button>
                  </div>
                ))}
              </div>
            ) : (
              // Level 2: Show categories for selected trade
              <div className="category-summaries">
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
                    
                    {/* Level 3: Detailed line items (expandable) */}
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
          </div>

          <div className="project-footer">
            <div className="footer-summary">
              <div>
                <label>Subtotal:</label>
                <span>${(totalCost / 1.1).toLocaleString()}</span>
              </div>
              <div>
                <label>Contingency ({project.contingency_percentage}%):</label>
                <span>${(totalCost * 0.1).toLocaleString()}</span>
              </div>
              <div className="total">
                <label>{selectedTrade !== 'all' ? `${TRADE_DISPLAY_NAMES[selectedTrade]} Total:` : 'Total Project Cost:'}</label>
                <span>${totalCost.toLocaleString()}</span>
              </div>
            </div>
          </div>
        </div>
      ) : (
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
        <ComparisonTool
          projectData={project}
          onClose={() => setShowComparisonTool(false)}
        />
      )}
    </div>
  );
}

export default ProgressiveProjectDetail;