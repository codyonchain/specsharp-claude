import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { useState, useEffect, lazy, Suspense } from 'react';
import './App.css';
import { logger } from '@/utils/logger';

// Eager load critical components
import Login from './components/Login';
// import LoginDebug from './components/LoginDebug';  // Debug version available if needed
import { HomePage } from './pages/HomePage';

// Lazy load heavy and non-critical components
const Dashboard = lazy(() => import('./components/Dashboard'));
const ScopeGenerator = lazy(() => import('./components/ScopeGenerator'));
const ProjectDetail = lazy(() => import('./components/ProjectDetail'));
const ProgressiveProjectDetail = lazy(() => import('./components/ProgressiveProjectDetail'));
const SharedProjectView = lazy(() => import('./components/SharedProjectView'));
const ComparisonPage = lazy(() => import('./pages/ComparisonPage'));
const DemoPage = lazy(() => import('./pages/DemoPage').then(m => ({ default: m.DemoPage })));

// Lazy load policy pages (rarely accessed)
const TermsOfService = lazy(() => import('./pages/TermsOfService').then(m => ({ default: m.TermsOfService })));
const PrivacyPolicy = lazy(() => import('./pages/PrivacyPolicy').then(m => ({ default: m.PrivacyPolicy })));
const CookiePolicy = lazy(() => import('./pages/CookiePolicy').then(m => ({ default: m.CookiePolicy })));
const PricingPage = lazy(() => import('./pages/PricingPage').then(m => ({ default: m.PricingPage })));
const FAQPage = lazy(() => import('./pages/FAQPage').then(m => ({ default: m.FAQPage })));

// Loading fallback component
const LoadingFallback = () => (
  <div style={{ 
    padding: '40px', 
    textAlign: 'center',
    minHeight: '100vh',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    flexDirection: 'column'
  }}>
    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900"></div>
    <p style={{ marginTop: '16px', color: '#666' }}>Loading...</p>
  </div>
);

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check for OAuth token in URL
    const urlParams = new URLSearchParams(window.location.search);
    const tokenFromUrl = urlParams.get('token');
    
    if (tokenFromUrl) {
      // Store the token and remove it from URL
      localStorage.setItem('token', tokenFromUrl);
      window.history.replaceState({}, document.title, window.location.pathname);
      setIsAuthenticated(true);
      setLoading(false);
      return;
    }
    
    // Check for existing authentication
    const token = localStorage.getItem('token');
    const hasCookie = document.cookie.includes('access_token');
    setIsAuthenticated(!!token || hasCookie);
    setLoading(false);
    logger.log('App loaded, authenticated:', !!token || hasCookie);
    logger.log('Current path:', window.location.pathname);
  }, []);

  if (loading) {
    return <div style={{ padding: '20px', textAlign: 'center' }}>Loading...</div>;
  }

  return (
    <Router>
      <div className="App">
        <Suspense fallback={<LoadingFallback />}>
          <Routes>
            <Route 
              path="/login" 
              element={
                isAuthenticated ? 
                <Navigate to="/dashboard" /> : 
                <Login setIsAuthenticated={setIsAuthenticated} />
              } 
            />
            <Route 
              path="/dashboard" 
              element={
                isAuthenticated ? 
                <Dashboard setIsAuthenticated={setIsAuthenticated} /> : 
                <Navigate to="/login" />
              } 
            />
            <Route 
              path="/scope/new" 
              element={
                isAuthenticated ? 
                <ScopeGenerator /> : 
                <Navigate to="/login" />
              } 
            />
            <Route 
              path="/project/:projectId" 
              element={
                isAuthenticated ? 
                <ProgressiveProjectDetail /> : 
                <Navigate to="/login" />
              } 
            />
            <Route 
              path="/compare" 
              element={
                isAuthenticated ? 
                <ComparisonPage /> : 
                <Navigate to="/login" />
              } 
            />
            {/* Public routes */}
            <Route path="/" element={<HomePage />} />
            <Route path="/demo" element={<DemoPage />} />
            <Route path="/share/:shareId" element={<SharedProjectView />} />
            <Route path="/terms" element={<TermsOfService />} />
            <Route path="/privacy" element={<PrivacyPolicy />} />
            <Route path="/cookies" element={<CookiePolicy />} />
            <Route path="/pricing" element={<PricingPage />} />
            <Route path="/faq" element={<FAQPage />} />
            
            {/* App routes - redirect to appropriate page based on auth */}
            <Route 
              path="/app" 
              element={
                isAuthenticated ? 
                <Navigate to="/dashboard" /> : 
                <Navigate to="/login" />
              } 
            />
          </Routes>
        </Suspense>
      </div>
    </Router>
  );
}

export default App;