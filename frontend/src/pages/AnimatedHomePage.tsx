import React, { useEffect } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { ArrowRight, Clock, DollarSign, CheckCircle, Building, Calculator } from 'lucide-react';
import { ROICalculator } from '../components/ROICalculator';
import { useSmoothScroll, useScrollAnimation } from '../hooks/useSmoothScroll';

// Animation variants
const fadeInUp = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0 }
};

const fadeInLeft = {
  hidden: { opacity: 0, x: -20 },
  visible: { opacity: 1, x: 0 }
};

const fadeInRight = {
  hidden: { opacity: 0, x: 20 },
  visible: { opacity: 1, x: 0 }
};

const scaleIn = {
  hidden: { opacity: 0, scale: 0.8 },
  visible: { opacity: 1, scale: 1 }
};

export const AnimatedHomePage: React.FC = () => {
  useSmoothScroll();
  useScrollAnimation();

  return (
    <div className="min-h-screen overflow-hidden">
      {/* Scroll Progress Bar */}
      <div 
        id="scroll-progress" 
        className="fixed top-0 left-0 h-1 bg-blue-600 z-50 transition-all duration-300"
        style={{ width: '0%' }}
      />

      {/* Hero Section */}
      <section className="bg-gradient-to-br from-blue-600 to-blue-800 text-white py-20 relative">
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute -top-40 -right-40 w-80 h-80 bg-blue-500 rounded-full opacity-20 animate-pulse" />
          <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-blue-700 rounded-full opacity-20 animate-pulse animation-delay-2000" />
        </div>
        
        <div className="container mx-auto px-4 relative z-10">
          <motion.div 
            className="max-w-4xl mx-auto text-center"
            initial="hidden"
            animate="visible"
            transition={{ staggerChildren: 0.2 }}
          >
            <motion.h1 
              className="text-5xl md:text-6xl font-bold mb-6"
              variants={fadeInUp}
              transition={{ duration: 0.6 }}
            >
              Your Estimator Costs $6,500/month.
              <motion.span 
                className="block text-yellow-300 mt-2"
                variants={fadeInUp}
                transition={{ duration: 0.6, delay: 0.2 }}
              >
                We Cost $799.
              </motion.span>
            </motion.h1>
            
            <motion.p 
              className="text-xl md:text-2xl mb-8 text-blue-100"
              variants={fadeInUp}
              transition={{ duration: 0.6, delay: 0.4 }}
            >
              Create professional construction estimates in 90 seconds instead of 3 hours.
            </motion.p>
            
            <motion.div 
              className="flex flex-col sm:flex-row gap-4 justify-center"
              variants={fadeInUp}
              transition={{ duration: 0.6, delay: 0.6 }}
            >
              <Link
                to="/demo"
                className="bg-yellow-400 text-blue-900 px-8 py-4 rounded-lg font-bold text-lg hover:bg-yellow-300 transition-all duration-300 inline-flex items-center justify-center hover:scale-105 transform"
              >
                Try It Now - No Signup Required <ArrowRight className="ml-2" />
              </Link>
              <a
                href="#roi-calculator"
                className="bg-transparent border-2 border-white text-white px-8 py-4 rounded-lg font-bold text-lg hover:bg-white hover:text-blue-800 transition-all duration-300 inline-flex items-center justify-center hover:scale-105 transform"
              >
                Calculate Your ROI <Calculator className="ml-2" />
              </a>
            </motion.div>
          </motion.div>
        </div>
      </section>

      {/* Quick Value Props */}
      <section className="py-16 bg-gray-50">
        <div className="container mx-auto px-4">
          <motion.div 
            className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto"
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, amount: 0.3 }}
            transition={{ staggerChildren: 0.2 }}
          >
            <motion.div 
              className="text-center"
              variants={scaleIn}
              transition={{ duration: 0.5 }}
              data-animate
            >
              <motion.div 
                className="bg-blue-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4"
                whileHover={{ scale: 1.1, rotate: 360 }}
                transition={{ duration: 0.3 }}
              >
                <Clock className="w-8 h-8 text-blue-600" />
              </motion.div>
              <h3 className="text-xl font-bold mb-2">90 Second Estimates</h3>
              <p className="text-gray-600">
                Type a description. Get a detailed scope. It's that simple.
              </p>
            </motion.div>
            
            <motion.div 
              className="text-center"
              variants={scaleIn}
              transition={{ duration: 0.5, delay: 0.1 }}
              data-animate
            >
              <motion.div 
                className="bg-green-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4"
                whileHover={{ scale: 1.1, rotate: 360 }}
                transition={{ duration: 0.3 }}
              >
                <Building className="w-8 h-8 text-green-600" />
              </motion.div>
              <h3 className="text-xl font-bold mb-2">All Building Types</h3>
              <p className="text-gray-600">
                Office, medical, schools, hotels, industrial - we've got them all.
              </p>
            </motion.div>
            
            <motion.div 
              className="text-center"
              variants={scaleIn}
              transition={{ duration: 0.5, delay: 0.2 }}
              data-animate
            >
              <motion.div 
                className="bg-purple-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4"
                whileHover={{ scale: 1.1, rotate: 360 }}
                transition={{ duration: 0.3 }}
              >
                <DollarSign className="w-8 h-8 text-purple-600" />
              </motion.div>
              <h3 className="text-xl font-bold mb-2">Regional Pricing</h3>
              <p className="text-gray-600">
                Accurate costs for your location, not national averages.
              </p>
            </motion.div>
          </motion.div>
        </div>
      </section>

      {/* ROI Calculator Section */}
      <section id="roi-calculator" className="py-20 bg-white">
        <div className="container mx-auto px-4">
          <motion.div 
            className="text-center mb-12"
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            variants={fadeInUp}
            transition={{ duration: 0.6 }}
          >
            <h2 className="text-4xl font-bold mb-4">
              See Your Monthly Savings
            </h2>
            <p className="text-xl text-gray-600">
              Most contractors save 20-40 hours per month with SpecSharp
            </p>
          </motion.div>
          
          <motion.div
            initial={{ opacity: 0, y: 40 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.8 }}
          >
            <ROICalculator />
          </motion.div>
        </div>
      </section>

      {/* How It Works */}
      <section className="py-20 bg-gray-50">
        <div className="container mx-auto px-4">
          <motion.h2 
            className="text-4xl font-bold text-center mb-12"
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            variants={fadeInUp}
            transition={{ duration: 0.6 }}
          >
            How It Works
          </motion.h2>
          
          <div className="max-w-4xl mx-auto">
            <div className="space-y-8">
              {/* Step 1 */}
              <motion.div 
                className="flex items-start space-x-4"
                initial="hidden"
                whileInView="visible"
                viewport={{ once: true }}
                variants={fadeInLeft}
                transition={{ duration: 0.6 }}
                data-animate
              >
                <motion.div 
                  className="bg-blue-600 text-white w-10 h-10 rounded-full flex items-center justify-center font-bold flex-shrink-0"
                  whileHover={{ scale: 1.2 }}
                >
                  1
                </motion.div>
                <div>
                  <h3 className="text-xl font-bold mb-2">
                    Describe Your Project
                  </h3>
                  <p className="text-gray-600 mb-3">
                    Type something like "100,000 sf medical office building with surgery center in Nashua, New Hampshire"
                  </p>
                  <motion.div 
                    className="bg-gray-100 p-4 rounded-lg font-mono text-sm"
                    whileHover={{ scale: 1.02 }}
                    transition={{ type: "spring", stiffness: 300 }}
                  >
                    "200 room hotel with conference center and restaurant in Nashville, Tennessee"
                  </motion.div>
                </div>
              </motion.div>

              {/* Step 2 */}
              <motion.div 
                className="flex items-start space-x-4"
                initial="hidden"
                whileInView="visible"
                viewport={{ once: true }}
                variants={fadeInRight}
                transition={{ duration: 0.6, delay: 0.2 }}
                data-animate
              >
                <motion.div 
                  className="bg-blue-600 text-white w-10 h-10 rounded-full flex items-center justify-center font-bold flex-shrink-0"
                  whileHover={{ scale: 1.2 }}
                >
                  2
                </motion.div>
                <div>
                  <h3 className="text-xl font-bold mb-2">
                    Get Instant Detailed Scope
                  </h3>
                  <p className="text-gray-600 mb-3">
                    SpecSharp generates 200+ line items with quantities, costs, and trade breakdowns
                  </p>
                  <div className="grid grid-cols-2 gap-4">
                    <motion.div 
                      className="bg-white p-3 rounded border"
                      whileHover={{ scale: 1.05, boxShadow: "0 10px 20px rgba(0,0,0,0.1)" }}
                    >
                      <p className="font-semibold">Mechanical</p>
                      <p className="text-2xl font-bold text-blue-600">$13.7M</p>
                    </motion.div>
                    <motion.div 
                      className="bg-white p-3 rounded border"
                      whileHover={{ scale: 1.05, boxShadow: "0 10px 20px rgba(0,0,0,0.1)" }}
                    >
                      <p className="font-semibold">Electrical</p>
                      <p className="text-2xl font-bold text-blue-600">$8.2M</p>
                    </motion.div>
                  </div>
                </div>
              </motion.div>

              {/* Step 3 */}
              <motion.div 
                className="flex items-start space-x-4"
                initial="hidden"
                whileInView="visible"
                viewport={{ once: true }}
                variants={fadeInLeft}
                transition={{ duration: 0.6, delay: 0.4 }}
                data-animate
              >
                <motion.div 
                  className="bg-blue-600 text-white w-10 h-10 rounded-full flex items-center justify-center font-bold flex-shrink-0"
                  whileHover={{ scale: 1.2 }}
                >
                  3
                </motion.div>
                <div>
                  <h3 className="text-xl font-bold mb-2">
                    Export and Share
                  </h3>
                  <p className="text-gray-600 mb-3">
                    Download Excel with formulas, PDF reports, or share with your team
                  </p>
                  <div className="flex space-x-4">
                    {['Excel Export', 'PDF Reports', 'Share Links'].map((item, index) => (
                      <motion.span 
                        key={item}
                        className="bg-green-100 text-green-700 px-4 py-2 rounded-lg font-medium"
                        initial={{ opacity: 0, scale: 0 }}
                        whileInView={{ opacity: 1, scale: 1 }}
                        viewport={{ once: true }}
                        transition={{ duration: 0.3, delay: 0.6 + index * 0.1 }}
                        whileHover={{ scale: 1.1 }}
                      >
                        ✓ {item}
                      </motion.span>
                    ))}
                  </div>
                </div>
              </motion.div>
            </div>
          </div>
        </div>
      </section>

      {/* Testimonial */}
      <section className="py-20 bg-blue-600 text-white relative overflow-hidden">
        <div className="absolute inset-0">
          <div className="absolute top-0 left-0 w-full h-full opacity-10">
            <svg className="w-full h-full" viewBox="0 0 100 100" preserveAspectRatio="none">
              <path d="M0,50 Q50,0 100,50 T200,50" stroke="currentColor" strokeWidth="0.5" fill="none" />
              <path d="M0,60 Q50,20 100,60 T200,60" stroke="currentColor" strokeWidth="0.5" fill="none" />
              <path d="M0,70 Q50,40 100,70 T200,70" stroke="currentColor" strokeWidth="0.5" fill="none" />
            </svg>
          </div>
        </div>
        
        <motion.div 
          className="container mx-auto px-4 relative z-10"
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          variants={scaleIn}
          transition={{ duration: 0.8 }}
        >
          <div className="max-w-3xl mx-auto text-center">
            <motion.p 
              className="text-2xl italic mb-6"
              variants={fadeInUp}
            >
              "We've cut our preliminary estimating time by 85%. 
              What used to take 3 days now takes 30 minutes."
            </motion.p>
            <motion.p 
              className="font-bold text-lg"
              variants={fadeInUp}
              transition={{ delay: 0.2 }}
            >
              Sarah Chen, Chief Estimator
            </motion.p>
            <motion.p 
              className="text-blue-200"
              variants={fadeInUp}
              transition={{ delay: 0.3 }}
            >
              Turner Construction
            </motion.p>
          </div>
        </motion.div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gray-900 text-white">
        <motion.div 
          className="container mx-auto px-4 text-center"
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          transition={{ staggerChildren: 0.2 }}
        >
          <motion.h2 
            className="text-4xl font-bold mb-6"
            variants={fadeInUp}
          >
            Ready to Save 40 Hours a Month?
          </motion.h2>
          <motion.p 
            className="text-xl mb-8 text-gray-300"
            variants={fadeInUp}
          >
            Join 500+ contractors already using SpecSharp
          </motion.p>
          <motion.div
            variants={fadeInUp}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <Link
              to="/demo"
              className="bg-yellow-400 text-gray-900 px-8 py-4 rounded-lg font-bold text-lg hover:bg-yellow-300 transition-colors inline-flex items-center"
            >
              Try Demo Now - No Signup Required <ArrowRight className="ml-2" />
            </Link>
          </motion.div>
          <motion.p 
            className="mt-4 text-gray-400"
            variants={fadeInUp}
          >
            No credit card required • 14-day free trial • Cancel anytime
          </motion.p>
        </motion.div>
      </section>
    </div>
  );
};