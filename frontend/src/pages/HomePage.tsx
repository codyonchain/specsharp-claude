import React, { useEffect } from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight, Clock, DollarSign, CheckCircle, Building, Calculator } from 'lucide-react';
import { ROICalculator } from '../components/ROICalculator';
import { trackCTAClick, trackPageView, setupViewTracking } from '../utils/analytics';

export const HomePage: React.FC = () => {
  useEffect(() => {
    trackPageView('Homepage');
    setupViewTracking();
  }, []);

  const handleCTAClick = (button: string, location: string) => {
    trackCTAClick(button, location);
  };

  return (
    <div className="min-h-screen">
      {/* Navigation Header */}
      <nav className="bg-white shadow-sm sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <div className="font-bold text-2xl text-blue-600">SpecSharp</div>
          <div className="hidden md:flex items-center space-x-6">
            <a href="#how-it-works" className="text-gray-700 hover:text-blue-600 transition-colors">
              How It Works
            </a>
            <a href="#roi-calculator" className="text-gray-700 hover:text-blue-600 transition-colors">
              ROI Calculator
            </a>
            <a href="/pricing" className="text-gray-700 hover:text-blue-600 transition-colors">
              Pricing
            </a>
            <Link to="/login" className="text-blue-600 hover:text-blue-700 transition-colors font-medium">
              Login
            </Link>
            <Link 
              to="/app" 
              className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
              onClick={() => handleCTAClick('Start Free Trial', 'navigation')}
            >
              Start Free Trial
            </Link>
          </div>
          {/* Mobile menu button */}
          <button className="md:hidden">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="bg-gradient-to-br from-blue-600 to-blue-800 text-white py-20">
        <div className="container mx-auto px-4">
          <div className="max-w-4xl mx-auto text-center">
            <h1 className="text-5xl md:text-6xl font-bold mb-6">
              Your Estimator Costs $6,500/month.
              <span className="block text-yellow-300 mt-2">We Cost $799.</span>
            </h1>
            <p className="text-xl md:text-2xl mb-8 text-blue-100">
              Create professional construction estimates in 90 seconds instead of 3 hours.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                to="/app"
                className="bg-yellow-400 text-blue-900 px-8 py-4 rounded-lg font-bold text-lg hover:bg-yellow-300 transition-colors inline-flex items-center justify-center"
                onClick={() => handleCTAClick('Start Free Trial', 'hero')}
              >
                Start Free Trial <ArrowRight className="ml-2" />
              </Link>
              <a
                href="#roi-calculator"
                className="bg-transparent border-2 border-white text-white px-8 py-4 rounded-lg font-bold text-lg hover:bg-white hover:text-blue-800 transition-colors inline-flex items-center justify-center"
              >
                Calculate Your ROI <Calculator className="ml-2" />
              </a>
            </div>
          </div>
        </div>
      </section>

      {/* Quick Value Props */}
      <section className="py-16 bg-gray-50">
        <div className="container mx-auto px-4">
          <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
            <div className="text-center">
              <div className="bg-blue-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                <Clock className="w-8 h-8 text-blue-600" />
              </div>
              <h3 className="text-xl font-bold mb-2">90 Second Estimates</h3>
              <p className="text-gray-600">
                Type a description. Get a detailed scope. It's that simple.
              </p>
            </div>
            <div className="text-center">
              <div className="bg-green-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                <Building className="w-8 h-8 text-green-600" />
              </div>
              <h3 className="text-xl font-bold mb-2">All Building Types</h3>
              <p className="text-gray-600">
                Office, medical, schools, hotels, industrial - we've got them all.
              </p>
            </div>
            <div className="text-center">
              <div className="bg-purple-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                <DollarSign className="w-8 h-8 text-purple-600" />
              </div>
              <h3 className="text-xl font-bold mb-2">Regional Pricing</h3>
              <p className="text-gray-600">
                Accurate costs for your location, not national averages.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* ROI Calculator Section */}
      <section id="roi-calculator" className="py-20 bg-white">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-bold mb-4">
              See Your Monthly Savings
            </h2>
            <p className="text-xl text-gray-600">
              Most contractors save 20-40 hours per month with SpecSharp
            </p>
          </div>
          <ROICalculator />
        </div>
      </section>

      {/* How It Works */}
      <section id="how-it-works" className="py-20 bg-gray-50">
        <div className="container mx-auto px-4">
          <h2 className="text-4xl font-bold text-center mb-12">
            How It Works
          </h2>
          <div className="max-w-4xl mx-auto">
            <div className="space-y-8">
              {/* Step 1 */}
              <div className="flex items-start space-x-4">
                <div className="bg-blue-600 text-white w-10 h-10 rounded-full flex items-center justify-center font-bold flex-shrink-0">
                  1
                </div>
                <div>
                  <h3 className="text-xl font-bold mb-2">
                    Describe Your Project
                  </h3>
                  <p className="text-gray-600 mb-3">
                    Type something like "150,000 sf hospital 4 stories with emergency department in Dallas"
                  </p>
                  <div className="bg-gray-100 p-4 rounded-lg font-mono text-sm">
                    "200 room hotel with conference center and restaurant in Austin Texas"
                  </div>
                </div>
              </div>

              {/* Step 2 */}
              <div className="flex items-start space-x-4">
                <div className="bg-blue-600 text-white w-10 h-10 rounded-full flex items-center justify-center font-bold flex-shrink-0">
                  2
                </div>
                <div>
                  <h3 className="text-xl font-bold mb-2">
                    Get Instant Detailed Scope
                  </h3>
                  <p className="text-gray-600 mb-3">
                    SpecSharp generates 200+ line items with quantities, costs, and trade breakdowns
                  </p>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="bg-white p-3 rounded border">
                      <p className="font-semibold">Mechanical</p>
                      <p className="text-2xl font-bold text-blue-600">$13.7M</p>
                    </div>
                    <div className="bg-white p-3 rounded border">
                      <p className="font-semibold">Electrical</p>
                      <p className="text-2xl font-bold text-blue-600">$8.2M</p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Step 3 */}
              <div className="flex items-start space-x-4">
                <div className="bg-blue-600 text-white w-10 h-10 rounded-full flex items-center justify-center font-bold flex-shrink-0">
                  3
                </div>
                <div>
                  <h3 className="text-xl font-bold mb-2">
                    Export and Share
                  </h3>
                  <p className="text-gray-600 mb-3">
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
      <section className="py-20 bg-blue-600 text-white">
        <div className="container mx-auto px-4">
          <div className="max-w-3xl mx-auto text-center">
            <p className="text-2xl italic mb-6">
              "We've cut our preliminary estimating time by 85%. 
              What used to take 3 days now takes 30 minutes."
            </p>
            <p className="font-bold text-lg">
              Sarah Chen, Chief Estimator
            </p>
            <p className="text-blue-200">
              Turner Construction
            </p>
          </div>
        </div>
      </section>

      {/* Logos Section */}
      <section className="py-12 bg-gray-50" data-track-section="logos">
        <div className="container mx-auto px-4">
          <p className="text-center text-gray-600 mb-8 text-lg">Trusted by leading contractors</p>
          <div className="flex flex-wrap justify-center items-center gap-8 md:gap-12 opacity-60">
            {/* Using text placeholders for logos - replace with actual logo images */}
            <div className="text-2xl font-bold text-gray-700">Turner</div>
            <div className="text-2xl font-bold text-gray-700">Skanska</div>
            <div className="text-2xl font-bold text-gray-700">PCL</div>
            <div className="text-2xl font-bold text-gray-700">Walsh</div>
            <div className="text-2xl font-bold text-gray-700">DPR</div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gray-900 text-white">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-4xl font-bold mb-6">
            Ready to Save 40 Hours a Month?
          </h2>
          <p className="text-xl mb-8 text-gray-300">
            Join 500+ contractors already using SpecSharp
          </p>
          <Link
            to="/app"
            className="bg-yellow-400 text-gray-900 px-8 py-4 rounded-lg font-bold text-lg hover:bg-yellow-300 transition-colors inline-flex items-center"
            onClick={() => handleCTAClick('Start Your Free Trial', 'footer')}
          >
            Start Your Free Trial <ArrowRight className="ml-2" />
          </Link>
          <p className="mt-4 text-gray-400">
            No credit card required • 14-day free trial • Cancel anytime
          </p>
        </div>
      </section>
    </div>
  );
};