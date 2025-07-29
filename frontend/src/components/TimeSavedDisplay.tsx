import React from 'react';
import { Clock, DollarSign } from 'lucide-react';
import './TimeSavedDisplay.css';

interface TimeSavedDisplayProps {
  generationTimeSeconds?: number;
  hourlyRate?: number;
}

const TimeSavedDisplay: React.FC<TimeSavedDisplayProps> = ({ 
  generationTimeSeconds, 
  hourlyRate = 75 
}) => {
  // Default generation time if not provided
  const actualGenerationTime = generationTimeSeconds || 2;
  
  // Manual estimation typically takes 3 hours
  const manualHours = 3;
  const manualMinutes = manualHours * 60;
  
  // Calculate time saved
  const timeSavedMinutes = manualMinutes - (actualGenerationTime / 60);
  const timeSavedHours = timeSavedMinutes / 60;
  
  // Calculate dollar value saved
  const dollarsSaved = timeSavedHours * hourlyRate;
  
  // Format display values
  const formatTime = (hours: number) => {
    if (hours >= 1) {
      const h = Math.floor(hours);
      const m = Math.round((hours - h) * 60);
      return m > 0 ? `${h} hour${h > 1 ? 's' : ''} ${m} min` : `${h} hour${h > 1 ? 's' : ''}`;
    } else {
      const m = Math.round(hours * 60);
      return `${m} minute${m !== 1 ? 's' : ''}`;
    }
  };
  
  return (
    <div className="time-saved-container">
      <div className="time-saved-card">
        <div className="time-saved-header">
          <Clock size={24} className="time-icon" />
          <h3>Time Saved</h3>
        </div>
        
        <div className="time-saved-content">
          <div className="time-comparison">
            <div className="time-item manual">
              <span className="time-label">Manual Estimation</span>
              <span className="time-value">~3 hours</span>
            </div>
            <div className="time-arrow">→</div>
            <div className="time-item actual">
              <span className="time-label">SpecSharp</span>
              <span className="time-value">{actualGenerationTime} seconds</span>
            </div>
          </div>
          
          <div className="savings-summary">
            <div className="savings-item">
              <span className="savings-label">Time Saved</span>
              <span className="savings-value time">{formatTime(timeSavedHours)}</span>
            </div>
            <div className="savings-divider"></div>
            <div className="savings-item">
              <DollarSign size={20} className="dollar-icon" />
              <span className="savings-label">Value</span>
              <span className="savings-value money">${dollarsSaved.toFixed(2)}</span>
              <span className="savings-rate">at ${hourlyRate}/hour</span>
            </div>
          </div>
        </div>
        
        <div className="time-saved-footer">
          This estimate would take ~3 hours manually. You did it in {actualGenerationTime} seconds.
        </div>
      </div>
    </div>
  );
};

export default TimeSavedDisplay;