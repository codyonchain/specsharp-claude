import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { useState, useEffect } from 'react';
import './App.css';
import Login from './components/Login';
import Dashboard from './components/Dashboard';
import ScopeGenerator from './components/ScopeGenerator';
import ProjectDetail from './components/ProjectDetail';
import ProgressiveProjectDetail from './components/ProgressiveProjectDetail';
import SharedProjectView from './components/SharedProjectView';
import ComparisonPage from './pages/ComparisonPage';
import { HomePage } from './pages/HomePage';
import { DemoPage } from './pages/DemoPage';
import { TermsOfService } from './pages/TermsOfService';
import { PrivacyPolicy } from './pages/PrivacyPolicy';
import { CookiePolicy } from './pages/CookiePolicy';
import { PricingPage } from './pages/PricingPage';
import { FAQPage } from './pages/FAQPage';

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
    console.log('App loaded, authenticated:', !!token || hasCookie);
    console.log('Current path:', window.location.pathname);
  }, []);

  if (loading) {
    return <div style={{ padding: '20px', textAlign: 'center' }}>Loading...</div>;
  }

  return (
    <Router>
      <div className="App">
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
      </div>
    </Router>
  );
}

export default App;