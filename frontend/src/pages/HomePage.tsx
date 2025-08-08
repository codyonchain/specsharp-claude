import React, { useEffect, useRef, useState } from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight, CheckCircle, Calculator, Zap, Brain, Share2, Shield, Lock, Award, Building2, Layers, HardHat } from 'lucide-react';
import { ROICalculator } from '../components/ROICalculator';
import { Footer } from '../components/Footer';
import { trackCTAClick, trackPageView, setupViewTracking } from '../utils/analytics';
import HowItWorksInteractive from '../components/HowItWorks/HowItWorksInteractive';
import ScenarioComparison from '../components/ScenarioComparison/ScenarioComparison';
import WhyChooseEnhanced from '../components/WhyChooseEnhanced/WhyChooseEnhanced';
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
              href="#scenario-comparison" 
              className="text-gray-700 hover:text-blue-600 transition-colors"
              onClick={(e) => {
                e.preventDefault();
                document.getElementById('scenario-comparison')?.scrollIntoView({ behavior: 'smooth' });
              }}
            >
              Compare Scenarios
            </a>
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
                href="#scenario-comparison" 
                className="block py-2 text-gray-700 hover:text-blue-600 transition-colors"
                onClick={(e) => {
                  e.preventDefault();
                  document.getElementById('scenario-comparison')?.scrollIntoView({ behavior: 'smooth' });
                  setIsMobileMenuOpen(false);
                }}
              >
                Compare Scenarios
              </a>
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

      {/* Enhanced Hero Section */}
      <section className="relative min-h-[600px] overflow-hidden">
        {/* Animated gradient background */}
        <div className="absolute inset-0 bg-gradient-to-br from-blue-600 via-blue-500 to-purple-600">
          {/* Animated gradient overlay for movement */}
          <div className="absolute inset-0 bg-gradient-to-t from-blue-600/50 via-transparent to-purple-600/50 animate-gradient-shift"></div>
        </div>
        
        {/* Floating grid pattern for depth */}
        <div className="absolute inset-0 opacity-10">
          <div className="absolute inset-0" style={{
            backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.4'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`,
            backgroundSize: '60px 60px'
          }}></div>
        </div>
        
        {/* Animated floating particles */}
        <div className="absolute inset-0 overflow-hidden">
          <div className="particle particle-1"></div>
          <div className="particle particle-2"></div>
          <div className="particle particle-3"></div>
          <div className="particle particle-4"></div>
        </div>
        
        {/* Subtle pulse rings emanating from center */}
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2">
          <div className="absolute w-96 h-96 border border-white/10 rounded-full animate-pulse-ring"></div>
          <div className="absolute w-96 h-96 border border-white/10 rounded-full animate-pulse-ring animation-delay-2"></div>
          <div className="absolute w-96 h-96 border border-white/10 rounded-full animate-pulse-ring animation-delay-4"></div>
        </div>
        
        {/* Main content - now with relative positioning */}
        <div className="relative z-10 container mx-auto px-4 py-20">
          <div className="text-center max-w-4xl mx-auto">
            {/* Animated badge */}
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-white/20 backdrop-blur-sm rounded-full mb-6 animate-fade-in-down">
              <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
              <span className="text-sm font-medium text-white">Trusted by 500+ Construction Pros</span>
            </div>
            
            {/* Main headline with stagger animation */}
            <h1 className="text-5xl md:text-6xl font-bold text-white mb-4">
              <span className="inline-block animate-fade-in-up">AI-Powered</span>{' '}
              <span className="inline-block animate-fade-in-up animation-delay-1">Construction</span>{' '}
              <span className="inline-block animate-fade-in-up animation-delay-2">Estimates</span>
            </h1>
            
            {/* Highlight the 60 seconds with special treatment */}
            <div className="text-3xl md:text-4xl text-yellow-400 font-bold mb-6 animate-fade-in-up animation-delay-3">
              in 60 Seconds
              <span className="inline-block ml-2 text-lg text-yellow-300 animate-pulse">⚡</span>
            </div>
            
            <p className="text-xl text-blue-100 mb-4 animate-fade-in-up animation-delay-4">
              Validate Your Vision Before Spending on Design
            </p>
            
            <p className="text-lg text-blue-200 mb-8 animate-fade-in-up animation-delay-5">
              Know if your project pencils out in 60 seconds.
            </p>
            
            {/* Buttons with hover effects */}
            <div className="flex flex-col sm:flex-row gap-4 justify-center animate-fade-in-up animation-delay-6">
              <Link
                to="/demo"
                className="group px-8 py-4 bg-yellow-400 text-gray-900 rounded-lg font-bold text-lg hover:bg-yellow-300 transform hover:scale-105 transition-all duration-200 shadow-xl hover:shadow-2xl"
                onClick={() => handleCTAClick('Create Your First Estimate', 'hero')}
              >
                Create Your First Estimate
                <span className="inline-block ml-2 group-hover:translate-x-1 transition-transform">→</span>
              </Link>
              <a
                href="#scenario-comparison"
                className="px-8 py-4 bg-white/10 backdrop-blur-sm text-white rounded-lg font-bold text-lg border-2 border-white/30 hover:bg-white/20 transform hover:scale-105 transition-all duration-200"
                onClick={(e) => {
                  e.preventDefault();
                  document.getElementById('scenario-comparison')?.scrollIntoView({ behavior: 'smooth' });
                }}
              >
                Compare Scenarios
                <span className="inline-block ml-2">📊</span>
              </a>
            </div>
            
            <p className="text-blue-200 mt-8 animate-fade-in-up animation-delay-7">
              Finally. Cost certainty before design commitment.
            </p>
          </div>
        </div>
        
        {/* Bottom wave for transition to next section */}
        <div className="absolute bottom-0 left-0 right-0">
          <svg viewBox="0 0 1440 120" className="w-full h-20 fill-white">
            <path d="M0,64 C240,120 480,0 720,48 C960,96 1200,16 1440,64 L1440,120 L0,120 Z" />
          </svg>
        </div>
      </section>

      {/* How It Works - Interactive Version (MOVED UP TO #2) */}
      <div id="how-it-works">
        <HowItWorksInteractive />
      </div>

      {/* Scenario Comparison - Interactive Version (MOVED UP TO #3) */}
      <div id="scenario-comparison">
        <ScenarioComparison />
      </div>

      {/* Why Choose SpecSharp - Enhanced Version (NOW #4 with new design) */}
      <WhyChooseEnhanced />

      {/* Who Uses SpecSharp - Three Audiences (MOVED DOWN TO #5) */}
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
                  <span className="text-gray-700">Produce common scope requirements for various project types</span>
                </li>
                <li className="flex items-start">
                  <CheckCircle className="w-5 h-5 text-green-500 mr-2 flex-shrink-0 mt-0.5" />
                  <span className="text-gray-700">Professional backup for negotiations</span>
                </li>
                <li className="flex items-start">
                  <CheckCircle className="w-5 h-5 text-green-500 mr-2 flex-shrink-0 mt-0.5" />
                  <span className="text-gray-700">Quickly generate client requested pricing</span>
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

      {/* Logos Section (MOVED UP TO #6) */}
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

      {/* Personalized Demo Section - Replaces ROI Calculator for Warm Leads */}
      <section className="py-16 bg-white">
        <div className="container mx-auto px-4">
          <div className="max-w-4xl mx-auto">
            <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl p-12 text-white relative">
              {/* Early Access Badge */}
              <div className="absolute top-6 right-6">
                <div className="inline-flex items-center gap-2 px-3 py-1 bg-white/20 backdrop-blur rounded-full">
                  <div className="w-2 h-2 bg-yellow-400 rounded-full animate-pulse"></div>
                  <span className="text-sm font-medium">Limited Early Access</span>
                </div>
              </div>
              
              <h2 className="text-3xl font-bold mb-4">
                See Your Project Estimated in Real-Time
              </h2>
              
              <p className="text-xl mb-8 text-blue-100">
                Bring your current project. Walk away with real numbers.
              </p>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
                <div>
                  <h3 className="font-semibold mb-3">What you'll get:</h3>
                  <ul className="space-y-2 text-sm">
                    <li className="flex items-start gap-2">
                      <span className="text-yellow-400">→</span>
                      <span>Complete cost breakdown for your project</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-yellow-400">→</span>
                      <span>3 alternate scenarios to optimize budget</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-yellow-400">→</span>
                      <span>Detailed PDF report to share with stakeholders</span>
                    </li>
                  </ul>
                </div>
                
                <div>
                  <h3 className="font-semibold mb-3">Perfect for:</h3>
                  <ul className="space-y-2 text-sm">
                    <li className="flex items-start gap-2">
                      <span className="text-green-400">✓</span>
                      <span>Active projects needing quick validation</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-green-400">✓</span>
                      <span>Teams evaluating multiple options</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-green-400">✓</span>
                      <span>Developers seeking investor-ready numbers</span>
                    </li>
                  </ul>
                </div>
              </div>
              
              <div className="flex flex-col sm:flex-row gap-4">
                <a
                  href="mailto:cody@specsharp.ai?subject=SpecSharp Demo Request - [Your Company]&body=Hi Cody,%0D%0A%0D%0AI'd like to schedule a personalized demo of SpecSharp.%0D%0A%0D%0AProject Details:%0D%0A- Company: %0D%0A- Project Type: %0D%0A- Approximate Square Footage: %0D%0A- Timeline: %0D%0A%0D%0ABest times for me:%0D%0A%0D%0AThanks!"
                  className="px-6 py-3 bg-white text-blue-600 rounded-lg font-semibold hover:bg-gray-100 transition-colors text-center shadow-lg"
                  onClick={() => handleCTAClick('Schedule Personalized Demo', 'personalized-demo')}
                >
                  Schedule Personalized Demo
                </a>
                <button 
                  onClick={() => window.location.href = '/demo'}
                  className="px-6 py-3 bg-transparent border-2 border-white/50 text-white rounded-lg font-semibold hover:bg-white/10 transition-colors"
                >
                  Try It Yourself First →
                </button>
              </div>
              
              <p className="text-center mt-6 text-sm text-blue-200">
                🔥 Currently onboarding 5 select firms this month
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* ROI Calculator Section - COMMENTED OUT FOR WARM LEADS */}
      {/* Uncomment this section when launching to public/cold traffic */}
      {/* 
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
      */}

      {/* CTA Section (KEPT AS FINAL #8) */}
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