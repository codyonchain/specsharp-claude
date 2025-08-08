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

      {/* Mobile-First Responsive Hero */}
      <section className="relative min-h-screen flex items-center overflow-hidden bg-gradient-to-br from-blue-600 via-blue-500 to-blue-600">
        {/* Animated mesh gradient background */}
        <div className="absolute inset-0">
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_20%_50%,rgba(59,130,246,0.3),transparent_50%)]"></div>
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_80%_50%,rgba(37,99,235,0.2),transparent_50%)]"></div>
        </div>

        {/* Moving grid overlay - hidden on mobile for performance */}
        <div className="hidden sm:block absolute inset-0" style={{
          backgroundImage: 'linear-gradient(rgba(59, 130, 246, 0.05) 1px, transparent 1px), linear-gradient(90deg, rgba(59, 130, 246, 0.05) 1px, transparent 1px)',
          backgroundSize: '40px 40px',
          animation: 'grid-flow 25s linear infinite'
        }}></div>

        {/* Floating metrics - hidden on mobile */}
        <div className="hidden lg:block absolute inset-0 overflow-hidden pointer-events-none">
          <div className="absolute top-[15%] left-[5%] opacity-30 text-white font-mono text-xs" style={{animation: 'float-slow 5s ease-in-out infinite'}}>
            <div className="bg-blue-500/10 backdrop-blur border border-blue-400/20 rounded px-3 py-2">
              <div className="text-blue-300">STRUCTURAL</div>
              <div className="text-2xl font-bold">$5.2M</div>
            </div>
          </div>

          <div className="absolute top-[20%] right-[8%] opacity-30 text-white font-mono text-xs" style={{animation: 'float-reverse 4.5s ease-in-out infinite'}}>
            <div className="bg-blue-500/10 backdrop-blur border border-blue-400/20 rounded px-3 py-2">
              <div className="text-cyan-300">MECHANICAL</div>
              <div className="text-2xl font-bold">$8.2M</div>
            </div>
          </div>

          <div className="absolute bottom-[25%] left-[10%] opacity-30 text-white font-mono text-xs" style={{animation: 'float-slow 5s ease-in-out infinite'}}>
            <div className="bg-blue-500/10 backdrop-blur border border-blue-400/20 rounded px-3 py-2">
              <div className="text-green-400">CONFIDENCE</div>
              <div className="text-2xl font-bold">92%</div>
            </div>
          </div>

          <div className="absolute bottom-[20%] right-[5%] opacity-30 text-white font-mono text-xs" style={{animation: 'float-reverse-slow 5.5s ease-in-out infinite'}}>
            <div className="bg-blue-500/10 backdrop-blur border border-blue-400/20 rounded px-3 py-2">
              <div className="text-yellow-400">TIME SAVED</div>
              <div className="text-2xl font-bold">3 hrs</div>
            </div>
          </div>
        </div>

        {/* Main Content - Mobile optimized */}
        <div className="relative z-10 w-full px-4 sm:px-6 lg:px-8">
          <div className="max-w-5xl mx-auto text-center">
            
            {/* Main headline - responsive sizes */}
            <h1 className="font-black tracking-tight mb-6">
              <span className="block text-3xl sm:text-5xl md:text-6xl lg:text-7xl text-white leading-tight" 
                    style={{animation: 'slide-in 0.5s ease-out both'}}>
                Instant AI Construction
              </span>
              <span className="block text-3xl sm:text-5xl md:text-6xl lg:text-7xl text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-cyan-400 leading-tight" 
                    style={{animation: 'slide-in 0.5s ease-out both', animationDelay: '0.1s'}}>
                Estimates
              </span>
            </h1>

            {/* The hook - in 60 seconds with pulse */}
            <div className="mb-6" style={{animation: 'slide-in 0.5s ease-out both', animationDelay: '0.2s'}}>
              <div className="relative inline-flex items-center justify-center">
                <span className="text-2xl sm:text-3xl md:text-4xl text-gray-300 mr-3">in</span>
                <span className="text-5xl sm:text-6xl md:text-7xl font-black text-yellow-400 
                               filter drop-shadow-[0_0_20px_rgba(250,204,21,0.4)]"
                      style={{animation: 'pulse-scale 2s ease-in-out infinite'}}>
                  60
                </span>
                <span className="text-2xl sm:text-3xl md:text-4xl text-yellow-400 ml-2 sm:ml-3 font-bold">Seconds</span>
              </div>
            </div>

            {/* Validate Your Vision */}
            <p className="text-xl sm:text-2xl md:text-3xl text-gray-200 mb-4" 
               style={{animation: 'slide-in 0.5s ease-out both', animationDelay: '0.3s'}}>
              Validate Your Vision Before Spending on Design
            </p>

            {/* Subheadline - Know if your project pencils out */}
            <p className="text-base sm:text-lg md:text-xl text-gray-200 mb-8 max-w-xl mx-auto px-4" 
               style={{animation: 'slide-in 0.5s ease-out both', animationDelay: '0.35s'}}>
              Know if your project pencils out in 60 seconds.
            </p>

            {/* CTAs - stack on mobile, side-by-side on desktop */}
            <div className="flex flex-col sm:flex-row gap-3 sm:gap-4 justify-center mb-6 px-4" 
                 style={{animation: 'slide-in 0.5s ease-out both', animationDelay: '0.4s'}}>
              <Link
                to="/demo"
                className="group relative px-6 sm:px-8 py-3 sm:py-4 bg-gradient-to-r from-yellow-400 to-amber-400 
                           rounded-lg font-bold text-base sm:text-lg text-gray-900 overflow-hidden
                           transform hover:scale-105 transition-all duration-200
                           shadow-[0_10px_30px_-10px_rgba(251,191,36,0.5)]"
                onClick={() => handleCTAClick('Create Your First Estimate', 'hero')}
              >
                <span className="relative z-10 flex items-center justify-center">
                  Create Your First Estimate
                  <svg className="w-4 sm:w-5 h-4 sm:h-5 ml-2 group-hover:translate-x-1 transition-transform" 
                       fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                  </svg>
                </span>
              </Link>

              <button 
                className="px-6 sm:px-8 py-3 sm:py-4 bg-white/5 backdrop-blur border border-white/20 
                           rounded-lg font-bold text-base sm:text-lg text-white
                           hover:bg-white/10 hover:border-white/30
                           transform hover:scale-105 transition-all duration-200"
                onClick={() => {
                  document.getElementById('scenario-comparison')?.scrollIntoView({ behavior: 'smooth' });
                }}
              >
                Compare Scenarios
                <span className="inline-block ml-2">📊</span>
              </button>
            </div>

            {/* Finally tagline */}
            <p className="text-base sm:text-lg md:text-xl text-gray-300 mb-8" 
               style={{animation: 'slide-in 0.5s ease-out both', animationDelay: '0.45s'}}>
              Finally. Cost certainty before design commitment.
            </p>

            {/* Trust row - responsive, wrap on mobile */}
            <div className="flex flex-wrap items-center justify-center gap-3 sm:gap-6 text-[10px] sm:text-xs text-gray-400" 
                 style={{animation: 'fade-in 0.5s ease-out both', animationDelay: '0.5s'}}>
              <div className="flex items-center gap-1">
                <svg className="w-3 h-3 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" />
                </svg>
                <span>SOC 2 Certified</span>
              </div>
              <div className="flex items-center gap-1">
                <svg className="w-3 h-3 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" />
                </svg>
                <span>Bank-Level Security</span>
              </div>
              <div className="flex items-center gap-1">
                <svg className="w-3 h-3 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" />
                </svg>
                <span>99.9% Uptime</span>
              </div>
            </div>
          </div>
        </div>

        {/* Scroll hint - hidden on mobile */}
        <div className="hidden sm:block absolute bottom-4 left-1/2 -translate-x-1/2 opacity-40 animate-bounce">
          <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19 14l-7 7m0 0l-7-7m7 7V3" />
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