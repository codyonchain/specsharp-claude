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
  
  const fullText = "52,000 sf hospital addition with 3 OR surgical suite and imaging center in Manchester NH";
  
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
      { icon: '🏥', text: 'Healthcare Facility', delay: 0 },
      { icon: '➕', text: 'Addition Project (+15%)', delay: 100 },
      { icon: '🔪', text: 'Surgical Requirements', delay: 200 },
      { icon: '📍', text: 'Manchester Market Data', delay: 300 },
      { icon: '❄️', text: 'Winter Conditions Factor', delay: 400 }
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
    const targets = { total: 28500000, perSF: 570, confidence: 92 };
    
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
        
        {/* Step 2: Show Live Results */}
        <AnimatePresence>
          {showResults && (
            <motion.div 
              className="step-showcase active"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
            >
              <div className="step-header">
                <div className="step-number">2</div>
                <h3>Get Instant Intelligence</h3>
              </div>
              
              <div className="results-preview">
                {/* Cost DNA Visualization */}
                <div className="cost-dna-preview">
                  <CostDNAMini />
                </div>
                
                {/* Key Metrics */}
                <div className="instant-insights">
                  <div className="insight-card">
                    <span className="big-number">
                      ${(displayValue.total / 1000000).toFixed(1)}M
                    </span>
                    <span className="label">Total Cost</span>
                  </div>
                  <div className="insight-card">
                    <span className="big-number">
                      ${displayValue.perSF}/SF
                    </span>
                    <span className="label">Cost/SF</span>
                  </div>
                  <div className="insight-card">
                    <span className="big-number">
                      {displayValue.confidence}%
                    </span>
                    <span className="label">Confidence</span>
                  </div>
                </div>
                
                {/* Trade Breakdown Preview */}
                <div className="breakdown-preview">
                  <div className="trade-item">
                    <span>Mechanical (Medical Grade HVAC)</span>
                    <motion.span 
                      className="amount"
                      initial={{ opacity: 0, x: 20 }}
                      animate={{ opacity: 1, x: 0 }}
                    >
                      $8.2M
                    </motion.span>
                  </div>
                  <div className="trade-item">
                    <span>Surgical Suite Build-Out</span>
                    <motion.span 
                      className="amount"
                      initial={{ opacity: 0, x: 20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: 0.1 }}
                    >
                      $3.1M
                    </motion.span>
                  </div>
                  <div className="trade-item">
                    <span>Structural Reinforcement</span>
                    <motion.span 
                      className="amount"
                      initial={{ opacity: 0, x: 20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: 0.2 }}
                    >
                      $2.4M
                    </motion.span>
                  </div>
                  <div className="see-more">+ 47 more detailed line items...</div>
                </div>
              </div>
              
              {/* Step 3: Export Preview */}
              <div className="export-section">
                <div className="step-header">
                  <div className="step-number">3</div>
                  <h3>Share Professional Results</h3>
                </div>
                
                <div className="export-showcase">
                  <div className="export-previews">
                    <motion.div 
                      className="preview-card"
                      whileHover={{ scale: 1.05 }}
                    >
                      <div className="preview-icon excel">📊</div>
                      <span>Excel with Live Formulas</span>
                    </motion.div>
                    
                    <motion.div 
                      className="preview-card"
                      whileHover={{ scale: 1.05 }}
                    >
                      <div className="preview-icon pdf">📄</div>
                      <span>Professional PDF Report</span>
                    </motion.div>
                    
                    <motion.div 
                      className="preview-card"
                      whileHover={{ scale: 1.05 }}
                    >
                      <div className="preview-icon share">🔗</div>
                      <span>Instant Share Links</span>
                    </motion.div>
                  </div>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
        
        {/* Replay Button */}
        <div className="text-center mt-8">
          <motion.button
            className="replay-button"
            onClick={() => setActiveStep(activeStep === 1 ? 2 : 1)}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            {activeStep === 1 ? 'Skip to Results' : '↻ Watch Again'}
          </motion.button>
        </div>
      </div>
    </section>
  );
};

// Mini Cost DNA Component for Preview
const CostDNAMini: React.FC = () => {
  const [bars, setBars] = useState<number[]>([]);
  
  useEffect(() => {
    // Generate animated bars
    const values = [45, 78, 62, 89, 54, 71, 83, 49, 66, 75];
    setBars([]);
    values.forEach((value, idx) => {
      setTimeout(() => {
        setBars(prev => [...prev, value]);
      }, idx * 100);
    });
  }, []);
  
  return (
    <div className="dna-mini">
      <h4>Cost DNA Fingerprint™</h4>
      <div className="dna-bars">
        {bars.map((height, idx) => (
          <motion.div
            key={idx}
            className="dna-bar"
            initial={{ height: 0 }}
            animate={{ height: `${height}%` }}
            style={{
              background: `hsl(${200 + idx * 15}, 70%, 50%)`,
            }}
          />
        ))}
      </div>
      <p className="dna-description">Unique cost signature for your project</p>
    </div>
  );
};

export default HowItWorksInteractive;