import { useState, useEffect, lazy, Suspense } from 'react';
import { useNavigate } from 'react-router-dom';
import { scopeService, authService, subscriptionService } from '../services/api';
import { Trash2, Copy, Settings, Users, Sliders, Edit2, Check, X } from 'lucide-react';
import { getDisplayBuildingType } from '../utils/buildingTypeDisplay';
import { formatCurrency, formatCurrencyPerSF, formatNumber } from '../utils/formatters';
import { calculateDeveloperMetrics, formatMetricValue } from '../utils/developerMetrics';
import './Dashboard.css';

// Lazy load modal components (not immediately visible)
const MarkupSettings = lazy(() => import('./MarkupSettings'));
const OnboardingFlow = lazy(() => import('./OnboardingFlow'));
const PaymentWall = lazy(() => import('./PaymentWall'));
const TeamSettings = lazy(() => import('./TeamSettings'));

interface DashboardProps {
  setIsAuthenticated: (value: boolean) => void;
}

// Loading component for lazy-loaded modals
const ModalLoading = () => (
  <div style={{
    position: 'fixed',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    zIndex: 9999
  }}>
    <div style={{
      backgroundColor: 'white',
      padding: '40px',
      borderRadius: '8px',
      textAlign: 'center'
    }}>
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900 mx-auto"></div>
      <p style={{ marginTop: '16px', color: '#666' }}>Loading...</p>
    </div>
  </div>
);

