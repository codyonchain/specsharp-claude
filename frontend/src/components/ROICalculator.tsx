import React, { useState, useEffect } from 'react';
import { Calculator, TrendingUp, Clock, DollarSign, Users } from 'lucide-react';

interface ROIMetrics {
  monthlyEstimates: number;
  hoursPerEstimate: number;
  hourlyRate: number;
  estimators: number;
  currentMonthlyCost: number;
  specsharpCost: number;
  timeSaved: number;
  moneySaved: number;
  roi: number;
  paybackDays: number;
}

export const ROICalculator: React.FC = () => {
  const [metrics, setMetrics] = useState<ROIMetrics>({
    monthlyEstimates: 20,
    hoursPerEstimate: 3,
    hourlyRate: 65,
    estimators: 1,
    currentMonthlyCost: 0,
    specsharpCost: 799,
    timeSaved: 0,
    moneySaved: 0,
    roi: 0,
    paybackDays: 0
  });

  // Calculate ROI whenever inputs change
  useEffect(() => {
    const totalHours = metrics.monthlyEstimates * metrics.hoursPerEstimate;
    const specsharpHours = metrics.monthlyEstimates * 0.025; // 90 seconds = 0.025 hours
    const savedHours = totalHours - specsharpHours;
    const currentCost = totalHours * metrics.hourlyRate * metrics.estimators;
    const savedMoney = (savedHours * metrics.hourlyRate * metrics.estimators) - metrics.specsharpCost;
    const roiPercent = (savedMoney / metrics.specsharpCost) * 100;
    const paybackDays = savedMoney > 0 ? Math.ceil(30 / (savedMoney / metrics.specsharpCost)) : 0;

    setMetrics(prev => ({
      ...prev,
      currentMonthlyCost: currentCost,
      timeSaved: savedHours * metrics.estimators,
      moneySaved: savedMoney,
      roi: roiPercent,
      paybackDays: paybackDays
    }));
  }, [metrics.monthlyEstimates, metrics.hoursPerEstimate, metrics.hourlyRate, metrics.estimators, metrics.specsharpCost]);

  const handleInputChange = (field: keyof ROIMetrics, value: number) => {
    setMetrics(prev => ({
      ...prev,
      [field]: value
    }));
  };

  return (
    <div className="max-w-6xl mx-auto">
      <div className="bg-white rounded-2xl shadow-xl overflow-hidden">
        <div className="bg-gradient-to-r from-blue-600 to-blue-700 p-6 text-white">
          <div className="flex items-center">
            <Calculator className="w-8 h-8 mr-3" />
            <h3 className="text-2xl font-bold">ROI Calculator</h3>
          </div>
          <p className="mt-2 text-blue-100">
            See how much time and money you'll save with SpecSharp
          </p>
        </div>

        <div className="p-6 lg:p-8">
          {/* Input Section */}
          <div className="grid md:grid-cols-2 gap-6 mb-8">
            <div>
              <h4 className="text-lg font-semibold mb-4 text-gray-800">Your Current Process</h4>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Monthly Estimates
                  </label>
                  <input
                    type="number"
                    value={metrics.monthlyEstimates}
                    onChange={(e) => handleInputChange('monthlyEstimates', parseInt(e.target.value) || 0)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Hours per Estimate
                  </label>
                  <input
                    type="number"
                    step="0.5"
                    value={metrics.hoursPerEstimate}
                    onChange={(e) => handleInputChange('hoursPerEstimate', parseFloat(e.target.value) || 0)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Hourly Rate ($)
                  </label>
                  <input
                    type="number"
                    value={metrics.hourlyRate}
                    onChange={(e) => handleInputChange('hourlyRate', parseInt(e.target.value) || 0)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Number of Estimators
                  </label>
                  <input
                    type="number"
                    value={metrics.estimators}
                    onChange={(e) => handleInputChange('estimators', parseInt(e.target.value) || 1)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
              </div>
            </div>

            {/* Results Section */}
            <div>
              <h4 className="text-lg font-semibold mb-4 text-gray-800">Your Savings with SpecSharp</h4>
              
              <div className="space-y-4">
                <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium text-gray-700">Monthly Time Saved</span>
                    <Clock className="w-5 h-5 text-green-600" />
                  </div>
                  <p className="text-3xl font-bold text-green-700">
                    {Math.round(metrics.timeSaved)} hours
                  </p>
                  <p className="text-sm text-green-600 mt-1">
                    {((metrics.timeSaved / (metrics.monthlyEstimates * metrics.hoursPerEstimate * metrics.estimators)) * 100).toFixed(0)}% reduction
                  </p>
                </div>

                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium text-gray-700">Monthly Savings</span>
                    <DollarSign className="w-5 h-5 text-blue-600" />
                  </div>
                  <p className="text-3xl font-bold text-blue-700">
                    ${metrics.moneySaved.toLocaleString()}
                  </p>
                  <p className="text-sm text-blue-600 mt-1">
                    After SpecSharp cost of ${metrics.specsharpCost}/mo
                  </p>
                </div>

                <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium text-gray-700">Return on Investment</span>
                    <TrendingUp className="w-5 h-5 text-purple-600" />
                  </div>
                  <p className="text-3xl font-bold text-purple-700">
                    {metrics.roi.toFixed(0)}%
                  </p>
                  <p className="text-sm text-purple-600 mt-1">
                    Payback in {metrics.paybackDays} days
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Comparison Bar */}
          <div className="bg-gray-50 rounded-lg p-6 mt-8">
            <h4 className="text-lg font-semibold mb-4 text-gray-800">Cost Comparison</h4>
            
            <div className="space-y-3">
              <div>
                <div className="flex justify-between mb-1">
                  <span className="text-sm font-medium">Current Process</span>
                  <span className="text-sm font-bold">${metrics.currentMonthlyCost.toLocaleString()}/mo</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-8">
                  <div 
                    className="bg-red-500 h-8 rounded-full flex items-center justify-end pr-3"
                    style={{ width: '100%' }}
                  >
                    <span className="text-xs text-white font-semibold">
                      {metrics.monthlyEstimates * metrics.hoursPerEstimate * metrics.estimators} hours
                    </span>
                  </div>
                </div>
              </div>

              <div>
                <div className="flex justify-between mb-1">
                  <span className="text-sm font-medium">With SpecSharp</span>
                  <span className="text-sm font-bold">${metrics.specsharpCost}/mo</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-8">
                  <div 
                    className="bg-green-500 h-8 rounded-full flex items-center justify-end pr-3"
                    style={{ width: `${(metrics.specsharpCost / metrics.currentMonthlyCost) * 100}%` }}
                  >
                    <span className="text-xs text-white font-semibold">
                      {(metrics.monthlyEstimates * 0.025 * metrics.estimators).toFixed(1)} hours
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Call to Action */}
          <div className="mt-8 text-center">
            <p className="text-lg font-semibold text-gray-800 mb-4">
              Ready to save ${Math.round(metrics.moneySaved).toLocaleString()} per month?
            </p>
            <button className="bg-blue-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors">
              Start Your Free Trial
            </button>
          </div>
        </div>
      </div>

      {/* Additional Benefits */}
      <div className="mt-8 grid md:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg p-6 shadow-lg">
          <div className="flex items-center mb-3">
            <div className="bg-blue-100 p-2 rounded-lg mr-3">
              <Clock className="w-6 h-6 text-blue-600" />
            </div>
            <h5 className="font-semibold">Win More Bids</h5>
          </div>
          <p className="text-gray-600 text-sm">
            Respond to RFPs 10x faster. Be first to bid while competitors are still estimating.
          </p>
        </div>

        <div className="bg-white rounded-lg p-6 shadow-lg">
          <div className="flex items-center mb-3">
            <div className="bg-green-100 p-2 rounded-lg mr-3">
              <TrendingUp className="w-6 h-6 text-green-600" />
            </div>
            <h5 className="font-semibold">Scale Without Hiring</h5>
          </div>
          <p className="text-gray-600 text-sm">
            Handle 10x more estimates without adding staff. Perfect for growing contractors.
          </p>
        </div>

        <div className="bg-white rounded-lg p-6 shadow-lg">
          <div className="flex items-center mb-3">
            <div className="bg-purple-100 p-2 rounded-lg mr-3">
              <Users className="w-6 h-6 text-purple-600" />
            </div>
            <h5 className="font-semibold">Consistent Accuracy</h5>
          </div>
          <p className="text-gray-600 text-sm">
            Eliminate human error and ensure every estimate follows your standards.
          </p>
        </div>
      </div>
    </div>
  );
};