import React, { useState, useEffect, useRef } from 'react';
import { motion, useInView } from 'framer-motion';
import { } from 'lucide-react';
import './WhyChooseEnhanced.css';

const WhyChooseEnhanced: React.FC = () => {
  const sectionRef = useRef<HTMLDivElement>(null);
  const isInView = useInView(sectionRef, { once: true, margin: "-100px" });
  
  const [animatedValues, setAnimatedValues] = useState({
    traditional: { investment: 0, scenarios: 0, costs: 0, guidance: 0 },
    specsharp: { investment: 100, scenarios: 100, costs: 100, guidance: 100 }
  });
  
  const [statsValues, setStatsValues] = useState({
    dealsSaved: 0,
    approved: 0,
    presentations: 0
  });
  
  useEffect(() => {
    if (isInView) {
      // Animate comparison bars
      const timer1 = setTimeout(() => {
        setAnimatedValues({
          traditional: { investment: 20, scenarios: 10, costs: 30, guidance: 0 },
          specsharp: { investment: 100, scenarios: 100, costs: 100, guidance: 100 }
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
    const targets = { dealsSaved: 450, approved: 87, presentations: 2400 };
    
    let current = { dealsSaved: 0, approved: 0, presentations: 0 };
    const increments = {
      dealsSaved: targets.dealsSaved / steps,
      approved: targets.approved / steps,
      presentations: targets.presentations / steps
    };
    
    const timer = setInterval(() => {
      current.dealsSaved += increments.dealsSaved;
      current.approved += increments.approved;
      current.presentations += increments.presentations;
      
      if (current.dealsSaved >= targets.dealsSaved) {
        setStatsValues(targets);
        clearInterval(timer);
      } else {
        setStatsValues({
          dealsSaved: Math.floor(current.dealsSaved),
          approved: Math.floor(current.approved),
          presentations: Math.floor(current.presentations)
        });
      }
    }, duration / steps);
  };
  
  return (
    <section className="why-choose-enhanced py-12 bg-gray-50" ref={sectionRef}>
      <div className="container mx-auto px-4">
        <h2 className="text-3xl font-bold text-center mb-8 text-gray-800">
          Why Developers & Investors Choose SpecSharp
        </h2>
        
        {/* Visual Comparison Grid */}
        <div className="max-w-5xl mx-auto grid md:grid-cols-2 gap-8 mb-12">
          
          {/* Traditional Method - Left Side */}
          <div className="comparison-side traditional">
            <h3 className="text-lg font-bold text-gray-700 mb-6 text-center">TRADITIONAL APPROACH</h3>
            <div className="space-y-5">
              {/* Investment Analysis */}
              <div className="metric-bar">
                <div className="flex justify-between text-sm mb-2">
                  <span className="font-medium">Investment Analysis</span>
                  <span className="text-red-600 font-semibold">Manual Excel</span>
                </div>
                <div className="h-3 bg-red-100 rounded-full overflow-hidden">
                  <motion.div 
                    className="h-3 bg-red-500 rounded-full"
                    initial={{ width: 0 }}
                    animate={{ width: `${animatedValues.traditional.investment}%` }}
                    transition={{ duration: 0.8, ease: "easeOut" }}
                  />
                </div>
              </div>
              
              {/* Scenario Comparison */}
              <div className="metric-bar">
                <div className="flex justify-between text-sm mb-2">
                  <span className="font-medium">Scenario Comparison</span>
                  <span className="text-orange-600 font-semibold">Hours per scenario</span>
                </div>
                <div className="h-3 bg-orange-100 rounded-full overflow-hidden">
                  <motion.div 
                    className="h-3 bg-orange-500 rounded-full"
                    initial={{ width: 0 }}
                    animate={{ width: `${animatedValues.traditional.scenarios}%` }}
                    transition={{ duration: 0.8, ease: "easeOut", delay: 0.2 }}
                  />
                </div>
              </div>
              
              {/* Complete Costs */}
              <div className="metric-bar">
                <div className="flex justify-between text-sm mb-2">
                  <span className="font-medium">Complete Costs</span>
                  <span className="text-yellow-600 font-semibold">Construction only</span>
                </div>
                <div className="h-3 bg-yellow-100 rounded-full overflow-hidden">
                  <motion.div 
                    className="h-3 bg-yellow-500 rounded-full"
                    initial={{ width: 0 }}
                    animate={{ width: `${animatedValues.traditional.costs}%` }}
                    transition={{ duration: 0.8, ease: "easeOut", delay: 0.4 }}
                  />
                </div>
              </div>
              
              {/* Decision Guidance */}
              <div className="metric-bar">
                <div className="flex justify-between text-sm mb-2">
                  <span className="font-medium">Decision Guidance</span>
                  <span className="text-gray-600 font-semibold">None</span>
                </div>
                <div className="h-3 bg-gray-100 rounded-full overflow-hidden">
                  <motion.div 
                    className="h-3 bg-gray-400 rounded-full"
                    initial={{ width: 0 }}
                    animate={{ width: `${animatedValues.traditional.guidance}%` }}
                    transition={{ duration: 0.8, ease: "easeOut", delay: 0.6 }}
                  />
                </div>
              </div>
              
              {/* Pain Points */}
              <div className="mt-6 p-4 bg-red-50 border border-red-200 rounded-lg">
                <ul className="text-sm text-red-700 space-y-2">
                  <li>❌ Pay architects before knowing if project works</li>
                  <li>❌ Missing soft costs surprises at closing</li>
                  <li>❌ No clear path when project doesn't pencil</li>
                </ul>
              </div>
            </div>
          </div>
          
          {/* SpecSharp - Right Side */}
          <div className="comparison-side specsharp">
            <h3 className="text-lg font-bold text-blue-600 mb-6 text-center">WITH SPECSHARP</h3>
            <div className="space-y-5">
              {/* Investment Analysis */}
              <div className="metric-bar">
                <div className="flex justify-between text-sm mb-2">
                  <span className="font-medium">Investment Analysis</span>
                  <span className="text-green-600 font-semibold">Instant IRR/NPV</span>
                </div>
                <div className="h-3 bg-green-100 rounded-full overflow-hidden">
                  <motion.div 
                    className="h-3 bg-green-500 rounded-full"
                    initial={{ width: 0 }}
                    animate={{ width: `${animatedValues.specsharp.investment}%` }}
                    transition={{ duration: 0.8, ease: "easeOut" }}
                  />
                </div>
              </div>
              
              {/* Scenario Comparison */}
              <div className="metric-bar">
                <div className="flex justify-between text-sm mb-2">
                  <span className="font-medium">Scenario Comparison</span>
                  <span className="text-green-600 font-semibold">10+ in 60 seconds</span>
                </div>
                <div className="h-3 bg-green-100 rounded-full overflow-hidden">
                  <motion.div 
                    className="h-3 bg-green-500 rounded-full"
                    initial={{ width: 0 }}
                    animate={{ width: `${animatedValues.specsharp.scenarios}%` }}
                    transition={{ duration: 0.8, ease: "easeOut", delay: 0.2 }}
                  />
                </div>
              </div>
              
              {/* Complete Costs */}
              <div className="metric-bar">
                <div className="flex justify-between text-sm mb-2">
                  <span className="font-medium">Complete Costs</span>
                  <span className="text-green-600 font-semibold">All-in with land & financing</span>
                </div>
                <div className="h-3 bg-green-100 rounded-full overflow-hidden">
                  <motion.div 
                    className="h-3 bg-green-500 rounded-full"
                    initial={{ width: 0 }}
                    animate={{ width: `${animatedValues.specsharp.costs}%` }}
                    transition={{ duration: 0.8, ease: "easeOut", delay: 0.4 }}
                  />
                </div>
              </div>
              
              {/* Decision Guidance */}
              <div className="metric-bar">
                <div className="flex justify-between text-sm mb-2">
                  <span className="font-medium">Decision Guidance</span>
                  <span className="text-green-600 font-semibold">Specific improvements</span>
                </div>
                <div className="h-3 bg-green-100 rounded-full overflow-hidden">
                  <motion.div 
                    className="h-3 bg-green-500 rounded-full"
                    initial={{ width: 0 }}
                    animate={{ width: `${animatedValues.specsharp.guidance}%` }}
                    transition={{ duration: 0.8, ease: "easeOut", delay: 0.6 }}
                  />
                </div>
              </div>
              
              {/* Benefits */}
              <div className="mt-6 p-4 bg-green-50 border border-green-200 rounded-lg">
                <ul className="text-sm text-green-700 space-y-2">
                  <li>✅ Know if deal works before LOI</li>
                  <li>✅ Complete investment picture day one</li>
                  <li>✅ Clear path to make any project feasible</li>
                </ul>
              </div>
            </div>
          </div>
        </div>

        {/* Key Metrics Section */}
        <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
          
          {/* Deals Saved */}
          <motion.div 
            className="metric-card text-center bg-white p-6 rounded-xl shadow-lg"
            initial={{ opacity: 0, y: 20 }}
            animate={isInView ? { opacity: 1, y: 0 } : {}}
            transition={{ delay: 0.6 }}
          >
            <span className="text-4xl mb-3 block">💰</span>
            <h3 className="font-bold text-xl mb-3 text-gray-800">Deals Saved</h3>
            <div className="text-4xl font-bold text-red-600 mb-2">${statsValues.dealsSaved}M</div>
            <p className="text-sm text-gray-600">In avoided bad investments</p>
          </motion.div>

          {/* Projects Approved */}
          <motion.div 
            className="metric-card text-center bg-white p-6 rounded-xl shadow-lg"
            initial={{ opacity: 0, y: 20 }}
            animate={isInView ? { opacity: 1, y: 0 } : {}}
            transition={{ delay: 0.7 }}
          >
            <span className="text-4xl mb-3 block">✅</span>
            <h3 className="font-bold text-xl mb-3 text-gray-800">Projects Approved</h3>
            <div className="text-4xl font-bold text-green-600 mb-2">{statsValues.approved}%</div>
            <p className="text-sm text-gray-600">After scenario optimization</p>
          </motion.div>

          {/* Board Presentations */}
          <motion.div 
            className="metric-card text-center bg-white p-6 rounded-xl shadow-lg"
            initial={{ opacity: 0, y: 20 }}
            animate={isInView ? { opacity: 1, y: 0 } : {}}
            transition={{ delay: 0.8 }}
          >
            <span className="text-4xl mb-3 block">📊</span>
            <h3 className="font-bold text-xl mb-3 text-gray-800">Board Presentations</h3>
            <div className="text-4xl font-bold text-blue-600 mb-2">{statsValues.presentations.toLocaleString()}+</div>
            <p className="text-sm text-gray-600">Generated for investment committees</p>
          </motion.div>
        </div>
      </div>
    </section>
  );
};

export default WhyChooseEnhanced;