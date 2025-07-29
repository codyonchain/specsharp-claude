import React, { useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight, Clock, DollarSign, CheckCircle, Building, Calculator, TrendingUp, Users, FileText, Zap, Brain, Share2, Shield, Lock, Award } from 'lucide-react';
import { ROICalculator } from '../components/ROICalculator';
import { Footer } from '../components/Footer';
import { trackCTAClick, trackPageView, setupViewTracking } from '../utils/analytics';
import './HomePage.css';

export const HomePage: React.FC = () => {
  const observerRef = useRef<IntersectionObserver | null>(null);

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

    return () => {
      observerRef.current?.disconnect();
    };
  }, []);

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
          <button className="md:hidden p-2">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>
        </div>
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
                <TrendingUp className="w-10 h-10 text-blue-600" />
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
                <p className="text-sm text-gray-700 italic">"Testing if a 150-room hotel pencils out in Nashville"</p>
                <div className="mt-3 pt-3 border-t border-gray-200">
                  <p className="text-xs text-gray-500">Average project value: $25M+</p>
                </div>
              </div>
            </div>

            {/* General Contractors */}
            <div className="audience-card" data-card="2">
              <div className="audience-icon bg-green-100">
                <Users className="w-10 h-10 text-green-600" />
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
                <FileText className="w-10 h-10 text-purple-600" />
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
                <p className="text-3xl font-bold text-blue-600">24/7</p>
                <p className="text-sm text-gray-600">Always Available</p>
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

      {/* Logos Section */}
      <section className="trust-section fade-in-section" data-track-section="logos">
        <div className="container mx-auto px-4">
          <h2 className="text-center text-gray-800 mb-2 text-3xl font-bold">Trusted by 500+ Construction Professionals</h2>
          <p className="text-center text-gray-600 mb-12 text-xl">From Fortune 500 developers to local contractors</p>
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