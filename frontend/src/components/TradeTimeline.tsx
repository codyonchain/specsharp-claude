import { useMemo } from 'react';
import { calculateProjectSchedule, getLongLeadItems } from '../services/schedulingEngine';
import { Clock, AlertCircle } from 'lucide-react';
import './TradeTimeline.css';

interface TradeTimelineProps {
  projectData: {
    buildingType: string;
    squareFootage: number;
    projectClassification: string;
    tradeCosts: Record<string, number>;
  };
}

function TradeTimeline({ projectData }: TradeTimelineProps) {
  const scheduleData = useMemo(() => {
    return calculateProjectSchedule(projectData);
  }, [projectData]);
  
  const longLeadWarning = useMemo(() => {
    return getLongLeadItems(projectData.buildingType);
  }, [projectData.buildingType]);

  // Create month markers for the timeline
  const monthMarkers = useMemo(() => {
    const markers = [];
    const maxMonths = Math.min(scheduleData.totalDuration, 24);
    for (let i = 0; i < maxMonths; i++) {
      if (i % 3 === 0) {
        markers.push(i + 1);
      }
    }
    return markers;
  }, [scheduleData.totalDuration]);

  return (
    <div className="trade-timeline-container">
      <div className="timeline-header">
        <div className="timeline-title-section">
          <h3 className="timeline-title">Construction Schedule</h3>
          <p className="timeline-subtitle">
            {scheduleData.totalDuration} month timeline with trade overlap
          </p>
        </div>
        <div className="timeline-summary">
          <Clock size={16} className="timeline-icon" />
          <span className="timeline-duration">{scheduleData.totalDuration} months</span>
        </div>
      </div>
      
      {/* Timeline Grid */}
      <div className="timeline-grid">
        {/* Month markers */}
        <div className="month-markers">
          <div className="timeline-label-column"></div>
          <div className="timeline-bars-column">
            <div className="month-markers-row">
              {monthMarkers.map((month) => (
                <span 
                  key={month} 
                  className="month-marker"
                  style={{ 
                    left: `${((month - 1) / scheduleData.totalDuration) * 100}%` 
                  }}
                >
                  M{month}
                </span>
              ))}
            </div>
          </div>
          <div className="timeline-duration-column"></div>
        </div>
        
        {/* Trade bars */}
        <div className="trade-bars">
          {scheduleData.schedule.map((trade, index) => (
            <div key={index} className="trade-row group">
              <div className="timeline-label-column">
                <span className="trade-label group-hover:text-gray-900 transition-colors">
                  {trade.phase}
                </span>
              </div>
              
              <div className="timeline-bars-column">
                <div className="timeline-track">
                  {/* Background track */}
                  <div className="timeline-track-bg"></div>
                  
                  {/* Enhanced Trade bar with gradient and hover effect */}
                  <div 
                    className="trade-bar enhanced timeline-bar-animated"
                    style={{
                      background: `linear-gradient(135deg, ${trade.color} 0%, ${trade.color}dd 100%)`,
                      left: `${((trade.startMonth - 1) / scheduleData.totalDuration) * 100}%`,
                      width: `${(trade.duration / scheduleData.totalDuration) * 100}%`,
                      '--index': index
                    } as React.CSSProperties}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.transform = 'translateY(-2px) scale(1.02)';
                      e.currentTarget.style.boxShadow = '0 10px 20px rgba(0,0,0,0.15)';
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.transform = 'translateY(0) scale(1)';
                      e.currentTarget.style.boxShadow = '0 2px 4px rgba(0,0,0,0.1)';
                    }}
                  >
                    <span className="trade-bar-label">
                      ${(trade.cost / 1000000).toFixed(0)}M
                    </span>
                  </div>
                </div>
              </div>
              
              <div className="timeline-duration-column">
                <span className="trade-duration group-hover:text-gray-700 transition-colors">
                  {trade.duration} mo
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
      
      {/* Critical Path Indicator */}
      <div className="timeline-footer">
        <div className="critical-path-section">
          <div className="critical-path-indicator">
            <div className="critical-path-dot"></div>
            <span className="critical-path-label">
              Critical Path: {scheduleData.criticalPath.join(' → ')}
            </span>
          </div>
          <div className="timeline-total">
            <span className="total-label">Total Duration:</span>
            <span className="total-value">{scheduleData.totalDuration} months</span>
          </div>
        </div>
        
        {/* Long-lead warning if applicable */}
        {longLeadWarning && (
          <div className="long-lead-warning">
            <AlertCircle size={16} className="warning-icon" />
            <p className="warning-text">{longLeadWarning}</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default TradeTimeline;