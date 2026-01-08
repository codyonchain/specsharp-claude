import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import './ScenarioComparison.css';

interface BuildingType {
  id: string;
  name: string;
  icon: string;
  costRange: string;
  unitMetric: string;
  features: string[];
  color: string;
}

const ScenarioComparison: React.FC = () => {
  const buildingTypes: BuildingType[] = [
    {
      id: 'healthcare',
      name: 'Healthcare',
      icon: '🏥',
      costRange: '$850-1,200/SF',
      unitMetric: 'Includes OSHPD requirements',
      features: ['Medical gas & OR costs', 'Redundant systems', 'ICRA compliance'],
      color: '#ef4444'
    },
    {
      id: 'office',
      name: 'Office',
      icon: '🏢',
      costRange: '$385-485/SF',
      unitMetric: 'Class A specifications',
      features: ['TI allowance modeling', 'Core factor analysis', 'LEED optimization'],
      color: '#3b82f6'
    },
    {
      id: 'multifamily',
      name: 'Multifamily',
      icon: '🏘️',
      costRange: '$165-285K/unit',
      unitMetric: 'Luxury to workforce',
      features: ['Amenity cost analysis', 'Parking ratio optimization', 'Unit mix modeling'],
      color: '#10b981'
    },
    {
      id: 'hospitality',
      name: 'Hospitality',
      icon: '🏨',
      costRange: '$185-350K/key',
      unitMetric: 'Select to luxury',
      features: ['FF&E by brand standards', 'RevPAR feasibility', 'PIP compliance'],
      color: '#8b5cf6'
    },
    {
      id: 'restaurant',
      name: 'Restaurant',
      icon: '🍽️',
      costRange: '$350-550/SF',
      unitMetric: 'All-in with equipment',
      features: ['Kitchen equipment sizing', 'Revenue per seat analysis', 'Grease trap requirements'],
      color: '#f59e0b'
    },
    {
      id: 'retail',
      name: 'Retail',
      icon: '🏪',
      costRange: '$185-285/SF',
      unitMetric: 'Vanilla shell to luxury',
      features: ['Tenant improvement costs', 'Sales/SF projections', 'Loading dock design'],
      color: '#06b6d4'
    },
    {
      id: 'industrial',
      name: 'Industrial',
      icon: '🏭',
      costRange: '$85-145/SF',
      unitMetric: 'Distribution to cold storage',
      features: ['Clear height pricing', 'Dock door requirements', 'Floor load capacity'],
      color: '#6b7280'
    },
    {
      id: 'education',
      name: 'Education',
      icon: '🏫',
      costRange: '$285-385/SF',
      unitMetric: 'K-12 to higher ed',
      features: ['Lab & tech infrastructure', 'Cost per student', 'E-rate compliance'],
      color: '#a855f7'
    }
  ];
  
  return (
    <section className="building-types-section">
      <div className="container mx-auto px-4">
        <h2 className="section-title text-center">Purpose-Built Intelligence for Every Asset Class</h2>
        <p className="section-subtitle text-center">
          Deep industry knowledge built into every calculation
        </p>
        
        {/* Building Types Grid */}
        <div className="building-types-grid">
          {buildingTypes.map((type, index) => (
            <motion.div
              key={type.id}
              className="building-type-card"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              whileHover={{ 
                scale: 1.05, 
                boxShadow: '0 10px 30px rgba(0,0,0,0.15)' 
              }}
            >
              <div className="type-header" style={{ borderBottomColor: type.color }}>
                <span className="type-icon">{type.icon}</span>
                <h3 className="type-name">{type.name}</h3>
              </div>
              
              <div className="type-metrics">
                <div className="cost-range" style={{ color: type.color }}>
                  {type.costRange}
                </div>
                <div className="unit-metric">
                  {type.unitMetric}
                </div>
              </div>
              
              <div className="type-features">
                {type.features.map((feature, idx) => (
                  <div key={idx} className="feature-item">
                    <span className="feature-check" style={{ color: type.color }}>✓</span>
                    <span className="feature-text">{feature}</span>
                  </div>
                ))}
              </div>
            </motion.div>
          ))}
        </div>
        
        {/* Accuracy Badge */}
        <motion.div 
          className="accuracy-badge"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.8 }}
        >
          <span className="accuracy-icon">🎯</span>
          <p className="accuracy-text">
            <strong>94% accuracy</strong> vs. actual bids across <strong>50,000+ projects</strong>
          </p>
        </motion.div>
        
        {/* CTA */}
        <motion.div 
          className="comparison-cta"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1 }}
        >
          <button 
            className="primary-btn large"
            onClick={() => window.location.href = '/demo'}
          >
            Try Your Building Type Now
            <span className="arrow">→</span>
          </button>
          <p className="cta-subtitle">Get asset-specific intelligence in 60 seconds</p>
        </motion.div>
      </div>
    </section>
  );
};

export default ScenarioComparison;