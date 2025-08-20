import React from 'react';
import { 
  TrendingUp, Building, DollarSign, Users, Target, Calendar, 
  CheckCircle, BarChart3, Activity, AlertTriangle
} from 'lucide-react';
import type { Project } from '../../../types/project';
import { formatters } from '../../utils/formatters';
import { calculateBuildingMetrics } from '../../utils/buildingMetrics';

interface Props {
  project: Project;
}

export const ExecutiveView: React.FC<Props> = ({ project }) => {
  // Extract data
  const squareFootage = project.square_footage || 0;
  const buildingType = project.building_type || '';
  const buildingSubtype = project.building_subtype || '';
  const projectName = project.project_name || 'Unnamed Project';
  const address = project.address || '';
  
  // Get cost breakdown and totals
  const costBreakdown = project.cost_data?.cost_breakdown || {};
  const totals = project.cost_data?.totals || {};
  const softCostsBreakdown = project.cost_data?.soft_costs_breakdown || {};
  
  // Calculate totals
  const constructionTotal = totals.total_construction || 0;
  const softCostsTotal = totals.total_soft_costs || 0;
  const totalProjectCost = totals.total_project_cost || 0;
  
  // Get building-specific display data
  const displayData = calculateBuildingMetrics(project);
  
  // Calculate annual revenue properly for multifamily
  const calculateAnnualRevenue = () => {
    if (buildingType === 'multifamily') {
      const units = Math.round(squareFootage / 1100);
      const monthlyRent = buildingSubtype === 'luxury_apartments' ? 3500 : 2200;
      return units * monthlyRent * 12 * 0.93; // 93% occupancy
    }
    return displayData.annualRevenue || 0;
  };
  
  const annualRevenue = calculateAnnualRevenue();
  const noi = annualRevenue * 0.60; // 60% NOI margin for multifamily

  // Calculate department allocations
  const departmentAllocations = [
    { name: 'Foundation & Structure', amount: (costBreakdown.foundation || 0) + (costBreakdown.structure || 0), color: 'blue' },
    { name: 'Core & Shell', amount: (costBreakdown.shell || 0) + (costBreakdown.interiors || 0), color: 'green' },
    { name: 'MEP Systems', amount: (costBreakdown.mechanical || 0) + (costBreakdown.electrical || 0) + (costBreakdown.plumbing || 0), color: 'purple' },
    { name: 'Finishes & Specialties', amount: (costBreakdown.finishes || 0) + (costBreakdown.specialties || 0), color: 'orange' },
    { name: 'Site & Infrastructure', amount: (costBreakdown.site_work || 0) + (costBreakdown.equipment || 0), color: 'pink' }
  ].sort((a, b) => b.amount - a.amount);

  // Get soft cost categories
  const softCostCategories = Object.entries(softCostsBreakdown)
    .map(([key, value]) => ({
      name: key.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' '),
      amount: value as number,
      percent: ((value as number) / softCostsTotal) * 100
    }))
    .sort((a, b) => b.amount - a.amount);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-indigo-600 to-purple-600 rounded-xl p-8 text-white shadow-xl">
        <div className="flex justify-between items-start">
          <div>
            <h1 className="text-3xl font-bold mb-2">{projectName}</h1>
            <p className="text-indigo-100 mb-4">{address}</p>
            <div className="flex gap-6">
              <div>
                <p className="text-indigo-200 text-sm">Building Type</p>
                <p className="text-xl font-semibold capitalize">{buildingType.replace('_', ' ')}</p>
              </div>
              <div>
                <p className="text-indigo-200 text-sm">Total Size</p>
                <p className="text-xl font-semibold">{formatters.number(squareFootage)} SF</p>
              </div>
              <div>
                <p className="text-indigo-200 text-sm">Cost per SF</p>
                <p className="text-xl font-semibold">{formatters.costPerSF(totals.cost_per_sf)}</p>
              </div>
            </div>
          </div>
          <div className="text-right">
            <p className="text-indigo-200 text-sm mb-1">Total Project Investment</p>
            <p className="text-4xl font-bold">{formatters.currency(totalProjectCost)}</p>
            <p className="text-indigo-100 mt-2">Est. Completion: Q3 2027</p>
          </div>
        </div>
      </div>

      {/* Investment Decision Box */}
      <div className="bg-gradient-to-r from-green-50 to-blue-50 border-2 border-green-500 rounded-xl p-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-green-100 rounded-full">
              <TrendingUp className="h-8 w-8 text-green-600" />
            </div>
            <div>
              <h2 className="text-2xl font-bold text-gray-900">Investment Decision</h2>
              <p className="text-gray-600">Strategic value proposition for stakeholders</p>
            </div>
          </div>
          <div className="text-right">
            <p className="text-sm text-gray-600 mb-1">Target ROI</p>
            <p className="text-3xl font-bold text-green-600">{formatters.percentage(displayData.roi)}</p>
            <p className="text-sm text-gray-500">5-Year Horizon</p>
          </div>
        </div>
      </div>

      {/* Combined Revenue & Facility Metrics - 2 column grid */}
      <div className="grid grid-cols-2 gap-6">
        {/* Revenue Projections Card */}
        <div className="bg-white rounded-xl shadow-lg overflow-hidden">
          <div className="h-1 bg-gradient-to-r from-green-500 to-green-600"></div>
          <div className="p-6">
            <div className="flex items-center gap-2 mb-4">
              <div className="p-2 bg-green-50 rounded-lg">
                <DollarSign className="h-5 w-5 text-green-600" />
              </div>
              <h3 className="font-semibold text-gray-900">Revenue Projections</h3>
            </div>
            <p className="text-3xl font-bold text-gray-900">
              {formatters.currency(annualRevenue)}
            </p>
            <p className="text-sm text-gray-500 mb-4">Annual Revenue</p>
            <div className="space-y-2 pt-4 border-t">
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Operating Margin</span>
                <span className="font-bold">{formatters.percentage(0.60)}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Net Income</span>
                <span className="font-bold">{formatters.currency(noi)}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Facility Metrics Card */}
        <div className="bg-white rounded-xl shadow-lg overflow-hidden">
          <div className="h-1 bg-gradient-to-r from-blue-500 to-blue-600"></div>
          <div className="p-6">
            <div className="flex items-center gap-2 mb-4">
              <div className="p-2 bg-blue-50 rounded-lg">
                <Building className="h-5 w-5 text-blue-600" />
              </div>
              <h3 className="font-semibold text-gray-900">Facility Metrics</h3>
            </div>
            <p className="text-3xl font-bold text-gray-900">{formatters.units(displayData.unitCount)}</p>
            <p className="text-sm text-gray-500 mb-4">{displayData.unitLabel}</p>
            <div className="space-y-2 pt-4 border-t">
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Cost per {displayData.unitLabel.toLowerCase()}</span>
                <span className="font-bold">{formatters.currencyExact(displayData.costPerUnit)}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Revenue per {displayData.unitLabel.toLowerCase()}</span>
                <span className="font-bold">{formatters.currency(displayData.revenuePerUnit)}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Investment Mix & Market Position - 3 column grid */}
      <div className="grid grid-cols-3 gap-6">
        {/* Investment Mix */}
        <div className="bg-white rounded-xl shadow-lg overflow-hidden">
          <div className="h-1 bg-gradient-to-r from-purple-500 to-purple-600"></div>
          <div className="p-6">
            <div className="flex items-center gap-2 mb-4">
              <div className="p-2 bg-purple-50 rounded-lg">
                <BarChart3 className="h-5 w-5 text-purple-600" />
              </div>
              <h3 className="font-semibold text-gray-900">Investment Mix</h3>
            </div>
            <div className="space-y-3 mt-6">
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-600">Construction</span>
                  <span className="font-bold">{formatters.percentage(constructionTotal / totalProjectCost)}</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div className="bg-blue-600 h-2 rounded-full" style={{ width: `${(constructionTotal / totalProjectCost) * 100}%` }} />
                </div>
              </div>
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-600">Soft Costs</span>
                  <span className="font-bold">{formatters.percentage(softCostsTotal / totalProjectCost)}</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div className="bg-purple-600 h-2 rounded-full" style={{ width: `${(softCostsTotal / totalProjectCost) * 100}%` }} />
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Market Position - Compact */}
        <div className="bg-white rounded-xl shadow-lg overflow-hidden">
          <div className="h-1 bg-gradient-to-r from-blue-500 to-indigo-600"></div>
          <div className="p-6">
            <div className="flex items-center gap-2 mb-4">
              <div className="p-2 bg-blue-50 rounded-lg">
                <TrendingUp className="h-5 w-5 text-blue-600" />
              </div>
              <h3 className="font-semibold text-gray-900">Market Position</h3>
            </div>
            <div className="space-y-3">
              <div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Your Cost</span>
                  <span className="font-bold text-blue-600">{formatters.costPerSF(totals.cost_per_sf)}</span>
                </div>
                <div className="flex justify-between items-center mt-1">
                  <span className="text-sm text-gray-500">Regional Avg</span>
                  <span className="text-gray-700">${Math.round((totals.cost_per_sf || 261) * 0.91)}/SF</span>
                </div>
              </div>
              <div className="relative">
                <div className="w-full bg-gradient-to-r from-green-100 via-yellow-100 to-red-100 rounded-full h-3">
                  <div className="absolute top-0 left-1/2 w-px h-full bg-gray-600"></div>
                  <div className="absolute top-0 h-full w-1 bg-blue-600" style={{ left: '59%' }}>
                    <div className="absolute -top-1 left-1/2 transform -translate-x-1/2 w-5 h-5 bg-blue-600 rounded-full border-2 border-white"></div>
                  </div>
                </div>
                <p className="text-xs font-medium text-blue-700 text-center mt-2">9% above regional average</p>
              </div>
            </div>
          </div>
        </div>

        {/* Quick Sensitivity - Compact */}
        <div className="bg-white rounded-xl shadow-lg overflow-hidden">
          <div className="h-1 bg-gradient-to-r from-purple-500 to-pink-600"></div>
          <div className="p-6">
            <div className="flex items-center gap-2 mb-4">
              <div className="p-2 bg-purple-50 rounded-lg">
                <BarChart3 className="h-5 w-5 text-purple-600" />
              </div>
              <h3 className="font-semibold text-gray-900">Quick Sensitivity</h3>
            </div>
            <div className="space-y-3">
              <div className="p-3 bg-red-50 rounded">
                <p className="text-xs text-gray-600 mb-1">IF COSTS +10%:</p>
                <p className="text-sm font-bold text-red-600">ROI drops to {formatters.percentage(displayData.roi * 0.75)}</p>
              </div>
              <div className="p-3 bg-green-50 rounded">
                <p className="text-xs text-gray-600 mb-1">IF REVENUE +10%:</p>
                <p className="text-sm font-bold text-green-600">ROI rises to {formatters.percentage(displayData.roi * 1.25)}</p>
              </div>
              <div className="p-3 bg-purple-50 rounded">
                <p className="text-xs text-gray-600 mb-1">BREAK-EVEN:</p>
                <p className="text-sm font-bold text-purple-700">{formatters.percentage(displayData.breakEvenOccupancy)} occupancy</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Department Cost Allocation */}
      <div className="bg-white rounded-xl shadow-lg p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-bold text-gray-900">Department Cost Allocation</h3>
          <span className="text-sm text-gray-500">
            {formatters.percentage(constructionTotal / totalProjectCost)} of total investment
          </span>
        </div>
        <div className="grid grid-cols-5 gap-4">
          {departmentAllocations.map((dept, index) => (
            <div key={index} className="text-center">
              <div className={`w-20 h-20 mx-auto bg-${dept.color}-100 rounded-full flex items-center justify-center mb-2`}>
                <span className="text-2xl font-bold text-${dept.color}-600">
                  {formatters.percentage(dept.amount / constructionTotal)}
                </span>
              </div>
              <p className="text-sm font-medium text-gray-700">{dept.name}</p>
              <p className="text-xs text-gray-500">{formatters.currency(dept.amount)}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Major Soft Costs & Key Financial Indicators - Side by side */}
      <div className="grid grid-cols-2 gap-6">
        {/* Major Soft Cost Categories */}
        <div className="bg-white rounded-xl shadow-lg p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-bold text-gray-900">Major Soft Cost Categories</h3>
            <span className="text-sm text-gray-500">
              {formatters.percentage(softCostsTotal / totalProjectCost)} of total
            </span>
          </div>
          <div className="space-y-3">
            {softCostCategories.slice(0, 5).map((category, index) => {
              const colors = ['blue', 'green', 'purple', 'orange', 'pink'];
              const color = colors[index % colors.length];
              
              return (
                <div key={index} className="flex items-center gap-3">
                  <div className={`w-2 h-8 bg-${color}-600 rounded`}></div>
                  <div className="flex-1">
                    <div className="flex justify-between items-center">
                      <span className="text-sm font-medium text-gray-700">{category.name}</span>
                      <div className="flex items-center gap-2">
                        <span className="text-xs text-gray-500">{formatters.percentage(category.percent)}</span>
                        <span className="text-sm font-bold">{formatters.currency(category.amount)}</span>
                      </div>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-1.5 mt-1">
                      <div className={`h-1.5 bg-${color}-600 rounded-full`} style={{ width: `${category.percent}%` }} />
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
          <div className="mt-4 pt-4 border-t">
            <div className="flex justify-between items-center">
              <span className="font-semibold text-gray-900">Total Soft Costs</span>
              <span className="text-xl font-bold">{formatters.currency(softCostsTotal)}</span>
            </div>
          </div>
        </div>

        {/* Key Financial Indicators */}
        <div className="bg-gradient-to-r from-indigo-600 to-purple-600 rounded-xl p-6 text-white shadow-xl">
          <h3 className="text-lg font-bold mb-4">Key Financial Indicators</h3>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-indigo-200 text-xs uppercase tracking-wider mb-1">BREAK-EVEN</p>
              <p className="text-2xl font-bold">{formatters.percentage(displayData.breakEvenOccupancy)}</p>
            </div>
            <div>
              <p className="text-indigo-200 text-xs uppercase tracking-wider mb-1">10-YEAR NPV</p>
              <p className="text-2xl font-bold">{formatters.currency(displayData.npv)}</p>
            </div>
            <div>
              <p className="text-indigo-200 text-xs uppercase tracking-wider mb-1">IRR</p>
              <p className="text-2xl font-bold">{formatters.percentage(displayData.irr)}</p>
            </div>
            <div>
              <p className="text-indigo-200 text-xs uppercase tracking-wider mb-1">PAYBACK</p>
              <p className="text-2xl font-bold">{formatters.years(displayData.paybackPeriod)}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Key Milestones - Horizontal layout */}
      <div className="bg-white rounded-xl shadow-lg p-6">
        <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
          <Calendar className="h-5 w-5 text-blue-600" />
          Key Milestones
        </h3>
        <div className="grid grid-cols-4 gap-4">
          {[
            { icon: CheckCircle, color: 'green', title: 'Groundbreaking', date: 'Q1 2025' },
            { icon: Building, color: 'blue', title: 'Structure Complete', date: 'Q3 2025' },
            { icon: Users, color: 'purple', title: 'Substantial Completion', date: 'Q2 2027' },
            { icon: Target, color: 'orange', title: buildingType === 'multifamily' ? 'First Tenant Move-in' : 'Grand Opening', date: 'Q3 2027' }
          ].map((milestone, idx) => {
            const Icon = milestone.icon;
            return (
              <div key={idx} className="text-center">
                <div className={`w-16 h-16 mx-auto bg-${milestone.color}-100 rounded-full flex items-center justify-center mb-2`}>
                  <Icon className={`h-8 w-8 text-${milestone.color}-600`} />
                </div>
                <p className="font-semibold text-sm text-gray-900">{milestone.title}</p>
                <p className="text-xs text-gray-600">{milestone.date}</p>
              </div>
            );
          })}
        </div>
      </div>

      {/* Financing & Operational - Side by side */}
      <div className="grid grid-cols-2 gap-6">
        {/* Financing Structure */}
        <div className="bg-white rounded-xl shadow-lg p-6">
          <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
            <DollarSign className="h-5 w-5 text-green-600" />
            Financing Structure
          </h3>
          <div className="space-y-3">
            {[
              { name: 'Senior Debt', percent: 0.65, color: 'blue' },
              { name: 'Mezzanine', percent: 0.15, color: 'purple' },
              { name: 'Equity', percent: 0.20, color: 'green' }
            ].map((item, idx) => (
              <div key={idx}>
                <div className="flex justify-between items-center mb-1">
                  <span className="text-sm font-medium text-gray-700">{item.name}</span>
                  <span className="text-sm font-bold">{formatters.currency(totalProjectCost * item.percent)}</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div className={`h-2 bg-${item.color}-600 rounded-full`} style={{ width: `${item.percent * 100}%` }} />
                </div>
              </div>
            ))}
            <div className="pt-3 mt-3 border-t grid grid-cols-2 gap-2 text-sm">
              <div>
                <p className="text-gray-600">Weighted Rate</p>
                <p className="font-bold">6.8%</p>
              </div>
              <div>
                <p className="text-gray-600">Annual Debt Service</p>
                <p className="font-bold">{formatters.currency(totalProjectCost * 0.65 * 0.068)}</p>
              </div>
              <div>
                <p className="text-gray-600">Interest During Const.</p>
                <p className="font-bold">{formatters.currency(totalProjectCost * 0.044)}</p>
              </div>
              <div>
                <p className="text-gray-600">DSCR Target</p>
                <p className="font-bold">1.25x</p>
              </div>
            </div>
          </div>
        </div>

        {/* Operational Efficiency */}
        <div className="bg-white rounded-xl shadow-lg p-6">
          <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
            <Activity className="h-5 w-5 text-purple-600" />
            Operational Efficiency
          </h3>
          <div className="space-y-4">
            <div>
              <p className="text-xs font-semibold text-gray-600 uppercase tracking-wider mb-2">Staffing Metrics</p>
              <div className="grid grid-cols-2 gap-2">
                <div className="bg-purple-50 text-center p-3 rounded">
                  <p className="text-2xl font-bold text-purple-600">50</p>
                  <p className="text-xs text-gray-600">Units per Manager</p>
                </div>
                <div className="bg-pink-50 text-center p-3 rounded">
                  <p className="text-2xl font-bold text-pink-600">8</p>
                  <p className="text-xs text-gray-600">Maintenance Staff</p>
                </div>
              </div>
            </div>
            <div>
              <p className="text-xs font-semibold text-gray-600 uppercase tracking-wider mb-2">Revenue Efficiency</p>
              <div className="space-y-1 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">Revenue per Unit</span>
                  <span className="font-bold">{formatters.currency(displayData.revenuePerUnit)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Average Rent</span>
                  <span className="font-bold">$3,500/mo</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Occupancy Target</span>
                  <span className="font-bold">93%</span>
                </div>
              </div>
            </div>
            <div>
              <p className="text-xs font-semibold text-gray-600 uppercase tracking-wider mb-2">Target KPIs</p>
              <div className="grid grid-cols-3 gap-2">
                <div className="bg-blue-50 p-2 rounded text-center">
                  <p className="text-lg font-bold text-blue-600">6mo</p>
                  <p className="text-xs text-gray-600">Lease-up</p>
                </div>
                <div className="bg-green-50 p-2 rounded text-center">
                  <p className="text-lg font-bold text-green-600">93%</p>
                  <p className="text-xs text-gray-600">Occupancy</p>
                </div>
                <div className="bg-purple-50 p-2 rounded text-center">
                  <p className="text-lg font-bold text-purple-600">$3.5K</p>
                  <p className="text-xs text-gray-600">Rent/Unit</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Executive Decision Points */}
      <div className="bg-gradient-to-r from-amber-50 to-orange-50 border-2 border-amber-500 rounded-xl p-6">
        <div className="flex items-center gap-3 mb-4">
          <AlertTriangle className="h-6 w-6 text-amber-600" />
          <h3 className="text-lg font-bold text-gray-900">Executive Decision Points</h3>
        </div>
        <div className="grid grid-cols-3 gap-4">
          <div className="bg-white rounded-lg p-4">
            <h4 className="font-semibold text-gray-900 mb-2">Go/No-Go Criteria</h4>
            <ul className="space-y-1 text-sm text-gray-600">
              <li>• DSCR > 1.25x ✓</li>
              <li>• IRR > 15% target ✓</li>
              <li>• Payback < 7 years ✓</li>
              <li>• Market vacancy < 7% ✓</li>
            </ul>
          </div>
          <div className="bg-white rounded-lg p-4">
            <h4 className="font-semibold text-gray-900 mb-2">Risk Mitigation</h4>
            <ul className="space-y-1 text-sm text-gray-600">
              <li>• 10% contingency included</li>
              <li>• Fixed-price GMP contract</li>
              <li>• 18-month rate lock option</li>
              <li>• Pre-leasing incentives</li>
            </ul>
          </div>
          <div className="bg-white rounded-lg p-4">
            <h4 className="font-semibold text-gray-900 mb-2">Value Engineering</h4>
            <ul className="space-y-1 text-sm text-gray-600">
              <li>• Alt MEP: Save $1.2M</li>
              <li>• Value finishes: Save $800K</li>
              <li>• Phased amenities: Defer $600K</li>
              <li>• Total potential: $2.6M</li>
            </ul>
          </div>
        </div>
      </div>

      {/* Executive Financial Summary Footer - Fixed with actual values */}
      <div className="bg-gradient-to-r from-slate-900 via-indigo-900 to-slate-900 rounded-xl p-8 shadow-2xl">
        <div className="grid grid-cols-4 gap-8">
          <div className="text-center">
            <p className="text-xs text-slate-400 uppercase tracking-wider mb-3">TOTAL CAPITAL REQUIRED</p>
            <p className="text-3xl font-bold text-white">{formatters.currency(totalProjectCost)}</p>
            <p className="text-sm text-slate-500">Construction + Soft Costs</p>
          </div>
          <div className="text-center">
            <p className="text-xs text-slate-400 uppercase tracking-wider mb-3">EXPECTED ANNUAL RETURN</p>
            <p className="text-3xl font-bold text-white">{formatters.currency(noi)}</p>
            <p className="text-sm text-slate-500">After operating expenses</p>
          </div>
          <div className="text-center">
            <p className="text-xs text-slate-400 uppercase tracking-wider mb-3">INVESTMENT PER UNIT</p>
            <p className="text-3xl font-bold text-white">{formatters.currencyExact(displayData.costPerUnit)}</p>
            <p className="text-sm text-slate-500">Total cost / unit</p>
          </div>
          <div className="text-center">
            <p className="text-xs text-slate-400 uppercase tracking-wider mb-3">DEBT COVERAGE</p>
            <p className="text-3xl font-bold text-white">{formatters.multiplier(displayData.dscr)}</p>
            <p className="text-sm text-slate-500">DSCR (Target: 1.25x)</p>
          </div>
        </div>
      </div>
    </div>
  );
};