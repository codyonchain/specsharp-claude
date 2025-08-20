import React, { Suspense, useEffect, useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { LoadingSpinner } from './components/common/LoadingSpinner';

// V2 Pages
import { Dashboard } from './pages/Dashboard/Dashboard';
import { NewProject } from './pages/NewProject/NewProject';
import { ProjectView } from './pages/ProjectView/ProjectView';
import { Diagnostics } from './pages/Diagnostics';

// Import the existing HomePage from the main src/pages
import { HomePage } from '../pages/HomePage';

// Import Login component from V1
import Login from '../components/Login';

// Import diagnostics (auto-loads into window.diagnose)
import './utils/diagnostics';

export const App: React.FC = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check for existing authentication in localStorage
    const token = localStorage.getItem('token');
    const hasCookie = document.cookie.includes('access_token');
    setIsAuthenticated(!!token || hasCookie);
    setLoading(false);
  }, []);

  if (loading) {
    return <LoadingSpinner size="large" message="Checking authentication..." />;
  }

  return (
    <Router>
      <Suspense fallback={<LoadingSpinner size="large" message="Loading..." />}>
        <Routes>
          {/* Homepage - always accessible */}
          <Route path="/" element={<HomePage />} />
          
          {/* Login route - auto-redirect to dashboard if already authenticated */}
          <Route 
            path="/login" 
            element={
              isAuthenticated ? 
              <Navigate to="/dashboard" replace /> : 
              <Login setIsAuthenticated={setIsAuthenticated} />
            } 
          />
          
          {/* Protected V2 routes */}
          <Route 
            path="/dashboard" 
            element={
              isAuthenticated ? 
              <Dashboard /> : 
              <Navigate to="/login" replace />
            } 
          />
          <Route 
            path="/new" 
            element={
              isAuthenticated ? 
              <NewProject /> : 
              <Navigate to="/login" replace />
            } 
          />
          <Route 
            path="/project/:id" 
            element={
              isAuthenticated ? 
              <ProjectView /> : 
              <Navigate to="/login" replace />
            } 
          />
          
          {/* Diagnostics route - for debugging */}
          <Route 
            path="/diagnostics" 
            element={
              isAuthenticated ? 
              <Diagnostics /> : 
              <Navigate to="/login" replace />
            } 
          />
          
          {/* Signup route - same as login for now */}
          <Route 
            path="/signup" 
            element={
              isAuthenticated ? 
              <Navigate to="/dashboard" replace /> : 
              <Login setIsAuthenticated={setIsAuthenticated} />
            } 
          />
          
          {/* Fallback - redirect to dashboard if authenticated, otherwise to homepage */}
          <Route path="*" element={isAuthenticated ? <Navigate to="/dashboard" replace /> : <Navigate to="/" replace />} />
        </Routes>
      </Suspense>
    </Router>
  );
};

export default App;