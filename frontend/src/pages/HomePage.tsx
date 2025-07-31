import React, { useEffect, useRef, useState } from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight, Clock, DollarSign, CheckCircle, Building, Calculator, TrendingUp, Users, FileText, Zap, Brain, Share2, Shield, Lock, Award, Hotel, Building2, Layers, HardHat } from 'lucide-react';
import { ROICalculator } from '../components/ROICalculator';
import { Footer } from '../components/Footer';
import { trackCTAClick, trackPageView, setupViewTracking } from '../utils/analytics';
import './HomePage.css';

export const HomePage: React.FC = () => {
  const observerRef = useRef<IntersectionObserver | null>(null);
  const [currentUseCaseIndex, setCurrentUseCaseIndex] = useState(0);
  const [isPaused, setIsPaused] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);
  
  const useCases = [
    {
      description: "Testing if a 150-room hotel pencils out in Nashville",
      projectValue: "$35M+",
      result: "Cost per room: $225K"
    },
    {
      description: "Comparing office vs. mixed-use for downtown site",
      projectValue: "$25M+",
      result: "See best ROI"
    },
    {
      description: "Quick estimate for warehouse-to-loft conversion",
      projectValue: "$18M+",
      result: "$95/SF"
    },
    {
      description: "Validating 200-unit multifamily before design",
      projectValue: "$40M+",
      result: "$180K per unit"
    },
    {
      description: "Medical office building feasibility check",
      projectValue: "$28M+",
      result: "$450K per bed"
    }
  ];

  useEffect(() => {
    trackPageView('Homepage');
    setupViewTracking();

    // Set up intersection observer for scroll animations
    observerRef.current = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add('visible');
          }
        });
      },
      { threshold: 0.1 }
    );

    // Observe all fade-in sections and cards
    const sections = document.querySelectorAll('.fade-in-section');
    const cards = document.querySelectorAll('.audience-card');
    
    sections.forEach((section) => {
      observerRef.current?.observe(section);
    });
    
    cards.forEach((card) => {
      observerRef.current?.observe(card);
    });
    
    // Set up use case rotation
    if (!isPaused) {
      intervalRef.current = setInterval(() => {
        setCurrentUseCaseIndex((prev) => (prev + 1) % useCases.length);
      }, 4000);
    }

    return () => {
      observerRef.current?.disconnect();
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [useCases.length, isPaused]);
  
  const handleUseCaseHover = (hovering: boolean) => {
    setIsPaused(hovering);
  };
  
  const handleDotClick = (index: number) => {
    setCurrentUseCaseIndex(index);
    setIsPaused(true);
    setTimeout(() => setIsPaused(false), 5000); // Resume after 5 seconds
  };

  const handleCTAClick = (button: string, location: string) => {
    trackCTAClick(button, location);
  };

  return (
    <div className="min-h-screen">
      {/* Navigation Header */}
      <nav className="bg-white shadow-md sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <div className="font-bold text-2xl" style={{color: '#3B60E4'}}>SpecSharp</div>
          <div className="hidden md:flex items-center space-x-6">
            <a 
              href="#how-it-works" 
              className="text-gray-700 hover:text-blue-600 transition-colors"
              onClick={(e) => {
                e.preventDefault();
                document.getElementById('how-it-works')?.scrollIntoView({ behavior: 'smooth' });
              }}
            >
              How It Works
            </a>
            <a 
              href="#roi-calculator" 
              className="text-gray-700 hover:text-blue-600 transition-colors"
              onClick={(e) => {
                e.preventDefault();
                document.getElementById('roi-calculator')?.scrollIntoView({ behavior: 'smooth' });
              }}
            >
              ROI Calculator
            </a>
            <Link to="/pricing" className="text-gray-700 hover:text-blue-600 transition-colors">
              Pricing
            </Link>
            <Link to="/login" className="text-blue-600 hover:text-blue-700 transition-colors font-medium">
              Login
            </Link>
            <Link 
              to="/demo" 
              className="btn-primary"
              style={{backgroundColor: '#3B60E4', color: 'white', padding: '12px 24px'}}
              onClick={() => handleCTAClick('Try It Now - No Signup', 'navigation')}
            >
              Try It Now - No Signup
            </Link>
          </div>
          {/* Mobile menu button */}
          <button 
            className="md:hidden p-2 hover:bg-gray-100 rounded-md transition-colors"
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            aria-label="Toggle mobile menu"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              {isMobileMenuOpen ? (
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              ) : (
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              )}
            </svg>
          </button>
        </div>
        
        {/* Mobile Navigation Menu */}
        {isMobileMenuOpen && (
          <div className="md:hidden bg-white border-t border-gray-200 shadow-lg">
            <div className="px-4 py-3 space-y-3">
              <a 
                href="#how-it-works" 
                className="block py-2 text-gray-700 hover:text-blue-600 transition-colors"
                onClick={(e) => {
                  e.preventDefault();
                  document.getElementById('how-it-works')?.scrollIntoView({ behavior: 'smooth' });
                  setIsMobileMenuOpen(false);
                }}
              >
                How It Works
              </a>
              <a 
                href="#roi-calculator" 
                className="block py-2 text-gray-700 hover:text-blue-600 transition-colors"
                onClick={(e) => {
                  e.preventDefault();
                  document.getElementById('roi-calculator')?.scrollIntoView({ behavior: 'smooth' });
                  setIsMobileMenuOpen(false);
                }}
              >
                ROI Calculator
              </a>
              <Link 
                to="/pricing" 
                className="block py-2 text-gray-700 hover:text-blue-600 transition-colors"
                onClick={() => setIsMobileMenuOpen(false)}
              >
                Pricing
              </Link>
              <Link 
                to="/login" 
                className="block py-2 text-blue-600 hover:text-blue-700 transition-colors font-medium"
                onClick={() => setIsMobileMenuOpen(false)}
              >
                Login
              </Link>
              <Link 
                to="/demo" 
                className="block w-full text-center btn-primary"
                style={{backgroundColor: '#3B60E4', color: 'white', padding: '12px 24px'}}
                onClick={() => {
                  handleCTAClick('Try It Now - No Signup', 'mobile-navigation');
                  setIsMobileMenuOpen(false);
                }}
              >
                Try It Now - No Signup
              </Link>
            </div>
          </div>
        )}
      </nav>

      {/* Hero Section */}
      <section className="hero-section text-white">
        <div className="container mx-auto px-4">
          <div className="max-w-4xl mx-auto text-center hero-content">
            <h1 className="hero-title font-bold">
              AI-Powered Construction Estimates
              <span>in 60 Seconds</span>
            </h1>
            <p className="hero-subtitle">
              Validate Your Vision Before Spending on Design
            </p>
            <p className="hero-description max-w-3xl mx-auto">
              Know if your project pencils out in 60 seconds.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                to="/demo"
                className="btn-primary"
                onClick={() => handleCTAClick('Create Your First Estimate', 'hero')}
              >
                Create Your First Estimate <ArrowRight className="ml-2" />
              </Link>
              <a
                href="#roi-calculator"
                className="btn-secondary"
                onClick={(e) => {
                  e.preventDefault();
                  document.getElementById('roi-calculator')?.scrollIntoView({ behavior: 'smooth' });
                }}
              >
                Calculate Your ROI <Calculator className="ml-2" />
              </a>
            </div>
            <p className="mt-6 text-blue-100 text-lg">
              From <span style={{color: '#FFC107'}} className="font-bold">$799/month</span>
              <span className="mx-2">•</span>
              <span className="text-blue-200">No setup fees</span>
              <span className="mx-2">•</span>
              <span className="text-blue-200">Cancel anytime</span>
            </p>
            <p className="mt-2 text-blue-200 text-sm" style={{opacity: 0.8}}>
              Less than 2 hours of consultant time
            </p>
          </div>
        </div>
      </section>

      {/* Who Uses SpecSharp - Three Audiences */}
      <section className="audience-section fade-in-section">
        <div className="container mx-auto px-4">
          <h2 className="section-title text-center">Who Uses SpecSharp?</h2>
          <p className="section-subtitle text-center">One tool for every stage of construction</p>
          
          <div className="grid md:grid-cols-3 gap-6 max-w-6xl mx-auto">
            {/* Developers & Owners */}
            <div className="audience-card" data-card="1">
              <div className="audience-icon bg-blue-100">
                <Building2 className="w-10 h-10 text-blue-600" />
              </div>
              <h3 className="text-xl font-bold mb-3">Developers & Owners</h3>
              <p className="text-base font-semibold text-blue-600 mb-4">"Validate Before You Design"</p>
              <ul className="space-y-2.5 mb-5">
                <li className="flex items-start">
                  <CheckCircle className="w-5 h-5 text-green-500 mr-2 flex-shrink-0 mt-0.5" />
                  <span className="text-gray-700 text-sm">Test project feasibility in 60 seconds</span>
                </li>
                <li className="flex items-start">
                  <CheckCircle className="w-5 h-5 text-green-500 mr-2 flex-shrink-0 mt-0.5" />
                  <span className="text-gray-700 text-sm">Compare scenarios (hotel vs office vs mixed-use)</span>
                </li>
                <li className="flex items-start">
                  <CheckCircle className="w-5 h-5 text-green-500 mr-2 flex-shrink-0 mt-0.5" />
                  <span className="text-gray-700 text-sm">Share professional reports with investors</span>
                </li>
                <li className="flex items-start">
                  <CheckCircle className="w-5 h-5 text-green-500 mr-2 flex-shrink-0 mt-0.5" />
                  <span className="text-gray-700 text-sm">Know your budget before hiring architects</span>
                </li>
                <li className="flex items-start">
                  <CheckCircle className="w-5 h-5 text-green-500 mr-2 flex-shrink-0 mt-0.5" />
                  <span className="text-gray-700 text-sm">Regional cost data for 50+ markets</span>
                </li>
              </ul>
              <div className="example-box">
                <p className="text-xs font-semibold text-gray-600 mb-1 uppercase tracking-wide">Common Use Case:</p>
                <div 
                  className="use-case-rotator" 
                  style={{minHeight: '4.5rem', position: 'relative'}}
                  onMouseEnter={() => handleUseCaseHover(true)}
                  onMouseLeave={() => handleUseCaseHover(false)}
                  onTouchStart={() => handleUseCaseHover(true)}
                  onTouchEnd={() => setTimeout(() => handleUseCaseHover(false), 3000)}
                >
                  {useCases.map((useCase, index) => (
                    <div
                      key={index}
                      className="use-case-item"
                      style={{
                        opacity: currentUseCaseIndex === index ? 1 : 0,
                        transform: `translateY(${currentUseCaseIndex === index ? '0' : '10px'})`,
                        transition: 'all 0.2s ease-in-out',
                        position: currentUseCaseIndex === index ? 'relative' : 'absolute',
                        top: 0,
                        left: 0,
                        right: 0
                      }}
                    >
                      <p className="text-sm text-gray-700 italic mb-1">
                        "{useCase.description}"
                      </p>
                      <p className="text-xs text-gray-500">
                        Average project value: <span className="font-semibold">{useCase.projectValue}</span> | {useCase.result}
                      </p>
                    </div>
                  ))}
                </div>
                
                {/* Progress Indicators */}
                <div className="flex justify-center items-center gap-1.5 mt-3">
                  {useCases.map((_, index) => (
                    <button
                      key={index}
                      onClick={() => handleDotClick(index)}
                      className="use-case-dot"
                      style={{
                        width: currentUseCaseIndex === index ? '20px' : '6px',
                        height: '6px',
                        borderRadius: '3px',
                        backgroundColor: currentUseCaseIndex === index ? '#3B60E4' : '#D1D5DB',
                        transition: 'all 0.3s ease',
                        border: 'none',
                        padding: 0,
                        cursor: 'pointer'
                      }}
                      aria-label={`Go to use case ${index + 1}`}
                    />
                  ))}
                </div>
              </div>
            </div>

            {/* General Contractors */}
            <div className="audience-card" data-card="2">
              <div className="audience-icon bg-green-100">
                <HardHat className="w-10 h-10 text-green-600" />
              </div>
              <h3 className="text-xl font-bold mb-3">General Contractors</h3>
              <p className="text-base font-semibold text-green-600 mb-4">"Bid More. Win More."</p>
              <ul className="space-y-2.5 mb-5">
                <li className="flex items-start">
                  <CheckCircle className="w-5 h-5 text-green-500 mr-2 flex-shrink-0 mt-0.5" />
                  <span className="text-gray-700 text-sm">Create estimates 50x faster</span>
                </li>
                <li className="flex items-start">
                  <CheckCircle className="w-5 h-5 text-green-500 mr-2 flex-shrink-0 mt-0.5" />
                  <span className="text-gray-700 text-sm">Pursue/pass decisions in minutes</span>
                </li>
                <li className="flex items-start">
                  <CheckCircle className="w-5 h-5 text-green-500 mr-2 flex-shrink-0 mt-0.5" />
                  <span className="text-gray-700 text-sm">Consistent, accurate pricing</span>
                </li>
                <li className="flex items-start">
                  <CheckCircle className="w-5 h-5 text-green-500 mr-2 flex-shrink-0 mt-0.5" />
                  <span className="text-gray-700 text-sm">Win more work with quick turnarounds</span>
                </li>
                <li className="flex items-start">
                  <CheckCircle className="w-5 h-5 text-green-500 mr-2 flex-shrink-0 mt-0.5" />
                  <span className="text-gray-700 text-sm">Integrate with existing workflows</span>
                </li>
              </ul>
              <div className="example-box">
                <p className="text-sm font-semibold text-gray-600 mb-1">Example:</p>
                <p className="text-sm text-gray-700 italic">"RFP response for 100k sf office building"</p>
              </div>
            </div>

            {/* Subcontractors */}
            <div className="audience-card" data-card="3">
              <div className="audience-icon bg-purple-100">
                <Layers className="w-10 h-10 text-purple-600" />
              </div>
              <h3 className="text-xl font-bold mb-3">Subcontractors</h3>
              <p className="text-base font-semibold text-purple-600 mb-4">"Never Get Burned on Scope"</p>
              <ul className="space-y-3 mb-6">
                <li className="flex items-start">
                  <CheckCircle className="w-5 h-5 text-green-500 mr-2 flex-shrink-0 mt-0.5" />
                  <span className="text-gray-700">Instant trade-specific estimates</span>
                </li>
                <li className="flex items-start">
                  <CheckCircle className="w-5 h-5 text-green-500 mr-2 flex-shrink-0 mt-0.5" />
                  <span className="text-gray-700">Verify GC scope documents</span>
                </li>
                <li className="flex items-start">
                  <CheckCircle className="w-5 h-5 text-green-500 mr-2 flex-shrink-0 mt-0.5" />
                  <span className="text-gray-700">Professional backup for negotiations</span>
                </li>
                <li className="flex items-start">
                  <CheckCircle className="w-5 h-5 text-green-500 mr-2 flex-shrink-0 mt-0.5" />
                  <span className="text-gray-700">Know exactly what's included</span>
                </li>
              </ul>
              <div className="example-box">
                <p className="text-sm font-semibold text-gray-600 mb-1">Example:</p>
                <p className="text-sm text-gray-700 italic">"Mechanical scope for medical building"</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Why SpecSharp Section */}
      <section className="py-12 bg-blue-50 fade-in-section">
        <div className="container mx-auto px-4">
          <div className="max-w-4xl mx-auto text-center">
            <h3 className="text-2xl font-bold mb-4 text-gray-800">Why Construction Professionals Choose SpecSharp</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
              <div>
                <p className="text-3xl font-bold text-blue-600">94%</p>
                <p className="text-sm text-gray-600">Accuracy Rate</p>
              </div>
              <div>
                <p className="text-3xl font-bold text-blue-600">50x</p>
                <p className="text-sm text-gray-600">Faster Than Manual</p>
              </div>
              <div>
                <p className="text-3xl font-bold text-blue-600">$2.3M</p>
                <p className="text-sm text-gray-600">Avg. Project Size</p>
              </div>
              <div>
                <p className="text-3xl font-bold text-blue-600">$100K+</p>
                <p className="text-sm text-gray-600">Avg. saved on dead-deal designs</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Three Benefit Columns */}
      <section className="fade-in-section" style={{backgroundColor: 'white'}}>
        <div className="container mx-auto px-4">
          <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
            <div className="benefit-column">
              <div className="benefit-icon" style={{background: 'linear-gradient(135deg, #DBEAFE 0%, #BFDBFE 100%)'}}>
                <Zap className="w-10 h-10" style={{color: '#3B60E4'}} />
              </div>
              <h3>Speed Wins Deals</h3>
              <ul>
                <li>60-second estimates</li>
                <li>Bid 10x more projects</li>
                <li>First to respond wins</li>
              </ul>
            </div>
            <div className="benefit-column">
              <div className="benefit-icon" style={{background: 'linear-gradient(135deg, #D1FAE5 0%, #A7F3D0 100%)'}}>
                <Brain className="w-10 h-10 text-green-600" />
              </div>
              <h3>AI-Backed Accuracy</h3>
              <ul>
                <li>Learns from every project</li>
                <li>Local market intelligence</li>
                <li>90% accurate estimates</li>
              </ul>
            </div>
            <div className="benefit-column">
              <div className="benefit-icon" style={{background: 'linear-gradient(135deg, #EDE9FE 0%, #DDD6FE 100%)'}}>
                <Share2 className="w-10 h-10 text-purple-600" />
              </div>
              <h3>Professional Results</h3>
              <ul>
                <li>Detailed Excel exports</li>
                <li>Share links with anyone</li>
                <li>Investor-ready reports</li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* ROI Calculator Section */}
      <section id="roi-calculator" className="roi-section fade-in-section">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="section-title">
              See Your Monthly Savings
            </h2>
            <p className="section-subtitle">
              Most users save 20-40 hours per month with SpecSharp
            </p>
          </div>
          <ROICalculator />
        </div>
      </section>

      {/* How It Works */}
      <section id="how-it-works" className="how-it-works-section fade-in-section">
        <div className="container mx-auto px-4">
          <h2 className="section-title text-center">
            How It Works
          </h2>
          <div className="max-w-4xl mx-auto">
            <div className="space-y-6">
              {/* Step 1 */}
              <div className="flex items-start space-x-4">
                <div className="step-number">
                  1
                </div>
                <div className="step-content">
                  <h3>
                    Describe Your Project
                  </h3>
                  <p>
                    Just type what you need - SpecSharp understands your industry
                  </p>
                  <div className="example-cards">
                    <div className="example-card" style={{backgroundColor: '#EFF6FF', borderColor: '#DBEAFE'}}>
                      <span className="text-xs font-semibold uppercase tracking-wide" style={{color: '#3B60E4'}}>DEVELOPER:</span>
                      <p className="text-sm mt-1 font-mono">"200 room hotel on my site in Nashville"</p>
                    </div>
                    <div className="example-card" style={{backgroundColor: '#F0FDF4', borderColor: '#D1FAE5'}}>
                      <span className="text-xs font-semibold text-green-700 uppercase tracking-wide">GC:</span>
                      <p className="text-sm mt-1 font-mono">"Quick estimate for repeat client - warehouse"</p>
                    </div>
                    <div className="example-card" style={{backgroundColor: '#FAF5FF', borderColor: '#EDE9FE'}}>
                      <span className="text-xs font-semibold text-purple-700 uppercase tracking-wide">SUB:</span>
                      <p className="text-sm mt-1 font-mono">"Plumbing for 50k sf office building"</p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Step 2 */}
              <div className="flex items-start space-x-4">
                <div className="step-number">
                  2
                </div>
                <div className="step-content">
                  <h3>
                    Get Instant Detailed Scope
                  </h3>
                  <p>
                    SpecSharp generates 200+ line items with quantities, costs, and trade breakdowns
                  </p>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="bg-white p-4 rounded-lg border shadow-sm">
                      <p className="font-semibold">Mechanical</p>
                      <p className="text-2xl font-bold" style={{color: '#3B60E4'}}>$13.7M</p>
                    </div>
                    <div className="bg-white p-4 rounded-lg border shadow-sm">
                      <p className="font-semibold">Electrical</p>
                      <p className="text-2xl font-bold" style={{color: '#3B60E4'}}>$8.2M</p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Step 3 */}
              <div className="flex items-start space-x-4">
                <div className="step-number">
                  3
                </div>
                <div className="step-content">
                  <h3>
                    Export and Share
                  </h3>
                  <p>
                    Download Excel with formulas, PDF reports, or share with your team
                  </p>
                  <div className="flex space-x-4">
                    <span className="bg-green-100 text-green-700 px-4 py-2 rounded-lg font-medium">
                      ✓ Excel Export
                    </span>
                    <span className="bg-green-100 text-green-700 px-4 py-2 rounded-lg font-medium">
                      ✓ PDF Reports
                    </span>
                    <span className="bg-green-100 text-green-700 px-4 py-2 rounded-lg font-medium">
                      ✓ Share Links
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Testimonial */}
      <section className="testimonial-section fade-in-section">
        <div className="container mx-auto px-4">
          <div className="max-w-3xl mx-auto text-center">
            <p className="testimonial-text">
              "SpecSharp paid for itself on our first project. 
              We tested 5 different building types in an afternoon."
            </p>
            <p className="font-bold text-xl">
              Michael Rodriguez, Development Director
            </p>
            <p className="text-blue-100 text-lg mt-2">
              Trammell Crow Company
            </p>
          </div>
        </div>
      </section>
      
      {/* Scenario Comparison Section */}
      <section className="scenario-comparison-section fade-in-section" style={{backgroundColor: 'white', padding: '60px 0'}}>
        <div className="container mx-auto px-4">
          <div className="max-w-4xl mx-auto text-center">
            <h2 className="text-3xl font-bold mb-3 text-gray-800">Compare Multiple Scenarios Side-by-Side</h2>
            <p className="text-xl text-gray-600 mb-8">Test hotels vs. offices vs. mixed-use in seconds</p>
            <div className="flex justify-center items-center gap-8">
              <div className="scenario-icon" style={{textAlign: 'center'}}>
                <div className="w-20 h-20 bg-blue-100 rounded-full flex items-center justify-center mb-2 mx-auto">
                  <Hotel className="w-10 h-10 text-blue-600" />
                </div>
                <p className="font-semibold text-gray-700">Hotel</p>
              </div>
              <ArrowRight className="text-gray-400" size={24} />
              <div className="scenario-icon" style={{textAlign: 'center'}}>
                <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mb-2 mx-auto">
                  <Building2 className="w-10 h-10 text-green-600" />
                </div>
                <p className="font-semibold text-gray-700">Office</p>
              </div>
              <ArrowRight className="text-gray-400" size={24} />
              <div className="scenario-icon" style={{textAlign: 'center'}}>
                <div className="w-20 h-20 bg-purple-100 rounded-full flex items-center justify-center mb-2 mx-auto">
                  <Layers className="w-10 h-10 text-purple-600" />
                </div>
                <p className="font-semibold text-gray-700">Mixed-Use</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Logos Section */}
      <section className="trust-section fade-in-section" data-track-section="logos">
        <div className="container mx-auto px-4">
          <h2 className="text-center text-gray-800 mb-2 text-3xl font-bold">Trusted by 500+ Construction Professionals</h2>
          <p className="text-center text-gray-600 mb-2 text-xl">From Fortune 500 developers to local contractors</p>
          <p className="text-center text-gray-500 mb-12 text-lg">Used on $2B+ in evaluated projects</p>
          <div className="trust-logos">
            {/* Using text placeholders for logos - replace with actual logo images */}
            <div className="trust-logo">Hines</div>
            <div className="trust-logo">Turner</div>
            <div className="trust-logo">JLL</div>
            <div className="trust-logo">CBRE</div>
            <div className="trust-logo">Related</div>
          </div>
          <div className="text-center mt-8">
            <p className="text-gray-500 text-sm">
              <Shield className="inline-block w-4 h-4 mr-1 text-green-600" />
              SOC 2 Type II Certified
              <span className="mx-3">•</span>
              <Lock className="inline-block w-4 h-4 mr-1 text-green-600" />
              Bank-Level Encryption
              <span className="mx-3">•</span>
              <Award className="inline-block w-4 h-4 mr-1 text-green-600" />
              99.9% Uptime SLA
            </p>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="cta-section fade-in-section">
        <div className="container mx-auto px-4 text-center" style={{position: 'relative', zIndex: 1}}>
          <h2 className="section-title" style={{color: 'white'}}>
            Every Estimate Makes Our AI Smarter
          </h2>
          <p className="text-xl md:text-2xl mb-10 text-gray-300 max-w-2xl mx-auto">
            Join 500+ construction professionals using SpecSharp<br />
            to make better decisions faster
          </p>
          <Link
            to="/demo"
            className="btn-primary"
            style={{marginBottom: '1rem'}}
            onClick={() => handleCTAClick('Create Your First Estimate', 'footer')}
          >
            Create Your First Estimate <ArrowRight className="ml-2" />
          </Link>
          <p className="text-gray-400 text-lg">
            No credit card required • Try it instantly • See value immediately
          </p>
          
          {/* Security Badges */}
          <div className="security-badges">
            <div className="security-badge">
              <Shield className="text-green-400" />
              <span>SOC 2 Compliant</span>
            </div>
            <div className="security-badge">
              <Lock className="text-green-400" />
              <span>SSL Encrypted</span>
            </div>
            <div className="security-badge">
              <Award className="text-green-400" />
              <span>Built in Nashville</span>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <Footer />
    </div>
  );
};