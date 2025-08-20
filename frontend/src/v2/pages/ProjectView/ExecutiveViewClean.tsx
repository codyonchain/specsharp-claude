import React from 'react';
import { Project } from '../../types';
import { formatters, safeGet, hasValue } from '../../utils/displayFormatters';
import { BackendDataMapper, DisplayData } from '../../utils/backendDataMapper';
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

// Icon mapping for departments
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
  'Building2': Building2,
  'Building': Building
};

export const ExecutiveViewClean: React.FC<Props> = ({ project }) => {
  // Early return if no project data
  if (!project?.analysis) {
    return (
      <div className="p-8 text-center text-gray-500">
        <p>Loading project data...</p>
      </div>
    );
  }
  
  // Map all backend data through the mapper
  const data: DisplayData = BackendDataMapper.mapToDisplay(project.analysis);
  
  // Get soft costs breakdown
  const softCostsBreakdown = project.analysis?.calculations?.soft_costs?.breakdown || {};
  const softCostCategories = Object.entries(softCostsBreakdown).map(([key, value]) => ({
    name: key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
    amount: value as number,
    percent: data.softCosts > 0 ? Math.round(((value as number) / data.softCosts) * 100) : 0
  }));
  
  return (
    <div className="space-y-6">
      {/* Executive Investment Dashboard Header */}
      <div className="bg-gradient-to-r from-blue-600 via-blue-700 to-indigo-700 rounded-2xl p-8 text-white shadow-2xl">
        <div className="flex justify-between items-start mb-8">
          <div>
            <h2 className="text-3xl font-bold mb-3">
              {formatters.squareFeet(data.squareFootage).replace(' SF', '')} SF {data.buildingSubtype.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
            </h2>
            <div className="flex items-center gap-6 text-sm text-blue-200">
              <span className="flex items-center gap-1.5">
                <MapPin className="h-4 w-4" />
                {data.location}
              </span>
              <span className="flex items-center gap-1.5">
                <Building className="h-4 w-4" />
                {data.floors} {data.floors === 1 ? 'Floor' : 'Floors'}
              </span>
            </div>
          </div>
          
          <div className="text-right">
            <p className="text-xs text-blue-200 uppercase tracking-wider mb-2 font-medium">TOTAL INVESTMENT REQUIRED</p>
            <p className="text-5xl font-bold">{formatters.currencyExact(data.totalProjectCost)}</p>
            <p className="text-lg text-blue-200">{formatters.costPerSF(data.costPerSF)}</p>
          </div>
        </div>
        
        <div className="grid grid-cols-4 gap-8 pt-6 mt-6 border-t border-white/20">
          <div>
            <p className="text-blue-200 text-xs uppercase tracking-wider mb-2 font-medium">CONSTRUCTION</p>
            <p className="text-3xl font-bold">{formatters.currency(data.constructionCost)}</p>
          </div>
          <div>
            <p className="text-blue-200 text-xs uppercase tracking-wider mb-2 font-medium">SOFT COSTS</p>
            <p className="text-3xl font-bold">{formatters.currency(data.softCosts)}</p>
          </div>
          <div>
            <p className="text-blue-200 text-xs uppercase tracking-wider mb-2 font-medium">EXPECTED ROI</p>
            <p className="text-3xl font-bold">{formatters.percentage(data.roi)}</p>
          </div>
          <div>
            <p className="text-blue-200 text-xs uppercase tracking-wider mb-2 font-medium">PAYBACK PERIOD</p>
            <p className="text-3xl font-bold">{formatters.years(data.paybackPeriod)}</p>
          </div>
        </div>
      </div>

      {/* Investment Decision Alert */}
      <div className={`${
        data.investmentDecision === 'NO-GO' ? 'bg-amber-50 border-amber-500' : 
        data.investmentDecision === 'GO' ? 'bg-green-50 border-green-500' : 
        'bg-gray-50 border-gray-500'
      } border-l-4 rounded-lg p-6`}>
        <div className="flex items-start gap-3">
          {data.investmentDecision === 'NO-GO' ? (
            <AlertCircle className="h-6 w-6 text-amber-600 flex-shrink-0" />
          ) : data.investmentDecision === 'GO' ? (
            <CheckCircle className="h-6 w-6 text-green-600 flex-shrink-0" />
          ) : (
            <Info className="h-6 w-6 text-gray-600 flex-shrink-0" />
          )}
          <div className="flex-1">
            <h3 className={`font-bold text-lg ${
              data.investmentDecision === 'NO-GO' ? 'text-amber-900' : 
              data.investmentDecision === 'GO' ? 'text-green-900' : 
              'text-gray-900'
            }`}>
              Investment Decision: {data.investmentDecision}
            </h3>
            <p className={`mt-1 ${
              data.investmentDecision === 'NO-GO' ? 'text-amber-700' : 
              data.investmentDecision === 'GO' ? 'text-green-700' : 
              'text-gray-700'
            }`}>
              {data.decisionReason}
            </p>
            
            {/* Display suggestions if NO-GO */}
            {data.investmentDecision === 'NO-GO' && data.suggestions.length > 0 && (
              <div className="mt-4 p-4 bg-white rounded-lg border border-amber-200">
                <h4 className="font-semibold text-amber-900 mb-2 flex items-center gap-2">
                  <Lightbulb className="h-4 w-4" />
                  How to Make This Project Pencil:
                </h4>
                <ul className="space-y-2">
                  {data.suggestions.map((suggestion, idx) => (
                    <li key={idx} className="flex items-start gap-2">
                      <span className="text-amber-600 mt-0.5">•</span>
                      <span className="text-sm text-gray-700">{suggestion}</span>
                    </li>
                  ))}
                </ul>
                
                {data.requiredRent > 0 && (
                  <div className="mt-3 pt-3 border-t border-amber-200">
                    <p className="text-sm text-gray-600">
                      Required rent for 8% return: <strong>{formatters.monthlyRent(data.requiredRent)}</strong>
                    </p>
                  </div>
                )}
              </div>
            )}
            
            <div className="flex items-center gap-6 mt-3">
              <span className="flex items-center gap-2">
                <span className={`w-2 h-2 ${data.roi >= 0.08 ? 'bg-green-500' : 'bg-red-500'} rounded-full`}></span>
                <span className="text-sm">ROI: <strong>{formatters.percentage(data.roi)}</strong></span>
              </span>
              <span className="flex items-center gap-2">
                <span className={`w-2 h-2 ${data.npv > 0 ? 'bg-green-500' : 'bg-red-500'} rounded-full`}></span>
                <span className="text-sm">10-yr NPV: <strong>{formatters.currency(data.npv)}</strong></span>
              </span>
              <span className="flex items-center gap-2">
                <span className={`w-2 h-2 ${data.dscr >= 1.25 ? 'bg-green-500' : 'bg-amber-500'} rounded-full`}></span>
                <span className="text-sm">DSCR: <strong>{formatters.multiplier(data.dscr)}</strong></span>
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
              {formatters.currency(data.annualRevenue)}
            </p>
            <p className="text-sm text-gray-500 mb-4">Annual Revenue</p>
            <div className="space-y-2 pt-4 border-t">
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Operating Margin</span>
                <span className="font-bold">{formatters.percentage(data.operatingMargin)}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Net Income</span>
                <span className="font-bold">{formatters.currency(data.noi)}</span>
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
            <p className="text-3xl font-bold text-gray-900">{formatters.number(data.unitCount)}</p>
            <p className="text-sm text-gray-500 mb-4">{data.unitLabel}</p>
            <div className="space-y-2 pt-4 border-t">
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Cost per {data.unitType}</span>
                <span className="font-bold">{formatters.currencyExact(data.costPerUnit)}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Revenue per {data.unitType}</span>
                <span className="font-bold">{formatters.currency(data.revenuePerUnit)}</span>
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
                  <span className="font-bold">
                    {formatters.percentage(data.constructionCost / data.totalProjectCost, 0)}
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-blue-600 h-2 rounded-full" 
                    style={{ width: `${(data.constructionCost / data.totalProjectCost) * 100}%` }} 
                  />
                </div>
              </div>
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-600">Soft Costs</span>
                  <span className="font-bold">
                    {formatters.percentage(data.softCosts / data.totalProjectCost, 0)}
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-purple-600 h-2 rounded-full" 
                    style={{ width: `${(data.softCosts / data.totalProjectCost) * 100}%` }} 
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Department Cost Allocation */}
      {data.departments.length > 0 && (
        <div>
          <h3 className="text-xl font-bold text-gray-900 mb-6">Department Cost Allocation</h3>
          <div className="grid grid-cols-3 gap-6">
            {data.departments.map((dept, idx) => {
              const Icon = iconMap[dept.icon_name || 'Building'] || Building;
              return (
                <div key={idx} className={`bg-gradient-to-br ${dept.gradient} rounded-xl p-6 text-white shadow-xl`}>
                  <div className="flex items-start justify-between mb-4">
                    <div className="p-3 bg-white/20 rounded-lg backdrop-blur">
                      <Icon className="h-6 w-6" />
                    </div>
                    <div className="text-right">
                      <p className="text-4xl font-bold">{formatters.percentage(dept.percent, 0)}</p>
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

      {/* Key Financial Indicators */}
      <div className="bg-gradient-to-r from-indigo-600 to-purple-600 rounded-xl p-8 text-white shadow-xl">
        <h3 className="text-2xl font-bold mb-6">Key Financial Indicators</h3>
        <div className="grid grid-cols-2 gap-8">
          <div>
            <p className="text-indigo-200 text-sm uppercase tracking-wider mb-2">BREAK-EVEN OCCUPANCY</p>
            <p className="text-4xl font-bold">{formatters.percentage(data.breakEvenOccupancy)}</p>
          </div>
          <div>
            <p className="text-indigo-200 text-sm uppercase tracking-wider mb-2">10-YEAR NPV</p>
            <p className="text-4xl font-bold">{formatters.currency(data.npv)}</p>
          </div>
          <div className="mt-6">
            <p className="text-indigo-200 text-sm uppercase tracking-wider mb-2">IRR</p>
            <p className="text-3xl font-bold">{formatters.percentage(data.irr)}</p>
          </div>
          <div className="mt-6">
            <p className="text-indigo-200 text-sm uppercase tracking-wider mb-2">PAYBACK PERIOD</p>
            <p className="text-3xl font-bold">{formatters.years(data.paybackPeriod)}</p>
          </div>
        </div>
      </div>

      {/* Operational Efficiency */}
      {(data.staffingMetrics.length > 0 || Object.keys(data.revenueMetrics).length > 0 || data.kpis.length > 0) && (
        <div className="bg-white rounded-xl shadow-lg p-6">
          <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
            <Activity className="h-5 w-5 text-purple-600" />
            Operational Efficiency
          </h3>
          
          {/* Staffing Metrics */}
          {data.staffingMetrics.length > 0 && (
            <div className="mb-4">
              <h4 className="text-sm font-bold text-gray-700 mb-3 uppercase tracking-wider">Staffing Metrics</h4>
              <div className="grid grid-cols-2 gap-3">
                {data.staffingMetrics.map((metric, idx) => (
                  <div key={idx} className="bg-gray-50 text-center p-4 rounded-lg">
                    <p className="text-3xl font-bold text-purple-600">{metric.value}</p>
                    <p className="text-xs text-gray-600">{metric.label}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
          
          {/* Revenue Efficiency */}
          {Object.keys(data.revenueMetrics).length > 0 && (
            <div className="mb-4">
              <h4 className="text-sm font-bold text-gray-700 mb-3 uppercase tracking-wider">Revenue Efficiency</h4>
              <div className="bg-white rounded-lg p-3 space-y-2 shadow-sm">
                {Object.entries(data.revenueMetrics).map(([key, value]) => (
                  <div key={key} className="flex justify-between text-sm">
                    <span className="text-gray-600">{key.replace(/_/g, ' ')}</span>
                    <span className="font-bold text-gray-900">{value}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
          
          {/* Target KPIs */}
          {data.kpis.length > 0 && (
            <div>
              <h4 className="text-sm font-bold text-gray-700 mb-3 uppercase tracking-wider">Target KPIs</h4>
              <div className="grid grid-cols-3 gap-2">
                {data.kpis.map((kpi, idx) => (
                  <div key={idx} className={`bg-${kpi.color}-50 p-3 rounded-lg text-center`}>
                    <p className={`text-xl font-bold text-${kpi.color}-700`}>{kpi.value}</p>
                    <p className={`text-xs text-${kpi.color}-600`}>{kpi.label}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Executive Financial Summary Footer */}
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
                  <p className="text-4xl font-bold text-white mb-2">{formatters.currencyExact(data.totalProjectCost)}</p>
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
                  <p className="text-4xl font-bold text-white mb-2">{formatters.currency(data.noi)}</p>
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
                      INVESTMENT PER {data.unitType.toUpperCase()}
                    </p>
                  </div>
                  <p className="text-4xl font-bold text-white mb-2">{formatters.currencyExact(data.costPerUnit)}</p>
                  <p className="text-sm text-purple-200">Total cost / {data.unitType}</p>
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
                  <p className="text-4xl font-bold text-white mb-2">{formatters.multiplier(data.dscr)}</p>
                  <p className="text-sm text-orange-200">DSCR (Target: 1.25x)</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};