import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';

// Use V2 App instead of V1
import App from './v2/App';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);