import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import './HowItWorks.css';

const HowItWorksInteractive: React.FC = () => {
  const [activeStep, setActiveStep] = useState(1);
  const [typedText, setTypedText] = useState('');
  const [detectedFactors, setDetectedFactors] = useState<string[]>([]);
  const [showResults, setShowResults] = useState(false);
  const [displayValue, setDisplayValue] = useState({
    total: 0,
    perSF: 0,
    confidence: 0
  });
  
  const fullText = "200-unit luxury apartment complex with amenity deck, parking garage, and ground floor retail in Manchester NH";
  
  // Typing animation effect
  useEffect(() => {
    if (activeStep === 1) {
      setTypedText('');
      setDetectedFactors([]);
      setShowResults(false);
      let index = 0;
      const interval = setInterval(() => {
        if (index <= fullText.length) {
          setTypedText(fullText.slice(0, index));
          index++;
        } else {
          clearInterval(interval);
          // Trigger detection animation
          setTimeout(() => showDetections(), 500);
        }
      }, 50);
      return () => clearInterval(interval);
    }
  }, [activeStep]);
  
  const showDetections = () => {
    const factors = [
      { icon: '🏘️', text: 'Multifamily Residential', delay: 0 },
      { icon: '🎯', text: '200 Units Configured', delay: 100 },
      { icon: '🚗', text: 'Structured Parking (+$45K/unit)', delay: 200 },
      { icon: '📍', text: 'Manchester Market Data', delay: 300 },
      { icon: '🏪', text: 'Mixed-Use Component', delay: 400 },
      { icon: '❄️', text: 'Winter Conditions Factor', delay: 500 }
    ];
    
    factors.forEach(factor => {
      setTimeout(() => {
        setDetectedFactors(prev => [...prev, `${factor.icon} ${factor.text}`]);
      }, factor.delay);
    });
    
    setTimeout(() => {
      setShowResults(true);
      animateCounters();
    }, 1000);
  };
  
  const animateCounters = () => {
    const duration = 1500;
    const steps = 60;
    const targets = { total: 47200000, perSF: 262, confidence: 94 };
    
    let current = { total: 0, perSF: 0, confidence: 0 };
    const increments = {
      total: targets.total / steps,
      perSF: targets.perSF / steps,
      confidence: targets.confidence / steps
    };
    
    const timer = setInterval(() => {
      current.total += increments.total;
      current.perSF += increments.perSF;
      current.confidence += increments.confidence;
      
      if (current.total >= targets.total) {
        setDisplayValue(targets);
        clearInterval(timer);
      } else {
        setDisplayValue({
          total: Math.floor(current.total),
          perSF: Math.floor(current.perSF),
          confidence: Math.floor(current.confidence)
        });
      }
    }, duration / steps);
  };
  
  return (
    <section className="how-it-works-interactive">
      <div className="container mx-auto px-4">
        <h2 className="section-title text-center">See SpecSharp in Action</h2>
        <p className="section-subtitle text-center">Watch real intelligence at work</p>
        
        {/* Step 1: Input with Live Detection */}
        <div className={`step-showcase ${activeStep === 1 ? 'active' : ''}`}>
          <div className="step-header">
            <div className="step-number">1</div>
            <h3>Describe Your Project</h3>
          </div>
          
          <div className="input-demo">
            <div className="typing-box">
              <span className="typed-text">{typedText}</span>
              <span className="cursor">|</span>
            </div>
          </div>
          
          <AnimatePresence>
            {detectedFactors.length > 0 && (
              <motion.div 
                className="instant-detection"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
              >
                <h4>✨ SpecSharp Instantly Detects:</h4>
                <div className="detection-badges">
                  {detectedFactors.map((factor, idx) => (
                    <motion.span 
                      key={idx}
                      className="badge"
                      initial={{ scale: 0 }}
                      animate={{ scale: 1 }}
                      transition={{ delay: idx * 0.1 }}
                    >
                      {factor}
                    </motion.span>
                  ))}
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
        
        {/* Step 2: Compare Your Options Instantly */}
        <AnimatePresence>
          {showResults && (
            <motion.div 
              className="step-showcase active"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
            >
              <div className="step-header">
                <div className="step-number">2</div>
                <h3>Compare Your Options Instantly</h3>
              </div>
              
              <div className="scenarios-comparison">
                {/* Current Plan */}
                <motion.div 
                  className="scenario-card base"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.1 }}
                >
                  <h4>Current Plan</h4>
                  <div className="scenario-metrics">
                    <div className="metric">
                      <span className="label">Total Investment</span>
                      <span className="value">$47.2M</span>
                    </div>
                    <div className="metric">
                      <span className="label">Cost/Unit</span>
                      <span className="value">$236K</span>
                    </div>
                    <div className="metric">
                      <span className="label">IRR</span>
                      <span className="value warning">6.8%</span>
                    </div>
                    <div className="metric decision">
                      <span className="label">Decision</span>
                      <span className="value no-go">NO-GO ✗</span>
                    </div>
                  </div>
                </motion.div>
                
                {/* No Parking Garage */}
                <motion.div 
                  className="scenario-card optimized"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.2 }}
                >
                  <div className="recommended-badge">Recommended</div>
                  <h4>No Parking Garage</h4>
                  <div className="scenario-metrics">
                    <div className="metric">
                      <span className="label">Total Investment</span>
                      <span className="value">$39.1M</span>
                      <span className="delta good">-$8.1M</span>
                    </div>
                    <div className="metric">
                      <span className="label">Cost/Unit</span>
                      <span className="value">$196K</span>
                      <span className="delta good">-$40K</span>
                    </div>
                    <div className="metric">
                      <span className="label">IRR</span>
                      <span className="value success">11.3%</span>
                      <span className="delta good">+4.5%</span>
                    </div>
                    <div className="metric decision">
                      <span className="label">Decision</span>
                      <span className="value go">GO ✓</span>
                    </div>
                  </div>
                </motion.div>
                
                {/* Add 20 Units */}
                <motion.div 
                  className="scenario-card premium"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.3 }}
                >
                  <h4>Add 20 Units</h4>
                  <div className="scenario-metrics">
                    <div className="metric">
                      <span className="label">Total Investment</span>
                      <span className="value">$52.4M</span>
                      <span className="delta bad">+$5.2M</span>
                    </div>
                    <div className="metric">
                      <span className="label">Cost/Unit</span>
                      <span className="value">$238K</span>
                      <span className="delta">—</span>
                    </div>
                    <div className="metric">
                      <span className="label">IRR</span>
                      <span className="value warning">8.1%</span>
                      <span className="delta good">+1.3%</span>
                    </div>
                    <div className="metric decision">
                      <span className="label">Decision</span>
                      <span className="value warning">MARGINAL</span>
                    </div>
                  </div>
                </motion.div>
              </div>
              
              <p className="step-caption">
                See how each decision impacts returns. Export all scenarios for your investment committee.
              </p>
              
              {/* Step 3: Get Actionable Investment Guidance */}
              <div className="export-section">
                <div className="step-header">
                  <div className="step-number">3</div>
                  <h3>Get Actionable Investment Guidance</h3>
                </div>
                
                <motion.div 
                  className="investment-analysis"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 0.4 }}
                >
                  <div className="analysis-header">
                    <span className="status-badge no-go">Investment Decision: NO-GO</span>
                    <h4>2 Criteria Not Met (Current Plan)</h4>
                  </div>
                  
                  <div className="criteria-feedback">
                    <motion.div 
                      className="criterion failed"
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: 0.5 }}
                    >
                      <span className="icon">❌</span>
                      <div className="details">
                        <strong>IRR: 6.8%</strong>
                        <span className="requirement">Minimum required: 10%</span>
                      </div>
                    </motion.div>
                    
                    <motion.div 
                      className="criterion failed"
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: 0.6 }}
                    >
                      <span className="icon">❌</span>
                      <div className="details">
                        <strong>Cost/Unit: $236K</strong>
                        <span className="requirement">Maximum target: $225K</span>
                      </div>
                    </motion.div>
                    
                    <motion.div 
                      className="criterion passed"
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: 0.7 }}
                    >
                      <span className="icon">✅</span>
                      <div className="details">
                        <strong>Debt Yield: 7.8%</strong>
                        <span className="requirement">Minimum required: 7.0%</span>
                      </div>
                    </motion.div>
                  </div>
                  
                  <motion.div 
                    className="improvement-paths"
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.8 }}
                  >
                    <h4>3 Ways to Make This Project Work:</h4>
                    <ul>
                      <li>Switch to surface parking: Save <strong>$8.1M</strong> ($40K per unit)</li>
                      <li>Increase rents by <strong>$125/month</strong> (still below market)</li>
                      <li>Reduce amenity package by <strong>$2.3M</strong> (remove rooftop deck)</li>
                    </ul>
                  </motion.div>
                  
                  <motion.div 
                    className="export-options"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.9 }}
                  >
                    <button className="export-btn powerpoint">
                      <span className="icon">📊</span>
                      <span>Export to PowerPoint</span>
                    </button>
                    <button className="export-btn excel">
                      <span className="icon">📈</span>
                      <span>Download Excel Model</span>
                    </button>
                    <button className="export-btn pdf">
                      <span className="icon">📄</span>
                      <span>Executive Summary PDF</span>
                    </button>
                  </motion.div>
                </motion.div>
                
                <p className="step-caption">
                  Specific, quantified guidance to get your project approved. Ready for your board in seconds.
                </p>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
        
        {/* Watch Again Button - Only show after animation completes */}
        {activeStep === 2 && (
          <div className="text-center mt-8">
            <motion.button
              className="replay-button"
              onClick={() => setActiveStep(1)}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.5 }}
            >
              ↻ Watch Again
            </motion.button>
          </div>
        )}
      </div>
    </section>
  );
};

