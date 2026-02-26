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

  const sampleScenarioRows = [
    {
      scenario: 'Base',
      totalProjectCost: '$57,482,040',
      annualRevenue: '$8,045,555',
      noi: '$3,218,222',
      dscr: '1.36',
      yieldOnCost: '5.6%',
      stabilizedValue: '$58,513,130',
    },
    {
      scenario: 'Conservative',
      totalProjectCost: '$69,553,268',
      annualRevenue: '$8,045,555',
      noi: '$3,218,222',
      dscr: '1.12',
      yieldOnCost: '4.6%',
      stabilizedValue: '$58,513,130',
    },
    {
      scenario: 'Amenity Overrun',
      totalProjectCost: '$70,810,898',
      annualRevenue: '$8,045,555',
      noi: '$3,218,222',
      dscr: '1.10',
      yieldOnCost: '4.5%',
      stabilizedValue: '$58,513,130',
    },
    {
      scenario: 'Amenity Systems Stress',
      totalProjectCost: '$64,152,506',
      annualRevenue: '$8,045,555',
      noi: '$3,218,222',
      dscr: '1.22',
      yieldOnCost: '5.0%',
      stabilizedValue: '$58,513,130',
    },
  ];

  const sampleProvenanceRows = [
    {
      scenario: 'Base',
      appliedTiles: '—',
      costScalar: '—',
      revenueScalar: '—',
      driverMetric: '—',
    },
    {
      scenario: 'Conservative',
      appliedTiles: 'cost_plus_10, cost_per_sf_plus_10',
      costScalar: '1.10',
      revenueScalar: '—',
      driverMetric: 'totals.cost_per_sf',
    },
    {
      scenario: 'Amenity Overrun',
      appliedTiles: 'cost_plus_10, cost_per_sf_plus_10, amenity_finish_plus_15',
      costScalar: '1.10',
      revenueScalar: '—',
      driverMetric: 'totals.cost_per_sf, trade_breakdown.finishes',
    },
    {
      scenario: 'Amenity Systems Stress',
      appliedTiles: 'cost_plus_10, amenity_mep_plus_10',
      costScalar: '1.10',
      revenueScalar: '—',
      driverMetric: 'trade_breakdown.mechanical',
    },
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
            <Link to="/coverage" className="text-gray-700 hover:text-blue-600 transition-colors">
              Coverage
            </Link>
            <Link to="/login" className="text-blue-600 hover:text-blue-700 transition-colors font-medium">
              Login
            </Link>
            <Link 
              to="/demo" 
              className="btn-primary"
              style={{backgroundColor: '#3B60E4', color: 'white', padding: '12px 24px'}}
              onClick={() => handleCTAClick('Request a DealShield Packet', 'navigation')}
            >
              Request a DealShield Packet
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
              <Link
                to="/coverage"
                className="block py-2 text-gray-700 hover:text-blue-600 transition-colors"
                onClick={() => setIsMobileMenuOpen(false)}
              >
                Coverage
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
                  handleCTAClick('Request a DealShield Packet', 'mobile-navigation');
                  setTimeout(() => setIsMobileMenuOpen(false), 0);
                }}
              >
                Request a DealShield Packet
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
                Decision Insurance for
              </span>
              <span className="block text-3xl sm:text-5xl md:text-6xl lg:text-7xl text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-cyan-400 leading-tight" 
                    style={{animation: 'slide-in 0.5s ease-out both', animationDelay: '0.1s'}}>
                Development Deals
              </span>
            </h1>

            <p className="text-xl sm:text-2xl md:text-3xl text-yellow-300 mb-4 font-semibold" 
               style={{animation: 'slide-in 0.5s ease-out both', animationDelay: '0.2s'}}>
              After discussion. Before delivery. The trust layer.
            </p>

            <p className="text-base sm:text-lg md:text-xl text-gray-200 mb-6 max-w-4xl mx-auto px-4" 
               style={{animation: 'slide-in 0.5s ease-out both', animationDelay: '0.3s'}}>
              SpecSharp generates a deterministic, auditable approval packet—DealShield + Executive + Construction—so your decision survives committee questions, lender scrutiny, and post-mortems.
            </p>

            <div className="max-w-4xl mx-auto mb-7 px-4" style={{animation: 'slide-in 0.5s ease-out both', animationDelay: '0.35s'}}>
              <ul className="space-y-3 text-left">
                <li className="flex items-start text-sm sm:text-base md:text-lg text-gray-100">
                  <CheckCircle className="w-5 h-5 text-green-400 flex-shrink-0 mr-2 mt-0.5" />
                  <span>What breaks first + breakpoints and flex bands</span>
                </li>
                <li className="flex items-start text-sm sm:text-base md:text-lg text-gray-100">
                  <CheckCircle className="w-5 h-5 text-green-400 flex-shrink-0 mr-2 mt-0.5" />
                  <span>What’s most likely wrong + question bank mapped to drivers</span>
                </li>
                <li className="flex items-start text-sm sm:text-base md:text-lg text-gray-100">
                  <CheckCircle className="w-5 h-5 text-green-400 flex-shrink-0 mr-2 mt-0.5" />
                  <span>Provenance on every run (inputs, overrides, what changed, Snapshot ID)</span>
                </li>
              </ul>
            </div>

            {/* CTAs - stack on mobile, side-by-side on desktop */}
            <div className="flex flex-col sm:flex-row gap-3 sm:gap-4 justify-center mb-6 px-4" 
                 style={{animation: 'slide-in 0.5s ease-out both', animationDelay: '0.4s'}}>
              <Link
                to="/new"
                className="group relative px-6 sm:px-8 py-3 sm:py-4 bg-gradient-to-r from-amber-500 to-orange-500 
                           rounded-lg font-bold text-base sm:text-lg text-white overflow-hidden
                           transform hover:scale-105 transition-all duration-200
                           shadow-[0_10px_30px_-10px_rgba(251,146,60,0.5)]"
                onClick={() => handleCTAClick('Generate Decision Packet', 'hero')}
              >
                <span className="relative z-10 flex items-center justify-center">
                  Generate Decision Packet
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
                  handleCTAClick('View a Sample DealShield', 'hero');
                  document.getElementById('sample-dealshield')?.scrollIntoView({ behavior: 'smooth' });
                }}
              >
                View a Sample DealShield
              </button>
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

      {/* Deliverables Strip */}
      <section className="py-16 bg-gray-50 border-b border-gray-200">
        <div className="container mx-auto px-4">
          <div className="text-center mb-8">
            <p className="inline-flex items-center rounded-full border border-blue-200 bg-blue-50 px-4 py-1 text-xs font-semibold uppercase tracking-[0.18em] text-blue-700">
              Forwardable Artifacts
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-6xl mx-auto">
            <div className="group relative overflow-hidden rounded-2xl border border-blue-100 bg-white p-6 shadow-sm transition-all duration-300 hover:-translate-y-1 hover:shadow-xl hover:shadow-blue-100/70">
              <div className="absolute top-0 left-0 h-1 w-full bg-gradient-to-r from-blue-500 to-cyan-400" />
              <div className="mb-4 inline-flex h-12 w-12 items-center justify-center rounded-xl bg-blue-100 text-blue-700">
                <Shield className="h-6 w-6" />
              </div>
              <h3 className="text-2xl font-extrabold tracking-tight text-gray-900">DealShield</h3>
              <p className="mt-1 text-sm font-semibold uppercase tracking-[0.14em] text-blue-700">
                1-page Policy Summary
              </p>
              <p className="mt-4 text-base font-medium text-gray-700">Forwardable in 60 seconds.</p>
            </div>

            <div className="group relative overflow-hidden rounded-2xl border border-indigo-100 bg-white p-6 shadow-sm transition-all duration-300 hover:-translate-y-1 hover:shadow-xl hover:shadow-indigo-100/70">
              <div className="absolute top-0 left-0 h-1 w-full bg-gradient-to-r from-indigo-500 to-blue-500" />
              <div className="mb-4 inline-flex h-12 w-12 items-center justify-center rounded-xl bg-indigo-100 text-indigo-700">
                <Layers className="h-6 w-6" />
              </div>
              <h3 className="text-2xl font-extrabold tracking-tight text-gray-900">Executive Appendix</h3>
              <p className="mt-4 text-base font-medium text-gray-700">Drivers, sensitivities, disclosures.</p>
            </div>

            <div className="group relative overflow-hidden rounded-2xl border border-emerald-100 bg-white p-6 shadow-sm transition-all duration-300 hover:-translate-y-1 hover:shadow-xl hover:shadow-emerald-100/70">
              <div className="absolute top-0 left-0 h-1 w-full bg-gradient-to-r from-emerald-500 to-teal-400" />
              <div className="mb-4 inline-flex h-12 w-12 items-center justify-center rounded-xl bg-emerald-100 text-emerald-700">
                <HardHat className="h-6 w-6" />
              </div>
              <h3 className="text-2xl font-extrabold tracking-tight text-gray-900">Construction Appendix</h3>
              <p className="mt-4 text-base font-medium text-gray-700">Scope + trades + schedule honesty.</p>
            </div>
          </div>

          <div className="mx-auto mt-8 max-w-4xl rounded-2xl border border-slate-200 bg-white/80 px-6 py-5 text-center shadow-sm">
            <p className="text-lg sm:text-xl font-bold tracking-tight text-slate-900">
              One deterministic packet your team can forward without rewriting the story.
            </p>
            <p className="mt-2 text-sm sm:text-base text-slate-600">
              Same assumptions, same decision logic, full provenance across committee, lender, and partner review.
            </p>
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

      {/* Sample DealShield (Page 1) */}
      <section id="sample-dealshield" className="py-16 bg-white border-b border-gray-200">
        <div className="container mx-auto px-4">
          <div className="text-center mb-8">
            <p className="inline-flex items-center rounded-full border border-blue-200 bg-blue-50 px-4 py-1 text-xs font-semibold uppercase tracking-[0.18em] text-blue-700">
              View a Sample DealShield
            </p>
            <h2 className="mt-4 text-3xl sm:text-4xl font-black tracking-tight text-slate-900">
              Page 1 Preview
            </h2>
          </div>

          <div className="max-w-5xl mx-auto rounded-3xl border border-slate-200 bg-slate-50 p-6 sm:p-10 shadow-xl shadow-slate-200/70">
            <header className="mb-6">
              <h3 className="text-4xl sm:text-5xl font-black tracking-tight text-slate-900">DealShield</h3>
              <p className="mt-2 text-xl text-slate-700">Profile: multifamily_luxury_apartments_v1</p>
              <p className="text-lg text-slate-600">Nashville, TN · 220,000 SF</p>
            </header>

            <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white">
              <table className="min-w-full text-left text-sm sm:text-base">
                <thead className="bg-slate-100 text-slate-800">
                  <tr>
                    <th className="px-4 py-3 font-bold">Scenario</th>
                    <th className="px-4 py-3 font-bold">Total Project Cost</th>
                    <th className="px-4 py-3 font-bold">Annual Revenue</th>
                    <th className="px-4 py-3 font-bold">NOI</th>
                    <th className="px-4 py-3 font-bold">DSCR</th>
                    <th className="px-4 py-3 font-bold">Yield on Cost</th>
                    <th className="px-4 py-3 font-bold">Stabilized Value</th>
                  </tr>
                </thead>
                <tbody className="text-slate-700">
                  {sampleScenarioRows.map((row) => (
                    <tr key={row.scenario} className="border-t border-slate-200">
                      <td className="px-4 py-3 font-semibold text-slate-900">{row.scenario}</td>
                      <td className="px-4 py-3">{row.totalProjectCost}</td>
                      <td className="px-4 py-3">{row.annualRevenue}</td>
                      <td className="px-4 py-3">{row.noi}</td>
                      <td className="px-4 py-3">{row.dscr}</td>
                      <td className="px-4 py-3">{row.yieldOnCost}</td>
                      <td className="px-4 py-3">{row.stabilizedValue}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <p className="mt-4 text-lg text-slate-600">
              DSCR and Yield reflect the underwriting/debt terms in this run — see Provenance.
            </p>

            <div className="mt-4 grid gap-3">
              <div className="rounded-xl border border-slate-200 bg-white p-4">
                <p className="text-sm font-bold uppercase tracking-wide text-slate-500">Decision Summary</p>
                <div className="mt-2 grid sm:grid-cols-2 gap-2 text-slate-700">
                  <p><span className="font-semibold text-slate-900">Stabilized Value:</span> $58,513,130</p>
                  <p><span className="font-semibold text-slate-900">Cap Rate Used:</span> 5.5%</p>
                  <p className="sm:col-span-2"><span className="font-semibold text-slate-900">Value Gap:</span> +$1,031,090 (+1.8% of cost)</p>
                </div>
              </div>

              <div className="rounded-xl border border-slate-200 bg-white p-4">
                <p className="text-sm font-bold uppercase tracking-wide text-slate-500">Assumptions</p>
                <ul className="mt-2 list-disc pl-5 space-y-1 text-slate-700">
                  <li>DealShield scenarios stress cost/revenue assumptions only; schedule slippage or acceleration impacts are not modeled here.</li>
                  <li>Not modeled: financing assumptions missing</li>
                </ul>
              </div>
            </div>

            <div className="mt-8">
              <h4 className="text-3xl font-black tracking-tight text-slate-900">Provenance</h4>
              <div className="mt-3 text-slate-700 space-y-2">
                <p><span className="font-semibold text-slate-900">Profiles &amp; Controls:</span> Tile: multifamily_luxury_apartments_v1 | Content: multifamily_luxury_apartments_v1 | Scope: multifamily_luxury_apartments_structural_v1 | Stress band: — | Anchor: —</p>
                <p><span className="font-semibold text-slate-900">Decision Policy:</span> Status: GO | Reason: base_value_gap_positive | Source: dealshield_policy_v1 | Policy ID: dealshield_canonical_policy_v1</p>
              </div>

              <div className="mt-4 overflow-x-auto rounded-xl border border-slate-200 bg-white">
                <table className="min-w-full text-left text-sm">
                  <thead className="bg-slate-100 text-slate-800">
                    <tr>
                      <th className="px-4 py-3 font-bold">Scenario</th>
                      <th className="px-4 py-3 font-bold">Applied Tiles</th>
                      <th className="px-4 py-3 font-bold">Cost Scalar</th>
                      <th className="px-4 py-3 font-bold">Revenue Scalar</th>
                      <th className="px-4 py-3 font-bold">Driver metric (Ugly only)</th>
                    </tr>
                  </thead>
                  <tbody className="text-slate-700">
                    {sampleProvenanceRows.map((row) => (
                      <tr key={row.scenario} className="border-t border-slate-200">
                        <td className="px-4 py-3 font-semibold text-slate-900">{row.scenario}</td>
                        <td className="px-4 py-3">{row.appliedTiles}</td>
                        <td className="px-4 py-3">{row.costScalar}</td>
                        <td className="px-4 py-3">{row.revenueScalar}</td>
                        <td className="px-4 py-3">{row.driverMetric}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            <div className="mt-8">
              <h4 className="text-3xl font-black tracking-tight text-slate-900">What would change this decision fastest?</h4>
              <ul className="mt-4 list-disc pl-6 space-y-3 text-slate-700">
                <li>
                  <p className="font-semibold text-slate-900">Confirm core hard-cost movement</p>
                  <p className="text-sm sm:text-base">Tile: cost_plus_10 | Metric: totals.total_project_cost | Transform: {"{"}"op": "mul", "value": 1.1{"}"}</p>
                </li>
                <li>
                  <p className="font-semibold text-slate-900">Validate high-spec cost per SF tolerance</p>
                  <p className="text-sm sm:text-base">Tile: cost_per_sf_plus_10 | Metric: totals.cost_per_sf | Transform: {"{"}"op": "mul", "value": 1.1{"}"}</p>
                </li>
                <li>
                  <p className="font-semibold text-slate-900">Validate premium amenity finish exposure</p>
                  <p className="text-sm sm:text-base">Tile: amenity_finish_plus_15 | Metric: trade_breakdown.finishes | Transform: {"{"}"op": "mul", "value": 1.15{"}"}</p>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </section>

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

      {/* Final CTA Section */}
      <section className="cta-section fade-in-section bg-gradient-to-br from-slate-800 to-slate-900 relative overflow-hidden">
        {/* Add subtle pattern overlay */}
        <div className="absolute inset-0 opacity-10">
          <div className="absolute inset-0" style={{
            backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.1'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`
          }}></div>
        </div>
        
        <div className="container mx-auto px-4 py-20 relative" style={{zIndex: 1}}>
          <div className="text-center mb-6">
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-blue-400/20 backdrop-blur rounded-full border border-blue-300/30">
              <Shield className="w-4 h-4 text-blue-100" />
              <span className="text-blue-100 font-semibold">Decision Insurance Workflow</span>
            </div>
          </div>
          
          <h2 className="section-title text-center" style={{color: 'white'}}>
            Run the Packet Before IC, Lender, and Partner Review
          </h2>
          <p className="text-xl md:text-2xl mb-12 text-gray-300 max-w-3xl mx-auto text-center">
            Standardize what gets debated: canonical decision status, first-break conditions,
            and snapshot-linked provenance in one forwardable packet.
          </p>
          
          {/* Two Column Layout */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-4xl mx-auto mb-12">
            {/* Runbook column */}
            <div className="bg-white/10 backdrop-blur rounded-lg p-6">
              <h3 className="text-lg font-bold text-white mb-4">Runbook (60-second flow):</h3>
              <ul className="space-y-3 text-gray-200">
                <li className="flex items-start gap-2">
                  <CheckCircle className="w-5 h-5 text-green-400 flex-shrink-0 mt-0.5" />
                  <span>Describe the deal (or paste your memo)</span>
                </li>
                <li className="flex items-start gap-2">
                  <CheckCircle className="w-5 h-5 text-green-400 flex-shrink-0 mt-0.5" />
                  <span>Confirm inferred assumptions and not-modeled items</span>
                </li>
                <li className="flex items-start gap-2">
                  <CheckCircle className="w-5 h-5 text-green-400 flex-shrink-0 mt-0.5" />
                  <span>Generate DealShield + Executive + Construction appendices</span>
                </li>
                <li className="flex items-start gap-2">
                  <CheckCircle className="w-5 h-5 text-green-400 flex-shrink-0 mt-0.5" />
                  <span>Rerun with overrides; each run stamps a new Snapshot ID</span>
                </li>
              </ul>
            </div>
            
            {/* Defensible output column */}
            <div className="bg-white/10 backdrop-blur rounded-lg p-6">
              <h3 className="text-lg font-bold text-white mb-4">What gets defended in the room:</h3>
              <ul className="space-y-3 text-gray-200">
                <li className="flex items-start gap-2">
                  <CheckCircle className="w-5 h-5 text-blue-300 flex-shrink-0 mt-0.5" />
                  <span>Canonical decision status + reason code</span>
                </li>
                <li className="flex items-start gap-2">
                  <CheckCircle className="w-5 h-5 text-blue-300 flex-shrink-0 mt-0.5" />
                  <span>First-break scenario, threshold, and flex-before-break</span>
                </li>
                <li className="flex items-start gap-2">
                  <CheckCircle className="w-5 h-5 text-blue-300 flex-shrink-0 mt-0.5" />
                  <span>Most-likely-wrong drivers + question bank</span>
                </li>
                <li className="flex items-start gap-2">
                  <CheckCircle className="w-5 h-5 text-blue-300 flex-shrink-0 mt-0.5" />
                  <span>Scope profile, schedule source, and applied controls</span>
                </li>
              </ul>
            </div>
          </div>
          
          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center mb-8">
            <Link
              to="/new"
              className="group relative px-8 py-4 bg-gradient-to-r from-amber-500 to-orange-500 
                         rounded-lg font-bold text-lg text-white overflow-hidden
                         transform hover:scale-105 transition-all duration-200
                         shadow-[0_10px_30px_-10px_rgba(251,146,60,0.5)]
                         flex flex-col items-center"
              onClick={() => handleCTAClick('Generate Decision Packet', 'footer-cta')}
            >
              <span className="flex items-center">
                Generate Decision Packet
                <ArrowRight className="ml-2 group-hover:translate-x-1 transition-transform" />
              </span>
              <span className="text-sm mt-1 text-orange-100 font-normal">
                Intake -&gt; confirm assumptions -&gt; stamp packet
              </span>
            </Link>
            
            <button
              className="px-8 py-4 bg-white/10 backdrop-blur border-2 border-white/30 
                         rounded-lg font-bold text-lg text-white
                         hover:bg-white/20 hover:border-white/50
                         transform hover:scale-105 transition-all duration-200
                         flex flex-col items-center"
              onClick={() => {
                handleCTAClick('View a Sample DealShield', 'footer-cta');
                document.getElementById('sample-dealshield')?.scrollIntoView({ behavior: 'smooth' });
              }}
            >
              <span>View a Sample DealShield</span>
              <span className="text-sm mt-1 text-gray-300 font-normal">
                See Page 1 packet format and provenance fields
              </span>
            </button>
          </div>

          <div className="text-center mb-6">
            <Link
              to="/coverage"
              className="inline-flex items-center text-blue-200 hover:text-white transition-colors text-sm font-semibold"
              onClick={() => handleCTAClick('See Coverage', 'footer-cta')}
            >
              See supported types and subtype coverage
              <ArrowRight className="w-4 h-4 ml-1" />
            </Link>
          </div>

          <div className="text-center">
            <p className="text-sm text-slate-300">
              No synthetic performance claims. Every packet reflects current inputs, policy logic, and explicit not-modeled disclosures.
            </p>
          </div>
        </div>
      </section>

      {/* Footer */}
      <Footer />
    </div>
  );
};
