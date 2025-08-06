import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';

function AppEmergency() {
  console.log('[EMERGENCY APP] Running with NO AUTH CHECKS');
  
  return (
    <Router>
      <Routes>
        <Route path="/" element={<div>Home - NO AUTH</div>} />
        <Route path="/test-page" element={<div>Test Page - NO AUTH</div>} />
        <Route path="/login" element={<div>Login Page - NO AUTH</div>} />
        <Route path="/dashboard" element={<div>Dashboard - NO AUTH CHECKS AT ALL</div>} />
        <Route path="*" element={<div>404 - NO AUTH</div>} />
      </Routes>
    </Router>
  );
}

export default AppEmergency;