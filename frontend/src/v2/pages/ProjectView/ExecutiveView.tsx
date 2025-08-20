import React from 'react';
import { Project } from '../../types';
import { formatCurrency, formatNumber, formatPercent } from '../../utils/formatters';
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

export const ExecutiveView: React.FC<Props> = ({ project }) => {
  // Early return if no project data
  if (!project || !project.analysis) {
    return (
      <div className="p-8 text-center text-gray-500">
        <p>Loading project data...</p>
      </div>
    );
  }
  
  const { analysis } = project;
  const { parsed_input, calculations } = analysis || {};
  
  // Early return if no calculations
  if (!calculations) {
    return (
      <div className="p-8 text-center text-gray-500">
        <p>No calculations available for this project.</p>
      </div>
    );
  }
  
  // Extract base values from backend
  const totals = calculations?.totals || {};
  const construction_costs = calculations?.construction_costs || {};
  const soft_costs = calculations?.soft_costs || {};
  const trade_breakdown = calculations?.trade_breakdown || {};
  const special_features = parsed_input?.special_features || [];
  
  const totalProjectCost = totals.total_project_cost || 0;
  const constructionTotal = totals.hard_costs || 0;
  const softCostsTotal = totals.soft_costs || 0;
  const specialFeaturesTotal = calculations?.special_features_cost || 0;
  const costPerSF = totals.cost_per_sf || 0;
  const squareFootage = parsed_input?.square_footage || 0;
  const buildingType = parsed_input?.building_type || 'office';
  const buildingSubtype = parsed_input?.building_subtype || parsed_input?.subtype || 'class_b';
  const location = parsed_input?.location || 'Nashville';
  const floors = parsed_input?.floors || 1;
  const finishLevel = parsed_input?.finish_level || 'standard';
  const projectComplexity = parsed_input?.project_complexity || 'ground_up';
  
  // Extract ALL financial metrics from backend ownership_analysis with safety
  const ownership = calculations?.ownership_analysis || {};
  const returnMetrics = ownership?.return_metrics || {};
  const debtMetrics = ownership?.debt_metrics || {};
  const investmentAnalysis = ownership?.investment_analysis || {};
  const projectInfo = ownership?.project_info || calculations?.project_info || {};
  
  // Get values DIRECTLY from backend - no calculations (with defaults)
  const roi = returnMetrics?.estimated_roi || returnMetrics?.cash_on_cash_return || 0;
  const npv = returnMetrics?.ten_year_npv || 0;
  const irr = returnMetrics?.irr || 0;
  const paybackPeriod = returnMetrics?.payback_period || 0;
  const dscr = debtMetrics?.calculated_dscr || 1.0;
  
  // Investment decision from backend (with safe defaults)
  const investmentDecision = investmentAnalysis?.decision || 'PENDING';
  const decisionReason = investmentAnalysis?.reason || '';
  const suggestions = Array.isArray(investmentAnalysis?.suggestions) ? investmentAnalysis.suggestions : [];
  const breakevenMetrics = investmentAnalysis?.breakeven_metrics || {};
  
  // Department allocations from backend (ensure array)
  const departments = Array.isArray(ownership?.department_allocation) ? ownership.department_allocation : 
                      Array.isArray(calculations?.department_allocation) ? calculations.department_allocation : [];
  
  // Operational metrics from backend (with safety)
  const operationalMetrics = ownership?.operational_metrics || calculations?.operational_metrics || {};
  const staffingMetrics = Array.isArray(operationalMetrics?.staffing) ? operationalMetrics.staffing : [];
  const revenueMetrics = operationalMetrics?.revenue || {};
  const targetKPIs = Array.isArray(operationalMetrics?.kpis) ? operationalMetrics.kpis : [];
  
  // Building-specific labels from backend
  const unitLabel = projectInfo.unit_label || 'Units';
  const unitCount = projectInfo.unit_count || 0;
  const unitType = projectInfo.unit_type || 'units';
  const milestoneLabel = projectInfo.completion_milestone || 'Grand Opening';
  
  // Annual revenue from backend analysis
  const annualRevenue = ownership?.annual_revenue || returnMetrics.annual_revenue || 0;
  
  // Map icon names from backend to Lucide icons
  const iconMap: { [key: string]: any } = {
    'Home': Home,
    'Heart': Heart,
    'Headphones': Headphones,
    'Cpu': Cpu,
    'Users': Users,
    'Shield': Shield,
    'GraduationCap': GraduationCap,
    'Activity': Activity,
    'Briefcase': Briefcase,
    'Building2': Building2
  };
  
  // Process departments from backend - add icons (with safety check)
  const departmentsWithIcons = (departments || []).map((dept: any) => ({
    ...dept,
    icon: iconMap[dept.icon_name] || Building
  }));
  
  console.log('📊 Backend data loaded:', {
    unitLabel,
    unitCount,
    investmentDecision,
    departmentsCount: departments.length,
    hasOwnershipAnalysis: !!ownership,
    hasOperationalMetrics: !!operationalMetrics
  });
  
  // Soft costs breakdown from backend
  const softCostCategories = Object.entries(soft_costs?.breakdown || {}).map(([key, value]) => ({
    name: key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
    amount: value as number,
    percent: Math.round(((value as number) / softCostsTotal) * 100)
  }));

  // Wrap in try-catch for debugging
  try {
    return (
    <div className="space-y-6">
      {/* Executive Investment Dashboard Header */}
      <div className="bg-gradient-to-r from-blue-600 via-blue-700 to-indigo-700 rounded-2xl p-8 text-white shadow-2xl">
        <div className="flex justify-between items-start mb-8">
          <div>
            <h2 className="text-3xl font-bold mb-3">
              {formatNumber(squareFootage)} SF {buildingSubtype.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
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
            <p className="text-5xl font-bold">{formatCurrency(totalProjectCost)}</p>
            <p className="text-lg text-blue-200">{formatCurrency(costPerSF)} per SF</p>
          </div>
        </div>
        
        <div className="flex items-center gap-6 text-xs text-blue-300">
          <Calendar className="h-4 w-4" />
          <span>27 Month Timeline</span>
          <span className="text-blue-400">•</span>
          <Clock className="h-4 w-4" />
          <span>Q1 2025 - Q2 2027</span>
        </div>
        
        <div className="grid grid-cols-4 gap-8 pt-6 mt-6 border-t border-white/20">
          <div>
            <p className="text-blue-200 text-xs uppercase tracking-wider mb-2 font-medium">CONSTRUCTION</p>
            <p className="text-3xl font-bold">{formatCurrency(constructionTotal)}</p>
          </div>
          <div>
            <p className="text-blue-200 text-xs uppercase tracking-wider mb-2 font-medium">SOFT COSTS</p>
            <p className="text-3xl font-bold">{formatCurrency(softCostsTotal)}</p>
          </div>
          <div>
            <p className="text-blue-200 text-xs uppercase tracking-wider mb-2 font-medium">EXPECTED ROI</p>
            <p className="text-3xl font-bold">{formatPercent(roi)}</p>
          </div>
          <div>
            <p className="text-blue-200 text-xs uppercase tracking-wider mb-2 font-medium">PAYBACK PERIOD</p>
            <p className="text-3xl font-bold">{paybackPeriod} yrs</p>
          </div>
        </div>
      </div>

      {/* Investment Decision Alert - Display backend analysis */}
      <div className={`${investmentDecision === 'NO-GO' ? 'bg-amber-50 border-amber-500' : investmentDecision === 'GO' ? 'bg-green-50 border-green-500' : 'bg-gray-50 border-gray-500'} border-l-4 rounded-lg p-6`}>
        <div className="flex items-start gap-3">
          {investmentDecision === 'NO-GO' ? (
            <AlertCircle className="h-6 w-6 text-amber-600 flex-shrink-0" />
          ) : investmentDecision === 'GO' ? (
            <CheckCircle className="h-6 w-6 text-green-600 flex-shrink-0" />
          ) : (
            <Info className="h-6 w-6 text-gray-600 flex-shrink-0" />
          )}
          <div className="flex-1">
            <h3 className={`font-bold text-lg ${investmentDecision === 'NO-GO' ? 'text-amber-900' : investmentDecision === 'GO' ? 'text-green-900' : 'text-gray-900'}`}>
              Investment Decision: {investmentDecision}
            </h3>
            <p className={`mt-1 ${investmentDecision === 'NO-GO' ? 'text-amber-700' : investmentDecision === 'GO' ? 'text-green-700' : 'text-gray-700'}`}>
              {decisionReason || (investmentDecision === 'NO-GO' 
                ? 'Project does not meet investment criteria. Consider value engineering or operational improvements.'
                : investmentDecision === 'GO' 
                ? 'Project meets investment criteria and is recommended for approval.'
                : 'Awaiting financial analysis...')}
            </p>
            
            {/* Display backend suggestions if NO-GO */}
            {investmentDecision === 'NO-GO' && suggestions && suggestions.length > 0 && (
              <div className="mt-4 p-4 bg-white rounded-lg border border-amber-200">
                <h4 className="font-semibold text-amber-900 mb-2 flex items-center gap-2">
                  <Lightbulb className="h-4 w-4" />
                  How to Make This Project Pencil:
                </h4>
                <ul className="space-y-2">
                  {suggestions.map((suggestion: string, idx: number) => (
                    <li key={idx} className="flex items-start gap-2">
                      <span className="text-amber-600 mt-0.5">•</span>
                      <span className="text-sm text-gray-700">{suggestion}</span>
                    </li>
                  ))}
                </ul>
                
                {/* Breakeven metrics from backend */}
                {breakevenMetrics.required_rent && (
                  <div className="mt-3 pt-3 border-t border-amber-200">
                    <p className="text-sm text-gray-600">
                      Required rent for 8% return: <strong>${breakevenMetrics.required_rent}/mo</strong>
                    </p>
                  </div>
                )}
              </div>
            )}
            <div className="flex items-center gap-6 mt-3">
              <span className="flex items-center gap-2">
                <span className={`w-2 h-2 ${roi < 0.08 ? 'bg-red-500' : 'bg-green-500'} rounded-full`}></span>
                <span className="text-sm">ROI: <strong className={roi < 0.08 ? 'text-red-600' : 'text-green-600'}>{formatPercent(roi)}</strong></span>
              </span>
              <span className="flex items-center gap-2">
                <span className={`w-2 h-2 ${dscr < 1.25 ? 'bg-red-500' : 'bg-green-500'} rounded-full`}></span>
                <span className="text-sm">DSCR: <strong className={dscr < 1.25 ? 'text-red-600' : 'text-green-600'}>{dscr}x</strong></span>
              </span>
              <span className="flex items-center gap-2">
                <span className={`w-2 h-2 ${paybackPeriod > 20 ? 'bg-amber-500' : 'bg-green-500'} rounded-full`}></span>
                <span className="text-sm">Payback: <strong className={paybackPeriod > 20 ? 'text-amber-600' : 'text-green-600'}>{paybackPeriod} yrs</strong></span>
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
              ${annualRevenue > 0 ? (annualRevenue / 1000000).toFixed(1) + 'M' : 'N/A'}
            </p>
            <p className="text-sm text-gray-500 mb-4">Annual Revenue</p>
            <div className="space-y-2 pt-4 border-t">
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Operating Margin</span>
                <span className="font-bold">20%</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Net Income</span>
                <span className="font-bold">{annualRevenue > 0 ? `${((annualRevenue * 0.2) / 1000000).toFixed(1)}M` : 'N/A'}</span>
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
            <p className="text-3xl font-bold text-gray-900">{unitCount}</p>
            <p className="text-sm text-gray-500 mb-4">{unitLabel}</p>
            <div className="space-y-2 pt-4 border-t">
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Cost per {unitType}</span>
                <span className="font-bold">{formatCurrency(totalProjectCost / Math.max(unitCount, 1))}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Revenue per {unitType}</span>
                <span className="font-bold">
                  {annualRevenue > 0 && unitCount > 0 ? formatCurrency(annualRevenue / unitCount) : 'N/A'}
                </span>
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
                  <span className="font-bold">{Math.round((constructionTotal / totalProjectCost) * 100)}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div className="bg-blue-600 h-2 rounded-full" style={{ width: `${(constructionTotal / totalProjectCost) * 100}%` }} />
                </div>
              </div>
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-600">Soft Costs</span>
                  <span className="font-bold">{Math.round((softCostsTotal / totalProjectCost) * 100)}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div className="bg-purple-600 h-2 rounded-full" style={{ width: `${(softCostsTotal / totalProjectCost) * 100}%` }} />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Department Cost Allocation - Beautiful Gradient Cards */}
      {departmentsWithIcons.length > 0 && (
      <div>
        <h3 className="text-xl font-bold text-gray-900 mb-6">Department Cost Allocation</h3>
        <div className="grid grid-cols-3 gap-6">
          {departmentsWithIcons.map((dept, idx) => {
            const Icon = dept.icon;
            return (
              <div key={idx} className={`bg-gradient-to-br ${dept.gradient} rounded-xl p-6 text-white shadow-xl`}>
                <div className="flex items-start justify-between mb-4">
                  <div className="p-3 bg-white/20 rounded-lg backdrop-blur">
                    <Icon className="h-6 w-6" />
                  </div>
                  <div className="text-right">
                    <p className="text-4xl font-bold">{Math.round(dept.percent * 100)}%</p>
                    <p className="text-sm text-white/80">of facility</p>
                  </div>
                </div>
                
                <h4 className="text-lg font-bold mb-1">{dept.name || 'Department'}</h4>
                <p className="text-3xl font-bold mb-4">{formatCurrency(dept.amount || 0)}</p>
                
                <div className="space-y-2 pt-4 border-t border-white/20">
                  <div className="flex justify-between text-sm">
                    <span className="text-white/80">Square Footage</span>
                    <span className="font-medium">{formatNumber(dept.square_footage || dept.squareFootage || 0)} SF</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-white/80">Cost per SF</span>
                    <span className="font-medium">{formatCurrency(dept.cost_per_sf || dept.costPerSF || 0)}</span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
      )}

      {/* Major Soft Cost Categories - Premium Styled */}
      <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-100">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-xl font-bold text-gray-900">Major Soft Cost Categories</h3>
          <div className="text-sm text-gray-500">
            {((softCostsTotal / totalProjectCost) * 100).toFixed(1)}% of total investment
          </div>
        </div>
        <div className="space-y-4">
          {softCostCategories.slice(0, 5).map((category, index) => {
            const percentage = (category.amount / softCostsTotal) * 100;
            const colors = ['blue', 'green', 'purple', 'orange', 'pink'];
            const color = colors[index % colors.length];
            
            return (
              <div key={index} className="group hover:bg-gray-50 rounded-lg p-3 transition-all">
                <div className="flex items-center gap-4">
                  <div className={`w-3 h-14 bg-${color}-600 rounded-full`}></div>
                  <div className="flex-1">
                    <div className="flex justify-between items-center mb-2">
                      <span className="text-sm font-semibold text-gray-800">{category.name}</span>
                      <div className="flex items-center gap-3">
                        <span className="text-xs px-2 py-1 bg-gray-100 rounded-full text-gray-600">
                          {percentage.toFixed(1)}%
                        </span>
                        <span className="text-lg font-bold text-gray-900">
                          {formatCurrency(category.amount)}
                        </span>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      <div className="flex-1 bg-gray-200 rounded-full h-2 overflow-hidden">
                        <div 
                          className={`h-2 bg-gradient-to-r from-${color}-500 to-${color}-600 rounded-full transition-all duration-500`}
                          style={{ width: `${Math.min(percentage, 100)}%` }}
                        />
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
        <div className="mt-6 pt-6 border-t border-gray-200 bg-gradient-to-r from-gray-50 to-gray-100 -mx-6 -mb-6 px-6 py-4 rounded-b-xl">
          <div className="flex justify-between items-center">
            <span className="text-lg font-semibold text-gray-900">Total Soft Costs</span>
            <div className="text-right">
              <span className="text-2xl font-bold text-gray-900">{formatCurrency(softCostsTotal)}</span>
              <span className="text-sm text-gray-500 block">{((softCostsTotal / constructionTotal) * 100).toFixed(1)}% of construction</span>
            </div>
          </div>
        </div>
      </div>

      {/* Key Financial Indicators - Display backend values */}
      <div className="bg-gradient-to-r from-indigo-600 to-purple-600 rounded-xl p-8 text-white shadow-xl">
        <h3 className="text-2xl font-bold mb-6">Key Financial Indicators</h3>
        <div className="grid grid-cols-2 gap-8">
          <div>
            <p className="text-indigo-200 text-sm uppercase tracking-wider mb-2">BREAK-EVEN OCCUPANCY</p>
            <p className="text-4xl font-bold">{formatPercent(breakevenMetrics.occupancy || 0.85)}</p>
          </div>
          <div>
            <p className="text-indigo-200 text-sm uppercase tracking-wider mb-2">10-YEAR NPV</p>
            <p className="text-4xl font-bold">
              {npv < 0 ? '-' : ''}${Math.abs(npv / 1000000).toFixed(1)}M
            </p>
          </div>
          <div className="mt-6">
            <p className="text-indigo-200 text-sm uppercase tracking-wider mb-2">IRR</p>
            <p className="text-3xl font-bold">{formatPercent(irr)}</p>
          </div>
          <div className="mt-6">
            <p className="text-indigo-200 text-sm uppercase tracking-wider mb-2">PAYBACK PERIOD</p>
            <p className="text-3xl font-bold">{paybackPeriod.toFixed(1)} yrs</p>
          </div>
        </div>
      </div>

      {/* Market Position & Quick Sensitivity - Premium Cards */}
      <div className="grid grid-cols-2 gap-6">
        {/* Market Position Card */}
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
                  <span className="text-xl font-bold text-blue-600">{formatCurrency(costPerSF)}/SF</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-500">Regional Average</span>
                  <span className="font-medium text-gray-700">${Math.round(costPerSF * 0.85)}/SF</span>
                </div>
              </div>
              
              <div className="relative">
                <div className="w-full bg-gradient-to-r from-green-100 via-yellow-100 to-red-100 rounded-full h-4 overflow-hidden">
                  <div className="absolute top-0 left-1/2 transform -translate-x-1/2 h-full w-0.5 bg-gray-700"></div>
                  <div 
                    className="absolute top-0 h-full w-1 bg-blue-600 shadow-lg"
                    style={{ left: '65%' }}
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

        {/* Quick Sensitivity Card */}
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
                <span className="text-lg font-bold text-red-600">ROI drops to 3.9%</span>
              </div>
            </div>
            <div className="bg-white rounded-lg p-4 shadow-sm">
              <p className="text-xs text-gray-500 uppercase tracking-wider mb-2">If revenue +10%:</p>
              <div className="flex items-center justify-between">
                <TrendingUp className="h-5 w-5 text-green-500" />
                <span className="text-lg font-bold text-green-600">ROI rises to 6.2%</span>
              </div>
            </div>
            <div className="p-4 bg-gradient-to-r from-purple-100 to-pink-100 rounded-lg">
              <p className="text-xs text-gray-600 uppercase tracking-wider mb-2">Break-even needs:</p>
              <span className="text-xl font-bold text-purple-700">85% occupancy</span>
            </div>
          </div>
        </div>
      </div>

      {/* Key Milestones Timeline - Premium Design */}
      <div className="bg-gradient-to-br from-white via-blue-50 to-indigo-50 rounded-xl shadow-lg p-8 border border-blue-100">
        <h3 className="text-xl font-bold text-gray-900 mb-6 flex items-center gap-2">
          <Calendar className="h-6 w-6 text-blue-600" />
          Key Milestones
        </h3>
        <div className="relative">
          <div className="absolute left-10 top-10 bottom-0 w-0.5 bg-gradient-to-b from-blue-400 via-purple-400 to-pink-400"></div>
          <div className="space-y-8">
            {[
              { icon: CheckCircle, color: 'green', title: 'Groundbreaking', date: 'Q1 2025', status: 'upcoming' },
              { icon: Building, color: 'blue', title: 'Structure Complete', date: 'Q3 2025', status: 'future' },
              { icon: Users, color: 'purple', title: 'Substantial Completion', date: 'Q2 2027', status: 'future' },
              { icon: Target, color: 'orange', title: milestoneLabel, date: 'Q3 2027', status: 'future' }
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

      {/* Financing Structure & Operational Efficiency - Premium Grid */}
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
                    <span className="text-sm font-semibold text-gray-700">{item.name} ({(item.percent * 100)}%)</span>
                    <span className="font-bold text-gray-900">{formatCurrency(totalProjectCost * item.percent)}</span>
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
                <span className="font-bold text-gray-900">${((totalProjectCost * 0.65 * 0.068) / 1000000).toFixed(1)}M</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Interest During Construction</span>
                <span className="font-bold text-gray-900">${((totalProjectCost * 0.044) / 1000000).toFixed(1)}M</span>
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
            <div className="mb-4">
              <h4 className="text-sm font-bold text-gray-700 mb-3 uppercase tracking-wider">Staffing Metrics</h4>
              <div className="grid grid-cols-2 gap-3">
                <div className="bg-white text-center p-4 rounded-lg shadow-sm">
                  <p className="text-3xl font-bold text-purple-600">
                    {buildingType === 'multifamily' ? '50' : 
                     buildingType === 'healthcare' ? '4.2' :
                     buildingType === 'educational' ? '25' : '150'}
                  </p>
                  <p className="text-xs text-gray-600">
                    {buildingType === 'multifamily' ? 'Units per Manager' : 
                     buildingType === 'healthcare' ? 'Beds per Nurse' :
                     buildingType === 'educational' ? 'Students per Teacher' : 'SF per Employee'}
                  </p>
                </div>
                <div className="bg-white text-center p-4 rounded-lg shadow-sm">
                  <p className="text-3xl font-bold text-pink-600">
                    {buildingType === 'multifamily' ? '8' : 
                     buildingType === 'healthcare' ? '750' :
                     buildingType === 'educational' ? '45' : '12'}
                  </p>
                  <p className="text-xs text-gray-600">
                    {buildingType === 'multifamily' ? 'Maintenance Staff' : 
                     buildingType === 'healthcare' ? 'Total FTEs Required' :
                     buildingType === 'educational' ? 'Faculty & Staff' : 'Janitorial Staff'}
                  </p>
                </div>
              </div>
            </div>
            
            <div className="mb-4">
              <h4 className="text-sm font-bold text-gray-700 mb-3 uppercase tracking-wider">Revenue Efficiency</h4>
              <div className="bg-white rounded-lg p-3 space-y-2 shadow-sm">
                {buildingType === 'multifamily' ? (
                  <>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">Revenue per Unit</span>
                      <span className="font-bold text-gray-900">
                        ${annualRevenue > 0 && unitCount > 0 ? ((annualRevenue / unitCount) / 1000).toFixed(1) : '0'}K
                      </span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">Average Rent</span>
                      <span className="font-bold text-gray-900">
                        ${buildingSubtype === 'luxury_apartments' ? '3,500' :
                          buildingSubtype === 'affordable_housing' ? '1,200' :
                          buildingSubtype === 'senior_living' ? '2,800' :
                          buildingSubtype === 'student_housing' ? '1,500' : '2,200'}/mo
                      </span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">Occupancy Target</span>
                      <span className="font-bold text-gray-900">93%</span>
                    </div>
                  </>
                ) : buildingType === 'healthcare' ? (
                  <>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">Revenue per Employee</span>
                      <span className="font-bold text-gray-900">$111K</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">Revenue per Bed</span>
                      <span className="font-bold text-gray-900">$553K</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">Labor Cost Ratio</span>
                      <span className="font-bold text-gray-900">52%</span>
                    </div>
                  </>
                ) : buildingType === 'educational' ? (
                  <>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">Cost per Student</span>
                      <span className="font-bold text-gray-900">$12K</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">Student/Teacher Ratio</span>
                      <span className="font-bold text-gray-900">15:1</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">State Funding %</span>
                      <span className="font-bold text-gray-900">65%</span>
                    </div>
                  </>
                ) : (
                  <>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">Revenue per SF</span>
                      <span className="font-bold text-gray-900">$35</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">Lease Rate</span>
                      <span className="font-bold text-gray-900">$35/SF</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">Occupancy Target</span>
                      <span className="font-bold text-gray-900">90%</span>
                    </div>
                  </>
                )}
              </div>
            </div>
            
            <div>
              <h4 className="text-sm font-bold text-gray-700 mb-3 uppercase tracking-wider">Target KPIs</h4>
              <div className="grid grid-cols-3 gap-2">
                {buildingType === 'multifamily' ? (
                  <>
                    <div className="bg-gradient-to-br from-blue-100 to-blue-200 p-3 rounded-lg text-center">
                      <p className="text-xl font-bold text-blue-700">6mo</p>
                      <p className="text-xs text-blue-600">Lease-up</p>
                    </div>
                    <div className="bg-gradient-to-br from-green-100 to-green-200 p-3 rounded-lg text-center">
                      <p className="text-xl font-bold text-green-700">93%</p>
                      <p className="text-xs text-green-600">Occupancy</p>
                    </div>
                    <div className="bg-gradient-to-br from-purple-100 to-purple-200 p-3 rounded-lg text-center">
                      <p className="text-xl font-bold text-purple-700">
                        ${buildingSubtype === 'luxury_apartments' ? '3.5K' :
                          buildingSubtype === 'affordable_housing' ? '1.2K' : '2.2K'}
                      </p>
                      <p className="text-xs text-purple-600">Rent/Unit</p>
                    </div>
                  </>
                ) : buildingType === 'healthcare' ? (
                  <>
                    <div className="bg-gradient-to-br from-blue-100 to-blue-200 p-3 rounded-lg text-center">
                      <p className="text-xl font-bold text-blue-700">3.8</p>
                      <p className="text-xs text-blue-600">ALOS (days)</p>
                    </div>
                    <div className="bg-gradient-to-br from-green-100 to-green-200 p-3 rounded-lg text-center">
                      <p className="text-xl font-bold text-green-700">85%</p>
                      <p className="text-xs text-green-600">Occupancy</p>
                    </div>
                    <div className="bg-gradient-to-br from-purple-100 to-purple-200 p-3 rounded-lg text-center">
                      <p className="text-xl font-bold text-purple-700">$11K</p>
                      <p className="text-xs text-purple-600">Rev/Admission</p>
                    </div>
                  </>
                ) : buildingType === 'educational' ? (
                  <>
                    <div className="bg-gradient-to-br from-blue-100 to-blue-200 p-3 rounded-lg text-center">
                      <p className="text-xl font-bold text-blue-700">180</p>
                      <p className="text-xs text-blue-600">School Days</p>
                    </div>
                    <div className="bg-gradient-to-br from-green-100 to-green-200 p-3 rounded-lg text-center">
                      <p className="text-xl font-bold text-green-700">95%</p>
                      <p className="text-xs text-green-600">Attendance</p>
                    </div>
                    <div className="bg-gradient-to-br from-purple-100 to-purple-200 p-3 rounded-lg text-center">
                      <p className="text-xl font-bold text-purple-700">15:1</p>
                      <p className="text-xs text-purple-600">Student Ratio</p>
                    </div>
                  </>
                ) : (
                  <>
                    <div className="bg-gradient-to-br from-blue-100 to-blue-200 p-3 rounded-lg text-center">
                      <p className="text-xl font-bold text-blue-700">$35/SF</p>
                      <p className="text-xs text-blue-600">Lease Rate</p>
                    </div>
                    <div className="bg-gradient-to-br from-green-100 to-green-200 p-3 rounded-lg text-center">
                      <p className="text-xl font-bold text-green-700">90%</p>
                      <p className="text-xs text-green-600">Occupancy</p>
                    </div>
                    <div className="bg-gradient-to-br from-purple-100 to-purple-200 p-3 rounded-lg text-center">
                      <p className="text-xl font-bold text-purple-700">$8/SF</p>
                      <p className="text-xs text-purple-600">NNN</p>
                    </div>
                  </>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Executive Decision Points - Premium Alert */}
      <div className="bg-gradient-to-r from-amber-50 via-orange-50 to-amber-50 border-l-4 border-amber-500 rounded-xl shadow-lg p-6">
        <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-3">
          <div className="p-2 bg-amber-100 rounded-lg">
            <Lightbulb className="h-6 w-6 text-amber-600" />
          </div>
          Executive Decision Points
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {[
            `Total investment of ${formatCurrency(totalProjectCost)} is ${
              buildingType === 'multifamily' ? '7% above regional multifamily' : 
              buildingType === 'healthcare' ? '9% above regional healthcare' : 
              '5% above regional'
            } average`,
            buildingType === 'multifamily' ? 
              `${unitCount} units with avg rent of $${
                buildingSubtype === 'luxury_apartments' ? '3,500' : 
                buildingSubtype === 'affordable_housing' ? '1,200' : '2,200'
              }/month` :
              '22-year payback suggests need for operational efficiency improvements',
            buildingType === 'multifamily' ?
              'Amenity package adds 8% to costs but supports premium rents' :
              'Consider phased opening to accelerate revenue generation',
            `Soft costs at ${((softCostsTotal / constructionTotal) * 100).toFixed(1)}% ${
              buildingType === 'multifamily' ? '- typical for luxury multifamily' : 
              '- opportunity for value engineering'
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

      {/* Executive Financial Summary Footer - Enhanced Premium Design */}
      <div className="bg-gradient-to-br from-indigo-900 via-purple-900 to-pink-900 rounded-xl shadow-2xl overflow-hidden">
        <div className="bg-gradient-to-r from-white/10 to-transparent p-1">
          <div className="bg-gradient-to-br from-indigo-800/90 to-purple-800/90 rounded-lg p-8 backdrop-blur-sm">
            <div className="grid grid-cols-4 gap-8">
              <div className="group hover:scale-105 transition-transform">
                <div className="p-6 bg-white/10 rounded-xl backdrop-blur border border-white/20 shadow-lg">
                  <div className="flex items-center gap-3 mb-4">
                    <div className="p-2 bg-blue-400/20 rounded-lg">
                      <DollarSign className="h-5 w-5 text-blue-300" />
                    </div>
                    <p className="text-blue-200 text-xs uppercase tracking-wider font-semibold">TOTAL CAPITAL REQUIRED</p>
                  </div>
                  <p className="text-4xl font-bold text-white mb-2">{formatCurrency(totalProjectCost)}</p>
                  <p className="text-sm text-blue-200">Construction + Soft Costs</p>
                </div>
              </div>
              
              <div className="group hover:scale-105 transition-transform">
                <div className="p-6 bg-white/10 rounded-xl backdrop-blur border border-white/20 shadow-lg">
                  <div className="flex items-center gap-3 mb-4">
                    <div className="p-2 bg-green-400/20 rounded-lg">
                      <TrendingUp className="h-5 w-5 text-green-300" />
                    </div>
                    <p className="text-green-200 text-xs uppercase tracking-wider font-semibold">EXPECTED ANNUAL RETURN</p>
                  </div>
                  <p className="text-4xl font-bold text-white mb-2">${((annualRevenue * 0.2) / 1000000).toFixed(1)}M</p>
                  <p className="text-sm text-green-200">After operating expenses</p>
                </div>
              </div>
              
              <div className="group hover:scale-105 transition-transform">
                <div className="p-6 bg-white/10 rounded-xl backdrop-blur border border-white/20 shadow-lg">
                  <div className="flex items-center gap-3 mb-4">
                    <div className="p-2 bg-purple-400/20 rounded-lg">
                      <Building className="h-5 w-5 text-purple-300" />
                    </div>
                    <p className="text-purple-200 text-xs uppercase tracking-wider font-semibold">
                      {buildingType === 'multifamily' ? 'INVESTMENT PER UNIT' :
                       buildingType === 'healthcare' ? 'INVESTMENT PER BED' :
                       buildingType === 'educational' ? 'INVESTMENT PER CLASSROOM' :
                       'INVESTMENT PER FLOOR'}
                    </p>
                  </div>
                  <p className="text-4xl font-bold text-white mb-2">{formatCurrency(totalProjectCost / Math.max(unitCount, 1))}</p>
                  <p className="text-sm text-purple-200">Total cost / {unitType}</p>
                </div>
              </div>
              
              <div className="group hover:scale-105 transition-transform">
                <div className="p-6 bg-white/10 rounded-xl backdrop-blur border border-white/20 shadow-lg">
                  <div className="flex items-center gap-3 mb-4">
                    <div className="p-2 bg-orange-400/20 rounded-lg">
                      <BarChart3 className="h-5 w-5 text-orange-300" />
                    </div>
                    <p className="text-orange-200 text-xs uppercase tracking-wider font-semibold">DEBT COVERAGE</p>
                  </div>
                  <p className="text-4xl font-bold text-white mb-2">{dscr}x</p>
                  <p className="text-sm text-orange-200">DSCR (Target: 1.25x)</p>
                </div>
              </div>
            </div>
            
            {/* Premium Footer Accent */}
            <div className="mt-8 pt-6 border-t border-white/20">
              <div className="flex items-center justify-center gap-2 text-white/60">
                <div className="w-2 h-2 bg-blue-400 rounded-full animate-pulse"></div>
                <span className="text-sm font-medium">Executive Financial Summary</span>
                <div className="w-2 h-2 bg-purple-400 rounded-full animate-pulse delay-150"></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
  } catch (error) {
    console.error('ExecutiveView Error:', error);
    return (
      <div className="p-8 bg-red-50 border border-red-200 rounded-lg">
        <h3 className="text-red-800 font-bold mb-2">Error Loading Executive View</h3>
        <p className="text-red-600 text-sm">{error instanceof Error ? error.message : 'Unknown error occurred'}</p>
        <details className="mt-4">
          <summary className="cursor-pointer text-red-700 text-sm">Debug Info</summary>
          <pre className="mt-2 text-xs bg-white p-2 rounded overflow-auto">
            {JSON.stringify({
              hasProject: !!project,
              hasAnalysis: !!analysis,
              hasCalculations: !!calculations,
              hasDepartments: departments.length,
              error: error instanceof Error ? error.stack : error
            }, null, 2)}
          </pre>
        </details>
      </div>
    );
  }
};