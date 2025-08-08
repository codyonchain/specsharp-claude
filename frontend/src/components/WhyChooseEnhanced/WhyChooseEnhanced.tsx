import React, { useState, useEffect, useRef } from 'react';
import { motion, useInView } from 'framer-motion';
import { Zap, Brain, Share2, FileSpreadsheet, Link2 as LinkIcon, FileText } from 'lucide-react';
import './WhyChooseEnhanced.css';

const WhyChooseEnhanced: React.FC = () => {
  const sectionRef = useRef<HTMLDivElement>(null);
  const isInView = useInView(sectionRef, { once: true, margin: "-100px" });
  
  const [animatedValues, setAnimatedValues] = useState({
    traditional: { time: 0, accuracy: 0, scenarios: 0 },
    specsharp: { time: 0, accuracy: 0, scenarios: 0 }
  });
  
  const [statsValues, setStatsValues] = useState({
    speed: 0,
    accuracy: 0,
    projectSize: 0
  });
  
  useEffect(() => {
    if (isInView) {
      // Animate comparison bars
      const timer1 = setTimeout(() => {
        setAnimatedValues({
          traditional: { time: 100, accuracy: 75, scenarios: 10 },
          specsharp: { time: 3, accuracy: 94, scenarios: 100 }
        });
      }, 200);
      
      // Animate stats counters
      animateStats();
      
      return () => clearTimeout(timer1);
    }
  }, [isInView]);
  
  const animateStats = () => {
    const duration = 2000;
    const steps = 60;
    const targets = { speed: 50, accuracy: 94, projectSize: 2.3 };
    
    let current = { speed: 0, accuracy: 0, projectSize: 0 };
    const increments = {
      speed: targets.speed / steps,
      accuracy: targets.accuracy / steps,
      projectSize: targets.projectSize / steps
    };
    
    const timer = setInterval(() => {
      current.speed += increments.speed;
      current.accuracy += increments.accuracy;
      current.projectSize += increments.projectSize;
      
      if (current.speed >= targets.speed) {
        setStatsValues(targets);
        clearInterval(timer);
      } else {
        setStatsValues({
          speed: Math.floor(current.speed),
          accuracy: Math.floor(current.accuracy),
          projectSize: parseFloat(current.projectSize.toFixed(1))
        });
      }
    }, duration / steps);
  };
  
  return (
    <section className="why-choose-enhanced py-12 bg-gray-50" ref={sectionRef}>
      <div className="container mx-auto px-4">
        <h2 className="text-3xl font-bold text-center mb-8 text-gray-800">
          Why Construction Professionals Choose SpecSharp
        </h2>
        
        {/* Visual Comparison Grid */}
        <div className="max-w-4xl mx-auto grid md:grid-cols-2 gap-8 mb-12">
          
          {/* Traditional Method - Left Side */}
          <div className="comparison-side traditional opacity-70">
            <h3 className="text-sm text-gray-500 mb-4 uppercase tracking-wide">Traditional Estimating</h3>
            <div className="space-y-4">
              {/* Time Bar */}
              <div className="metric-bar">
                <div className="flex justify-between text-sm mb-1">
                  <span>Time</span>
                  <span className="text-red-600 font-semibold">3+ hours</span>
                </div>
                <div className="h-2 bg-red-200 rounded-full overflow-hidden">
                  <motion.div 
                    className="h-2 bg-red-500 rounded-full"
                    initial={{ width: 0 }}
                    animate={{ width: `${animatedValues.traditional.time}%` }}
                    transition={{ duration: 0.8, ease: "easeOut" }}
                  />
                </div>
              </div>
              
              {/* Accuracy Bar */}
              <div className="metric-bar">
                <div className="flex justify-between text-sm mb-1">
                  <span>Accuracy</span>
                  <span className="text-orange-600 font-semibold">~75%</span>
                </div>
                <div className="h-2 bg-orange-200 rounded-full overflow-hidden">
                  <motion.div 
                    className="h-2 bg-orange-500 rounded-full"
                    initial={{ width: 0 }}
                    animate={{ width: `${animatedValues.traditional.accuracy}%` }}
                    transition={{ duration: 0.8, ease: "easeOut", delay: 0.2 }}
                  />
                </div>
              </div>
              
              {/* Coverage Bar */}
              <div className="metric-bar">
                <div className="flex justify-between text-sm mb-1">
                  <span>Scenarios</span>
                  <span className="text-gray-600 font-semibold">1 version</span>
                </div>
                <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                  <motion.div 
                    className="h-2 bg-gray-500 rounded-full"
                    initial={{ width: 0 }}
                    animate={{ width: `${animatedValues.traditional.scenarios}%` }}
                    transition={{ duration: 0.8, ease: "easeOut", delay: 0.4 }}
                  />
                </div>
              </div>
              
              {/* Pain Points */}
              <div className="mt-4 p-3 bg-red-50 rounded-lg">
                <ul className="text-xs text-red-700 space-y-1">
                  <li>• Manual spreadsheets</li>
                  <li>• Version control issues</li>
                  <li>• Inconsistent pricing</li>
                </ul>
              </div>
            </div>
          </div>
          
          {/* SpecSharp - Right Side */}
          <div className="comparison-side specsharp">
            <h3 className="text-sm font-semibold text-blue-600 mb-4 uppercase tracking-wide">With SpecSharp</h3>
            <div className="space-y-4">
              {/* Time Bar */}
              <div className="metric-bar">
                <div className="flex justify-between text-sm mb-1">
                  <span>Time</span>
                  <span className="text-green-600 font-semibold">60 seconds</span>
                </div>
                <div className="h-2 bg-green-200 rounded-full overflow-hidden">
                  <motion.div 
                    className="h-2 bg-green-500 rounded-full animate-pulse"
                    initial={{ width: 0 }}
                    animate={{ width: `${animatedValues.specsharp.time}%` }}
                    transition={{ duration: 0.8, ease: "easeOut" }}
                  />
                </div>
              </div>
              
              {/* Accuracy Bar */}
              <div className="metric-bar">
                <div className="flex justify-between text-sm mb-1">
                  <span>Accuracy</span>
                  <span className="text-green-600 font-semibold">94%</span>
                </div>
                <div className="h-2 bg-green-200 rounded-full overflow-hidden">
                  <motion.div 
                    className="h-2 bg-green-500 rounded-full"
                    initial={{ width: 0 }}
                    animate={{ width: `${animatedValues.specsharp.accuracy}%` }}
                    transition={{ duration: 0.8, ease: "easeOut", delay: 0.2 }}
                  />
                </div>
              </div>
              
              {/* Coverage Bar */}
              <div className="metric-bar">
                <div className="flex justify-between text-sm mb-1">
                  <span>Scenarios</span>
                  <span className="text-green-600 font-semibold">10+ versions</span>
                </div>
                <div className="h-2 bg-green-200 rounded-full overflow-hidden">
                  <motion.div 
                    className="h-2 bg-green-500 rounded-full"
                    initial={{ width: 0 }}
                    animate={{ width: `${animatedValues.specsharp.scenarios}%` }}
                    transition={{ duration: 0.8, ease: "easeOut", delay: 0.4 }}
                  />
                </div>
              </div>
              
              {/* Benefits */}
              <div className="mt-4 p-3 bg-green-50 rounded-lg">
                <ul className="text-xs text-green-700 space-y-1">
                  <li>✓ AI-powered intelligence</li>
                  <li>✓ Real-time collaboration</li>
                  <li>✓ Consistent methodology</li>
                </ul>
              </div>
            </div>
          </div>
        </div>

        {/* Key Stats Row with Enhanced Visuals */}
        <div className="grid md:grid-cols-3 gap-8 max-w-4xl mx-auto">
          
          {/* Speed Wins Deals */}
          <motion.div 
            className="stat-card text-center"
            initial={{ opacity: 0, y: 20 }}
            animate={isInView ? { opacity: 1, y: 0 } : {}}
            transition={{ delay: 0.6 }}
          >
            <div className="inline-flex items-center justify-center w-12 h-12 bg-blue-100 rounded-full mb-3">
              <Zap className="w-6 h-6 text-blue-600" />
            </div>
            <h3 className="font-semibold text-lg mb-2 text-gray-800">Speed Wins Deals</h3>
            <div className="text-3xl font-bold text-blue-600 mb-1">{statsValues.speed}x</div>
            <p className="text-sm text-gray-600 mb-2">Faster than manual</p>
            <div className="testimonial-chip p-2 bg-blue-50 rounded text-xs text-blue-700">
              "Won 3 deals this week by responding first"
              <div className="text-blue-500 mt-1">- Turner Construction</div>
            </div>
          </motion.div>

          {/* AI-Backed Accuracy */}
          <motion.div 
            className="stat-card text-center"
            initial={{ opacity: 0, y: 20 }}
            animate={isInView ? { opacity: 1, y: 0 } : {}}
            transition={{ delay: 0.7 }}
          >
            <div className="inline-flex items-center justify-center w-12 h-12 bg-green-100 rounded-full mb-3">
              <Brain className="w-6 h-6 text-green-600" />
            </div>
            <h3 className="font-semibold text-lg mb-2 text-gray-800">AI-Backed Accuracy</h3>
            <div className="text-3xl font-bold text-green-600 mb-1">{statsValues.accuracy}%</div>
            <p className="text-sm text-gray-600 mb-2">Match rate with actuals</p>
            {/* Mini sparkline showing improvement */}
            <div className="flex justify-center gap-1 mb-2">
              <motion.div 
                className="w-2 h-8 bg-gray-300 rounded"
                initial={{ height: 0 }}
                animate={isInView ? { height: 32 } : {}}
                transition={{ delay: 0.8 }}
              />
              <motion.div 
                className="w-2 h-10 bg-gray-400 rounded"
                initial={{ height: 0 }}
                animate={isInView ? { height: 40 } : {}}
                transition={{ delay: 0.9 }}
              />
              <motion.div 
                className="w-2 h-12 bg-green-400 rounded"
                initial={{ height: 0 }}
                animate={isInView ? { height: 48 } : {}}
                transition={{ delay: 1.0 }}
              />
              <motion.div 
                className="w-2 h-14 bg-green-500 rounded"
                initial={{ height: 0 }}
                animate={isInView ? { height: 56 } : {}}
                transition={{ delay: 1.1 }}
              />
              <motion.div 
                className="w-2 h-16 bg-green-600 rounded animate-pulse"
                initial={{ height: 0 }}
                animate={isInView ? { height: 64 } : {}}
                transition={{ delay: 1.2 }}
              />
            </div>
            <p className="text-xs text-gray-500">Getting smarter daily</p>
          </motion.div>

          {/* Professional Results */}
          <motion.div 
            className="stat-card text-center"
            initial={{ opacity: 0, y: 20 }}
            animate={isInView ? { opacity: 1, y: 0 } : {}}
            transition={{ delay: 0.8 }}
          >
            <div className="inline-flex items-center justify-center w-12 h-12 bg-purple-100 rounded-full mb-3">
              <Share2 className="w-6 h-6 text-purple-600" />
            </div>
            <h3 className="font-semibold text-lg mb-2 text-gray-800">Professional Results</h3>
            <div className="text-3xl font-bold text-purple-600 mb-1">${statsValues.projectSize}M</div>
            <p className="text-sm text-gray-600 mb-2">Avg. project size</p>
            <div className="flex flex-col gap-1">
              <div className="inline-flex items-center justify-center gap-2 text-xs">
                <span className="export-badge">
                  <FileSpreadsheet className="w-3 h-3 inline mr-1" />Excel
                </span>
                <span className="export-badge">
                  <LinkIcon className="w-3 h-3 inline mr-1" />Share
                </span>
                <span className="export-badge">
                  <FileText className="w-3 h-3 inline mr-1" />PDF
                </span>
              </div>
              <p className="text-xs text-gray-500 mt-1">Investor-ready exports</p>
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  );
};

export default WhyChooseEnhanced;