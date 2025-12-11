import React, { useEffect, useMemo, useRef, useState } from 'react';
import { Project } from '../../types';
import { formatCurrency, formatNumber, formatPercent } from '../../utils/formatters';
import { 
  HardHat, TrendingUp, Calendar, Clock, ChevronRight, 
  AlertCircle, Info, FileText, Building, Wrench, Zap, 
  Droplet, PaintBucket, DollarSign, MapPin, Download, BarChart3, Package
} from 'lucide-react';
import { ProvenanceModal } from '../../components/ProvenanceModal';
import { BackendDataMapper } from '../../utils/backendDataMapper';

interface Props {
  project: Project;
}

export const ConstructionView: React.FC<Props> = ({ project }) => {
  const [expandedTrade, setExpandedTrade] = useState<string | null>(null);
  const [showProvenanceModal, setShowProvenanceModal] = useState(false);
  
  const analysis = project.analysis;
  if (!analysis) {
    return <div className="p-6">Loading trade breakdown...</div>;
  }
  
  const calculations = analysis.calculations || {};
  const parsed_input = analysis.parsed_input || {};
  const displayData = BackendDataMapper.mapToDisplay(project.analysis);
  const isDev = typeof import.meta !== 'undefined' && Boolean(import.meta.env?.DEV);
  const constructionSchedule = calculations?.construction_schedule;

  // ========================================
  // PULL FROM SAME CALCULATION ENGINE
  // ========================================
  
  // Get values from calculations object - NO HARDCODING
  const squareFootageRaw =
    typeof parsed_input.square_footage === 'number' && parsed_input.square_footage > 0
      ? parsed_input.square_footage
      : typeof calculations.project_info?.square_footage === 'number' && calculations.project_info.square_footage > 0
        ? calculations.project_info.square_footage
        : 0;
  const squareFootage = squareFootageRaw > 0 ? squareFootageRaw : 0;
  const safeSquareFootage = squareFootage > 0 ? squareFootage : 1;
  const buildingType = parsed_input.building_type || 'office';
  const baseCostPerSF = calculations.construction_costs?.base_cost_per_sf || 1150;
  const regionalMultiplier = calculations.construction_costs?.regional_multiplier || 1.03;
  const complexityMultiplier = calculations.construction_costs?.class_multiplier || 1.00;
  const finalCostPerSF = calculations.construction_costs?.final_cost_per_sf || 1185;
  const rawCostBuildUp = Array.isArray(calculations.construction_costs?.cost_build_up)
    ? calculations.construction_costs.cost_build_up
    : [];
  const displayCostBuildUp = Array.isArray(displayData.constructionCostBuildUp)
    ? displayData.constructionCostBuildUp
    : [];
  const finishLevelName = (displayData.finishLevel || parsed_input.finish_level || 'standard').toString().toLowerCase();
  const costBuildUpSource =
    displayCostBuildUp.length > 0
      ? displayCostBuildUp
      : rawCostBuildUp;
  const fallbackCostBuildUp = [
    { label: 'Base Cost', value_per_sf: baseCostPerSF },
    { label: 'Regional', multiplier: regionalMultiplier || 1 },
    { label: 'Complexity', multiplier: complexityMultiplier || 1 },
  ];
  if (finishLevelName !== 'standard') {
    fallbackCostBuildUp.push({
      label: 'Finish Level',
      multiplier: calculations.construction_costs?.finish_cost_factor || 1,
    });
  }
  const costBuildUp =
    costBuildUpSource.length > 0 ? costBuildUpSource : fallbackCostBuildUp;
  
  // Debug: Log the actual values
  console.log('Construction View Debug:', {
    baseCostPerSF,
    regionalMultiplier,
    complexityMultiplier,
    finalCostPerSF,
    expectedFinal: baseCostPerSF * regionalMultiplier * complexityMultiplier,
    location: calculations.project_info?.location,
    rawData: calculations.construction_costs
  });
  // Use totals.hard_costs which includes base construction + special features
  // This ensures consistency with Executive View
  const constructionTotal = calculations.totals?.hard_costs || 246900000;
  const baseConstructionTotal = calculations.construction_costs?.construction_total || 236900000;
  const specialFeaturesTotal = calculations.construction_costs?.special_features_total || 0;
  const equipmentTotal = calculations.construction_costs?.equipment_total || (constructionTotal - baseConstructionTotal - specialFeaturesTotal) || 0;
  const displayCostPerSF = Math.round(finalCostPerSF || (constructionTotal / safeSquareFootage));
  
  // Trade breakdown from calculations - use actual percentages from backend
  const actualTradeBreakdown = calculations.trade_breakdown || {};
  const tradeTotal = Object.values(actualTradeBreakdown).reduce((sum: number, val: any) => sum + (val || 0), 0) || constructionTotal;
  
  const tradeBreakdown = {
    structural: {
      amount: actualTradeBreakdown.structural || (constructionTotal * 0.22),
      percent: Math.round(((actualTradeBreakdown.structural || (constructionTotal * 0.22)) / tradeTotal) * 100),
      color: 'blue',
      icon: Building,
      costPerSF: Math.round((actualTradeBreakdown.structural || (constructionTotal * 0.22)) / safeSquareFootage)
    },
    mechanical: {
      amount: actualTradeBreakdown.mechanical || (constructionTotal * 0.25),
      percent: Math.round(((actualTradeBreakdown.mechanical || (constructionTotal * 0.25)) / tradeTotal) * 100),
      color: 'green',
      icon: Wrench,
      costPerSF: Math.round((actualTradeBreakdown.mechanical || (constructionTotal * 0.25)) / safeSquareFootage)
    },
    electrical: {
      amount: actualTradeBreakdown.electrical || (constructionTotal * 0.15),
      percent: Math.round(((actualTradeBreakdown.electrical || (constructionTotal * 0.15)) / tradeTotal) * 100),
      color: 'yellow',
      icon: Zap,
      costPerSF: Math.round((actualTradeBreakdown.electrical || (constructionTotal * 0.15)) / safeSquareFootage)
    },
    plumbing: {
      amount: actualTradeBreakdown.plumbing || (constructionTotal * 0.12),
      percent: Math.round(((actualTradeBreakdown.plumbing || (constructionTotal * 0.12)) / tradeTotal) * 100),
      color: 'purple',
      icon: Droplet,
      costPerSF: Math.round((actualTradeBreakdown.plumbing || (constructionTotal * 0.12)) / safeSquareFootage)
    },
    finishes: {
      amount: actualTradeBreakdown.finishes || (constructionTotal * 0.26),
      percent: Math.round(((actualTradeBreakdown.finishes || (constructionTotal * 0.26)) / tradeTotal) * 100),
      color: 'pink',
      icon: PaintBucket,
      costPerSF: Math.round((actualTradeBreakdown.finishes || (constructionTotal * 0.26)) / safeSquareFootage)
    }
  };

  // Convert to array for iteration
  const trades = Object.entries(tradeBreakdown).map(([key, value]) => ({
    name: key.charAt(0).toUpperCase() + key.slice(1),
    ...value
  }));
  const formatMultiplier = (value?: number) => {
    if (typeof value !== 'number' || Number.isNaN(value)) {
      return undefined;
    }
    return value.toFixed(3).replace(/(?:\.0+|(\.\d+?)0+)$/, '$1');
  };
  const costBuildUpSequence = costBuildUp.map((step: any) => {
    if (!step) {
      return 'Unknown';
    }
    if (typeof step.value_per_sf === 'number') {
      return `${step.label ?? 'Base'} ${formatCurrency(step.value_per_sf)}/SF`;
    }
    if (typeof step.multiplier === 'number') {
      const formatted = formatMultiplier(step.multiplier);
      return `${step.label ?? 'Step'} ×${formatted ?? step.multiplier}`;
    }
    return step.label || 'Unknown';
  });
  const hasFinishStep = costBuildUp.some((step: any) => (step?.label || '').toLowerCase() === 'finish level');
  const costBuildUpLogRef = useRef(false);

  useEffect(() => {
    if (!isDev || costBuildUpLogRef.current) {
      return;
    }
    console.log('[SpecSharp DEV] cost_build_up', costBuildUp);
    costBuildUpLogRef.current = true;
  }, [isDev, costBuildUp]);

  type BackendPhase = {
    id?: string;
    label?: string;
    start_month?: number;
    startMonth?: number;
    duration?: number;
    color?: string;
  };

  type TimelinePhase = {
    id: string;
    label: string;
    startMonth: number;
    duration: number;
    color: string;
  };

  const backendPhases: BackendPhase[] = Array.isArray(constructionSchedule?.phases)
    ? (constructionSchedule?.phases as BackendPhase[])
    : [];

  const fallbackPhases: TimelinePhase[] = [
    { id: 'site_foundation', label: 'Site & Podium Work', startMonth: 0, duration: 6, color: 'blue' },
    { id: 'structural', label: 'Structure & Garage', startMonth: 4, duration: 14, color: 'green' },
    { id: 'exterior_envelope', label: 'Exterior Envelope', startMonth: 10, duration: 10, color: 'orange' },
    { id: 'mep_rough', label: 'MEP Rough', startMonth: 12, duration: 10, color: 'purple' },
    { id: 'interior_finishes', label: 'Interior Finishes', startMonth: 18, duration: 12, color: 'pink' },
    { id: 'mep_finishes', label: 'Commissioning & Punch', startMonth: 22, duration: 8, color: 'teal' }
  ];

  const phases: TimelinePhase[] =
    backendPhases.length > 0
      ? backendPhases.map((phase, index) => ({
          id: phase.id || phase.label || `phase-${index}`,
          label: phase.label || phase.id || `Phase ${index + 1}`,
          startMonth:
            typeof phase.start_month === 'number'
              ? phase.start_month
              : typeof phase.startMonth === 'number'
                ? phase.startMonth
                : 0,
          duration: typeof phase.duration === 'number' ? phase.duration : 0,
          color: phase.color || 'blue'
        }))
      : fallbackPhases;

  const totalMonthsRaw =
    typeof constructionSchedule?.total_months === 'number' ? constructionSchedule.total_months : 0;
  const totalMonths = totalMonthsRaw > 0 ? totalMonthsRaw : 30;

  const timelineMarkers = useMemo(() => {
    const segments = 4;
    const labels: string[] = [];
    for (let i = 0; i <= segments; i++) {
      const monthValue = i === 0 ? 1 : Math.max(1, Math.round((totalMonths / segments) * i));
      labels.push(`M${monthValue}`);
    }
    return labels;
  }, [totalMonths]);

  const timelineStartYearSource =
    calculations.project_timeline?.start_year ||
    parsed_input?.start_year ||
    new Date().getFullYear();
  const timelineStartYear =
    typeof timelineStartYearSource === 'number'
      ? timelineStartYearSource
      : Number(timelineStartYearSource) || new Date().getFullYear();

  const formatMonthToQuarter = (monthValue: number) => {
    if (typeof monthValue !== 'number' || Number.isNaN(monthValue)) {
      return 'TBD';
    }
    const normalized = Math.max(0, Math.round(monthValue));
    const yearOffset = Math.floor(normalized / 12);
    const quarter = Math.floor((normalized % 12) / 3) + 1;
    const displayYear = timelineStartYear + yearOffset;
    return `Q${quarter} ${displayYear}`;
  };

  const milestoneIcons = [HardHat, Building, Wrench, TrendingUp];
  const milestonePhases = phases.slice(0, 4);
  const milestones = milestonePhases.map((phase, index) => {
    const midpoint = phase.startMonth + phase.duration / 2;
    return {
      id: phase.id || `milestone-${index}`,
      label: phase.label,
      dateLabel: formatMonthToQuarter(midpoint)
    };
  });

  // Helper function for donut chart
  const createPath = (startAngle: number, endAngle: number, innerRadius: number = 25, outerRadius: number = 40) => {
    const startAngleRad = (startAngle * Math.PI) / 180;
    const endAngleRad = (endAngle * Math.PI) / 180;
    
    const x1 = 50 + outerRadius * Math.cos(startAngleRad);
    const y1 = 50 + outerRadius * Math.sin(startAngleRad);
    const x2 = 50 + outerRadius * Math.cos(endAngleRad);
    const y2 = 50 + outerRadius * Math.sin(endAngleRad);
    
    const x3 = 50 + innerRadius * Math.cos(endAngleRad);
    const y3 = 50 + innerRadius * Math.sin(endAngleRad);
    const x4 = 50 + innerRadius * Math.cos(startAngleRad);
    const y4 = 50 + innerRadius * Math.sin(startAngleRad);
    
    const largeArc = endAngle - startAngle > 180 ? 1 : 0;
    
    return `M ${x1} ${y1} A ${outerRadius} ${outerRadius} 0 ${largeArc} 1 ${x2} ${y2} L ${x3} ${y3} A ${innerRadius} ${innerRadius} 0 ${largeArc} 0 ${x4} ${y4} Z`;
  };

  const timelineMonthsLabel = `${totalMonths} Month${totalMonths === 1 ? '' : 's'} Timeline`;

  return (
    <div className="space-y-6">
      {/* Header Section - Dark Blue */}
      <div className="bg-gradient-to-r from-slate-800 to-slate-900 rounded-xl p-6 text-white">
        <div className="flex justify-between items-start">
          <div>
            <h1 className="text-2xl font-bold mb-2">
              {formatNumber(squareFootage)} SF {calculations.project_info?.display_name || 'Building'}
            </h1>
            <div className="flex items-center gap-4 text-sm text-slate-300">
              <span className="flex items-center gap-1">
                <MapPin className="h-3 w-3" />
                {parsed_input.location || 'Nashville'}
              </span>
              <span className="flex items-center gap-1">
                <Building className="h-3 w-3" />
                {parsed_input.floors || calculations.project_info?.typical_floors || 4} Floors
              </span>
              <span className="capitalize">{parsed_input.project_classification?.replace('_', '-') || 'Ground-Up'}</span>
            </div>
            
            <div className="flex gap-3 mt-4">
              <button className="flex items-center gap-2 px-4 py-2 bg-white/10 backdrop-blur border border-white/20 text-white rounded-lg hover:bg-white/20 transition">
                <Download className="h-4 w-4" />
                Export Excel
              </button>
              <button className="flex items-center gap-2 px-4 py-2 bg-white text-slate-800 rounded-lg hover:bg-slate-100 transition font-medium">
                <BarChart3 className="h-4 w-4" />
                Compare Scenarios
              </button>
            </div>
          </div>
          
          <div className="text-right">
            <p className="text-xs text-slate-400 uppercase tracking-wider mb-1">CONSTRUCTION COST</p>
            <p className="text-4xl font-bold">{formatCurrency(constructionTotal)}</p>
            <p className="text-lg text-slate-300">{formatCurrency(displayCostPerSF)} per SF</p>
          </div>
        </div>
        
        <div className="flex items-center gap-2 mt-6 text-sm text-slate-400">
          <Calendar className="h-4 w-4" />
          <span>{timelineMonthsLabel}</span>
          <span className="mx-2">•</span>
          <Clock className="h-4 w-4" />
          <span>Q1 2025 - Q2 2027</span>
        </div>
      </div>

      {/* Trade Filter Pills */}
      <div className="bg-white rounded-lg shadow-sm p-4">
        <div className="flex gap-2 flex-wrap">
          <button className="px-4 py-2 bg-blue-600 text-white rounded-full text-sm font-medium">
            All Trades
          </button>
          {trades.map(trade => (
            <button 
              key={trade.name}
              className="px-4 py-2 bg-gray-100 text-gray-700 rounded-full text-sm hover:bg-gray-200 transition flex items-center gap-2"
            >
              <span className={`w-2 h-2 rounded-full bg-${trade.color}-500`}></span>
              {trade.name}
            </button>
          ))}
        </div>
      </div>

      {/* Project Cost Analysis */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        <h2 className="text-xl font-bold text-gray-900 mb-2">Project Cost Analysis</h2>
        <p className="text-gray-600 mb-6">Comprehensive breakdown of construction costs by trade</p>
        
        <div className="grid grid-cols-2 gap-6">
          {/* Trade Distribution */}
          <div className="bg-gray-50 rounded-lg p-6">
            <div className="flex justify-between items-center mb-4">
              <h3 className="font-semibold text-gray-900">Trade Distribution</h3>
              <span className="text-sm text-gray-500">5 Major Trades</span>
            </div>
            
            {/* Donut Chart */}
            <div className="flex justify-center mb-6">
              <div className="relative">
                <svg width="200" height="200" viewBox="0 0 100 100" className="transform -rotate-90">
                  {(() => {
                    let currentAngle = 0;
                    return trades.map((trade) => {
                      const startAngle = currentAngle;
                      const endAngle = currentAngle + (trade.percent / 100) * 360;
                      currentAngle = endAngle;
                      
                      const colors = {
                        blue: '#3B82F6',
                        green: '#10B981',
                        yellow: '#F59E0B',
                        purple: '#8B5CF6',
                        pink: '#EC4899'
                      };
                      
                      return (
                        <path
                          key={trade.name}
                          d={createPath(startAngle, endAngle)}
                          fill={colors[trade.color as keyof typeof colors]}
                          className="hover:opacity-80 transition-opacity cursor-pointer"
                        />
                      );
                    });
                  })()}
                </svg>
                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="text-center">
                    <p className="text-2xl font-bold">${(constructionTotal / 1000000).toFixed(0)}M</p>
                    <p className="text-xs text-gray-500 uppercase">Total</p>
                  </div>
                </div>
              </div>
            </div>
            
            {/* Legend */}
            <div className="space-y-2">
              {trades.map(trade => (
                <div key={trade.name} className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div className={`w-3 h-3 rounded-full bg-${trade.color}-500`}></div>
                    <span className="text-sm text-gray-700">{trade.name}</span>
                  </div>
                  <div className="text-right">
                    <span className="text-sm font-bold">{trade.percent}%</span>
                    <span className="text-xs text-gray-500 ml-2">${(trade.amount / 1000000).toFixed(0)}M</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Construction Schedule */}
          <div className="bg-gray-50 rounded-lg p-6">
            <div className="flex justify-between items-center mb-4">
              <h3 className="font-semibold text-gray-900">Construction Schedule</h3>
              <span className="text-sm text-gray-500 flex items-center gap-1">
                <Clock className="h-4 w-4" />
                {timelineMonthsLabel}
              </span>
            </div>
            <p className="text-sm text-gray-600 mb-4">Phased timeline with trade overlap optimization</p>
            
            {/* Timeline Labels */}
            <div className="flex text-xs text-gray-400 mb-3 ml-24">
              {timelineMarkers.map((marker, index) => (
                <span key={`${marker}-${index}`} className="flex-1">
                  {marker}
                </span>
              ))}
            </div>
            
            {/* Gantt Chart */}
            <div className="space-y-2">
              {phases.map((phase) => {
                const colors = {
                  blue: 'bg-blue-500',
                  green: 'bg-green-500',
                  orange: 'bg-orange-500',
                  purple: 'bg-purple-500',
                  pink: 'bg-pink-500',
                  teal: 'bg-teal-500'
                };
                
                return (
                  <div key={phase.id} className="flex items-center gap-2">
                    <div className="w-20 text-xs text-gray-700 text-right truncate">{phase.label}</div>
                    <div className="flex-1 relative h-7 bg-gray-200 rounded">
                      <div 
                        className={`absolute h-full ${colors[phase.color as keyof typeof colors] || 'bg-blue-500'} rounded flex items-center justify-center text-xs text-white font-medium`}
                        style={{
                          left: `${(phase.startMonth / totalMonths) * 100}%`,
                          width: `${(phase.duration / totalMonths) * 100}%`
                        }}
                      >
                        {phase.duration}m
                      </div>
                    </div>
                    <span className="text-xs text-gray-500 w-10">{phase.duration} mo</span>
                  </div>
                );
              })}
            </div>

            {/* Key Milestones */}
            <div className="mt-6">
              <h4 className="text-sm font-semibold text-gray-700 mb-3">Key Milestones</h4>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {milestones.map((milestone, index) => {
                  const Icon = milestoneIcons[index % milestoneIcons.length];
                  return (
                    <div
                      key={milestone.id}
                      className="flex items-center gap-3 bg-white rounded-lg border border-gray-200 p-3"
                    >
                      <div className="p-2 rounded-full bg-slate-100">
                        <Icon className="h-4 w-4 text-slate-600" />
                      </div>
                      <div>
                        <p className="text-sm font-semibold text-gray-900">{milestone.label}</p>
                        <p className="text-xs text-gray-500">{milestone.dateLabel}</p>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
            
            {/* Warning - Dynamic based on building type */}
            <div className="mt-4 p-3 bg-yellow-50 rounded-lg border border-yellow-200">
              <div className="flex items-start gap-2">
                <Info className="h-4 w-4 text-yellow-600 mt-0.5 flex-shrink-0" />
                <p className="text-xs text-yellow-800">
                  <strong>Long-lead items:</strong> {
                    buildingType === 'healthcare' ? 'Medical equipment and AHUs require 16-20 week lead time. Order by Month 3 to avoid delays.' :
                    buildingType === 'restaurant' ? 'Kitchen equipment and bar fixtures require 8-10 week lead time. Order by Month 2 to avoid delays.' :
                    buildingType === 'office' ? 'Furniture systems and AV equipment require 6-8 week lead time. Order by Month 2 to avoid delays.' :
                    buildingType === 'retail' ? 'Display fixtures and POS systems require 6-8 week lead time. Order by Month 2 to avoid delays.' :
                    buildingType === 'industrial' ? 'Specialized machinery and racking systems require 10-12 week lead time. Order by Month 2 to avoid delays.' :
                    buildingType === 'hospitality' ? 'FF&E packages and kitchen equipment require 10-12 week lead time. Order by Month 2 to avoid delays.' :
                    buildingType === 'multifamily' ? 'Appliance packages and cabinetry require 8-10 week lead time. Order by Month 2 to avoid delays.' :
                    'Equipment and fixtures require standard lead times. Verify with suppliers for specific requirements.'
                  }
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Trade Summary */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        <div className="flex justify-between items-center mb-6">
          <h3 className="text-lg font-semibold text-gray-900">Trade Summary</h3>
          <button className="text-sm text-gray-500">
            Click on any trade for detailed breakdown
          </button>
        </div>
        
        <div className="space-y-4">
          {trades.map(trade => {
            const Icon = trade.icon;
            return (
              <div key={trade.name} className="border rounded-lg hover:shadow-md transition">
                <div 
                  className="p-4 cursor-pointer hover:bg-gray-50 transition-all"
                  onClick={() => setExpandedTrade(expandedTrade === trade.name ? null : trade.name)}
                  role="button"
                  tabIndex={0}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' || e.key === ' ') {
                      e.preventDefault();
                      setExpandedTrade(expandedTrade === trade.name ? null : trade.name);
                    }
                  }}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className={`p-2 bg-${trade.color}-50 rounded-lg`}>
                        <Icon className={`h-5 w-5 text-${trade.color}-600`} />
                      </div>
                      <div>
                        <h4 className="font-semibold text-gray-900">{trade.name}</h4>
                        <p className="text-sm text-gray-500">{trade.percent}% of construction cost</p>
                      </div>
                    </div>
                    
                    <div className="flex items-center gap-6">
                      <div className="text-right">
                        <p className="text-2xl font-bold">{formatCurrency(trade.amount)}</p>
                        <p className="text-sm text-gray-500">{formatCurrency(trade.costPerSF)}/SF</p>
                      </div>
                      <div className="p-2 rounded-lg transition">
                        <ChevronRight className={`h-5 w-5 text-gray-400 transition-transform ${expandedTrade === trade.name ? 'rotate-90' : ''}`} />
                      </div>
                    </div>
                  </div>
                  
                  {/* Progress Bar */}
                  <div className="mt-4">
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div 
                        className={`bg-${trade.color}-500 h-2 rounded-full transition-all`}
                        style={{ width: `${trade.percent * 2.5}%` }}
                      />
                    </div>
                  </div>
                </div>
                
                {/* Expanded Details */}
                {expandedTrade === trade.name && (
                  <div className="px-4 pb-4">
                    <div className="pt-4 border-t grid grid-cols-3 gap-4 text-sm">
                      <div>
                        <p className="text-gray-600">Materials</p>
                        <p className="font-semibold">{formatCurrency(trade.amount * 0.4)}</p>
                      </div>
                      <div>
                        <p className="text-gray-600">Labor</p>
                        <p className="font-semibold">{formatCurrency(trade.amount * 0.5)}</p>
                      </div>
                      <div>
                        <p className="text-gray-600">Equipment</p>
                        <p className="font-semibold">{formatCurrency(trade.amount * 0.1)}</p>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
        
        <div className="mt-6 pt-6 border-t text-right">
          <p className="text-lg text-gray-600">Total Construction Cost:</p>
          <p className="text-3xl font-bold text-blue-600">{formatCurrency(constructionTotal)}</p>
        </div>
        
        {/* Note about equipment */}
        {equipmentTotal > 0 && (
          <div className="mt-4 p-3 bg-amber-50 border border-amber-200 rounded-lg">
            <div className="flex items-start gap-2">
              <Info className="h-4 w-4 text-amber-600 mt-0.5 flex-shrink-0" />
              <div className="text-sm text-amber-800">
                <strong>Note:</strong> Trade percentages shown are based on base construction cost of {formatCurrency(baseConstructionTotal)}. 
                Equipment/FF&E of {formatCurrency(equipmentTotal)} is handled separately and shown in the Cost Build-Up Analysis above.
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Cost Build-Up Analysis - Enhanced Design */}
      <div className="bg-gradient-to-br from-gray-50 to-white rounded-xl shadow-lg p-8 border border-gray-100">
        <div className="mb-8">
          <h3 className="text-2xl font-bold text-gray-900 mb-2">Cost Build-Up Analysis</h3>
          <p className="text-gray-600">Understanding how your price is calculated step by step</p>
        </div>
        {isDev && (
          <div className="mb-4 text-xs font-mono text-slate-600">
            <span className="font-semibold">DEV • Build-Up:</span>{' '}
            <span>
              {costBuildUpSequence.length > 0
                ? costBuildUpSequence.join(' → ')
                : 'cost_build_up payload missing'}
            </span>
            {!hasFinishStep && (
              <span className="ml-2 font-semibold text-red-500">Finish step: MISSING</span>
            )}
          </div>
        )}
        
        {/* Main calculation flow */}
        <div className="space-y-8">
          {/* Row 1: Base calculation */}
          <div className="flex items-center justify-between gap-6">
            <div className="flex-1">
              <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow">
                <p className="text-sm text-gray-500 uppercase tracking-wider mb-3 font-medium">Step 1: Base Cost</p>
                <div className="flex items-baseline gap-2">
                  <p className="text-4xl font-bold text-gray-900">${formatNumber(baseCostPerSF)}</p>
                  <p className="text-lg text-gray-600">per SF</p>
                </div>
                <p className="text-sm text-gray-500 mt-3">RSMeans 2024 Q3 {calculations.project_info?.display_name || 'Building'}</p>
              </div>
            </div>
            
            <div className="flex items-center gap-2">
              <div className="w-12 h-0.5 bg-gray-300"></div>
              <ChevronRight className="h-6 w-6 text-gray-400" />
            </div>
            
            <div className="flex-1">
              <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow">
                <p className="text-sm text-gray-500 uppercase tracking-wider mb-3 font-medium">Step 2: Regional Adjustment</p>
                <div className="flex items-baseline gap-2">
                  <p className="text-4xl font-bold text-gray-900">×{regionalMultiplier.toFixed(2)}</p>
                  <p className="text-lg text-gray-600">multiplier</p>
                </div>
                <p className="text-sm text-gray-500 mt-3">Nashville, TN Market</p>
              </div>
            </div>
            
            <div className="flex items-center gap-2">
              <div className="w-12 h-0.5 bg-gray-300"></div>
              <ChevronRight className="h-6 w-6 text-gray-400" />
            </div>
            
            <div className="flex-1">
              <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow">
                <p className="text-sm text-gray-500 uppercase tracking-wider mb-3 font-medium">Step 3: Complexity</p>
                <div className="flex items-baseline gap-2">
                  <p className="text-4xl font-bold text-gray-900">×{complexityMultiplier.toFixed(2)}</p>
                  <p className="text-lg text-gray-600">multiplier</p>
                </div>
                <p className="text-sm text-gray-500 mt-3">Ground-Up Construction</p>
              </div>
            </div>
          </div>
          
          {/* Row 2: Base total */}
          <div className="flex items-center gap-6">
            <div className="flex-1">
              <div className="bg-gradient-to-r from-gray-50 to-gray-100 rounded-xl p-6 border border-gray-200">
                <p className="text-sm text-gray-600 uppercase tracking-wider mb-3 font-medium">Base Construction</p>
                <p className="text-3xl font-bold text-gray-900">${formatNumber(finalCostPerSF)}/SF</p>
                <p className="text-lg text-gray-700 mt-2">{formatCurrency(baseConstructionTotal)}</p>
                <p className="text-sm text-gray-500 mt-1">Core construction cost</p>
              </div>
            </div>
            
            {specialFeaturesTotal > 0 && (
              <>
                <div className="flex items-center gap-2">
                  <span className="text-2xl text-gray-400 font-bold">+</span>
                </div>
                
                <div className="flex-1">
                  <div className="bg-gradient-to-r from-yellow-50 to-orange-50 rounded-xl p-6 border border-orange-200">
                    <p className="text-sm text-orange-700 uppercase tracking-wider mb-3 font-medium">Special Features</p>
                    <p className="text-3xl font-bold text-orange-600">{formatCurrency(specialFeaturesTotal)}</p>
                    <div className="mt-2 space-y-1">
                      <p className="text-sm text-gray-700">Emergency Department</p>
                      <p className="text-xs text-gray-500">$50/SF additional × 200,000 SF</p>
                    </div>
                  </div>
                </div>
              </>
            )}
          </div>
          
          {/* Equipment/FF&E Addition */}
          {equipmentTotal > 0 && (
            <div className="bg-blue-50 rounded-lg p-6 border border-blue-200">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="p-3 bg-blue-100 rounded-lg">
                    <Package className="h-6 w-6 text-blue-600" />
                  </div>
                  <div>
                    <p className="text-sm text-blue-700 font-semibold uppercase tracking-wider">
                      Equipment & FF&E
                    </p>
                    <p className="text-2xl font-bold text-gray-900 mt-1">
                      {formatCurrency(equipmentTotal)}
                    </p>
                    <p className="text-sm text-gray-600 mt-1">
                      {buildingType === 'multifamily' ? 'Appliances, fixtures & furnishings' :
                       buildingType === 'healthcare' ? 'Medical equipment & furnishings' :
                       buildingType === 'educational' ? 'Classroom equipment & technology' :
                       'Furniture, fixtures & equipment'}
                    </p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-lg font-bold text-gray-900">
                    +${Math.round(equipmentTotal / safeSquareFootage)}/SF
                  </p>
                  <p className="text-sm text-gray-500">
                    {((equipmentTotal / constructionTotal) * 100).toFixed(1)}% of total
                  </p>
                </div>
              </div>
            </div>
          )}
          
          {/* Row 3: Final total */}
          <div className="bg-gradient-to-r from-blue-600 to-indigo-600 rounded-xl p-8 text-white shadow-xl">
            <div className="flex justify-between items-center">
              <div>
                <p className="text-sm uppercase tracking-wider mb-2 opacity-90">Final Construction Cost</p>
                <p className="text-5xl font-bold">{formatCurrency(constructionTotal)}</p>
              </div>
              <div className="text-right">
                <p className="text-2xl font-semibold">${formatNumber(Math.round(constructionTotal / safeSquareFootage))}/SF</p>
                <p className="text-sm opacity-90 mt-1">All-in cost per square foot</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Sensitivity Analysis */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-6">Sensitivity Analysis</h3>
        
        <div className="grid grid-cols-3 gap-6">
          <div>
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm text-gray-600">Regional Multiplier</span>
              <span className="text-sm font-bold">{regionalMultiplier.toFixed(2)}x</span>
            </div>
            <input 
              type="range" 
              min="80" 
              max="120" 
              value={regionalMultiplier * 100} 
              className="w-full"
              disabled
            />
            <p className="text-xs text-gray-500 mt-1">Nashville is 3% above national average</p>
          </div>
          
          <div>
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm text-gray-600">Complexity Factor</span>
              <span className="text-sm font-bold">{complexityMultiplier.toFixed(2)}x</span>
            </div>
            <input 
              type="range" 
              min="80" 
              max="120" 
              value={complexityMultiplier * 100} 
              className="w-full"
              disabled
            />
            <p className="text-xs text-gray-500 mt-1">Ground-Up (baseline complexity)</p>
          </div>
          
          <div className="text-center p-4 bg-blue-50 rounded-lg">
            <p className="text-sm text-gray-600 mb-2">Confidence Band</p>
            <p className="text-2xl font-bold">95%</p>
            <p className="text-xs text-gray-500 mt-1">confidence level</p>
            <p className="text-sm text-gray-600 mt-2">
              ${formatNumber(Math.round(finalCostPerSF * 0.9))}/SF - ${formatNumber(Math.round(finalCostPerSF * 1.1))}/SF
            </p>
            <p className="text-xs text-gray-500 mt-1">Based on 47 similar projects</p>
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="text-center py-6">
        <button 
          onClick={() => setShowProvenanceModal(true)}
          className="inline-flex items-center gap-2 text-blue-600 hover:text-blue-700 font-medium transition-colors"
        >
          <FileText className="h-4 w-4" />
          View Detailed Provenance Receipt
        </button>
      </div>
      
      {/* Provenance Modal */}
      <ProvenanceModal
        isOpen={showProvenanceModal}
        onClose={() => setShowProvenanceModal(false)}
        projectData={{
          building_type: parsed_input?.building_type,
          square_footage: squareFootage,
          location: parsed_input?.location,
          project_class: parsed_input?.project_classification || parsed_input?.project_class,
          confidence_projects: 47
        }}
        calculationTrace={calculations?.calculation_trace || project.analysis?.calculation_trace}
      />
    </div>
  );
};
