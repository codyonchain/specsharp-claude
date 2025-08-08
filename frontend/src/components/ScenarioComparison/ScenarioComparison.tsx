import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import './ScenarioComparison.css';

interface Scenario {
  id: string;
  name: string;
  icon: string;
  cost: number;
  costPerSF: number;
  roi: string;
  keyFeatures: string[];
  insight: string;
  color: string;
}

const ScenarioComparison: React.FC = () => {
  const scenarios: Scenario[] = [
    {
      id: 'medical',
      name: 'Medical Office Building',
      icon: '🏥',
      cost: 17800000,
      costPerSF: 356,
      roi: '3.2 years',
      keyFeatures: ['Medical-grade HVAC', 'Reinforced structure', 'Specialized plumbing'],
      insight: 'Highest cost but stable long-term tenants. Premium rents offset higher construction.',
      color: '#3B82F6'
    },
    {
      id: 'mixed',
      name: 'Mixed-Use Complex',
      icon: '🏢',
      cost: 22400000,
      costPerSF: 448,
      roi: '4.1 years',
      keyFeatures: ['Retail ground floor', '40 residential units', 'Parking garage'],
      insight: 'Multiple revenue streams. Retail provides immediate cash flow while residential builds equity.',
      color: '#10B981'
    },
    {
      id: 'hotel',
      name: 'Boutique Hotel',
      icon: '🏨',
      cost: 31200000,
      costPerSF: 624,
      roi: '5.8 years',
      keyFeatures: ['120 rooms', 'Restaurant & bar', 'Conference facilities'],
      insight: 'Premium finishes required. Highest potential returns but longer payback period.',
      color: '#8B5CF6'
    }
  ];
  
  const [activeScenario, setActiveScenario] = useState(scenarios[0]);
  const [isTransitioning, setIsTransitioning] = useState(false);
  
  const handleScenarioChange = (scenario: Scenario) => {
    if (scenario.id === activeScenario.id) return;
    setIsTransitioning(true);
    setTimeout(() => {
      setActiveScenario(scenario);
      setIsTransitioning(false);
    }, 300);
  };
  
  const getComparison = (current: number, baseline: number): string => {
    const diff = ((current - baseline) / baseline) * 100;
    if (diff > 0) return `+${diff.toFixed(0)}% vs medical`;
    if (diff < 0) return `${diff.toFixed(0)}% vs medical`;
    return 'Baseline scenario';
  };
  
  return (
    <section className="scenario-comparison">
      <div className="container mx-auto px-4">
        <h2 className="section-title text-center">One Site, Infinite Possibilities</h2>
        <p className="section-subtitle text-center">
          Same 50,000 SF lot in Nashville - See how different uses transform your investment
        </p>
        
        {/* Scenario Selector */}
        <div className="scenario-selector">
          {scenarios.map(scenario => (
            <motion.button
              key={scenario.id}
              className={`scenario-btn ${activeScenario.id === scenario.id ? 'active' : ''}`}
              onClick={() => handleScenarioChange(scenario)}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              style={{
                borderColor: activeScenario.id === scenario.id ? scenario.color : 'transparent'
              }}
            >
              <span className="scenario-icon">{scenario.icon}</span>
              <span className="scenario-name">{scenario.name}</span>
            </motion.button>
          ))}
        </div>
        
        {/* Dynamic Display */}
        <AnimatePresence mode="wait">
          <motion.div
            key={activeScenario.id}
            className="scenario-display"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
          >
            {/* Metrics Cards */}
            <div className="metrics-row">
              <MetricCard
                label="Total Investment"
                value={`$${(activeScenario.cost / 1000000).toFixed(1)}M`}
                trend={getComparison(activeScenario.cost, scenarios[0].cost)}
                color={activeScenario.color}
              />
              
              <MetricCard
                label="Cost per SF"
                value={`$${activeScenario.costPerSF}`}
                trend={`Market avg: $340/SF`}
                color={activeScenario.color}
              />
              
              <MetricCard
                label="ROI Timeline"
                value={activeScenario.roi}
                trend="To positive cash flow"
                color={activeScenario.color}
              />
            </div>
            
            {/* Visual Building Representation */}
            <div className="building-visual">
              <BuildingVisualization type={activeScenario.id} color={activeScenario.color} />
            </div>
            
            {/* Key Features */}
            <div className="features-section">
              <h4>What's Included:</h4>
              <div className="features-grid">
                {activeScenario.keyFeatures.map((feature, idx) => (
                  <motion.div
                    key={idx}
                    className="feature-chip"
                    initial={{ opacity: 0, scale: 0.8 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: idx * 0.1 }}
                    style={{ borderColor: activeScenario.color }}
                  >
                    ✓ {feature}
                  </motion.div>
                ))}
              </div>
            </div>
            
            {/* Insight Box */}
            <motion.div 
              className="insight-box"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.3 }}
              style={{ borderLeftColor: activeScenario.color }}
            >
              <strong>Key Insight:</strong> {activeScenario.insight}
            </motion.div>
          </motion.div>
        </AnimatePresence>
        
        {/* CTA */}
        <motion.div 
          className="comparison-cta"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
        >
          <button 
            className="primary-btn large"
            onClick={() => window.location.href = '/demo'}
          >
            Compare Your Own Scenarios
            <span className="arrow">→</span>
          </button>
          <p className="cta-subtitle">Takes less than 60 seconds</p>
        </motion.div>
      </div>
    </section>
  );
};

