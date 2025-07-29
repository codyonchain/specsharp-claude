import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { shareService } from '../services/api';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';
import ArchitecturalFloorPlan from './ArchitecturalFloorPlan';
import FloorPlanViewer from './FloorPlanViewer';
import ProfessionalFloorPlan from './ProfessionalFloorPlan';
import TradeSummary from './TradeSummary';
import { getDisplayBuildingType as getDisplayBuildingTypeUtil } from '../utils/buildingTypeDisplay';
import { formatCurrency, formatCurrencyPerSF, formatNumber } from '../utils/formatters';
import './SharedProjectView.css';

function SharedProjectView() {
  const { shareId } = useParams<{ shareId: string }>();
  const navigate = useNavigate();
  const [project, setProject] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>('');
  const [activeTab, setActiveTab] = useState<'details' | 'floorplan'>('details');

  useEffect(() => {
    if (shareId) {
      loadSharedProject();
    }
  }, [shareId]);

  const loadSharedProject = async () => {
    try {
      const data = await shareService.getSharedProject(shareId!);
      setProject(data);
    } catch (error: any) {
      console.error('Failed to load shared project:', error);
      if (error.response?.status === 410) {
        setError('This share link has expired.');
      } else if (error.response?.status === 403) {
        setError('This share link has been deactivated.');
      } else if (error.response?.status === 404) {
        setError('Share link not found.');
      } else {
        setError('Failed to load project. Please check the link and try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  const getDisplayBuildingType = () => {
    if (!project?.project_data) return '';
    const requestData = project.project_data.request_data || {};
    return getDisplayBuildingTypeUtil(requestData);
  };

  const prepareChartData = () => {
    if (!project?.project_data?.categories) return [];
    
    return project.project_data.categories.map((category: any) => ({
      name: category.name,
      value: category.subtotal || 0,
    }));
  };

  const COLORS = ['#667eea', '#48bb78', '#ed8936', '#38b2ac', '#e53e3e', '#805ad5', '#d69e2e'];

  if (loading) {
    return <div className="loading">Loading project...</div>;
  }

  if (error) {
    return (
      <div className="error-container">
        <div className="error-content">
          <h2>Unable to Load Project</h2>
          <p>{error}</p>
          <button onClick={() => navigate('/')} className="home-btn">
            Go to SpecSharp Home
          </button>
          <div className="cta-section">
            <h3>Want to create your own estimates?</h3>
            <p>Join thousands of contractors using SpecSharp for fast, accurate construction estimates.</p>
            <button onClick={() => navigate('/demo')} className="cta-btn">
              Try It Now - No Signup Required
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (!project) return null;

  const projectData = project.project_data;
  const costBreakdown = prepareChartData();

  return (
    <div className="shared-project-view">
      {/* Top Branding Banner */}
      <div className="powered-by-banner">
        <span className="banner-text">
          Powered by <a href="https://specsharp.ai?ref=shared" target="_blank" rel="noopener noreferrer" className="specsharp-link">SpecSharp</a> 
          {' '}— Create professional estimates in 90 seconds
        </span>
      </div>

      <header className="shared-header">
        <div className="shared-info-section">
          <div>
            <p className="shared-by-label">Shared by {project.shared_by}</p>
            <h1 className="project-name">{project.project_name}</h1>
          </div>
          <div className="powered-by-section">
            <p className="powered-label">Powered by</p>
            <a href="https://specsharp.ai?ref=shared" target="_blank" rel="noopener noreferrer" className="specsharp-logo-link">
              SpecSharp →
            </a>
          </div>
        </div>
        <div className="header-meta">
          <span className="view-count">View #{project.view_count}</span>
          <span className="separator">•</span>
          <span className="read-only-badge">Read-Only</span>
          <span className="separator">•</span>
          <span className="expire-info">Expires {new Date(project.expires_at).toLocaleDateString()}</span>
        </div>
      </header>

      {/* CTA Banner */}
      <div className="cta-banner">
        <p className="cta-text">
          Want to create your own estimates in 90 seconds? 
          <button onClick={() => navigate('/demo')} className="cta-link-btn">
            Try SpecSharp Free →
          </button>
        </p>
      </div>

      {projectData.floor_plan && (
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

      {activeTab === 'details' ? (
        <div className="project-content">
          <div className="project-summary">
            <h2>Project Summary</h2>
            <div className="summary-grid">
              <div className="summary-item">
                <label>Location</label>
                <span>{projectData.request_data?.location}</span>
              </div>
              <div className="summary-item">
                <label>Type</label>
                <span>{getDisplayBuildingType()}</span>
              </div>
              <div className="summary-item">
                <label>Square Footage</label>
                <span>{projectData.request_data?.square_footage?.toLocaleString()} sq ft</span>
              </div>
              <div className="summary-item">
                <label>Floors</label>
                <span>{projectData.request_data?.num_floors}</span>
              </div>
              <div className="summary-item">
                <label>Total Cost</label>
                <span className="total-cost">{formatCurrency(projectData.total_cost || 0)}</span>
              </div>
              <div className="summary-item">
                <label>Cost per SF</label>
                <span>{formatCurrencyPerSF(projectData.cost_per_sqft || 0)}</span>
              </div>
            </div>
          </div>

          <div className="cost-breakdown">
            <h2>Cost Breakdown</h2>
            <div className="breakdown-content">
              <div className="chart-container">
                <ResponsiveContainer width="100%" height={400}>
                  <PieChart>
                    <Pie
                      data={costBreakdown}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                      outerRadius={120}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {costBreakdown.map((entry: any, index: number) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip formatter={(value: any) => formatCurrency(value)} />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              </div>
              <div className="breakdown-table">
                <table>
                  <thead>
                    <tr>
                      <th>Category</th>
                      <th>Cost</th>
                      <th>% of Total</th>
                    </tr>
                  </thead>
                  <tbody>
                    {projectData.categories?.map((category: any) => (
                      <tr key={category.name}>
                        <td>{category.name}</td>
                        <td>{formatCurrency(category.subtotal || 0)}</td>
                        <td>{((category.subtotal / projectData.total_cost) * 100).toFixed(1)}%</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          {projectData.trade_summaries && (
            <div className="trade-summaries-section">
              <h2>Trade Summaries</h2>
              <TradeSummary 
                tradeSummaries={projectData.trade_summaries}
                onGeneratePackage={() => {}} // Disabled in shared view
                isReadOnly={true}
              />
            </div>
          )}

          <div className="systems-detail">
            <h2>System Details</h2>
            {projectData.categories?.map((category: any) => (
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
                    {category.systems?.map((system: any, index: number) => (
                      <tr key={index}>
                        <td>{system.name}</td>
                        <td>{system.quantity?.toLocaleString()}</td>
                        <td>{system.unit}</td>
                        <td>${system.unit_cost?.toFixed(2)}</td>
                        <td>{formatCurrency(system.total_cost || 0)}</td>
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
        </div>
      ) : (
        <div className="floorplan-container">
          {projectData.floor_plan?.layout_type === 'professional' ? (
            <ProfessionalFloorPlan floorPlanData={projectData.floor_plan} />
          ) : projectData.floor_plan?.layout_type === 'architectural' ? (
            <ArchitecturalFloorPlan floorPlanData={projectData.floor_plan} />
          ) : (
            <FloorPlanViewer floorPlanData={projectData.floor_plan} />
          )}
        </div>
      )}

      <footer className="shared-footer">
        <div className="footer-content">
          <div className="footer-brand">
            <h3>🚀 Powered by SpecSharp</h3>
            <p>Professional construction estimates in 90 seconds</p>
            <a href="https://specsharp.ai?ref=shared-footer" target="_blank" rel="noopener noreferrer" className="footer-link">
              specsharp.ai →
            </a>
          </div>
          <div className="footer-cta">
            <h4>Ready to save 3+ hours per estimate?</h4>
            <button onClick={() => navigate('/demo')} className="footer-cta-btn">
              Try Demo Now - No Signup Required →
            </button>
            <p className="cta-subtext">No credit card required • 3 free estimates • Join 1,000+ contractors</p>
          </div>
        </div>
        <div className="footer-bottom">
          <p>This estimate was created in 90 seconds using SpecSharp • <a href="https://specsharp.ai?ref=shared" target="_blank" rel="noopener noreferrer">Get your own account</a></p>
        </div>
      </footer>
    </div>
  );
}

export default SharedProjectView;