import React from 'react';
import { Project } from '../../types';
import { formatters, safeGet } from '../../utils/displayFormatters';
import { BackendDataMapper } from '../../utils/backendDataMapper';
import { 
  TrendingUp, DollarSign, Building, Clock, AlertCircle,
  Heart, Headphones, Cpu, MapPin, Calendar, ChevronRight,
  BarChart3, Users, Building2, Home, Briefcase, Target,
  GraduationCap, CheckCircle, Info, ArrowUpRight, XCircle,
  Activity, Shield, Wrench, Zap, Droplet, PaintBucket,
  TrendingDown, AlertTriangle, Lightbulb, Download
} from 'lucide-react';

interface Props {
  project: Project;
}

export const ExecutiveViewComplete: React.FC<Props> = ({ project }) => {
  // Early return if no project data
  if (!project?.analysis) {
    return (
      <div className="p-8 text-center text-gray-500">
        <p>Loading project data...</p>
      </div>
    );
  }

  const { analysis } = project;
  
  // Map backend data through our mapper
  const displayData = BackendDataMapper.mapToDisplay(analysis);
  
  // Extract additional raw data we need
  const parsed = analysis?.parsed_input || {};
  const calculations = analysis?.calculations || {};
  const totals = calculations?.totals || {};
  const construction_costs = calculations?.construction_costs || {};
  const soft_costs = calculations?.soft_costs || {};
  const ownership = calculations?.ownership_analysis || {};
  const investmentAnalysis = ownership?.investment_analysis || {};
  
  // Basic project info
  const squareFootage = parsed?.square_footage || 0;
  const buildingType = parsed?.building_type || 'office';
  const buildingSubtype = parsed?.building_subtype || parsed?.subtype || 'general';
  const location = parsed?.location || 'Nashville';
  const floors = parsed?.floors || 1;
  
  // Financial values with formatting
  const totalProjectCost = totals.total_project_cost || 0;
  const constructionTotal = totals.hard_costs || 0;
  const softCostsTotal = totals.soft_costs || 0;
  
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
  
  // Get department icons based on building type
  const getDepartmentIcon = (deptName: string) => {
    if (deptName.includes('Residential')) return Home;
    if (deptName.includes('Clinical')) return Heart;
    if (deptName.includes('Academic')) return GraduationCap;
    if (deptName.includes('Office')) return Briefcase;
    if (deptName.includes('Common')) return Users;
    if (deptName.includes('Support')) return Headphones;
    if (deptName.includes('Infrastructure')) return Cpu;
    if (deptName.includes('Amenities')) return Shield;
    if (deptName.includes('Athletics')) return Activity;
    return Building2;
  };
  
  // Get department gradient based on index
  const getDepartmentGradient = (index: number) => {
    const gradients = [
      'from-blue-600 to-blue-700',
      'from-green-600 to-green-700',
      'from-purple-600 to-purple-700'
    ];
    return gradients[index % gradients.length];
  };
  
  // Soft costs breakdown
  const softCostCategories = Object.entries(soft_costs?.breakdown || soft_costs || {})
    .filter(([key]) => key !== 'total' && key !== 'soft_cost_percentage')
    .map(([key, value]) => ({
      name: key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
      amount: value as number,
      percent: softCostsTotal > 0 ? ((value as number) / softCostsTotal) * 100 : 0
    }))
    .sort((a, b) => b.amount - a.amount)
    .slice(0, 5);

  return (
    <div className="space-y-6">
      {/* Executive Investment Dashboard Header */}
      <div className="bg-gradient-to-r from-blue-600 via-blue-700 to-indigo-700 rounded-2xl p-8 text-white shadow-2xl">
        <div className="flex justify-between items-start mb-8">
          <div>
            <h2 className="text-3xl font-bold mb-3">
              {formatters.squareFeet(squareFootage)} {buildingSubtype.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
            </h2>
            <div className="flex items-center gap-6 text-sm text-blue-200">
              <span className="flex items-center gap-1.5">
                <MapPin className="h-4 w-4" />
                {location}
              </span>
              <span className="flex items-center gap-1.5">
                <Building className="h-4 w-4" />
                {floors} Floors
              </span>
              <span className="flex items-center gap-1.5">
                <Calendar className="h-4 w-4" />
                Ground-Up
              </span>
            </div>
            
            <div className="flex gap-3 mt-4">
              <button className="px-4 py-2 bg-white/10 backdrop-blur border border-white/20 text-white rounded-lg hover:bg-white/20 transition flex items-center gap-2">
                <Download className="h-4 w-4" />
                Export Excel
              </button>
              <button className="px-4 py-2 bg-white text-blue-700 rounded-lg hover:bg-blue-50 transition font-medium flex items-center gap-2">
                <BarChart3 className="h-4 w-4" />
                Compare Scenarios
              </button>
            </div>
          </div>
          
          <div className="text-right">
            <p className="text-xs text-blue-200 uppercase tracking-wider mb-2 font-medium">TOTAL INVESTMENT REQUIRED</p>
            <p className="text-5xl font-bold">{formatters.currency(totalProjectCost)}</p>
            <p className="text-lg text-blue-200">{formatters.costPerSF(totals.cost_per_sf)}</p>
          </div>
        </div>
        
        <div className="grid grid-cols-4 gap-8 pt-6 mt-6 border-t border-white/20">
          <div>
            <p className="text-blue-200 text-xs uppercase tracking-wider mb-2 font-medium">CONSTRUCTION</p>
            <p className="text-3xl font-bold">{formatters.currency(constructionTotal)}</p>
          </div>
          <div>
            <p className="text-blue-200 text-xs uppercase tracking-wider mb-2 font-medium">SOFT COSTS</p>
            <p className="text-3xl font-bold">{formatters.currency(softCostsTotal)}</p>
          </div>
          <div>
            <p className="text-blue-200 text-xs uppercase tracking-wider mb-2 font-medium">EXPECTED ROI</p>
            <p className="text-3xl font-bold">{formatters.percentage(displayData.roi)}</p>
          </div>
          <div>
            <p className="text-blue-200 text-xs uppercase tracking-wider mb-2 font-medium">PAYBACK PERIOD</p>
            <p className="text-3xl font-bold">{formatters.years(displayData.paybackPeriod)}</p>
          </div>
        </div>
      </div>

      {/* Investment Decision Alert */}
      <div className={`${displayData.investmentDecision === 'NO-GO' ? 'bg-red-50 border-red-500' : 'bg-green-50 border-green-500'} border-l-4 rounded-lg p-6`}>
        <div className="flex items-start gap-3">
          {displayData.investmentDecision === 'NO-GO' ? (
            <AlertCircle className="h-6 w-6 text-red-600 flex-shrink-0" />
          ) : (
            <CheckCircle className="h-6 w-6 text-green-600 flex-shrink-0" />
          )}
          <div className="flex-1">
            <h3 className={`font-bold text-lg ${displayData.investmentDecision === 'NO-GO' ? 'text-red-900' : 'text-green-900'}`}>
              Investment Decision: {displayData.investmentDecision}
            </h3>
            <p className={`mt-1 ${displayData.investmentDecision === 'NO-GO' ? 'text-red-700' : 'text-green-700'}`}>
              {displayData.decisionReason}
            </p>
            
            {/* Display suggestions if NO-GO */}
            {displayData.investmentDecision === 'NO-GO' && displayData.suggestions.length > 0 && (
              <div className="mt-4 p-4 bg-white rounded-lg border border-red-200">
                <h4 className="font-semibold text-red-900 mb-2 flex items-center gap-2">
                  <Lightbulb className="h-4 w-4" />
                  How to Make This Project Pencil:
                </h4>
                <ul className="space-y-2">
                  {displayData.suggestions.map((suggestion, idx) => (
                    <li key={idx} className="flex items-start gap-2">
                      <span className="text-red-600 mt-0.5">•</span>
                      <span className="text-sm text-gray-700">{suggestion}</span>
                    </li>
                  ))}
                </ul>
                
                {displayData.requiredRent > 0 && (
                  <div className="mt-3 pt-3 border-t border-red-200">
                    <p className="text-sm text-gray-600">
                      Required rent for 8% return: <strong>{formatters.monthlyRent(displayData.requiredRent)}</strong>
                    </p>
                  </div>
                )}
              </div>
            )}
            
            <div className="flex items-center gap-6 mt-3">
              <span className="flex items-center gap-2">
                <span className={`w-2 h-2 ${displayData.roi >= 0.08 ? 'bg-green-500' : 'bg-red-500'} rounded-full`}></span>
                <span className="text-sm">ROI: <strong>{formatters.percentage(displayData.roi)}</strong></span>
              </span>
              <span className="flex items-center gap-2">
                <span className={`w-2 h-2 ${displayData.dscr >= 1.25 ? 'bg-green-500' : 'bg-amber-500'} rounded-full`}></span>
                <span className="text-sm">DSCR: <strong>{formatters.multiplier(displayData.dscr)}</strong></span>
              </span>
              <span className="flex items-center gap-2">
                <span className={`w-2 h-2 ${displayData.paybackPeriod <= 20 ? 'bg-green-500' : 'bg-amber-500'} rounded-full`}></span>
                <span className="text-sm">Payback: <strong>{formatters.years(displayData.paybackPeriod)}</strong></span>
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Three Key Metrics Cards */}
      <div className="grid grid-cols-3 gap-6">
        {/* Revenue Projections */}
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

        {/* Facility Metrics */}
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
                <span className="text-gray-600">Cost per {displayData.unitType}</span>
                <span className="font-bold">{formatters.currencyExact(displayData.costPerUnit)}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Revenue per {displayData.unitType}</span>
                <span className="font-bold">{formatters.currency(displayData.revenuePerUnit)}</span>
              </div>
            </div>
          </div>
        </div>

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
      </div>

      {/* Department Cost Allocation */}
      {displayData.departments.length > 0 && (
        <div>
          <h3 className="text-xl font-bold text-gray-900 mb-6">Department Cost Allocation</h3>
          <div className="grid grid-cols-3 gap-6">
            {displayData.departments.map((dept, idx) => {
              const Icon = getDepartmentIcon(dept.name);
              const gradient = getDepartmentGradient(idx);
              return (
                <div key={idx} className={`bg-gradient-to-br ${gradient} rounded-xl p-6 text-white shadow-xl`}>
                  <div className="flex items-start justify-between mb-4">
                    <div className="p-3 bg-white/20 rounded-lg backdrop-blur">
                      <Icon className="h-6 w-6" />
                    </div>
                    <div className="text-right">
                      <p className="text-4xl font-bold">{formatters.percentage(dept.percent)}</p>
                      <p className="text-sm text-white/80">of facility</p>
                    </div>
                  </div>
                  
                  <h4 className="text-lg font-bold mb-1">{dept.name}</h4>
                  <p className="text-3xl font-bold mb-4">{formatters.currency(dept.amount)}</p>
                  
                  <div className="space-y-2 pt-4 border-t border-white/20">
                    <div className="flex justify-between text-sm">
                      <span className="text-white/80">Square Footage</span>
                      <span className="font-medium">{formatters.squareFeet(dept.square_footage)}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-white/80">Cost per SF</span>
                      <span className="font-medium">{formatters.costPerSF(dept.cost_per_sf)}</span>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Major Soft Cost Categories */}
      {softCostCategories.length > 0 && (
        <div className="bg-white rounded-xl shadow-lg p-6">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-xl font-bold text-gray-900">Major Soft Cost Categories</h3>
            <div className="text-sm text-gray-500">
              {formatters.percentage(softCostsTotal / totalProjectCost)} of total investment
            </div>
          </div>
          <div className="space-y-4">
            {softCostCategories.map((category, index) => {
              const colors = ['blue', 'green', 'purple', 'orange', 'pink'];
              const color = colors[index % colors.length];
              
              return (
                <div key={index} className="flex items-center gap-4">
                  <div className={`w-3 h-12 bg-${color}-600 rounded`}></div>
                  <div className="flex-1">
                    <div className="flex justify-between items-center mb-2">
                      <span className="text-sm font-semibold text-gray-800">{category.name}</span>
                      <div className="flex items-center gap-3">
                        <span className="text-xs px-2 py-1 bg-gray-100 rounded-full text-gray-600">
                          {formatters.percentage(category.percent)}
                        </span>
                        <span className="text-lg font-bold text-gray-900">
                          {formatters.currency(category.amount)}
                        </span>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      <div className="flex-1 bg-gray-200 rounded-full h-2 overflow-hidden">
                        <div 
                          className={`h-2 bg-gradient-to-r from-${color}-500 to-${color}-600 rounded-full`}
                          style={{ width: `${Math.min(category.percent, 100)}%` }}
                        />
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
          <div className="mt-6 pt-6 border-t border-gray-200">
            <div className="flex justify-between items-center">
              <span className="text-lg font-semibold text-gray-900">Total Soft Costs</span>
              <div className="text-right">
                <span className="text-2xl font-bold text-gray-900">{formatters.currency(softCostsTotal)}</span>
                <span className="text-sm text-gray-500 block">{formatters.percentage(softCostsTotal / constructionTotal)} of construction</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Key Financial Indicators */}
      <div className="bg-gradient-to-r from-indigo-600 to-purple-600 rounded-xl p-8 text-white shadow-xl">
        <h3 className="text-2xl font-bold mb-6">Key Financial Indicators</h3>
        <div className="grid grid-cols-2 gap-8">
          <div>
            <p className="text-indigo-200 text-sm uppercase tracking-wider mb-2">BREAK-EVEN OCCUPANCY</p>
            <p className="text-4xl font-bold">{formatters.percentage(displayData.breakEvenOccupancy)}</p>
          </div>
          <div>
            <p className="text-indigo-200 text-sm uppercase tracking-wider mb-2">10-YEAR NPV</p>
            <p className="text-4xl font-bold">{formatters.currency(displayData.npv)}</p>
          </div>
          <div className="mt-6">
            <p className="text-indigo-200 text-sm uppercase tracking-wider mb-2">IRR</p>
            <p className="text-3xl font-bold">{formatters.percentage(displayData.irr)}</p>
          </div>
          <div className="mt-6">
            <p className="text-indigo-200 text-sm uppercase tracking-wider mb-2">PAYBACK PERIOD</p>
            <p className="text-3xl font-bold">{formatters.years(displayData.paybackPeriod)}</p>
          </div>
        </div>
      </div>

      {/* Market Position & Quick Sensitivity */}
      <div className="grid grid-cols-2 gap-6">
        {/* Market Position */}
        <div className="bg-gradient-to-br from-white to-blue-50 rounded-xl shadow-lg border border-blue-100 overflow-hidden">
          <div className="bg-gradient-to-r from-blue-600 to-indigo-600 px-6 py-3">
            <h3 className="text-lg font-bold text-white flex items-center gap-2">
              <TrendingUp className="h-5 w-5" />
              Market Position
            </h3>
          </div>
          <div className="p-6">
            <div className="space-y-4">
              <div className="bg-white rounded-lg p-4 shadow-sm">
                <div className="flex justify-between items-center mb-3">
                  <span className="text-sm font-medium text-gray-600">Your Cost</span>
                  <span className="text-xl font-bold text-blue-600">{formatters.costPerSF(totals.cost_per_sf)}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-500">Regional Average</span>
                  <span className="font-medium text-gray-700">${Math.round((totals.cost_per_sf || 261) * 0.91)}/SF</span>
                </div>
              </div>
              
              <div className="relative">
                <div className="w-full bg-gradient-to-r from-green-100 via-yellow-100 to-red-100 rounded-full h-4 overflow-hidden">
                  <div className="absolute top-0 left-1/2 transform -translate-x-1/2 h-full w-0.5 bg-gray-700"></div>
                  <div 
                    className="absolute top-0 h-full w-1 bg-blue-600 shadow-lg"
                    style={{ left: '59%' }}
                  >
                    <div className="absolute -top-1 left-1/2 transform -translate-x-1/2 w-6 h-6 bg-blue-600 rounded-full border-2 border-white shadow-lg"></div>
                  </div>
                </div>
                <div className="flex justify-between text-xs text-gray-500 mt-2">
                  <span>-20%</span>
                  <span>Market Avg</span>
                  <span>+20%</span>
                </div>
                <div className="mt-4 p-3 bg-blue-50 rounded-lg text-center">
                  <p className="text-sm font-bold text-blue-700">9% above regional average</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Quick Sensitivity */}
        <div className="bg-gradient-to-br from-white to-purple-50 rounded-xl shadow-lg border border-purple-100 overflow-hidden">
          <div className="bg-gradient-to-r from-purple-600 to-pink-600 px-6 py-3">
            <h3 className="text-lg font-bold text-white flex items-center gap-2">
              <BarChart3 className="h-5 w-5" />
              Quick Sensitivity
            </h3>
          </div>
          <div className="p-6 space-y-4">
            <div className="bg-white rounded-lg p-4 shadow-sm">
              <p className="text-xs text-gray-500 uppercase tracking-wider mb-2">If costs +10%:</p>
              <div className="flex items-center justify-between">
                <TrendingDown className="h-5 w-5 text-red-500" />
                <span className="text-lg font-bold text-red-600">ROI drops to {formatters.percentage(displayData.roi * 0.75)}</span>
              </div>
            </div>
            <div className="bg-white rounded-lg p-4 shadow-sm">
              <p className="text-xs text-gray-500 uppercase tracking-wider mb-2">If revenue +10%:</p>
              <div className="flex items-center justify-between">
                <TrendingUp className="h-5 w-5 text-green-500" />
                <span className="text-lg font-bold text-green-600">ROI rises to {formatters.percentage(displayData.roi * 1.25)}</span>
              </div>
            </div>
            <div className="p-4 bg-gradient-to-r from-purple-100 to-pink-100 rounded-lg">
              <p className="text-xs text-gray-600 uppercase tracking-wider mb-2">Break-even needs:</p>
              <span className="text-xl font-bold text-purple-700">{formatters.percentage(displayData.breakEvenOccupancy)} occupancy</span>
            </div>
          </div>
        </div>
      </div>

      {/* Key Milestones Timeline */}
      <div className="bg-gradient-to-br from-white via-blue-50 to-indigo-50 rounded-xl shadow-lg p-8 border border-blue-100">
        <h3 className="text-xl font-bold text-gray-900 mb-6 flex items-center gap-2">
          <Calendar className="h-6 w-6 text-blue-600" />
          Key Milestones
        </h3>
        <div className="relative">
          <div className="absolute left-10 top-10 bottom-0 w-0.5 bg-gradient-to-b from-blue-400 via-purple-400 to-pink-400"></div>
          <div className="space-y-8">
            {[
              { icon: CheckCircle, color: 'green', title: 'Groundbreaking', date: 'Q1 2025' },
              { icon: Building, color: 'blue', title: 'Structure Complete', date: 'Q3 2025' },
              { icon: Users, color: 'purple', title: 'Substantial Completion', date: 'Q2 2027' },
              { icon: Target, color: 'orange', title: buildingType === 'multifamily' ? 'First Tenant Move-in' : 'Grand Opening', date: 'Q3 2027' }
            ].map((milestone, idx) => {
              const Icon = milestone.icon;
              return (
                <div key={idx} className="flex items-center gap-6 group">
                  <div className={`w-20 h-20 bg-gradient-to-br from-${milestone.color}-100 to-${milestone.color}-200 rounded-full flex items-center justify-center flex-shrink-0 shadow-lg group-hover:scale-110 transition-transform`}>
                    <Icon className={`h-10 w-10 text-${milestone.color}-600`} />
                  </div>
                  <div className="flex-1 bg-white rounded-lg p-4 shadow-md group-hover:shadow-lg transition-shadow">
                    <p className="font-bold text-gray-900 text-lg">{milestone.title}</p>
                    <p className="text-sm text-gray-600">{milestone.date}</p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Financing Structure & Operational Efficiency */}
      <div className="grid grid-cols-2 gap-6">
        {/* Financing Structure */}
        <div className="bg-gradient-to-br from-green-50 to-emerald-50 rounded-xl shadow-lg border border-green-100 overflow-hidden">
          <div className="bg-gradient-to-r from-green-600 to-emerald-600 px-6 py-4">
            <h3 className="text-lg font-bold text-white flex items-center gap-2">
              <DollarSign className="h-5 w-5" />
              Financing Structure
            </h3>
          </div>
          <div className="p-6">
            <div className="space-y-4">
              {[
                { name: 'Senior Debt', percent: 0.65, color: 'blue' },
                { name: 'Mezzanine', percent: 0.15, color: 'purple' },
                { name: 'Equity', percent: 0.20, color: 'green' }
              ].map((item, idx) => (
                <div key={idx} className="bg-white rounded-lg p-3 shadow-sm">
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-sm font-semibold text-gray-700">{item.name} ({formatters.percentage(item.percent)})</span>
                    <span className="font-bold text-gray-900">{formatters.currency(totalProjectCost * item.percent)}</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
                    <div 
                      className={`h-3 bg-gradient-to-r from-${item.color}-500 to-${item.color}-600 rounded-full`}
                      style={{ width: `${item.percent * 100}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
            
            <div className="mt-6 pt-6 border-t border-green-200 space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Weighted Rate</span>
                <span className="font-bold text-gray-900">6.8%</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Annual Debt Service</span>
                <span className="font-bold text-gray-900">{formatters.currency(totalProjectCost * 0.65 * 0.068)}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Interest During Construction</span>
                <span className="font-bold text-gray-900">{formatters.currency(totalProjectCost * 0.044)}</span>
              </div>
              <div className="bg-green-100 rounded-lg p-3 mt-3">
                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium text-green-700">DSCR Target</span>
                  <span className="font-bold text-green-800">1.25x</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Operational Efficiency */}
        <div className="bg-gradient-to-br from-purple-50 to-pink-50 rounded-xl shadow-lg border border-purple-100 overflow-hidden">
          <div className="bg-gradient-to-r from-purple-600 to-pink-600 px-6 py-4">
            <h3 className="text-lg font-bold text-white flex items-center gap-2">
              <Activity className="h-5 w-5" />
              Operational Efficiency
            </h3>
          </div>
          <div className="p-6">
            {/* Staffing Metrics */}
            {displayData.staffingMetrics.length > 0 && (
              <div className="mb-4">
                <h4 className="text-sm font-bold text-gray-700 mb-3 uppercase tracking-wider">Staffing Metrics</h4>
                <div className="grid grid-cols-2 gap-3">
                  {displayData.staffingMetrics.slice(0, 2).map((metric, idx) => (
                    <div key={idx} className="bg-white text-center p-4 rounded-lg shadow-sm">
                      <p className={`text-3xl font-bold ${idx === 0 ? 'text-purple-600' : 'text-pink-600'}`}>
                        {metric.value}
                      </p>
                      <p className="text-xs text-gray-600">{metric.label}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}
            
            {/* Revenue Efficiency */}
            {Object.keys(displayData.revenueMetrics).length > 0 && (
              <div className="mb-4">
                <h4 className="text-sm font-bold text-gray-700 mb-3 uppercase tracking-wider">Revenue Efficiency</h4>
                <div className="bg-white rounded-lg p-3 space-y-2 shadow-sm">
                  {Object.entries(displayData.revenueMetrics).slice(0, 3).map(([key, value]) => (
                    <div key={key} className="flex justify-between text-sm">
                      <span className="text-gray-600">{key.replace(/_/g, ' ')}</span>
                      <span className="font-bold text-gray-900">{value}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
            
            {/* Target KPIs */}
            {displayData.kpis.length > 0 && (
              <div>
                <h4 className="text-sm font-bold text-gray-700 mb-3 uppercase tracking-wider">Target KPIs</h4>
                <div className="grid grid-cols-3 gap-2">
                  {displayData.kpis.slice(0, 3).map((kpi, idx) => (
                    <div key={idx} className={`bg-gradient-to-br from-${kpi.color}-100 to-${kpi.color}-200 p-3 rounded-lg text-center`}>
                      <p className={`text-xl font-bold text-${kpi.color}-700`}>{kpi.value}</p>
                      <p className={`text-xs text-${kpi.color}-600`}>{kpi.label}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Executive Decision Points */}
      <div className="bg-gradient-to-r from-amber-50 via-orange-50 to-amber-50 border-l-4 border-amber-500 rounded-xl shadow-lg p-6">
        <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-3">
          <div className="p-2 bg-amber-100 rounded-lg">
            <Lightbulb className="h-6 w-6 text-amber-600" />
          </div>
          Executive Decision Points
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {[
            `Total investment of ${formatters.currency(totalProjectCost)} is 7% above regional ${buildingType} average`,
            buildingType === 'multifamily' ? 
              `${displayData.unitCount} units with avg rent of $3,500/month` :
              '22-year payback suggests need for operational efficiency improvements',
            buildingType === 'multifamily' ?
              'Amenity package adds 8% to costs but supports premium rents' :
              'Consider phased opening to accelerate revenue generation',
            `Soft costs at ${formatters.percentage(softCostsTotal / constructionTotal)} - ${
              buildingType === 'multifamily' ? 'typical for luxury multifamily' : 'opportunity for value engineering'
            }`
          ].map((point, idx) => (
            <div key={idx} className="flex items-start gap-3 bg-white rounded-lg p-3 shadow-sm">
              <div className="w-6 h-6 bg-amber-200 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                <span className="text-amber-700 text-xs font-bold">{idx + 1}</span>
              </div>
              <span className="text-sm text-gray-700">{point}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Executive Financial Summary Footer */}
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
            <p className="text-xs text-slate-400 uppercase tracking-wider mb-3">
              INVESTMENT PER {displayData.unitType.toUpperCase()}
            </p>
            <p className="text-3xl font-bold text-white">{formatters.currencyExact(displayData.costPerUnit)}</p>
            <p className="text-sm text-slate-500">Total cost / {displayData.unitType}</p>
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