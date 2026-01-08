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

  const resolveProjectId = (project: any): string | undefined => project?.id || project?.project_id;

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
      {/* Executive Dashboard Header */}
      <header className="bg-gradient-to-r from-gray-900 to-gray-800 shadow-xl">
        <div className="max-w-7xl mx-auto px-6 py-8">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold text-white">Cost Estimates</h1>
              <p className="text-gray-400 mt-1">Early-stage feasibility analysis and cost validation</p>
            </div>
            <div className="flex items-center gap-3">
              <button onClick={() => setShowTeamSettings(true)} className="flex items-center gap-2 px-4 py-2 bg-gray-700 text-gray-300 rounded-lg hover:bg-gray-600 transition-colors">
                <Users size={18} />
                <span>Team</span>
              </button>
              <button onClick={() => setShowMarkupSettings(true)} className="flex items-center gap-2 px-4 py-2 bg-gray-700 text-gray-300 rounded-lg hover:bg-gray-600 transition-colors">
                <Settings size={18} />
                <span>Settings</span>
              </button>
              <button onClick={handleLogout} className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors">
                Logout
              </button>
            </div>
          </div>
        </div>
      </header>

      <div className="dashboard-content">
        <div className="max-w-7xl mx-auto px-6 py-6">

          {/* Action Section */}
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-2xl font-bold text-gray-900">Recent Estimates</h2>
            <div className="flex gap-3">
              {projects.length >= 2 && (
                <button
                  onClick={toggleComparisonMode}
                  className={`flex items-center gap-2 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors ${isComparisonMode ? 'bg-blue-100 text-blue-700' : ''}`}
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                  <span>{isComparisonMode ? 'Exit Compare' : 'Compare Scenarios'}</span>
                </button>
              )}
              <button 
                onClick={() => navigate('/scope/new')}
                className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                </svg>
                New Estimate
              </button>
            </div>
          </div>
        </div>

        {deleteMessage && (
          <div className={`message ${deleteMessage.includes('successfully') ? 'success' : 'error'}`}>
            {deleteMessage}
          </div>
        )}

        <div className="projects-section max-w-7xl mx-auto px-6">
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
                  const projectId = resolveProjectId(project);
                  if (!projectId) {
                    return null;
                  }
                  // Calculate total investment (including soft costs)
                  const totalInvestment = project.total_cost * 1.46; // Assuming 46% soft costs average
                  const constructionCost = project.total_cost;
                  const costPerSF = project.square_footage ? totalInvestment / project.square_footage : 0;
                  
                  return (
                    <div 
                      key={projectId} 
                      className={`bg-white rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 overflow-hidden group cursor-pointer ${isComparisonMode && selectedForComparison.includes(projectId) ? 'ring-2 ring-blue-500' : ''}`}
                      onClick={() => {
                        if (isComparisonMode) {
                          toggleComparisonSelection(projectId);
                        } else {
                          navigate(`/project/${projectId}`);
                        }
                      }}
                    >
                      {/* Gradient Header Bar */}
                      <div className="h-1 bg-gradient-to-r from-blue-600 to-indigo-600"></div>
                      
                      <div className="p-6">
                        {/* Header with Title and Actions */}
                        <div className="flex justify-between items-start mb-4">
                          <div className="flex-1">
                            {isComparisonMode && (
                              <div className="mb-2">
                                {selectedForComparison.includes(projectId) ? (
                                  <span className="inline-flex items-center px-2 py-1 text-xs font-medium bg-blue-100 text-blue-700 rounded">✓ Selected</span>
                                ) : (
                                  <span className="inline-flex items-center px-2 py-1 text-xs font-medium bg-gray-100 text-gray-600 rounded">Click to select</span>
                                )}
                              </div>
                            )}
                            <h3 className="text-lg font-bold text-gray-900 group-hover:text-blue-600 transition-colors">
                              {project.name || project.description || `${formatNumber(project.square_footage)} SF ${getDisplayBuildingType(project.scope_data?.request_data || {})}`}
                            </h3>
                            <div className="flex items-center gap-3 mt-1">
                              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                                {getDisplayBuildingType(project.scope_data?.request_data || {
                                  project_type: project.project_type,
                                  occupancy_type: project.occupancy_type || project.building_type
                                })}
                              </span>
                              <span className="text-xs text-gray-500">{project.location}</span>
                              {project.project_classification === 'addition' && <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-amber-100 text-amber-800">Addition</span>}
                              {project.project_classification === 'renovation' && <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-purple-100 text-purple-800">Renovation</span>}
                            </div>
                          </div>
                          <div className="flex gap-1" onClick={(e) => e.stopPropagation()}>
                            <button 
                              className="p-1.5 text-gray-400 hover:text-gray-600 transition-colors"
                              onClick={(e) => handleDuplicateClick(e, projectId, project.name)}
                              title="Duplicate project"
                            >
                              <Copy size={16} />
                            </button>
                            <button 
                              className="p-1.5 text-gray-400 hover:text-red-600 transition-colors"
                              onClick={(e) => handleDeleteClick(e, projectId, project.name)}
                              title="Delete project"
                            >
                              <Trash2 size={16} />
                            </button>
                          </div>
                        </div>
                        {/* Key Metrics Grid */}
                        <div className="space-y-3">
                          {/* Construction Cost */}
                          <div className="flex justify-between items-center py-2 border-b border-gray-100">
                            <div className="flex items-center gap-2">
                              <div className="w-8 h-8 bg-gray-100 rounded-lg flex items-center justify-center">
                                <svg className="w-4 h-4 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                                </svg>
                              </div>
                              <span className="text-sm text-gray-600">Construction</span>
                            </div>
                            <span className="text-lg font-bold text-gray-900">
                              ${(constructionCost / 1000000).toFixed(1)}M
                            </span>
                          </div>

                          {/* Total Investment */}
                          <div className="flex justify-between items-center py-2 border-b border-gray-100">
                            <div className="flex items-center gap-2">
                              <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center">
                                <svg className="w-4 h-4 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                                </svg>
                              </div>
                              <span className="text-sm text-gray-600">Total Investment</span>
                            </div>
                            <span className="text-lg font-bold text-blue-600">
                              ${(totalInvestment / 1000000).toFixed(1)}M
                            </span>
                          </div>

                          {/* Square Footage */}
                          <div className="flex justify-between items-center py-2">
                            <div className="flex items-center gap-2">
                              <div className="w-8 h-8 bg-green-100 rounded-lg flex items-center justify-center">
                                <svg className="w-4 h-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4" />
                                </svg>
                              </div>
                              <span className="text-sm text-gray-600">Size</span>
                            </div>
                            <span className="text-sm font-medium text-gray-700">
                              {(project.square_footage / 1000).toFixed(0)}K SF
                            </span>
                          </div>
                        </div>

                        {/* Footer with Date and Action */}
                        <div className="flex justify-between items-center mt-4 pt-4 border-t border-gray-100">
                          <span className="text-xs text-gray-500">
                            Created {new Date(project.created_at).toLocaleDateString()}
                          </span>
                          <div 
                            className="inline-flex items-center gap-1 text-sm font-medium text-blue-600 hover:text-blue-700 transition-colors"
                            onClick={(e) => e.stopPropagation()}
                          >
                            View Details
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                            </svg>
                          </div>
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
