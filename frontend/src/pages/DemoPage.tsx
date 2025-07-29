import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { Clock, Sparkles, ArrowRight, CheckCircle } from 'lucide-react';
import { demoService, authService } from '../services/api';
import { formatCurrency, formatCurrencyPerSF } from '../utils/formatters';
import { Footer } from '../components/Footer';
import './DemoPage.css';

interface SignupBannerProps {
  onSignup: (email: string, password: string) => void;
  isLoading: boolean;
  error: string | null;
  onDismiss?: () => void;
  estimatesRemaining?: number;
  isDismissible?: boolean;
}

const SignupBanner: React.FC<SignupBannerProps> = ({ 
  onSignup, 
  isLoading, 
  error, 
  onDismiss,
  estimatesRemaining = 2,
  isDismissible = true 
}) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isExpanded, setIsExpanded] = useState(!isDismissible); // Auto-expand if not dismissible

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSignup(email, password);
  };

  const getBannerMessage = () => {
    if (estimatesRemaining === 0) {
      return <strong>You've used all 3 free estimates. Sign up to continue.</strong>;
    } else if (estimatesRemaining === 1) {
      return <><strong>Wow! You just saved 3 hours.</strong> Create 1 more free estimate →</>;
    } else {
      return <><strong>Wow! You just saved 3 hours.</strong> Create {estimatesRemaining} more free estimates →</>;
    }
  };

  if (!isExpanded && isDismissible) {
    return (
      <div className="signup-banner-collapsed">
        <div className="banner-content">
          <div className="banner-left">
            <Sparkles className="sparkle-icon-small" />
            <span className="banner-text">
              {getBannerMessage()}
            </span>
          </div>
          <div className="banner-actions">
            <button 
              className="expand-button"
              onClick={() => setIsExpanded(true)}
            >
              Sign Up
            </button>
            {onDismiss && (
              <button 
                className="dismiss-button"
                onClick={onDismiss}
                aria-label="Dismiss"
              >
                ✕
              </button>
            )}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="signup-banner-expanded">
      {isDismissible && (
        <button 
          className="collapse-button"
          onClick={() => setIsExpanded(false)}
          aria-label="Collapse"
        >
          ↓
        </button>
      )}
      
      <div className="banner-header">
        <Sparkles className="sparkle-icon" />
        <h3>
          {estimatesRemaining === 0 
            ? 'Sign up to continue creating estimates'
            : `Create ${estimatesRemaining} more estimate${estimatesRemaining === 1 ? '' : 's'} free - sign up in 10 seconds`
          }
        </h3>
      </div>
      
      <form onSubmit={handleSubmit} className="banner-form">
        <input
          type="email"
          placeholder="Your email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
          autoFocus
          className="banner-input"
        />
        <input
          type="password"
          placeholder="Choose a password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          minLength={6}
          className="banner-input"
        />
        
        <button type="submit" disabled={isLoading} className="banner-submit">
          {isLoading ? 'Creating...' : 'Continue →'}
        </button>
      </form>
      
      {error && <div className="banner-error">{error}</div>}
      
      <p className="banner-note">
        No credit card required • 3 free estimates total
      </p>
    </div>
  );
};

