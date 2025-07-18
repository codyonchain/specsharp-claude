import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { scopeService, authService } from '../services/api';
import './Dashboard.css';

interface DashboardProps {
  setIsAuthenticated: (value: boolean) => void;
}

type TradeType = 'electrical' | 'plumbing' | 'hvac' | 'structural' | 'general';

const TRADES = [
  { value: 'general', label: 'General Contractor', category: null },
  { value: 'electrical', label: 'Electrical', category: 'electrical' },
  { value: 'plumbing', label: 'Plumbing', category: 'plumbing' },
  { value: 'hvac', label: 'HVAC', category: 'mechanical' },
  { value: 'structural', label: 'Framing', category: 'structural' },
];

function Dashboard({ setIsAuthenticated }: DashboardProps) {
  const [projects, setProjects] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [isSubcontractorMode, setIsSubcontractorMode] = useState(
    localStorage.getItem('subcontractorMode') === 'true'
  );
  const [selectedTrade, setSelectedTrade] = useState<TradeType>(
    (localStorage.getItem('selectedTrade') as TradeType) || 'general'
  );
  const navigate = useNavigate();

  useEffect(() => {
    loadProjects();
  }, []);

  const loadProjects = async () => {
    try {
      const data = await scopeService.getProjects();
      setProjects(data);
    } catch (error) {
      console.error('Failed to load projects:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    authService.logout();
    setIsAuthenticated(false);
    navigate('/login');
  };

  const handleSubcontractorToggle = () => {
    const newMode = !isSubcontractorMode;
    setIsSubcontractorMode(newMode);
    localStorage.setItem('subcontractorMode', newMode.toString());
    
    if (!newMode) {
      // Reset to general contractor when turning off subcontractor mode
      setSelectedTrade('general');
      localStorage.setItem('selectedTrade', 'general');
    }
  };

  const handleTradeChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const trade = e.target.value as TradeType;
    setSelectedTrade(trade);
    localStorage.setItem('selectedTrade', trade);
  };

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <h1>SpecSharp Dashboard</h1>
        <button onClick={handleLogout} className="logout-btn">Logout</button>
      </header>

      <div className="dashboard-content">
        <div className="dashboard-actions">
          <button 
            onClick={() => navigate('/scope/new')}
            className="primary-btn"
          >
            Create New Scope
          </button>
          
          <div className="view-controls">
            <label className="toggle-container">
              <input
                type="checkbox"
                checked={isSubcontractorMode}
                onChange={handleSubcontractorToggle}
              />
              <span className="toggle-label">Subcontractor View</span>
            </label>
            
            {isSubcontractorMode && (
              <select
                value={selectedTrade}
                onChange={handleTradeChange}
                className="trade-select"
              >
                {TRADES.map(trade => (
                  <option key={trade.value} value={trade.value}>
                    {trade.label}
                  </option>
                ))}
              </select>
            )}
          </div>
        </div>

        <div className="projects-section">
          <h2>Your Projects</h2>
          {loading ? (
            <p>Loading projects...</p>
          ) : projects.length === 0 ? (
            <p>No projects yet. Create your first scope!</p>
          ) : (
            <div className="projects-grid">
              {projects.map((project) => (
                <div 
                  key={project.project_id} 
                  className="project-card"
                  onClick={() => navigate(`/project/${project.project_id}`)}
                >
                  <h3>{project.name}</h3>
                  <p>{project.location}</p>
                  <p>{project.square_footage.toLocaleString()} sq ft</p>
                  <p className="project-cost">
                    ${project.total_cost.toLocaleString()}
                  </p>
                  <p className="project-date">
                    {new Date(project.created_at).toLocaleDateString()}
                  </p>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default Dashboard;