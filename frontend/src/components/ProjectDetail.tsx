import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { scopeService, costService } from '../services/api';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';
import ArchitecturalFloorPlan from './ArchitecturalFloorPlan';
import FloorPlanViewer from './FloorPlanViewer';
import ProfessionalFloorPlan from './ProfessionalFloorPlan';
import TradePackageModal from './TradePackageModal';
import ComparisonTool from './ComparisonTool';
import TradeSummary from './TradeSummary';
import { Package, Sliders, FileSpreadsheet, Download } from 'lucide-react';
import { getDisplayBuildingType as getDisplayBuildingTypeUtil } from '../utils/buildingTypeDisplay';
import { excelService } from '../services/api';
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

  useEffect(() => {
    if (projectId) {
      loadProjectDetails();
    }
  }, [projectId]);

  const loadProjectDetails = async () => {
    try {
      const projectData = await scopeService.getProject(projectId!);
      console.log('Project data loaded:', projectData);
      console.log('Trade summaries:', projectData.trade_summaries);
      setProject(projectData);
      
      const breakdown = await costService.calculateBreakdown(projectData);
      setCostBreakdown(breakdown);
    } catch (error) {
      console.error('Failed to load project:', error);
    } finally {
      setLoading(false);
    }
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

  const openTradePackageModal = (trade: TradeType) => {
    setSelectedTradePackage(trade);
    setShowTradePackageModal(true);
  };

  // Excel export handlers
  const handleExportFullProject = async () => {
    try {
      const response = await excelService.exportProject(project.project_id);
      
      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `${project.project_name}_estimate.xlsx`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Failed to export Excel:', error);
      alert('Failed to export Excel file. Please try again.');
    }
  };

  const handleExportTrade = async (tradeName: string) => {
    try {
      const response = await excelService.exportTrade(project.project_id, tradeName);
      
      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]));
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
        <button onClick={() => navigate('/dashboard')} className="back-btn">
          ← Back to Dashboard
        </button>
        <h1>{project.project_name}</h1>
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
              <label>Square Footage</label>
              <span>{project.request_data.square_footage.toLocaleString()} sq ft</span>
            </div>
            <div className="summary-item">
              <label>Floors</label>
              <span>{project.request_data.num_floors}</span>
            </div>
            <div className="summary-item">
              <label>{selectedTrade !== 'general' ? `${TRADE_CATEGORY_MAP[selectedTrade]} Cost` : 'Total Cost'}</label>
              <span className="highlight">${filteredTotals.total.toLocaleString()}</span>
            </div>
            <div className="summary-item">
              <label>Cost per Sq Ft</label>
              <span>${(filteredTotals.total / project.request_data.square_footage).toFixed(2)}</span>
            </div>
          </div>
        </div>

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
                  <Tooltip formatter={(value: number) => `$${value.toLocaleString()}`} />
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
                      <td>${item.subtotal.toLocaleString()}</td>
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
                <h3>{category.name}</h3>
                <table>
                  <thead>
                    <tr>
                      <th>System</th>
                      <th>Quantity</th>
                      <th>Unit</th>
                      <th>Unit Cost</th>
                      <th>Total Cost</th>
                      <th>Confidence</th>
                    </tr>
                  </thead>
                  <tbody>
                    {category.systems.map((system: any, index: number) => (
                      <tr key={index}>
                        <td>{system.name}</td>
                        <td>{system.quantity.toLocaleString()}</td>
                        <td>{system.unit}</td>
                        <td>${system.unit_cost.toFixed(2)}</td>
                        <td>${system.total_cost.toLocaleString()}</td>
                        <td>
                          <span 
                            className={`confidence-badge confidence-${system.confidence_label?.toLowerCase() || 'high'}`}
                            title={`Confidence Score: ${system.confidence_score || 95}%`}
                          >
                            {system.confidence_label || 'High'}
                          </span>
                        </td>
                      </tr>
                    ))}
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
                <h3>{category.name}</h3>
                <table>
                  <thead>
                    <tr>
                      <th>System</th>
                      <th>Quantity</th>
                      <th>Unit</th>
                      <th>Unit Cost</th>
                      <th>Total Cost</th>
                      <th>Confidence</th>
                    </tr>
                  </thead>
                  <tbody>
                    {category.systems.map((system: any, index: number) => (
                      <tr key={index}>
                        <td>{system.name}</td>
                        <td>{system.quantity.toLocaleString()}</td>
                        <td>{system.unit}</td>
                        <td>${system.unit_cost.toFixed(2)}</td>
                        <td>${system.total_cost.toLocaleString()}</td>
                        <td>
                          <span 
                            className={`confidence-badge confidence-${system.confidence_label?.toLowerCase() || 'high'}`}
                            title={`Confidence Score: ${system.confidence_score || 95}%`}
                          >
                            {system.confidence_label || 'High'}
                          </span>
                        </td>
                      </tr>
                    ))}
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
                  <span>${project.markup_summary.total_base_cost?.toLocaleString() || project.base_subtotal?.toLocaleString() || filteredTotals.subtotal.toLocaleString()}</span>
                </div>
                <div>
                  <label>Markup ({project.markup_summary.average_markup_percent?.toFixed(1) || 0}%):</label>
                  <span>${project.markup_summary.total_markup?.toLocaleString() || 0}</span>
                </div>
              </>
            )}
            <div>
              <label>Subtotal:</label>
              <span>${filteredTotals.subtotal.toLocaleString()}</span>
            </div>
            <div>
              <label>Contingency ({project.contingency_percentage}%):</label>
              <span>${filteredTotals.contingencyAmount.toLocaleString()}</span>
            </div>
            <div className="total">
              <label>{selectedTrade !== 'general' ? `${TRADE_CATEGORY_MAP[selectedTrade]} Total Cost:` : 'Total Project Cost:'}</label>
              <span>${filteredTotals.total.toLocaleString()}</span>
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

export default ProjectDetail;