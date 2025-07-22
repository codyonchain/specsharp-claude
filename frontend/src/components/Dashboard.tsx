import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { scopeService, authService } from '../services/api';
import { Trash2 } from 'lucide-react';
import './Dashboard.css';

interface DashboardProps {
  setIsAuthenticated: (value: boolean) => void;
}

function Dashboard({ setIsAuthenticated }: DashboardProps) {
  const [projects, setProjects] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [deleteConfirm, setDeleteConfirm] = useState<{ projectId: string; name: string } | null>(null);
  const [deleteMessage, setDeleteMessage] = useState<string>('');
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

  const handleDeleteClick = (e: React.MouseEvent, projectId: string, projectName: string) => {
    e.stopPropagation(); // Prevent navigation to project detail
    setDeleteConfirm({ projectId, name: projectName });
  };

  const handleDeleteConfirm = async () => {
    if (!deleteConfirm) return;

    try {
      await scopeService.deleteProject(deleteConfirm.projectId);
      setDeleteMessage(`Project "${deleteConfirm.name}" deleted successfully`);
      setDeleteConfirm(null);
      
      // Reload projects
      loadProjects();
      
      // Clear success message after 3 seconds
      setTimeout(() => setDeleteMessage(''), 3000);
    } catch (error) {
      console.error('Failed to delete project:', error);
      setDeleteMessage('Failed to delete project. Please try again.');
      setTimeout(() => setDeleteMessage(''), 3000);
    }
  };

  const handleDeleteCancel = () => {
    setDeleteConfirm(null);
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

        {deleteMessage && (
          <div className={`message ${deleteMessage.includes('successfully') ? 'success' : 'error'}`}>
            {deleteMessage}
          </div>
        )}

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
                  <button
                    className="delete-btn"
                    onClick={(e) => handleDeleteClick(e, project.project_id, project.name)}
                    title="Delete project"
                  >
                    <Trash2 size={18} />
                  </button>
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

      {/* Delete Confirmation Modal */}
      {deleteConfirm && (
        <div className="modal-overlay" onClick={handleDeleteCancel}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h3>Delete project?</h3>
            <p>Are you sure you want to delete "{deleteConfirm.name}"?</p>
            <p className="warning">This will permanently delete the project and cannot be undone.</p>
            <div className="modal-actions">
              <button onClick={handleDeleteCancel} className="cancel-btn">
                Cancel
              </button>
              <button onClick={handleDeleteConfirm} className="delete-confirm-btn">
                Delete Project
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default Dashboard;