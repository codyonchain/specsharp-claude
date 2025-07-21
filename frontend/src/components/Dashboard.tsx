import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { scopeService, authService } from '../services/api';
import './Dashboard.css';

interface DashboardProps {
  setIsAuthenticated: (value: boolean) => void;
}

function Dashboard({ setIsAuthenticated }: DashboardProps) {
  const [projects, setProjects] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
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