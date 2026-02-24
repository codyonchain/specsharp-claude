import React, { useEffect, useRef, useState } from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight, CheckCircle, Calculator, Zap, Brain, Share2, Shield, Lock, Award, Building2, Layers, HardHat, TrendingUp, Briefcase } from 'lucide-react';
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
                  setTimeout(() => setIsMobileMenuOpen(false), 0);
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
            <div className="bg-blue-500/10 backdrop-blur border border-blue-400/20 rounded-lg px-4 py-3">
              <div className="text-blue-300 text-[10px] uppercase tracking-wide mb-1">Internal Rate of Return</div>
              <div className="text-3xl font-bold">18.5%</div>
            </div>
          </div>

          <div className="absolute top-[20%] right-[8%] opacity-30 text-white font-mono text-xs" style={{animation: 'float-reverse 4.5s ease-in-out infinite'}}>
            <div className="bg-blue-500/10 backdrop-blur border border-blue-400/20 rounded-lg px-4 py-3">
              <div className="text-cyan-300 text-[10px] uppercase tracking-wide mb-1">Equity Multiple</div>
              <div className="text-3xl font-bold">1.8x</div>
            </div>
          </div>

          <div className="absolute bottom-[25%] left-[10%] opacity-30 text-white font-mono text-xs" style={{animation: 'float-slow 5s ease-in-out infinite'}}>
            <div className="bg-blue-500/10 backdrop-blur border border-blue-400/20 rounded-lg px-4 py-3">
              <div className="text-green-400 text-[10px] uppercase tracking-wide mb-1">Development Yield</div>
              <div className="text-3xl font-bold">7.2%</div>
            </div>
          </div>

          <div className="absolute bottom-[20%] right-[5%] opacity-30 text-white font-mono text-xs" style={{animation: 'float-reverse-slow 5.5s ease-in-out infinite'}}>
            <div className="bg-blue-500/10 backdrop-blur border border-blue-400/20 rounded-lg px-4 py-3">
              <div className="text-yellow-400 text-[10px] uppercase tracking-wide mb-1">Stabilized Cap Rate</div>
              <div className="text-3xl font-bold">5.8%</div>
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
                Investment-Grade Project
              </span>
              <span className="block text-3xl sm:text-5xl md:text-6xl lg:text-7xl text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-cyan-400 leading-tight" 
                    style={{animation: 'slide-in 0.5s ease-out both', animationDelay: '0.1s'}}>
                Analysis
              </span>
            </h1>

            {/* The hook - Before You Sign the LOI */}
            <div className="mb-6" style={{animation: 'slide-in 0.5s ease-out both', animationDelay: '0.2s'}}>
              <div className="relative inline-flex items-center justify-center">
                <span className="text-2xl sm:text-3xl md:text-4xl font-bold text-yellow-400 
                               filter drop-shadow-[0_0_20px_rgba(250,204,21,0.4)]">
                  Before You Sign the LOI
                </span>
              </div>
            </div>

            {/* Complete development costs */}
            <p className="text-xl sm:text-2xl md:text-3xl text-gray-200 mb-4" 
               style={{animation: 'slide-in 0.5s ease-out both', animationDelay: '0.3s'}}>
              Complete development costs. ROI projections. Board-ready scenarios.
            </p>

            {/* Subheadline - Know your all-in number */}
            <p className="text-base sm:text-lg md:text-xl text-gray-200 mb-6 max-w-3xl mx-auto px-4" 
               style={{animation: 'slide-in 0.5s ease-out both', animationDelay: '0.35s'}}>
              Know your all-in number—construction, soft costs, land, financing—instantly.
            </p>

            {/* Urgency text */}
            <p className="text-base sm:text-lg text-yellow-300 mb-6 font-medium" 
               style={{animation: 'slide-in 0.5s ease-out both', animationDelay: '0.38s'}}>
              ⏰ Deal on your desk? Get your numbers before tomorrow's meeting.
            </p>

            {/* CTAs - stack on mobile, side-by-side on desktop */}
            <div className="flex flex-col sm:flex-row gap-3 sm:gap-4 justify-center mb-6 px-4" 
                 style={{animation: 'slide-in 0.5s ease-out both', animationDelay: '0.4s'}}>
              <Link
                to="/demo"
                className="group relative px-6 sm:px-8 py-3 sm:py-4 bg-gradient-to-r from-amber-500 to-orange-500 
                           rounded-lg font-bold text-base sm:text-lg text-white overflow-hidden
                           transform hover:scale-105 transition-all duration-200
                           shadow-[0_10px_30px_-10px_rgba(251,146,60,0.5)]"
                onClick={() => handleCTAClick('Analyze Your Next Deal', 'hero')}
              >
                <span className="relative z-10 flex items-center justify-center">
                  Analyze Your Next Deal
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
              Finally. Know if the deal works before spending $100K on design.
            </p>

            {/* Trust bar with developer focus */}
            <div className="hero-trust-bar mt-8 pt-6 border-t border-white/10" 
                 style={{animation: 'fade-in 0.5s ease-out both', animationDelay: '0.5s'}}>
              <p className="text-sm sm:text-base text-gray-300">
                Trusted by <span className="font-bold text-yellow-400">500+</span> developers | 
                <span className="font-bold text-yellow-400"> $28B+</span> projects analyzed | 
                <span className="font-bold text-yellow-400"> 50,000+</span> scenarios compared
              </p>
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

      {/* Value Propositions - Investment focused metrics */}
      <section className="py-16 bg-gray-50 border-b border-gray-200">
        <div className="container mx-auto px-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-5xl mx-auto">
            <div className="text-center bg-white rounded-lg p-6 shadow-sm">
              <div className="text-3xl sm:text-4xl font-bold text-yellow-600 mb-2">$2.9M</div>
              <div className="text-lg font-semibold text-gray-800">All-in Investment</div>
              <div className="text-sm text-gray-600">Construction + Soft Costs + Land</div>
            </div>
            <div className="text-center bg-white rounded-lg p-6 shadow-sm">
              <div className="text-3xl sm:text-4xl font-bold text-blue-600 mb-2">12.8%</div>
              <div className="text-lg font-semibold text-gray-800">Target IRR</div>
              <div className="text-sm text-gray-600">With clear path to achieve</div>
            </div>
            <div className="text-center bg-white rounded-lg p-6 shadow-sm">
              <div className="text-3xl sm:text-4xl font-bold text-green-600 mb-2">&lt; 5 min</div>
              <div className="text-lg font-semibold text-gray-800">Full Analysis</div>
              <div className="text-sm text-gray-600">Including scenario comparison</div>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works - Interactive Version (MOVED UP TO #2) */}
      <div id="how-it-works" className="py-16 bg-white border-b border-gray-200">
        <HowItWorksInteractive />
      </div>

      {/* Scenario Comparison - Interactive Version (MOVED UP TO #3) */}
      <div id="scenario-comparison" className="py-16 bg-gray-50 border-b border-gray-200">
        <ScenarioComparison />
      </div>

      {/* Why Choose SpecSharp - Enhanced Version (NOW #4 with new design) */}
      <div className="py-16 bg-white border-b border-gray-200">
        <WhyChooseEnhanced />
      </div>

      {/* Who Uses SpecSharp - Investment Decision-Makers */}
      <section className="who-uses-section fade-in-section py-16 bg-gray-50 border-b border-gray-200">
        <div className="container mx-auto px-4">
          <h2 className="section-title text-center">Trusted by Industry Leaders</h2>
          <p className="section-subtitle text-center">From single projects to billion-dollar portfolios</p>
          
          <div className="grid md:grid-cols-3 gap-6 max-w-6xl mx-auto">
            {/* Real Estate Developers */}
            <div className="persona-card" data-card="1">
              <div className="persona-header bg-gradient-to-br from-blue-500 to-blue-600">
                <Building2 className="w-12 h-12 text-white mb-3" />
                <h3 className="text-xl font-bold text-white">Real Estate Developers</h3>
              </div>
              <div className="persona-content">
                <p className="quote text-base italic text-gray-700 mb-4">
                  "We evaluate 50+ deals per year. SpecSharp tells us which 5 to pursue."
                </p>
                <ul className="space-y-2.5 mb-5">
                  <li className="flex items-start">
                    <CheckCircle className="w-5 h-5 text-green-500 mr-2 flex-shrink-0 mt-0.5" />
                    <span className="text-gray-700 text-sm">Instant LOI decisions</span>
                  </li>
                  <li className="flex items-start">
                    <CheckCircle className="w-5 h-5 text-green-500 mr-2 flex-shrink-0 mt-0.5" />
                    <span className="text-gray-700 text-sm">Scenario optimization before design</span>
                  </li>
                  <li className="flex items-start">
                    <CheckCircle className="w-5 h-5 text-green-500 mr-2 flex-shrink-0 mt-0.5" />
                    <span className="text-gray-700 text-sm">Board-ready investment packages</span>
                  </li>
                </ul>
                <div className="recent-win bg-green-50 p-3 rounded-lg">
                  <strong className="text-green-700">Recent Win:</strong>
                  <p className="text-sm text-green-600 mt-1">
                    Saved $4.2M on 200-unit project through parking optimization
                  </p>
                </div>
              </div>
            </div>

            {/* Private Equity / REITs */}
            <div className="persona-card" data-card="2">
              <div className="persona-header bg-gradient-to-br from-blue-600 to-blue-700">
                <TrendingUp className="w-12 h-12 text-white mb-3" />
                <h3 className="text-xl font-bold text-white">Private Equity / REITs</h3>
              </div>
              <div className="persona-content">
                <p className="quote text-base italic text-gray-700 mb-4">
                  "Every basis point matters. SpecSharp finds them."
                </p>
                <ul className="space-y-2.5 mb-5">
                  <li className="flex items-start">
                    <CheckCircle className="w-5 h-5 text-green-500 mr-2 flex-shrink-0 mt-0.5" />
                    <span className="text-gray-700 text-sm">Portfolio-wide scenario analysis</span>
                  </li>
                  <li className="flex items-start">
                    <CheckCircle className="w-5 h-5 text-green-500 mr-2 flex-shrink-0 mt-0.5" />
                    <span className="text-gray-700 text-sm">Acquisition due diligence</span>
                  </li>
                  <li className="flex items-start">
                    <CheckCircle className="w-5 h-5 text-green-500 mr-2 flex-shrink-0 mt-0.5" />
                    <span className="text-gray-700 text-sm">LP reporting packages</span>
                  </li>
                </ul>
                <div className="recent-win bg-blue-50 p-3 rounded-lg">
                  <strong className="text-blue-700">Recent Win:</strong>
                  <p className="text-sm text-blue-600 mt-1">
                    Identified $12M value-add across 5-property portfolio
                  </p>
                </div>
              </div>
            </div>

            {/* Institutional Investors */}
            <div className="persona-card" data-card="3">
              <div className="persona-header bg-gradient-to-br from-green-500 to-green-600">
                <Briefcase className="w-12 h-12 text-white mb-3" />
                <h3 className="text-xl font-bold text-white">Institutional Investors</h3>
              </div>
              <div className="persona-content">
                <p className="quote text-base italic text-gray-700 mb-4">
                  "Finally, consistent underwriting across all our deals."
                </p>
                <ul className="space-y-2.5 mb-5">
                  <li className="flex items-start">
                    <CheckCircle className="w-5 h-5 text-green-500 mr-2 flex-shrink-0 mt-0.5" />
                    <span className="text-gray-700 text-sm">Standardized investment analysis</span>
                  </li>
                  <li className="flex items-start">
                    <CheckCircle className="w-5 h-5 text-green-500 mr-2 flex-shrink-0 mt-0.5" />
                    <span className="text-gray-700 text-sm">Risk-adjusted returns modeling</span>
                  </li>
                  <li className="flex items-start">
                    <CheckCircle className="w-5 h-5 text-green-500 mr-2 flex-shrink-0 mt-0.5" />
                    <span className="text-gray-700 text-sm">Committee-ready presentations</span>
                  </li>
                </ul>
                <div className="recent-win bg-green-50 p-3 rounded-lg">
                  <strong className="text-green-700">Recent Win:</strong>
                  <p className="text-sm text-green-600 mt-1">
                    87% faster investment committee approvals
                  </p>
                </div>
              </div>
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

      {/* CTA Section - Investment Focused */}
      <section className="cta-section fade-in-section bg-gradient-to-br from-slate-800 to-slate-900 relative overflow-hidden">
        {/* Add subtle pattern overlay */}
        <div className="absolute inset-0 opacity-10">
          <div className="absolute inset-0" style={{
            backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.1'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`
          }}></div>
        </div>
        
        <div className="container mx-auto px-4 py-20 relative" style={{zIndex: 1}}>
          {/* Urgency Badge */}
          <div className="text-center mb-6">
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-yellow-400/20 backdrop-blur rounded-full">
              <span className="text-yellow-400 text-2xl">⚡</span>
              <span className="text-yellow-400 font-semibold">Limited Early Access</span>
            </div>
          </div>
          
          <h2 className="section-title text-center" style={{color: 'white'}}>
            Your Next Deal is Waiting
          </h2>
          <p className="text-xl md:text-2xl mb-12 text-gray-300 max-w-3xl mx-auto text-center">
            Know if it pencils before you commit. Get your complete investment analysis now.
          </p>
          
          {/* Two Column Layout */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-4xl mx-auto mb-12">
            {/* What you'll get column */}
            <div className="bg-white/10 backdrop-blur rounded-lg p-6">
              <h3 className="text-lg font-bold text-white mb-4">In your first session:</h3>
              <ul className="space-y-3 text-gray-200">
                <li className="flex items-start gap-2">
                  <CheckCircle className="w-5 h-5 text-green-400 flex-shrink-0 mt-0.5" />
                  <span>Complete investment analysis with IRR/NPV</span>
                </li>
                <li className="flex items-start gap-2">
                  <CheckCircle className="w-5 h-5 text-green-400 flex-shrink-0 mt-0.5" />
                  <span>3 scenarios showing path to feasibility</span>
                </li>
                <li className="flex items-start gap-2">
                  <CheckCircle className="w-5 h-5 text-green-400 flex-shrink-0 mt-0.5" />
                  <span>Board-ready presentation package</span>
                </li>
                <li className="flex items-start gap-2">
                  <CheckCircle className="w-5 h-5 text-green-400 flex-shrink-0 mt-0.5" />
                  <span>Specific improvements to hit target returns</span>
                </li>
              </ul>
            </div>
            
            {/* Perfect for column */}
            <div className="bg-white/10 backdrop-blur rounded-lg p-6">
              <h3 className="text-lg font-bold text-white mb-4">Ready to analyze:</h3>
              <ul className="space-y-3 text-gray-200">
                <li className="flex items-start gap-2">
                  <Zap className="w-5 h-5 text-yellow-400 flex-shrink-0 mt-0.5" />
                  <span>Deals under LOI consideration</span>
                </li>
                <li className="flex items-start gap-2">
                  <Zap className="w-5 h-5 text-yellow-400 flex-shrink-0 mt-0.5" />
                  <span>Projects stuck at NO-GO status</span>
                </li>
                <li className="flex items-start gap-2">
                  <Zap className="w-5 h-5 text-yellow-400 flex-shrink-0 mt-0.5" />
                  <span>Tomorrow's investment committee</span>
                </li>
                <li className="flex items-start gap-2">
                  <Zap className="w-5 h-5 text-yellow-400 flex-shrink-0 mt-0.5" />
                  <span>Portfolio optimization opportunities</span>
                </li>
              </ul>
            </div>
          </div>
          
          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center mb-8">
            <Link
              to="/demo"
              className="group relative px-8 py-4 bg-gradient-to-r from-amber-500 to-orange-500 
                         rounded-lg font-bold text-lg text-white overflow-hidden
                         transform hover:scale-105 transition-all duration-200
                         shadow-[0_10px_30px_-10px_rgba(251,146,60,0.5)]
                         flex flex-col items-center"
              onClick={() => handleCTAClick('Analyze Your Deal Now', 'footer-cta')}
            >
              <span className="flex items-center">
                Analyze Your Deal Now
                <ArrowRight className="ml-2 group-hover:translate-x-1 transition-transform" />
              </span>
              <span className="text-sm mt-1 text-orange-100 font-normal">
                Get GO/NO-GO decision in 60 seconds
              </span>
            </Link>
            
            <a
              href="mailto:cody@specsharp.ai?subject=SpecSharp Expert Walkthrough Request&body=Hi Cody,%0D%0A%0D%0AI'd like to schedule a 15-minute expert walkthrough with my actual project.%0D%0A%0D%0AProject Type: %0D%0A%0D%0ABest times for me:%0D%0A%0D%0AThanks!"
              className="px-8 py-4 bg-white/10 backdrop-blur border-2 border-white/30 
                         rounded-lg font-bold text-lg text-white
                         hover:bg-white/20 hover:border-white/50
                         transform hover:scale-105 transition-all duration-200
                         flex flex-col items-center"
              onClick={() => handleCTAClick('Schedule Expert Walkthrough', 'footer-cta')}
            >
              <span>Schedule Expert Walkthrough</span>
              <span className="text-sm mt-1 text-gray-300 font-normal">
                15-min demo with your actual project
              </span>
            </a>
          </div>
          
          {/* Social Proof */}
          <div className="text-center mb-8">
            <span className="inline-flex items-center gap-2 px-4 py-2 bg-white/10 backdrop-blur rounded-full">
              <span className="text-2xl">🔥</span>
              <span className="text-white font-semibold">$1.2B in deals analyzed this quarter</span>
            </span>
          </div>
          
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