// Animated Trade Breakdown Component for Preview
const CostDNAMini: React.FC = () => {
  const [isVisible, setIsVisible] = useState(false);
  
  useEffect(() => {
    // Trigger animation when component mounts
    setIsVisible(true);
  }, []);

  const trades = [
    {
      name: 'Parking Garage',
      amount: '$8.1M',
      percentage: 17,
      description: '$45K per unit',
      color: 'from-gray-400 to-gray-500',
      delay: 0.2
    },
    {
      name: 'Structural & Shell',
      amount: '$14.2M',
      percentage: 30,
      description: 'Concrete podium',
      color: 'from-blue-400 to-blue-500',
      delay: 0.4
    },
    {
      name: 'Unit Interiors',
      amount: '$11.8M',
      percentage: 25,
      description: 'Luxury finishes',
      color: 'from-purple-400 to-purple-500',
      delay: 0.6
    },
    {
      name: 'MEP Systems',
      amount: '$7.1M',
      percentage: 15,
      description: 'All utilities',
      color: 'from-green-400 to-emerald-500',
      delay: 0.8
    },
    {
      name: 'Amenities & Retail',
      amount: '$6.0M',
      percentage: 13,
      description: 'Pool, gym, retail',
      color: 'from-indigo-400 to-indigo-500',
      delay: 1.0
    }
  ];
  
  return (
    <div className="bg-gradient-to-br from-blue-600 to-purple-600 rounded-2xl p-6">
      <h4 className="text-xl font-bold text-white mb-2">Trade Cost Breakdown</h4>
      <p className="text-blue-100 text-sm mb-4">See exactly where your budget goes</p>
      
      {/* Animated Trade Bars */}
      <div className="space-y-3">
        {trades.map((trade, idx) => (
          <div key={idx} className="relative">
            <div className="flex justify-between text-white mb-1">
              <span className="text-sm font-medium">{trade.name}</span>
              <span className="text-sm font-bold">{trade.amount}</span>
            </div>
            <div className="h-6 bg-white/20 rounded-full overflow-hidden">
              <motion.div 
                className={`h-full bg-gradient-to-r ${trade.color} rounded-full`}
                initial={{ width: 0, opacity: 0 }}
                animate={isVisible ? { 
                  width: `${trade.percentage}%`, 
                  opacity: 1 
                } : {}}
                transition={{ 
                  duration: 1, 
                  delay: trade.delay,
                  ease: "easeOut"
                }}
              />
            </div>
            <span className="text-xs text-blue-200">
              {trade.percentage}% - {trade.description}
            </span>
          </div>
        ))}
      </div>

      {/* Total at bottom */}
      <motion.div 
        className="mt-4 pt-3 border-t border-white/20"
        initial={{ opacity: 0 }}
        animate={isVisible ? { opacity: 1 } : {}}
        transition={{ delay: 1.5 }}
      >
        <div className="flex justify-between items-center text-white">
          <span className="text-sm">Total Project Cost:</span>
          <span className="text-lg font-bold">$47.2M</span>
        </div>
      </motion.div>
    </div>
  );
};

export default HowItWorksInteractive;