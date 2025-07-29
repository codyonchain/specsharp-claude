import React, { useEffect } from 'react';
import { Link } from 'react-router-dom';
import { CheckCircle, ArrowRight } from 'lucide-react';
import { Footer } from '../components/Footer';

export const PricingPage: React.FC = () => {
  useEffect(() => {
    window.scrollTo(0, 0);
  }, []);

  return (
    <div className="min-h-screen flex flex-col">
      {/* Navigation Header */}
      <nav className="bg-white shadow-sm sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <Link to="/" className="font-bold text-2xl text-blue-600">SpecSharp</Link>
          <div className="flex items-center space-x-4">
            <Link to="/" className="text-gray-700 hover:text-blue-600 transition-colors">
              Back to Home
            </Link>
            <Link 
              to="/demo" 
              className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
            >
              Try Demo
            </Link>
          </div>
        </div>
      </nav>

      {/* Pricing Content */}
      <main className="flex-grow bg-gray-50 py-20">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <h1 className="text-4xl font-bold mb-4">Simple, Transparent Pricing</h1>
            <p className="text-xl text-gray-600">Save $5,700/month compared to a full-time estimator</p>
          </div>

          <div className="max-w-lg mx-auto">
            <div className="bg-white rounded-lg shadow-lg p-8">
              <div className="text-center mb-8">
                <h2 className="text-3xl font-bold mb-2">Professional Plan</h2>
                <div className="text-5xl font-bold text-blue-600 mb-2">$799<span className="text-2xl text-gray-600">/month</span></div>
                <p className="text-gray-600">Cancel anytime</p>
              </div>

              <ul className="space-y-4 mb-8">
                <li className="flex items-start">
                  <CheckCircle className="w-6 h-6 text-green-500 mr-3 flex-shrink-0 mt-0.5" />
                  <span>Unlimited construction estimates</span>
                </li>
                <li className="flex items-start">
                  <CheckCircle className="w-6 h-6 text-green-500 mr-3 flex-shrink-0 mt-0.5" />
                  <span>Professional PDF & Excel exports with formulas</span>
                </li>
                <li className="flex items-start">
                  <CheckCircle className="w-6 h-6 text-green-500 mr-3 flex-shrink-0 mt-0.5" />
                  <span>Location-based pricing for all 50 states</span>
                </li>
                <li className="flex items-start">
                  <CheckCircle className="w-6 h-6 text-green-500 mr-3 flex-shrink-0 mt-0.5" />
                  <span>Trade package generation</span>
                </li>
                <li className="flex items-start">
                  <CheckCircle className="w-6 h-6 text-green-500 mr-3 flex-shrink-0 mt-0.5" />
                  <span>Share links for collaboration</span>
                </li>
                <li className="flex items-start">
                  <CheckCircle className="w-6 h-6 text-green-500 mr-3 flex-shrink-0 mt-0.5" />
                  <span>Priority support</span>
                </li>
                <li className="flex items-start">
                  <CheckCircle className="w-6 h-6 text-green-500 mr-3 flex-shrink-0 mt-0.5" />
                  <span>30-day money-back guarantee</span>
                </li>
              </ul>

              <Link 
                to="/demo" 
                className="w-full bg-blue-600 text-white py-4 px-6 rounded-lg font-bold text-lg hover:bg-blue-700 transition-colors flex items-center justify-center"
              >
                Create Your First Estimate <ArrowRight className="ml-2" />
              </Link>
            </div>
          </div>

          <div className="mt-16 max-w-3xl mx-auto">
            <h3 className="text-2xl font-bold text-center mb-8">Compare the Costs</h3>
            <div className="grid md:grid-cols-2 gap-8">
              <div className="bg-white p-6 rounded-lg border-2 border-gray-200">
                <h4 className="text-xl font-semibold mb-4">Traditional Estimator</h4>
                <p className="text-3xl font-bold mb-4">$6,500/month</p>
                <ul className="space-y-2 text-gray-600">
                  <li>• Salary + benefits + overhead</li>
                  <li>• Limited to 40 hours/week</li>
                  <li>• Vacation & sick days</li>
                  <li>• Training required</li>
                  <li>• 3+ hours per estimate</li>
                </ul>
              </div>
              <div className="bg-white p-6 rounded-lg border-2 border-blue-600">
                <h4 className="text-xl font-semibold mb-4 text-blue-600">SpecSharp</h4>
                <p className="text-3xl font-bold mb-4 text-blue-600">$799/month</p>
                <ul className="space-y-2 text-gray-600">
                  <li>• No overhead costs</li>
                  <li>• Available 24/7</li>
                  <li>• Always available</li>
                  <li>• No training needed</li>
                  <li>• 60 seconds per estimate</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </main>

      <Footer />
    </div>
  );
};