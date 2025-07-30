import React, { useEffect, useState } from 'react';

interface OAuthDebugInfo {
  timestamp: string;
  apiUrl: string;
  fullOAuthUrl: string;
  env: string;
  origin: string;
}

export const OAuthDebugger: React.FC = () => {
  const [debugInfo, setDebugInfo] = useState<OAuthDebugInfo | null>(null);
  const [currentInfo, setCurrentInfo] = useState<any>({});

  useEffect(() => {
    // Get stored OAuth debug info
    const stored = sessionStorage.getItem('oauth_debug');
    if (stored) {
      try {
        setDebugInfo(JSON.parse(stored));
      } catch (e) {
        console.error('Failed to parse OAuth debug info:', e);
      }
    }

    // Current environment info
    setCurrentInfo({
      currentUrl: window.location.href,
      origin: window.location.origin,
      pathname: window.location.pathname,
      search: window.location.search,
      envMode: import.meta.env.MODE,
      apiUrl: import.meta.env.VITE_API_URL,
      googleClientId: import.meta.env.VITE_GOOGLE_CLIENT_ID,
      allEnvVars: Object.keys(import.meta.env).filter(key => key.startsWith('VITE_')),
    });
  }, []);

  if (!import.meta.env.DEV) {
    return null; // Only show in development
  }

  return (
    <div style={{
      position: 'fixed',
      bottom: 20,
      right: 20,
      background: 'rgba(0, 0, 0, 0.9)',
      color: 'white',
      padding: '20px',
      borderRadius: '8px',
      fontSize: '12px',
      maxWidth: '400px',
      maxHeight: '500px',
      overflow: 'auto',
      zIndex: 9999,
      fontFamily: 'monospace'
    }}>
      <h3 style={{ margin: '0 0 10px 0', color: '#4ade80' }}>OAuth Debug Panel</h3>
      
      <div style={{ marginBottom: '15px' }}>
        <h4 style={{ color: '#60a5fa', margin: '0 0 5px 0' }}>Current Environment</h4>
        <div style={{ marginLeft: '10px' }}>
          <div>Mode: {currentInfo.envMode}</div>
          <div>API URL: {currentInfo.apiUrl || 'NOT SET'}</div>
          <div>Google Client ID: {currentInfo.googleClientId ? '✓ Set' : '✗ Not Set'}</div>
          <div>Origin: {currentInfo.origin}</div>
        </div>
      </div>

      {debugInfo && (
        <div style={{ marginBottom: '15px' }}>
          <h4 style={{ color: '#60a5fa', margin: '0 0 5px 0' }}>Last OAuth Attempt</h4>
          <div style={{ marginLeft: '10px' }}>
            <div>Time: {new Date(debugInfo.timestamp).toLocaleTimeString()}</div>
            <div>API URL: {debugInfo.apiUrl}</div>
            <div>OAuth URL: {debugInfo.fullOAuthUrl}</div>
            <div>Origin: {debugInfo.origin}</div>
          </div>
        </div>
      )}

      <div style={{ marginBottom: '15px' }}>
        <h4 style={{ color: '#60a5fa', margin: '0 0 5px 0' }}>Expected OAuth Flow</h4>
        <ol style={{ margin: '5px 0 0 20px', padding: 0 }}>
          <li>Frontend: https://specsharp.ai/login</li>
          <li>→ Backend: https://api.specsharp.ai/api/v1/oauth/login/google</li>
          <li>→ Google: accounts.google.com with redirect_uri</li>
          <li>→ Backend: https://api.specsharp.ai/api/v1/oauth/callback/google</li>
          <li>→ Frontend: https://specsharp.ai/?token=...</li>
        </ol>
      </div>

      <div style={{ marginBottom: '15px' }}>
        <h4 style={{ color: '#60a5fa', margin: '0 0 5px 0' }}>URL Parameters</h4>
        <div style={{ marginLeft: '10px' }}>
          {currentInfo.search ? (
            new URLSearchParams(currentInfo.search).toString().split('&').map((param, i) => (
              <div key={i}>{param}</div>
            ))
          ) : (
            <div>No parameters</div>
          )}
        </div>
      </div>

      <button
        onClick={() => {
          sessionStorage.removeItem('oauth_debug');
          window.location.reload();
        }}
        style={{
          background: '#ef4444',
          border: 'none',
          color: 'white',
          padding: '5px 10px',
          borderRadius: '4px',
          cursor: 'pointer',
          marginTop: '10px'
        }}
      >
        Clear Debug Info
      </button>
    </div>
  );
};