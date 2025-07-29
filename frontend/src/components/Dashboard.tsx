import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { scopeService, authService, subscriptionService } from '../services/api';
import { Trash2, Copy, Settings, Users, Sliders, Edit2, Check, X } from 'lucide-react';
import { getDisplayBuildingType } from '../utils/buildingTypeDisplay';
import { formatCurrency, formatCurrencyPerSF, formatNumber } from '../utils/formatters';
import { calculateDeveloperMetrics, formatMetricValue } from '../utils/developerMetrics';
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
  const [selectedForComparison, setSelectedForComparison] = useState<string[]>([]);
  const [isComparisonMode, setIsComparisonMode] = useState(false);
  const [editingProjectId, setEditingProjectId] = useState<string | null>(null);
  const [editingProjectName, setEditingProjectName] = useState<string>('');
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

  const toggleComparisonSelection = (projectId: string) => {
    setSelectedForComparison(prev => {
      if (prev.includes(projectId)) {
        return prev.filter(id => id !== projectId);
      } else if (prev.length < 3) {
        return [...prev, projectId];
      }
      return prev;
    });
  };

  const toggleComparisonMode = () => {
    setIsComparisonMode(!isComparisonMode);
    if (isComparisonMode) {
      // Clear selections when exiting comparison mode
      setSelectedForComparison([]);
    }
  };

  const handleCompareProjects = () => {
    if (selectedForComparison.length >= 2) {
      // Navigate to comparison view with selected project IDs
      navigate(`/compare?projects=${selectedForComparison.join(',')}`);
    }
  };

  const handleEditProjectName = (e: React.MouseEvent, projectId: string, currentName: string) => {
    e.stopPropagation();
    setEditingProjectId(projectId);
    setEditingProjectName(currentName);
  };

  const handleSaveProjectName = async (projectId: string) => {
    if (!editingProjectName.trim()) {
      // Reset to original name if empty
      setEditingProjectId(null);
      return;
    }

    try {
      await scopeService.updateProjectName(projectId, editingProjectName.trim());
      setDeleteMessage(`Project name updated successfully`);
      setEditingProjectId(null);
      
      // Reload projects
      loadProjects();
      
      // Clear success message after 3 seconds
      setTimeout(() => setDeleteMessage(''), 3000);
    } catch (error) {
      console.error('Failed to update project name:', error);
      setDeleteMessage('Failed to update project name. Please try again.');
      setTimeout(() => setDeleteMessage(''), 3000);
    }
  };

  const handleCancelEdit = () => {
    setEditingProjectId(null);
    setEditingProjectName('');
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
          {projects.length >= 2 && (
            <button
              onClick={toggleComparisonMode}
              className={`comparison-mode-btn ${isComparisonMode ? 'active' : ''}`}
            >
              <Sliders size={20} />
              {isComparisonMode ? 'Exit Compare Mode' : 'Compare Projects'}
            </button>
          )}
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
            <>
              {isComparisonMode && (
                <div className="comparison-bar">
                  <p>
                    {selectedForComparison.length === 0 
                      ? 'Select 2-3 projects to compare' 
                      : `${selectedForComparison.length} project${selectedForComparison.length > 1 ? 's' : ''} selected`}
                  </p>
                  <button 
                    className="compare-btn"
                    onClick={handleCompareProjects}
                    disabled={selectedForComparison.length < 2}
                  >
                    View Comparison ({selectedForComparison.length}/3)
                  </button>
                </div>
              )}
              <div className="projects-grid">
                {projects.map((project) => {
                  const metrics = calculateDeveloperMetrics(project);
                  const primaryMetric = metrics.find(m => m.label !== 'Cost per SF') || metrics[0];
                  
                  return (
                    <div 
                      key={project.project_id} 
                      className={`project-card ${isComparisonMode && selectedForComparison.includes(project.project_id) ? 'selected-for-comparison' : ''} ${isComparisonMode ? 'comparison-mode' : ''}`}
                      onClick={() => {
                        if (isComparisonMode) {
                          toggleComparisonSelection(project.project_id);
                        } else {
                          navigate(`/project/${project.project_id}`);
                        }
                      }}
                    >
                      {isComparisonMode && (
                        <div className="comparison-indicator">
                          {selectedForComparison.includes(project.project_id) ? (
                            <span className="check-icon">✓</span>
                          ) : (
                            <span className="plus-icon">+</span>
                          )}
                        </div>
                      )}
                      <div className="project-actions">
                        <button
                          className="duplicate-btn"
                          onClick={(e) => handleDuplicateClick(e, project.project_id, project.name)}
                          title="Create a copy of this project"
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
                  <div className="project-name-container">
                    {editingProjectId === project.project_id ? (
                      <div className="project-name-edit" onClick={(e) => e.stopPropagation()}>
                        <input
                          type="text"
                          value={editingProjectName}
                          onChange={(e) => setEditingProjectName(e.target.value)}
                          onKeyPress={(e) => {
                            if (e.key === 'Enter') {
                              handleSaveProjectName(project.project_id);
                            }
                          }}
                          onKeyDown={(e) => {
                            if (e.key === 'Escape') {
                              handleCancelEdit();
                            }
                          }}
                          autoFocus
                          className="project-name-input"
                        />
                        <button
                          className="save-btn"
                          onClick={() => handleSaveProjectName(project.project_id)}
                          title="Save"
                        >
                          <Check size={16} />
                        </button>
                        <button
                          className="cancel-btn"
                          onClick={handleCancelEdit}
                          title="Cancel"
                        >
                          <X size={16} />
                        </button>
                      </div>
                    ) : (
                      <h3 className="project-name">
                        {project.name}
                        <button
                          className="edit-name-btn"
                          onClick={(e) => handleEditProjectName(e, project.project_id, project.name)}
                          title="Edit project name"
                        >
                          <Edit2 size={14} />
                        </button>
                      </h3>
                    )}
                  </div>
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
                  {primaryMetric && (
                    <div className="developer-metric">
                      <span className="metric-label">{primaryMetric.label}:</span>
                      <span className="metric-value">{formatMetricValue(primaryMetric.value)}{primaryMetric.unit}</span>
                    </div>
                  )}
                  <div className="project-meta">
                    <p className="project-date">
                      {new Date(project.created_at).toLocaleDateString()}
                    </p>
                    {project.created_by && (
                      <p className="project-creator">by {project.created_by}</p>
                    )}
                  </div>
                    </div>
                  );
                })}
              </div>
            </>
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