// Metric Card Component
const MetricCard: React.FC<{
  label: string;
  value: string;
  trend: string;
  color: string;
}> = ({ label, value, trend, color }) => (
  <motion.div 
    className="metric-card"
    whileHover={{ y: -5 }}
    style={{ borderTopColor: color }}
  >
    <span className="metric-label">{label}</span>
    <span className="metric-value" style={{ color }}>{value}</span>
    <span className="metric-trend">{trend}</span>
  </motion.div>
);

// Building Visualization Component
const BuildingVisualization: React.FC<{ type: string; color: string }> = ({ type, color }) => {
  const buildingConfigs = {
    medical: {
      floors: 4,
      label: 'Medical Office',
      features: ['Exam Rooms', 'Labs', 'Imaging', 'Pharmacy']
    },
    mixed: {
      floors: 6,
      label: 'Mixed-Use',
      features: ['Retail', 'Office', 'Residential', 'Parking']
    },
    hotel: {
      floors: 8,
      label: 'Hotel',
      features: ['Lobby', 'Rooms', 'Restaurant', 'Conference']
    }
  };
  
  const config = buildingConfigs[type as keyof typeof buildingConfigs];
  
  return (
    <div className="building-viz-container">
      <svg viewBox="0 0 200 250" className="building-svg">
        {/* Building base */}
        <motion.rect
          x="50"
          y={250 - config.floors * 25}
          width="100"
          height={config.floors * 25}
          fill={color}
          fillOpacity={0.2}
          stroke={color}
          strokeWidth={2}
          initial={{ height: 0 }}
          animate={{ height: config.floors * 25 }}
          transition={{ duration: 0.8 }}
        />
        
        {/* Floors */}
        {Array.from({ length: config.floors }).map((_, i) => (
          <motion.g key={i}>
            <line
              x1="50"
              y1={250 - (i + 1) * 25}
              x2="150"
              y2={250 - (i + 1) * 25}
              stroke={color}
              strokeOpacity={0.3}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: i * 0.1 }}
            />
            {/* Windows */}
            {[60, 80, 100, 120, 140].map((x, j) => (
              <motion.rect
                key={`${i}-${j}`}
                x={x - 3}
                y={250 - (i + 1) * 25 + 8}
                width={6}
                height={10}
                fill={color}
                fillOpacity={0.6}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: i * 0.1 + j * 0.02 }}
              />
            ))}
          </motion.g>
        ))}
        
        {/* Label */}
        <text
          x="100"
          y={270}
          textAnchor="middle"
          fill={color}
          fontSize="14"
          fontWeight="bold"
        >
          {config.label}
        </text>
      </svg>
      
      <div className="building-features">
        {config.features.map((feature, idx) => (
          <motion.div
            key={idx}
            className="feature-label"
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: idx * 0.1 }}
            style={{ color }}
          >
            Floor {config.floors - idx}: {feature}
          </motion.div>
        ))}
      </div>
    </div>
  );
};

export default ScenarioComparison;