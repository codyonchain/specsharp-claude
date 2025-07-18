import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { scopeService, costService } from '../services/api';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';
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
  
  // Get subcontractor mode settings from localStorage
  const isSubcontractorMode = localStorage.getItem('subcontractorMode') === 'true';
  const selectedTrade = (localStorage.getItem('selectedTrade') as TradeType) || 'general';

  useEffect(() => {
    if (projectId) {
      loadProjectDetails();
    }
  }, [projectId]);

  const loadProjectDetails = async () => {
    try {
      const projectData = await scopeService.getProject(projectId!);
      setProject(projectData);
      
      const breakdown = await costService.calculateBreakdown(projectData);
      setCostBreakdown(breakdown);
    } catch (error) {
      console.error('Failed to load project:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="loading">Loading project details...</div>;
  }

  if (!project) {
    return <div className="error">Project not found</div>;
  }

  // Filter categories based on selected trade
  const getFilteredCategories = () => {
    if (!isSubcontractorMode || selectedTrade === 'general') {
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

  const filteredTotals = isSubcontractorMode && selectedTrade !== 'general' 
    ? calculateFilteredTotals() 
    : { 
        subtotal: project.subtotal, 
        contingencyAmount: project.contingency_amount, 
        total: project.total_cost 
      };

  // Filter cost breakdown for chart
  const filteredCostBreakdown = isSubcontractorMode && selectedTrade !== 'general'
    ? costBreakdown.filter(item => 
        item.category.toLowerCase() === TRADE_CATEGORY_MAP[selectedTrade]?.toLowerCase()
      )
    : costBreakdown;

  const chartData = filteredCostBreakdown.map(item => ({
    name: item.category,
    value: item.subtotal,
    percentage: isSubcontractorMode && selectedTrade !== 'general' ? 100 : item.percentage_of_total,
  }));

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

  return (
    <div className={`project-detail ${isSubcontractorMode ? 'subcontractor-mode' : ''}`}>
      {isSubcontractorMode && selectedTrade !== 'general' && (
        <div className="trade-banner">
          <span>Viewing as: {TRADE_CATEGORY_MAP[selectedTrade]} Subcontractor</span>
        </div>
      )}
      
      <header className="page-header">
        <button onClick={() => navigate('/dashboard')} className="back-btn">
          ← Back to Dashboard
        </button>
        <h1>{project.project_name}</h1>
      </header>

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
              <span>{project.request_data.project_type}</span>
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
              <label>Total Cost</label>
              <span className="highlight">${filteredTotals.total.toLocaleString()}</span>
            </div>
            <div className="summary-item">
              <label>Cost per Sq Ft</label>
              <span>${(filteredTotals.total / project.request_data.square_footage).toFixed(2)}</span>
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
                    {chartData.map((entry, index) => (
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
                      <td>{isSubcontractorMode && selectedTrade !== 'general' ? '100.0' : item.percentage_of_total.toFixed(1)}%</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <div className="systems-detail">
          <h2>System Details</h2>
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
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ))}
        </div>

        <div className="project-footer">
          <div className="footer-summary">
            <div>
              <label>Subtotal:</label>
              <span>${filteredTotals.subtotal.toLocaleString()}</span>
            </div>
            <div>
              <label>Contingency ({project.contingency_percentage}%):</label>
              <span>${filteredTotals.contingencyAmount.toLocaleString()}</span>
            </div>
            <div className="total">
              <label>{isSubcontractorMode && selectedTrade !== 'general' ? `${TRADE_CATEGORY_MAP[selectedTrade]} Total Cost:` : 'Total Project Cost:'}</label>
              <span>${filteredTotals.total.toLocaleString()}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ProjectDetail;