// Quick start templates configuration with complete form data
const quickTemplates = [
  {
    name: "Hospital",
    icon: "🏥",
    bgColor: "#fee2e2",
    borderColor: "#fca5a5",
    naturalLanguage: "New 200000 sf 7 story hospital with emergency department, imaging center, 150 beds, and surgical suites in Nashville, TN. Standard finishes.",
    formData: {
      project_name: "Regional Medical Center",
      building_type: "healthcare",
      building_subtype: "hospital",
      location: "Nashville, TN",
      square_footage: 200000,
      num_floors: 7,
      ceiling_height: 12,
      special_requirements: "Emergency department, imaging center with MRI/CT, 150 patient beds, 8 operating rooms, ICU, laboratory, pharmacy, cafeteria",
      finish_level: "standard",
      project_classification: "ground_up"
    }
  },
  {
    name: "School", 
    icon: "🏫",
    bgColor: "#fef3c7",
    borderColor: "#fcd34d",
    naturalLanguage: "New 95000 sf 3 story middle school with 800 student capacity, gymnasium, science labs, cafeteria, and library in Manchester, NH. Standard educational finishes.",
    formData: {
      project_name: "Lincoln Middle School",
      building_type: "educational",
      building_subtype: "middle_school",
      location: "Manchester, NH",
      square_footage: 95000,
      num_floors: 3,
      ceiling_height: 12,
      special_requirements: "40 classrooms, gymnasium with basketball courts, 6 science labs, cafeteria for 400 students, library/media center, music room, art studio",
      finish_level: "standard",
      project_classification: "ground_up"
    }
  },
  {
    name: "Office TI",
    icon: "🏢",
    bgColor: "#dbeafe",
    borderColor: "#93c5fd",
    naturalLanguage: "15000 sf office tenant improvement with open workspace, conference rooms, kitchen, and reception area in Denver, CO. Premium finishes.",
    formData: {
      project_name: "Tech Company Office Buildout",
      building_type: "commercial",
      building_subtype: "office",
      location: "Denver, CO",
      square_footage: 15000,
      num_floors: 1,
      ceiling_height: 10,
      special_requirements: "Open workspace for 80 employees, 5 conference rooms, phone booths, kitchen/break room, reception area, IT server room, wellness room",
      finish_level: "premium",
      project_classification: "tenant_improvement"
    }
  },
  {
    name: "Hotel",
    icon: "🏨",
    bgColor: "#e9d5ff",
    borderColor: "#c084fc",
    naturalLanguage: "New 120000 sf 12 story luxury hotel with 150 rooms, rooftop restaurant, spa, conference facilities, and valet parking in Miami, FL. Premium hospitality finishes.",
    formData: {
      project_name: "Downtown Luxury Hotel",
      building_type: "hospitality",
      building_subtype: "full_service_hotel",
      location: "Miami, FL",
      square_footage: 120000,
      num_floors: 12,
      ceiling_height: 10,
      special_requirements: "150 guest rooms including 20 suites, rooftop restaurant and bar, full-service spa, 5000 sf conference center, business center, outdoor pool, valet parking",
      finish_level: "premium",
      project_classification: "ground_up"
    }
  },
  {
    name: "Apartments",
    icon: "🏘️",
    bgColor: "#ccfbf1",
    borderColor: "#5eead4",
    naturalLanguage: "New 150000 sf 5 story luxury apartment complex with 200 units, amenity deck, fitness center, co-working space, and structured parking in Austin, TX. Premium residential finishes.",
    formData: {
      project_name: "Urban Living Apartments",
      building_type: "residential",
      building_subtype: "apartments",
      location: "Austin, TX",
      square_footage: 150000,
      num_floors: 5,
      ceiling_height: 9,
      special_requirements: "200 units (mix of studios, 1BR, 2BR), rooftop amenity deck with pool, fitness center, yoga studio, co-working spaces, pet spa, bike storage, 250-space parking garage",
      finish_level: "premium",
      project_classification: "ground_up"
    }
  }
];

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
      <Suspense fallback={<ModalLoading />}>
        <OnboardingFlow 
          onComplete={handleOnboardingComplete}
          currentEstimateCount={subscriptionStatus?.estimate_count || 0}
        />
      </Suspense>
    );
  }

  // Show payment wall if free limit reached
  if (showPaymentWall) {
    return (
      <Suspense fallback={<ModalLoading />}>
        <PaymentWall
          totalTimeSaved={totalTimeSaved}
          estimatesCreated={subscriptionStatus?.estimate_count || 3}
          onPaymentSuccess={handlePaymentSuccess}
        />
      </Suspense>
    );
  }

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <div className="header-content">
          <h1>Projects</h1>
          <div className="header-actions">
            <button onClick={() => setShowTeamSettings(true)} className="header-btn secondary">
              <Users size={18} />
              <span>Team</span>
            </button>
            <button onClick={() => setShowMarkupSettings(true)} className="header-btn secondary">
              <Settings size={18} />
              <span>Settings</span>
            </button>
            <button onClick={handleLogout} className="header-btn danger">Logout</button>
          </div>
        </div>
      </header>

      <div className="dashboard-content">
        {/* Professional CTA Section */}
        <div className="cta-section">
          <div className="cta-card">
            <div className="cta-card-content">
              <div className="cta-text">
                <h2 className="cta-title">Create New Cost Estimate</h2>
                <p className="cta-subtitle">Professional cost analysis in 90 seconds</p>
              </div>
              <div className="cta-actions">
                {projects.length >= 2 && (
                  <button
                    onClick={toggleComparisonMode}
                    className={`btn-secondary ${isComparisonMode ? 'active' : ''}`}
                  >
                    <span>📊</span>
                    <span>{isComparisonMode ? 'Exit Compare' : 'Compare Scenarios'}</span>
                  </button>
                )}
                <button 
                  onClick={() => navigate('/scope/new')}
                  className="btn-primary"
                >
                  + New Estimate
                </button>
              </div>
            </div>
          </div>
        </div>

        {deleteMessage && (
          <div className={`message ${deleteMessage.includes('successfully') ? 'success' : 'error'}`}>
            {deleteMessage}
          </div>
        )}

        <div className="projects-section">
          <div className="section-header">
            <h2>Recent Projects</h2>
            {projects.length > 0 && (
              <span className="project-count">{projects.length} project{projects.length !== 1 ? 's' : ''}</span>
            )}
          </div>
          {loading ? (
            <div className="loading-state">
              <div className="spinner"></div>
              <p>Loading your projects...</p>
            </div>
          ) : projects.length === 0 ? (
            <div className="empty-state">
              <p className="empty-message">No projects yet</p>
              <p className="empty-hint">Start with a quick template below or create a custom estimate</p>
            </div>
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
                  // Only show $/SF for contractor view (no per-unit metrics)
                  const costPerSF = project.square_footage ? project.total_cost / project.square_footage : 0;
                  
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
                  <div className="project-badges">
                    <span className="project-type-badge">
                      {getDisplayBuildingType(project.scope_data?.request_data || {
                        project_type: project.project_type,
                        occupancy_type: project.occupancy_type || project.building_type
                      })}
                    </span>
                    {project.project_classification === 'addition' && <span className="classification-tag addition">Addition</span>}
                    {project.project_classification === 'renovation' && <span className="classification-tag renovation">Renovation</span>}
                  </div>
                  
                  <div className="project-details">
                    <p className="project-location">{project.location}</p>
                    <p className="project-size">{formatNumber(project.square_footage)} SF</p>
                  </div>
                  
                  <div className="project-metrics">
                    <div className="metric-primary">
                      <span className="metric-label">COST PER SQ FT</span>
                      <span className="metric-value">{formatCurrencyPerSF(costPerSF)}</span>
                    </div>
                    <div className="metric-total">
                      <span className="metric-label">TOTAL PROJECT</span>
                      <span className="metric-value">{formatCurrency(project.total_cost)}</span>
                    </div>
                  </div>
                  <div className="project-footer">
                    <p className="project-date">
                      Created {new Date(project.created_at).toLocaleDateString()}
                    </p>
                    <div className="project-actions-footer">
                      <button
                        className="action-link"
                        onClick={(e) => {
                          e.stopPropagation();
                          navigate(`/project/${project.project_id}`);
                        }}
                      >
                        View Details →
                      </button>
                    </div>
                  </div>
                    </div>
                  );
                })}
              </div>
            </>
          )}
        </div>
        
        {/* Quick Start Templates Section */}
        <div className="templates-section">
          <div className="section-header">
            <h2>Quick Start Templates</h2>
            <span className="template-hint">Start with a pre-configured template</span>
          </div>
          <div className="templates-grid">
            {quickTemplates.map((template) => (
              <button
                key={template.name}
                className="template-card"
                style={{
                  background: template.bgColor,
                  borderColor: template.borderColor
                }}
                onClick={() => navigate('/scope/new', { state: { 
                  templateData: template.formData,
                  naturalLanguageInput: template.naturalLanguage,
                  templateName: template.name
                } })}
              >
                <span className="template-icon">{template.icon}</span>
                <span className="template-name">{template.name}</span>
              </button>
            ))}
          </div>
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
      {showMarkupSettings && (
        <Suspense fallback={<ModalLoading />}>
          <MarkupSettings
            isOpen={showMarkupSettings}
            onClose={() => setShowMarkupSettings(false)}
            onSave={() => {
              // Optionally reload projects to reflect new markup calculations
              loadProjects();
            }}
          />
        </Suspense>
      )}

      {/* Team Settings Modal */}
      {showTeamSettings && (
        <Suspense fallback={<ModalLoading />}>
          <TeamSettings
            isOpen={showTeamSettings}
            onClose={() => setShowTeamSettings(false)}
          />
        </Suspense>
      )}
    </div>
  );
}

export default Dashboard;