export const DemoPage: React.FC = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [description, setDescription] = useState('4000 sf full-service restaurant with commercial kitchen, dining room, bar, and bathrooms in Manchester, New Hampshire');
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedProject, setGeneratedProject] = useState<any>(null);
  const [showSignup, setShowSignup] = useState(false);
  const [signupError, setSignupError] = useState<string | null>(null);
  const [isSigningUp, setIsSigningUp] = useState(false);
  const [timeSaved, setTimeSaved] = useState(0);
  const [estimatesUsed, setEstimatesUsed] = useState(0);
  const [estimatesRemaining, setEstimatesRemaining] = useState(3);
  const [limitReached, setLimitReached] = useState(false);
  const [showLimitModal, setShowLimitModal] = useState(false);
  
  const testMode = searchParams.get('test') === 'true';
  const isAuthenticated = authService.isAuthenticated();

  useEffect(() => {
    // Check if user is already authenticated and redirect to main app
    // Allow bypass with ?test=true for developer testing
    if (isAuthenticated && !testMode) {
      navigate('/app');
      return;
    }
    
    // Auto-focus the generate button on mount
    const generateBtn = document.getElementById('generate-btn');
    generateBtn?.focus();
  }, [navigate, searchParams, isAuthenticated, testMode]);

  const handleGenerateScope = async () => {
    setIsGenerating(true);
    const startTime = Date.now();
    
    try {
      // Call demo endpoint (no auth required)
      const response = await demoService.generateDemoScope({
        description,
        is_demo: true
      });
      
      setGeneratedProject(response);
      
      // Update estimate counts
      if (response.estimates_used) {
        setEstimatesUsed(response.estimates_used);
        setEstimatesRemaining(response.estimates_remaining);
      }
      
      // Calculate time saved (mock 3 hours)
      const generationTime = (Date.now() - startTime) / 1000;
      setTimeSaved(3 * 60 * 60 - generationTime); // 3 hours minus actual time
      
      // Scroll to results
      setTimeout(() => {
        document.getElementById('results-section')?.scrollIntoView({ 
          behavior: 'smooth',
          block: 'start'
        });
      }, 100);
      
      // Show signup prompt based on estimates used
      if (response.estimates_remaining === 0) {
        // Last free estimate - disable form but delay modal to let user see results
        setLimitReached(true);
        // Delay modal by 5 seconds to let user explore the results
        setTimeout(() => {
          setShowLimitModal(true);
        }, 5000);
      } else {
        // Still have estimates left - show dismissible banner after delay
        setTimeout(() => {
          setShowSignup(true);
        }, 7000);
      }
      
    } catch (error: any) {
      console.error('Failed to generate demo scope:', error);
      console.error('Error response:', error.response);
      console.error('Error details:', {
        status: error.response?.status,
        statusText: error.response?.statusText,
        data: error.response?.data,
        headers: error.response?.headers
      });
      
      // Check if it's a limit reached error
      if (error.response?.status === 403 && error.response?.data?.error === 'demo_limit_reached') {
        setLimitReached(true);
        setShowLimitModal(true);
        setEstimatesUsed(error.response.data.estimates_used);
        setEstimatesRemaining(0);
      } else {
        const errorMessage = error.response?.data?.detail || error.message || 'Unknown error';
        alert(`Failed to generate estimate: ${errorMessage}\nStatus: ${error.response?.status || 'No response'}`);
      }
    } finally {
      setIsGenerating(false);
    }
  };

  const handleQuickSignup = async (email: string, password: string) => {
    if (!email || !password) {
      return;
    }
    
    setIsSigningUp(true);
    setSignupError(null);
    
    try {
      // Create account
      await demoService.quickSignup({
        email,
        password,
        demo_project_id: generatedProject?.project_id
      });
      
      // Navigate to dashboard with onboarding continuation
      navigate('/app?continue_demo=true');
      
    } catch (error: any) {
      setSignupError(error.response?.data?.detail || 'Signup failed. Please try again.');
    } finally {
      setIsSigningUp(false);
    }
  };

  const handleDismissBanner = () => {
    setShowSignup(false);
  };

  const formatTime = (seconds: number) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    return `${hours} hours ${minutes} minutes`;
  };

  return (
    <div className="demo-page">
      {/* Test Mode Indicator */}
      {testMode && isAuthenticated && (
        <div style={{
          position: 'fixed',
          top: '10px',
          right: '10px',
          background: '#fbbf24',
          color: '#1f2937',
          padding: '8px 12px',
          borderRadius: '6px',
          fontSize: '12px',
          fontWeight: '600',
          zIndex: 1001,
          boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
        }}>
          🧪 TEST MODE - Authenticated user testing demo
        </div>
      )}
      
      {/* Header */}
      <nav className="demo-nav">
        <div className="nav-container">
          <div className="logo" onClick={() => navigate('/')}>
            SpecSharp
          </div>
          <div className="nav-links">
            <a href="/" className="nav-link">Home</a>
            <a href="/login" className="nav-link">Login</a>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="demo-hero">
        <div className="hero-content">
          <h1 className="hero-title">
            See How SpecSharp Creates Professional Estimates in Seconds
          </h1>
          <p className="hero-subtitle">
            No signup required. Just click generate and watch the magic happen.
          </p>
        </div>
      </section>

      {/* Demo Form */}
      <section className="demo-form-section">
        <div className="demo-container">
          <div className="demo-form-card">
            {estimatesUsed > 0 && (
              <div className="estimates-counter">
                <span className="counter-text">
                  {estimatesRemaining > 0 
                    ? `${estimatesRemaining} free estimate${estimatesRemaining === 1 ? '' : 's'} remaining`
                    : 'All free estimates used'
                  }
                </span>
              </div>
            )}
            
            {!limitReached ? (
              <>
                <label className="form-label">
                  Describe your project (or use our example):
                </label>
                <textarea
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  className="demo-textarea"
                  rows={3}
                  placeholder="e.g., 200 room hotel with conference center in Nashville, Tennessee"
                />
                
                <button
                  id="generate-btn"
                  onClick={handleGenerateScope}
                  disabled={isGenerating || !description.trim()}
                  className={`generate-button ${isGenerating ? 'generating' : ''}`}
                >
                  {isGenerating ? (
                    <>
                      <div className="spinner" />
                      Generating Detailed Scope...
                    </>
                  ) : (
                    <>
                      <Sparkles className="button-icon" />
                      Generate Scope
                    </>
                  )}
                </button>
                
                <p className="demo-note">
                  This normally takes estimators 3+ hours. Watch it happen in 90 seconds.
                </p>
              </>
            ) : (
              <div className="limit-reached-section">
                <div className="limit-message">
                  <h3>🎉 You've created 3 amazing estimates!</h3>
                  <p>Ready to unlock the full power of professional cost estimation?</p>
                </div>
                <button
                  onClick={() => setShowLimitModal(true)}
                  className="signup-cta-button"
                >
                  <ArrowRight className="button-icon" />
                  Sign Up to Continue
                </button>
                <p className="demo-note">
                  Join thousands of contractors saving 3+ hours per estimate.
                </p>
              </div>
            )}
          </div>
        </div>
      </section>

      {/* Results Section */}
      {generatedProject && (
        <section id="results-section" className="results-section">
          {/* Time Saved Banner */}
          <div className="time-saved-banner">
            <Clock className="time-icon" />
            <span className="time-text">
              You just saved <strong>{formatTime(timeSaved)}</strong> of work!
            </span>
            <span className="time-value">
              That's worth <strong>${Math.round(timeSaved / 3600 * 75)}</strong> at $75/hour
            </span>
          </div>

          <div className="results-container">
            <div className="results-header">
              <h2>{generatedProject.project_name}</h2>
              <div className="project-meta">
                <span className="meta-item">
                  {generatedProject.square_footage?.toLocaleString()} SF
                </span>
                <span className="meta-item">
                  {generatedProject.num_floors} Floors
                </span>
                <span className="meta-item">
                  {generatedProject.location}
                </span>
              </div>
            </div>

            <div className="cost-summary">
              <div className="total-cost">
                <label>Total Project Cost</label>
                <div className="cost-value">{formatCurrency(generatedProject.total_cost || 0)}</div>
                <div className="cost-per-sf">{formatCurrencyPerSF(generatedProject.cost_per_sqft || 0)}</div>
              </div>
              <div className="cost-note">
                <small>
                  <strong>Note:</strong> Demo shows base construction costs. 
                  Registered users can add their overhead & profit margins (typically 10-20%).
                </small>
              </div>
            </div>

            <div className="trade-breakdown">
              <h3>Trade Breakdown</h3>
              <div className="trades-grid">
                {generatedProject.categories?.map((category: any) => (
                  <div key={category.name} className="trade-card">
                    <div className="trade-name">{category.name}</div>
                    <div className="trade-cost">{formatCurrency(category.subtotal || 0)}</div>
                    <div className="trade-percentage">
                      {((category.subtotal / generatedProject.total_cost) * 100).toFixed(1)}%
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="demo-features">
              <h3>In the full version you also get:</h3>
              <div className="features-list">
                <div className="feature-item">
                  <CheckCircle className="feature-icon" />
                  <span>200+ detailed line items with quantities</span>
                </div>
                <div className="feature-item">
                  <CheckCircle className="feature-icon" />
                  <span>Excel export with formulas</span>
                </div>
                <div className="feature-item">
                  <CheckCircle className="feature-icon" />
                  <span>Professional PDF reports</span>
                </div>
                <div className="feature-item">
                  <CheckCircle className="feature-icon" />
                  <span>Shareable links for clients</span>
                </div>
                <div className="feature-item">
                  <CheckCircle className="feature-icon" />
                  <span>Regional pricing adjustments</span>
                </div>
              </div>
            </div>
          </div>
        </section>
      )}

      {/* Signup Banner - Dismissible */}
      {showSignup && !showLimitModal && (
        <SignupBanner
          onSignup={handleQuickSignup}
          isLoading={isSigningUp}
          error={signupError}
          onDismiss={handleDismissBanner}
          estimatesRemaining={estimatesRemaining}
          isDismissible={true}
        />
      )}
      
      {/* Signup Modal - Dismissible with close button */}
      {showLimitModal && (
        <div className="modal-overlay" onClick={() => setShowLimitModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <button 
              className="modal-close"
              onClick={() => setShowLimitModal(false)}
              aria-label="Close modal"
            >
              ×
            </button>
            <SignupBanner
              onSignup={handleQuickSignup}
              isLoading={isSigningUp}
              error={signupError}
              estimatesRemaining={0}
              isDismissible={true}
              onDismiss={() => setShowLimitModal(false)}
            />
          </div>
        </div>
      )}

      <Footer />
    </div>
  );
};