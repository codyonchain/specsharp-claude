import React from 'react';
import { Building2, Heart } from 'lucide-react';
import './ViewToggle.css';

interface ViewToggleProps {
  currentView: 'trade' | 'healthcare';
  onViewChange: (view: 'trade' | 'healthcare') => void;
  className?: string;
}

export const ViewToggle: React.FC<ViewToggleProps> = ({ 
  currentView, 
  onViewChange, 
  className 
}) => {
  return (
    <div className={`view-toggle ${className || ''}`}>
      <button
        onClick={() => onViewChange('trade')}
        className={`toggle-button ${currentView === 'trade' ? 'active' : ''}`}
      >
        <Building2 style={{ marginRight: '8px', height: '16px', width: '16px' }} />
        Trade Breakdown
      </button>
      <button
        onClick={() => onViewChange('healthcare')}
        className={`toggle-button ${currentView === 'healthcare' ? 'active' : ''}`}
      >
        <Heart style={{ marginRight: '8px', height: '16px', width: '16px' }} />
        Healthcare View
      </button>
    </div>
  );
};