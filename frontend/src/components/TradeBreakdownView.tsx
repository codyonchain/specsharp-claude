import { useMemo, useState } from 'react';
import { Package, FileSpreadsheet, Eye } from 'lucide-react';
import TradeTimeline from './TradeTimeline';

interface TradeBreakdownViewProps {
  tradeSummaries: any[];
  selectedTrade: string;
  selectedTradeData: any[];
  chartData: any[];
  totalCost: number;
  squareFootage: number;
  onTradeSelect: (trade: string) => void;
  onExportTrade: (trade: string) => void;
  onGeneratePackage: (trade: string) => void;
  onViewDetails: (trade: string) => void;
  projectData?: any; // Add projectData prop for timeline
}

const TRADE_COLORS: Record<string, string> = {
  structural: '#3B82F6',  // Blue
  mechanical: '#10B981',  // Green
  electrical: '#F59E0B',  // Orange
  plumbing: '#8B5CF6',   // Purple
  finishes: '#EC4899'     // Pink
};

const TRADE_ICONS: Record<string, string> = {
  structural: '🏗️',
  mechanical: '🔧',
  electrical: '⚡',
  plumbing: '🚿',
  finishes: '🎨'
};

function TradeBreakdownView({
  tradeSummaries,
  selectedTrade,
  selectedTradeData,
  chartData,
  totalCost,
  squareFootage,
  onTradeSelect,
  onExportTrade,
  onGeneratePackage,
  onViewDetails,
  projectData
}: TradeBreakdownViewProps) {
  // Local state for trade filter
  const [activeTradeFilter, setActiveTradeFilter] = useState<string>('all');
  
  // Handle trade filter click
  const handleTradeFilterClick = (trade: string) => {
    setActiveTradeFilter(trade);
    onTradeSelect(trade);
  };
  // Calculate donut chart segments
  const donutSegments = useMemo(() => {
    const data = selectedTrade === 'all' ? tradeSummaries : selectedTradeData;
    let cumulativePercentage = 0;
    
    return data.map(item => {
      const startAngle = cumulativePercentage * 3.6;
      cumulativePercentage += item.percentage;
      const endAngle = cumulativePercentage * 3.6;
      
      return {
        ...item,
        startAngle,
        endAngle,
        color: TRADE_COLORS[item.name] || '#94A3B8'
      };
    });
  }, [tradeSummaries, selectedTradeData, selectedTrade]);

  // Create SVG path for donut segment
  const createPath = (startAngle: number, endAngle: number, innerRadius: number, outerRadius: number) => {
    const angleRad = (angle: number) => (angle - 90) * Math.PI / 180;
    
    const x1 = 100 + outerRadius * Math.cos(angleRad(startAngle));
    const y1 = 100 + outerRadius * Math.sin(angleRad(startAngle));
    const x2 = 100 + outerRadius * Math.cos(angleRad(endAngle));
    const y2 = 100 + outerRadius * Math.sin(angleRad(endAngle));
    
    const x3 = 100 + innerRadius * Math.cos(angleRad(startAngle));
    const y3 = 100 + innerRadius * Math.sin(angleRad(startAngle));
    const x4 = 100 + innerRadius * Math.cos(angleRad(endAngle));
    const y4 = 100 + innerRadius * Math.sin(angleRad(endAngle));
    
    const largeArc = endAngle - startAngle > 180 ? 1 : 0;
    
    return `
      M ${x1} ${y1}
      A ${outerRadius} ${outerRadius} 0 ${largeArc} 1 ${x2} ${y2}
      L ${x4} ${y4}
      A ${innerRadius} ${innerRadius} 0 ${largeArc} 0 ${x3} ${y3}
      Z
    `;
  };

  return (
    <div className="trade-breakdown-modern">
      {/* Trade Navigation Tabs */}
      <div className="trade-navigation-tabs">
        <div className="trade-filter-tabs">
          <button
            onClick={() => handleTradeFilterClick('all')}
            className={`trade-tab ${selectedTrade === 'all' ? 'active' : ''}`}
          >
            All Trades
          </button>
          
          {tradeSummaries.map((trade) => (
            <button
              key={trade.name}
              onClick={() => handleTradeFilterClick(trade.name)}
              className={`trade-tab ${selectedTrade === trade.name ? 'active' : ''}`}
            >
              <span className="trade-tab-icon">{TRADE_ICONS[trade.name]}</span>
              <span className="trade-tab-name">{trade.displayName}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Main Container */}
      <div className="container">
        {/* Project Header Card */}
        <div className="header-card">
          <div className="header-content">
            <h1 className="header-title">Project Cost Analysis</h1>
            <p className="header-subtitle">
              Comprehensive breakdown of construction costs by trade
            </p>
          </div>
          <div className="header-metrics">
            <div className="metric">
              <span className="metric-label">Total Project Cost</span>
              <span className="metric-value">${(totalCost / 1000000).toFixed(2)}M</span>
            </div>
            <div className="metric">
              <span className="metric-label">Cost per SF</span>
              <span className="metric-value">${Math.round(totalCost / squareFootage)}</span>
            </div>
          </div>
        </div>

        {/* Metrics Grid */}
        <div className="metrics-grid">
          {/* Trade Mix Card */}
          <div className="metric-card">
            <div className="card-header">
              <h3 className="card-title">Trade Distribution</h3>
              {selectedTrade === 'all' && (
                <span className="card-badge">{tradeSummaries.length} Trades</span>
              )}
            </div>
            <div className="card-body">
              <div className="donut-container">
                <svg viewBox="0 0 200 200" className="donut-chart">
                  {donutSegments.map((segment, index) => (
                    <path
                      key={index}
                      d={createPath(segment.startAngle, segment.endAngle, 50, 80)}
                      fill={segment.color}
                      className="donut-segment"
                      onClick={() => selectedTrade === 'all' && onTradeSelect(segment.name)}
                    />
                  ))}
                </svg>
                <div className="donut-center">
                  <div className="center-value">${(totalCost / 1000000).toFixed(1)}M</div>
                  <div className="center-label">Total</div>
                </div>
              </div>
              <div className="legend">
                {donutSegments.map((segment, index) => (
                  <div 
                    key={index} 
                    className="legend-item"
                    onClick={() => selectedTrade === 'all' && onTradeSelect(segment.name)}
                  >
                    <div 
                      className="legend-dot" 
                      style={{ backgroundColor: segment.color }}
                    />
                    <span className="legend-label">{segment.displayName || segment.name}</span>
                    <span className="legend-value">{segment.percentage.toFixed(0)}%</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Trade Timeline Card - Replaces redundant Cost Breakdown */}
          {projectData && (
            <div className="metric-card">
              <TradeTimeline 
                projectData={{
                  buildingType: projectData.buildingType || projectData.building_type || 'office',
                  squareFootage: projectData.squareFootage || projectData.square_footage || squareFootage,
                  projectClassification: projectData.projectClassification || projectData.project_classification || 'ground_up',
                  tradeCosts: tradeSummaries.reduce((acc, trade) => {
                    acc[trade.name] = trade.total;
                    return acc;
                  }, {} as Record<string, number>)
                }}
              />
            </div>
          )}

          {/* Trade Details Card */}
          <div className="metric-card full-width">
            <div className="card-header">
              <h3 className="card-title">
                {selectedTrade === 'all' ? 'Trade Summary' : `${selectedTrade.charAt(0).toUpperCase() + selectedTrade.slice(1)} Details`}
              </h3>
              {selectedTrade === 'all' && (
                <span className="card-subtitle">Click on any trade for detailed breakdown</span>
              )}
            </div>
            <div className="card-body">
              <div className="trade-bars">
                {(selectedTrade === 'all' ? tradeSummaries : selectedTradeData).map((trade, index) => (
                  <div 
                    key={index} 
                    className={`trade-bar-item ${selectedTrade === 'all' ? 'clickable-trade' : ''}`}
                    onClick={selectedTrade === 'all' ? () => onViewDetails(trade.name) : undefined}
                    role={selectedTrade === 'all' ? 'button' : undefined}
                    tabIndex={selectedTrade === 'all' ? 0 : undefined}
                    onKeyDown={selectedTrade === 'all' ? (e) => {
                      if (e.key === 'Enter' || e.key === ' ') {
                        e.preventDefault();
                        onViewDetails(trade.name);
                      }
                    } : undefined}
                  >
                    <div className="trade-bar-header">
                      <div className="trade-info">
                        <span className="trade-icon">{TRADE_ICONS[trade.name] || '📊'}</span>
                        <span className="trade-name">{trade.displayName || trade.name}</span>
                      </div>
                      <div className="trade-values">
                        <span className="trade-amount">${(trade.total / 1000000).toFixed(2)}M</span>
                        <span className="trade-percentage">({trade.percentage.toFixed(1)}%)</span>
                      </div>
                    </div>
                    <div className="progress-bar">
                      <div 
                        className="progress-fill"
                        style={{ 
                          width: `${trade.percentage}%`,
                          backgroundColor: TRADE_COLORS[trade.name] || '#94A3B8'
                        }}
                      />
                    </div>
                    {selectedTrade === 'all' && (
                      <div className="view-details-indicator">
                        <span className="view-details-text">View Details</span>
                        <span className="view-details-arrow">→</span>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}

export default TradeBreakdownView;