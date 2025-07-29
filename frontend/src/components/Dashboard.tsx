import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { scopeService, authService, subscriptionService } from '../services/api';
import { Trash2, Copy, Settings, Users } from 'lucide-react';
import { getDisplayBuildingType } from '../utils/buildingTypeDisplay';
import { formatCurrency, formatCurrencyPerSF, formatNumber } from '../utils/formatters';
import MarkupSettings from './MarkupSettings';
import OnboardingFlow from './OnboardingFlow';
import PaymentWall from './PaymentWall';
import TeamSettings from './TeamSettings';
import './Dashboard.css';

interface DashboardProps {
  setIsAuthenticated: (value: boolean) => void;
}

function Dashboard({ setIsAuthenticated }: DashboardProps) {
  const [projects, setProjects] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [deleteConfirm, setDeleteConfirm] = useState<{ projectId: string; name: string } | null>(null);
  const [deleteMessage, setDeleteMessage] = useState<string>('');
  const [showMarkupSettings, setShowMarkupSettings] = useState(false);
  const [showTeamSettings, setShowTeamSettings] = useState(false);
  const [showOnboarding, setShowOnboarding] = useState(false);
  const [showPaymentWall, setShowPaymentWall] = useState(false);
  const [subscriptionStatus, setSubscriptionStatus] = useState<any>(null);
  const [totalTimeSaved, setTotalTimeSaved] = useState(0);
  const navigate = useNavigate();

  useEffect(() => {
    loadProjects();
    checkSubscriptionStatus();
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

  const handleDuplicateClick = async (e: React.MouseEvent, projectId: string, projectName: string) => {
    e.stopPropagation(); // Prevent navigation to project detail
    
    try {
      const duplicatedProject = await scopeService.duplicateProject(projectId);
      setDeleteMessage(`Project "${projectName}" duplicated successfully`);
      
      // Reload projects
      loadProjects();
      
      // Clear success message after 3 seconds
      setTimeout(() => setDeleteMessage(''), 3000);
    } catch (error) {
      console.error('Failed to duplicate project:', error);
      setDeleteMessage('Failed to duplicate project. Please try again.');
      setTimeout(() => setDeleteMessage(''), 3000);
    }
  };

  const checkSubscriptionStatus = async () => {
    try {
      const status = await subscriptionService.getStatus();
      setSubscriptionStatus(status);
      
      // Check if user should see onboarding
      if (!status.has_completed_onboarding && status.estimate_count === 0) {
        setShowOnboarding(true);
      }
      
      // Check if user has hit free limit and needs to pay
      // TEMPORARILY DISABLED FOR TESTING - Re-enable by uncommenting below
      // if (!status.is_subscribed && status.estimate_count >= 3) {
      //   // Calculate total time saved (3 hours per estimate)
      //   setTotalTimeSaved(status.estimate_count * 3);
      //   setShowPaymentWall(true);
      // }
    } catch (error) {
      console.error('Failed to check subscription status:', error);
    }
  };

  const handleOnboardingComplete = async () => {
    setShowOnboarding(false);
    // Check if payment wall should be shown after onboarding
    await checkSubscriptionStatus();
    // Reload projects to show the newly created ones
    await loadProjects();
  };

  const handlePaymentSuccess = async () => {
    setShowPaymentWall(false);
    // Refresh subscription status
    await checkSubscriptionStatus();
  };

  // Show onboarding flow for new users
  if (showOnboarding) {
    return (
      <OnboardingFlow 
        onComplete={handleOnboardingComplete}
        currentEstimateCount={subscriptionStatus?.estimate_count || 0}
      />
    );
  }

  // Show payment wall if free limit reached
  if (showPaymentWall) {
    return (
      <PaymentWall
        totalTimeSaved={totalTimeSaved}
        estimatesCreated={subscriptionStatus?.estimate_count || 3}
        onPaymentSuccess={handlePaymentSuccess}
      />
    );
  }

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <h1>SpecSharp Dashboard</h1>
        <div className="header-actions">
          <button onClick={() => setShowTeamSettings(true)} className="team-btn">
            <Users size={20} />
            Team
          </button>
          <button onClick={() => setShowMarkupSettings(true)} className="settings-btn">
            <Settings size={20} />
            Markup Settings
          </button>
          <button onClick={handleLogout} className="logout-btn">Logout</button>
        </div>
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
                  <div className="project-actions">
                    <button
                      className="duplicate-btn"
                      onClick={(e) => handleDuplicateClick(e, project.project_id, project.name)}
                      title="Duplicate project"
                    >
                      <Copy size={18} />
                    </button>
                    <button
                      className="delete-btn"
                      onClick={(e) => handleDeleteClick(e, project.project_id, project.name)}
                      title="Delete project"
                    >
                      <Trash2 size={18} />
                    </button>
                  </div>
                  <h3>{project.name}</h3>
                  <p className="project-type">
                    {getDisplayBuildingType(project.scope_data?.request_data || {
                      project_type: project.project_type,
                      occupancy_type: project.occupancy_type || project.building_type
                    })}
                  </p>
                  <p>{project.location}</p>
                  <p>{formatNumber(project.square_footage)} sq ft</p>
                  <p className="project-cost">
                    {formatCurrency(project.total_cost)}
                    {project.cost_per_sqft && ` (${formatCurrencyPerSF(project.cost_per_sqft)})`}
                  </p>
                  <div className="project-meta">
                    <p className="project-date">
                      {new Date(project.created_at).toLocaleDateString()}
                    </p>
                    {project.created_by && (
                      <p className="project-creator">by {project.created_by}</p>
                    )}
                  </div>
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

      {/* Markup Settings Modal */}
      <MarkupSettings
        isOpen={showMarkupSettings}
        onClose={() => setShowMarkupSettings(false)}
        onSave={() => {
          // Optionally reload projects to reflect new markup calculations
          loadProjects();
        }}
      />

      {/* Team Settings Modal */}
      <TeamSettings
        isOpen={showTeamSettings}
        onClose={() => setShowTeamSettings(false)}
      />
    </div>
  );
}

export default Dashboard;