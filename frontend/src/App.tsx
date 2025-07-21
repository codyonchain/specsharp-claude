import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { useState, useEffect } from 'react';
import './App.css';
import Login from './components/Login';
import Dashboard from './components/Dashboard';
import ScopeGenerator from './components/ScopeGenerator';
import ProjectDetail from './components/ProjectDetail';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('token');
    setIsAuthenticated(!!token);
    setLoading(false);
    console.log('App loaded, authenticated:', !!token);
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
              <ProjectDetail /> : 
              <Navigate to="/login" />
            } 
          />
          <Route path="/" element={<Navigate to="/dashboard" />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;