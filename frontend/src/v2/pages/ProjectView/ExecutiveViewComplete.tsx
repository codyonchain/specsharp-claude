import React, { useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { Project } from '../../types';
import { formatters, safeGet } from '../../utils/displayFormatters';
import { BackendDataMapper } from '../../utils/backendDataMapper';
// Removed FinancialRequirementsCard - was only implemented for hospital
import * as XLSX from 'xlsx';
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
  const navigate = useNavigate();
  
  // Early return if no project data - check multiple paths for data
  if (!project?.analysis && !project?.calculation_data) {
    return (
      <div className="p-8 text-center text-gray-500">
        <p>Loading project data...</p>
      </div>
    );
  }

  // Get analysis from project or use project itself if it has the data
  const analysis = project?.analysis || { calculations: project?.calculation_data } || project;
  
  // Map backend data through our mapper
  const displayData = BackendDataMapper.mapToDisplay(analysis);
  const investmentDecisionFromDisplay = displayData.investmentDecision;
  const feasibilityFlag = typeof displayData.feasible === 'boolean' ? displayData.feasible : undefined;
  const derivedDecision = typeof investmentDecisionFromDisplay === 'string'
    ? investmentDecisionFromDisplay
    : investmentDecisionFromDisplay?.recommendation || 'PENDING';
  const decisionStatus = feasibilityFlag === true
    ? 'GO'
    : feasibilityFlag === false
      ? 'NO-GO'
      : derivedDecision;
  const decisionReasonText = displayData.decisionReason || (
    typeof investmentDecisionFromDisplay === 'object'
      ? investmentDecisionFromDisplay?.summary
      : undefined
  ) || 'Investment analysis in progress';
  const feasibilityChipLabel = feasibilityFlag === true
    ? 'Feasible'
    : feasibilityFlag === false
      ? 'Needs Work'
      : 'Pending Review';
  
  // Extract additional raw data we need - check multiple paths for data
  const parsed = analysis?.parsed_input || {};
  // Look for calculations in multiple places due to data mapping
  const calculations = analysis?.calculations || project?.calculation_data || project || {};
  const totals = calculations?.totals || {};
  const construction_costs = calculations?.construction_costs || {};
  const soft_costs = calculations?.soft_costs || {};
  const ownership = calculations?.ownership_analysis || {};
  const investmentAnalysis = ownership?.investment_analysis || {};
  const calculationTrace = Array.isArray(calculations?.calculation_trace)
    ? calculations.calculation_trace.filter((entry: any) => entry && typeof entry === 'object' && entry.step)
    : [];

  const getLatestTrace = (step: string) => {
    for (let i = calculationTrace.length - 1; i >= 0; i -= 1) {
      const entry = calculationTrace[i];
      if (entry?.step === step) {
        return entry;
      }
    }
    return undefined;
  };

  const finishSourceEntry = getLatestTrace('finish_level_source');
  const modifiersTrace = getLatestTrace('modifiers_applied');
  const inferredTrace = getLatestTrace('finish_level_inferred');

  const normalizeFinishLevel = (value?: string | null) => {
    if (!value || typeof value !== 'string') {
      return undefined;
    }
    const trimmed = value.trim();
    if (!trimmed) {
      return undefined;
    }
    return trimmed.charAt(0).toUpperCase() + trimmed.slice(1).toLowerCase();
  };

  const finishLevelFromDisplay = normalizeFinishLevel(displayData.finishLevel);
  const finishLevelFromProject = normalizeFinishLevel(calculations?.project_info?.finish_level);
  const finishLevelFromTrace = normalizeFinishLevel(inferredTrace?.data?.finish_level || modifiersTrace?.data?.finish_level);
  const finishLevel = finishLevelFromProject || finishLevelFromDisplay || finishLevelFromTrace;

  const displayFinishSource = displayData.finishLevelSource;
  const finishSourceRaw = finishSourceEntry?.data?.source;
  const finishSource =
    displayFinishSource === 'explicit' || displayFinishSource === 'description' || displayFinishSource === 'default'
      ? displayFinishSource
      : finishSourceRaw === 'explicit' || finishSourceRaw === 'description'
        ? finishSourceRaw
        : 'default';

  const costFactorFromDisplay = typeof displayData.costFactor === 'number' ? displayData.costFactor : undefined;
  const revenueFactorFromDisplay = typeof displayData.revenueFactor === 'number' ? displayData.revenueFactor : undefined;
  const costFactor = costFactorFromDisplay ?? (typeof modifiersTrace?.data?.cost_factor === 'number' ? modifiersTrace.data.cost_factor : undefined);
  const revenueFactor = revenueFactorFromDisplay ?? (typeof modifiersTrace?.data?.revenue_factor === 'number' ? modifiersTrace.data.revenue_factor : undefined);

  const isDev = typeof import.meta !== 'undefined' && Boolean(import.meta.env?.DEV);

  const formatMultiplier = (value?: number) => {
    if (typeof value !== 'number' || Number.isNaN(value)) {
      return undefined;
    }
    return value.toFixed(3).replace(/(?:\.0+|(\.\d+?)0+)$/, '$1');
  };

  const costFactorText = formatMultiplier(costFactor);
  const revenueFactorText = formatMultiplier(revenueFactor);

  const finishChipTooltip = finishSource === 'explicit'
    ? 'Source: Selected in form'
    : finishSource === 'description'
      ? 'Source: Inferred from description'
      : 'Source: Default (Standard)';

  const hasFinishPayload = Boolean(finishLevel || costFactor || revenueFactor);
  const finishChipDetail = hasFinishPayload
    ? `Finish: ${finishLevel || 'Standard'} ${costFactorText && revenueFactorText
      ? `(Cost ×${costFactorText} · Rev ×${revenueFactorText})`
      : '(applied)'}`.trim()
    : 'MISSING';

  const finishChipClasses = hasFinishPayload
    ? 'ml-2 inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-semibold border bg-indigo-500/15 text-indigo-100 border-indigo-400/40'
    : 'ml-2 inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-semibold border bg-red-500/15 text-red-100 border-red-400/40';

  const finishDevLogRef = useRef(false);

  useEffect(() => {
    if (!isDev || finishDevLogRef.current) {
      return;
    }
    console.log('[SpecSharp DEV] Finish chip payload', {
      finishLevel: finishLevel || 'Standard',
      costFactor,
      revenueFactor,
      modifiersTrace: modifiersTrace?.data || null,
      finishSource
    });
    finishDevLogRef.current = true;
  }, [isDev, finishLevel, modifiersTrace, finishSource, costFactor, revenueFactor]);
  
  // Basic project info
  const squareFootage = parsed?.square_footage || 0;
  const buildingType = parsed?.building_type || 'office';
  const buildingSubtype = parsed?.building_subtype || parsed?.subtype || 'general';
  const location = parsed?.location || 'Nashville';
  // For multifamily and other building types, use typical_floors if available (more accurate)
  const floors = calculations?.project_info?.typical_floors || parsed?.floors || 1;
  
  // Financial values with formatting
  const totalProjectCost = totals.total_project_cost || 0;
  const constructionTotal = totals.hard_costs || 0;
  const softCostsTotal = totals.soft_costs || 0;
  
  // TRACE CONSTRUCTION COST ISSUE
  console.log('=== CONSTRUCTION COST TRACE ===');
  console.log('1. Raw project data:', project);
  console.log('2. Analysis object:', project?.analysis);
  console.log('3. Calculations object:', calculations);
  console.log('4. Totals object:', totals);
  console.log('5. Hard costs value from totals:', totals?.hard_costs);
  console.log('6. DisplayData object:', displayData);
  console.log('7. DisplayData construction cost:', displayData?.constructionCost);
  console.log('8. ConstructionTotal variable:', constructionTotal);
  console.log('9. TotalProjectCost:', totalProjectCost);
  console.log('10. SoftCostsTotal:', softCostsTotal);
  console.log('=== END TRACE ===');
  
  // DETAILED REVENUE DEBUG
  console.log('=== DETAILED REVENUE DEBUG ===');
  console.log('Full project prop:', project);
  console.log('project.calculation_data:', project?.calculation_data);
  console.log('project.roi_analysis:', project?.roi_analysis);
  console.log('project.revenue_analysis:', project?.revenue_analysis);
  console.log('analysis object:', analysis);
  console.log('analysis.calculations:', analysis?.calculations);
  console.log('calculations object (merged):', calculations);
  console.log('calculations keys:', Object.keys(calculations || {}));
  
  // Check all possible revenue paths
  console.log('Path checks:');
  console.log('  roi_analysis exists:', !!calculations?.roi_analysis);
  console.log('  financial_metrics exists:', !!calculations?.roi_analysis?.financial_metrics);
  console.log('  annual_revenue in financial_metrics:', calculations?.roi_analysis?.financial_metrics?.annual_revenue);
  console.log('  revenue_analysis exists:', !!calculations?.revenue_analysis);
  console.log('  annual_revenue in revenue_analysis:', calculations?.revenue_analysis?.annual_revenue);
  console.log('  direct annual_revenue:', calculations?.annual_revenue);
  console.log('=== END REVENUE DEBUG ===');
  
  // Get values from backend calculations using correct data paths
  const annualRevenue = 
    calculations?.roi_analysis?.financial_metrics?.annual_revenue ||
    calculations?.revenue_analysis?.annual_revenue ||
    calculations?.financial_metrics?.annual_revenue ||
    calculations?.annual_revenue ||
    0; // No hardcoded value, just 0 if missing
    
  console.log('=== FINAL REVENUE VALUES ===');
  console.log('annualRevenue calculated as:', annualRevenue);
  console.log('operatingMargin will be calculated from paths...');
  const noi = 
    calculations?.roi_analysis?.financial_metrics?.net_income ||
    calculations?.revenue_analysis?.net_income ||
    calculations?.return_metrics?.estimated_annual_noi ||
    calculations?.net_income || 
    0;
  
  // Operating margin from backend calculations
  const operatingMargin = 
    calculations?.roi_analysis?.financial_metrics?.operating_margin ||
    calculations?.revenue_analysis?.operating_margin ||
    calculations?.operating_margin ||
    0.08; // Default 8% for unknown types
    
  console.log('operatingMargin calculated as:', operatingMargin);
  console.log('noi calculated as:', noi);
  console.log('=== END FINAL VALUES ===');
  
  // Revenue Requirements data
  const revenueReq = calculations?.revenue_requirements || 
                     calculations?.ownership_analysis?.revenue_requirements || 
                     null;

  // Financial Requirements removed - was only implemented for hospital
  
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
  
  // Soft costs breakdown from backend
  const softCostCategories = Object.entries(soft_costs?.breakdown || soft_costs || {})
    .filter(([key]) => key !== 'total' && key !== 'soft_cost_percentage')
    .map(([key, value]) => ({
      name: key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
      amount: value as number,
      percent: calculations?.soft_costs?.percentages?.[key] || 
               (softCostsTotal > 0 ? ((value as number) / softCostsTotal) * 100 : 0)
    }))
    .sort((a, b) => b.amount - a.amount)
    .slice(0, 5);

  // Export to Excel handler
  const handleExportExcel = () => {
    try {
      // Create workbook
      const wb = XLSX.utils.book_new();
      
      // Sheet 1: Executive Summary
      const summaryData = [
        ['SPECSHARP PROJECT ANALYSIS'],
        [''],
        ['Project:', project?.name || `${formatters.squareFeet(squareFootage)} ${buildingSubtype.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}`],
        ['Location:', location],
        ['Building Type:', `${buildingType} - ${buildingSubtype}`],
        ['Square Footage:', formatters.squareFeet(squareFootage)],
        ['Floors:', floors],
        [''],
        ['FINANCIAL SUMMARY'],
        ['Total Investment Required', formatters.currency(totalProjectCost)],
        ['Construction Cost', formatters.currency(constructionTotal)],
        ['Soft Costs', formatters.currency(softCostsTotal)],
        ['Cost per SF', formatters.costPerSF(totals.cost_per_sf)],
        [''],
        ['INVESTMENT METRICS'],
        ['Expected ROI', `${(displayData.roi * 100).toFixed(1)}%`],
        ['NPV (10-year)', formatters.currency(displayData.npv)],
        ['Payback Period', `${displayData.paybackPeriod} years`],
        ['IRR', `${(displayData.irr || 12).toFixed(1)}%`],
        ['Annual Revenue', formatters.currency(annualRevenue)],
        ['Annual NOI', formatters.currency(noi)],
        [''],
        ['DECISION', decisionStatus === 'PENDING' ? 'Under Review' : decisionStatus],
        ['Reason', decisionReasonText]
      ];
      
      const ws1 = XLSX.utils.aoa_to_sheet(summaryData);
      XLSX.utils.book_append_sheet(wb, ws1, 'Executive Summary');
      
      // Sheet 2: Department Breakdown
      if (displayData.departmentAllocations?.length > 0) {
        const deptData = [
          ['DEPARTMENT COST ALLOCATION'],
          [''],
          ['Department', 'Cost', 'Percentage', 'Cost/SF'],
          ...displayData.departmentAllocations.map(dept => [
            dept.name,
            formatters.currency(dept.cost),
            `${dept.percentage}%`,
            formatters.costPerSF(dept.costPerSF)
          ])
        ];
        const ws2 = XLSX.utils.aoa_to_sheet(deptData);
        XLSX.utils.book_append_sheet(wb, ws2, 'Department Costs');
      }
      
      // Sheet 3: Trade Package Details
      if (displayData.trades?.length > 0) {
        const tradeData = [
          ['TRADE PACKAGE BREAKDOWN'],
          [''],
          ['Trade', 'Cost', 'Percentage', 'Cost/SF'],
          ...displayData.trades.map(trade => [
            trade.name,
            formatters.currency(trade.cost),
            `${trade.percentage.toFixed(1)}%`,
            formatters.costPerSF(trade.costPerSF)
          ])
        ];
        const ws3 = XLSX.utils.aoa_to_sheet(tradeData);
        XLSX.utils.book_append_sheet(wb, ws3, 'Trade Packages');
      }
      
      // Sheet 4: Investment Criteria
      const criteriaData = [
        ['INVESTMENT CRITERIA ASSESSMENT'],
        [''],
        ['Metric', 'Current', 'Required', 'Status'],
        ['ROI', `${(displayData.roi * 100).toFixed(1)}%`, '8%', displayData.roi >= 0.08 ? 'PASS' : 'FAIL'],
        ['NPV (10-year)', formatters.currency(displayData.npv), '> $0', displayData.npv > 0 ? 'PASS' : 'FAIL'],
        ['Payback Period', `${displayData.paybackPeriod} years`, '≤ 7 years', displayData.paybackPeriod <= 7 ? 'PASS' : 'FAIL'],
        ['DSCR', (displayData.dscr || 1.4).toFixed(2) + 'x', '≥ 1.25x', (displayData.dscr || 1.4) >= 1.25 ? 'PASS' : 'FAIL']
      ];
      const ws4 = XLSX.utils.aoa_to_sheet(criteriaData);
      XLSX.utils.book_append_sheet(wb, ws4, 'Investment Criteria');
      
      // Sheet 5: Improvement Recommendations
      if (displayData.improvementsNeeded?.length > 0) {
        const improvementData = [
          ['PATHS TO FEASIBILITY'],
          [''],
          ['Priority', 'Action Required', 'Impact'],
          ...displayData.improvementsNeeded.map((imp, idx) => [
            idx + 1,
            imp.metric || imp.action || imp.description || 'Action Required',
            imp.suggestion || imp.impact || imp.recommendation || ''
          ])
        ];
        const ws5 = XLSX.utils.aoa_to_sheet(improvementData);
        XLSX.utils.book_append_sheet(wb, ws5, 'Improvements');
      }
      
      // Sheet 6: Soft Costs Breakdown
      if (softCostCategories.length > 0) {
        const softCostData = [
          ['SOFT COSTS BREAKDOWN'],
          [''],
          ['Category', 'Amount', 'Percentage of Soft Costs'],
          ...softCostCategories.map(cat => [
            cat.name,
            formatters.currency(cat.amount),
            `${cat.percent.toFixed(1)}%`
          ])
        ];
        const ws6 = XLSX.utils.aoa_to_sheet(softCostData);
        XLSX.utils.book_append_sheet(wb, ws6, 'Soft Costs');
      }
      
      // Sheet 7: 10-Year Cash Flow Projection
      const years = Array.from({length: 10}, (_, i) => i + 1);
      const revenue = annualRevenue || 0;
      const operatingExpenses = revenue * (1 - operatingMargin);
      const debtService = 
        calculations?.debt_metrics?.annual_debt_service ||
        calculations?.ownership_analysis?.debt_metrics?.annual_debt_service ||
        displayData.debtService || 
        0;
      
      const cashFlowData = [
        ['10-YEAR CASH FLOW PROJECTION'],
        [''],
        ['Year', ...years],
        ['Revenue', ...years.map(y => formatters.currency(revenue * Math.pow(1.03, y-1)))],
        ['Operating Expenses', ...years.map(y => formatters.currency(operatingExpenses * Math.pow(1.025, y-1)))],
        ['NOI', ...years.map(y => formatters.currency(revenue * operatingMargin * Math.pow(1.03, y-1)))],
        ['Debt Service', ...years.map(_ => formatters.currency(debtService))],
        ['Cash Flow', ...years.map(y => formatters.currency((revenue * operatingMargin * Math.pow(1.03, y-1)) - debtService))]
      ];
      const ws7 = XLSX.utils.aoa_to_sheet(cashFlowData);
      XLSX.utils.book_append_sheet(wb, ws7, 'Cash Flow');
      
      // Generate filename with date
      const date = new Date().toISOString().split('T')[0];
      const projectName = project?.name?.replace(/[^a-z0-9]/gi, '_') || 'Project';
      const filename = `SpecSharp_${projectName}_${date}.xlsx`;
      
      // Download the file
      XLSX.writeFile(wb, filename);
    } catch (error) {
      console.error('Export failed:', error);
      alert('Failed to export Excel file. Please try again.');
    }
  };

  return (
    <>
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
                {floors} {floors === 1 ? 'Floor' : 'Floors'}
              </span>
              <span className="flex items-center gap-1.5">
                <Calendar className="h-4 w-4" />
                Ground-Up
              </span>
            </div>
            
            <div className="flex gap-3 mt-4">
              <button 
                onClick={handleExportExcel}
                className="px-4 py-2 bg-white/10 backdrop-blur border border-white/20 text-white rounded-lg hover:bg-white/20 transition flex items-center gap-2"
              >
                <Download className="h-4 w-4" />
                Export Excel
              </button>
            </div>
          </div>
          
          <div className="text-right">
            <p className="text-xs text-blue-200 uppercase tracking-wider mb-2 font-medium">TOTAL INVESTMENT REQUIRED</p>
            <p className="text-5xl font-bold">{formatters.currency(totalProjectCost)}</p>
            <p className="text-lg text-blue-200">{formatters.costPerSF(totals.cost_per_sf)}</p>
            <div className="mt-3 flex justify-end gap-2 flex-wrap">
              <span
                className={`inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-semibold border ${decisionStatus === 'GO'
                  ? 'bg-green-500/15 text-green-100 border-green-400/40'
                  : decisionStatus === 'NO-GO'
                    ? 'bg-red-500/15 text-red-100 border-red-400/40'
                    : 'bg-amber-500/15 text-amber-100 border-amber-400/40'}`}
              >
                {decisionStatus === 'GO' ? <CheckCircle className="h-3 w-3" /> : decisionStatus === 'NO-GO' ? <AlertCircle className="h-3 w-3" /> : <Clock className="h-3 w-3" />}
                {feasibilityChipLabel}
              </span>
              {isDev && (
                <span className={finishChipClasses} title={hasFinishPayload ? finishChipTooltip : undefined}>
                  {hasFinishPayload ? (
                    <>
                      <span className="font-semibold tracking-wide">DEV • Finish</span>
                      <span className="ml-1">{finishChipDetail}</span>
                    </>
                  ) : (
                    'DEV • Finish: MISSING'
                  )}
                </span>
              )}
            </div>
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

      {/* Investment Decision Section with Enhanced Feedback */}
      <div className="space-y-4">
        {/* Decision Header */}
        <div
          className={`${decisionStatus === 'GO'
            ? 'bg-green-50 border-green-500'
            : decisionStatus === 'NO-GO'
              ? 'bg-red-50 border-red-500'
              : 'bg-amber-50 border-amber-500'} border-l-4 rounded-lg p-6`}
        >
          <div className="flex items-start gap-3">
            {decisionStatus === 'GO' ? (
              <CheckCircle className="h-6 w-6 text-green-600 flex-shrink-0" />
            ) : decisionStatus === 'NO-GO' ? (
              <AlertCircle className="h-6 w-6 text-red-600 flex-shrink-0" />
            ) : (
              <Clock className="h-6 w-6 text-amber-600 flex-shrink-0" />
            )}
            <div className="flex-1">
              <h3
                className={`font-bold text-lg ${decisionStatus === 'GO'
                  ? 'text-green-900'
                  : decisionStatus === 'NO-GO'
                    ? 'text-red-900'
                    : 'text-amber-900'}`}
              >
                Investment Decision: {decisionStatus === 'PENDING' ? 'Under Review' : decisionStatus}
              </h3>
              <p
                className={`mt-1 ${decisionStatus === 'GO'
                  ? 'text-green-700'
                  : decisionStatus === 'NO-GO'
                    ? 'text-red-700'
                    : 'text-amber-700'}`}
              >
                {decisionReasonText}
              </p>
            </div>
          </div>
        </div>
        
        {/* Metrics Table */}
        {displayData.metricsTable && displayData.metricsTable.length > 0 && (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
            <div className="px-6 py-3 bg-gray-50 border-b border-gray-200">
              <h4 className="font-semibold text-gray-900">Investment Criteria Assessment</h4>
            </div>
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Metric</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Current</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Required</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {displayData.metricsTable.map((metric, idx) => (
                  <tr key={idx}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{metric.metric}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{metric.current}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">{metric.required}</td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {metric.status === 'pass' ? (
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                          <CheckCircle className="h-3 w-3 mr-1" /> Pass
                        </span>
                      ) : (
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                          <XCircle className="h-3 w-3 mr-1" /> Fail
                        </span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        
        {/* Actionable Improvements for NO-GO */}
        {decisionStatus === 'NO-GO' && displayData.failedCriteria && displayData.failedCriteria.length > 0 && (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200">
            <div className="px-6 py-4 border-b border-gray-200">
              <h4 className="font-semibold text-gray-900 flex items-center gap-2">
                <Target className="h-5 w-5 text-blue-600" />
                How to Make This Project Feasible
              </h4>
              <p className="text-sm text-gray-600 mt-1">Specific actions to meet investment criteria</p>
            </div>
            <div className="p-6 space-y-4">
              {displayData.failedCriteria.map((failure, idx) => (
                <div key={idx} className="flex gap-4 p-4 bg-gray-50 rounded-lg">
                  <div className="flex-shrink-0">
                    <div className="w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center font-bold text-sm">
                      {idx + 1}
                    </div>
                  </div>
                  <div className="flex-1">
                    <div className="flex items-baseline justify-between mb-2">
                      <span className="font-semibold text-gray-900">{failure.metric}</span>
                      <span className="text-sm text-red-600">Gap: {failure.gap}</span>
                    </div>
                    <p className="text-sm text-gray-700 mb-2">{failure.fix}</p>
                    <div className="flex gap-4 text-xs text-gray-500">
                      <span>Current: {failure.current}</span>
                      <span>→</span>
                      <span>Required: {failure.required}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
            
            {/* Legacy improvements display - now handled above */}
            {false && decisionStatus === 'NO-GO' && displayData.improvementsNeeded && displayData.improvementsNeeded.length > 0 && (
              <div className="mt-4 p-4 bg-white rounded-lg border border-red-200">
                <h4 className="font-semibold text-red-900 mb-3 flex items-center gap-2">
                  <AlertCircle className="h-4 w-4" />
                  Required Improvements:
                </h4>
                <div className="space-y-3">
                  {displayData.improvementsNeeded.map((improvement, idx) => (
                    <div key={idx} className="border-l-2 border-red-300 pl-3">
                      <div className="flex items-center justify-between mb-1">
                        <span className="font-medium text-gray-900">{improvement.metric}</span>
                        <div className="flex items-center gap-2 text-sm">
                          <span className="text-red-600">Current: {formatters.formatMetricValue(improvement.current, improvement.metric)}</span>
                          <span className="text-gray-400">→</span>
                          <span className="text-green-600">Required: {formatters.formatMetricValue(improvement.required, improvement.metric)}</span>
                        </div>
                      </div>
                      <p className="text-sm text-gray-600">{improvement.suggestion}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}
            
            {/* Display suggestions if NO-GO */}
            {decisionStatus === 'NO-GO' && displayData.suggestions.length > 0 && (
              <div className="mt-4 p-4 bg-white rounded-lg border border-amber-200">
                <h4 className="font-semibold text-amber-900 mb-2 flex items-center gap-2">
                  <Lightbulb className="h-4 w-4" />
                  Additional Optimization Strategies:
                </h4>
                <ul className="space-y-2">
                  {displayData.suggestions.map((suggestion, idx) => (
                    <li key={idx} className="flex items-start gap-2">
                      <span className="text-amber-600 mt-0.5">•</span>
                      <span className="text-sm text-gray-700">{suggestion}</span>
                    </li>
                  ))}
                </ul>
                
                {displayData.requiredRent > 0 && (
                  <div className="mt-3 pt-3 border-t border-amber-200">
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
                <span className="font-bold">{formatters.percentage(operatingMargin)}</span>
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

        {/* Investment Mix */}
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

      {/* Revenue Requirements Card */}
      {revenueReq && (
        <div className="bg-white rounded-xl shadow-lg overflow-hidden">
          <div className="bg-gradient-to-r from-emerald-500 to-teal-600 px-6 py-4">
            <h3 className="text-lg font-bold text-white">Revenue Requirements</h3>
            <p className="text-sm text-emerald-100">What you need to charge for 8% ROI</p>
          </div>
          <div className="p-6">
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="text-center p-4 bg-gray-50 rounded-lg">
                  <p className="text-sm text-gray-600 mb-1">Required {revenueReq.metric_name}</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {formatters.currency(revenueReq.required_value)}
                  </p>
                </div>
                <div className="text-center p-4 bg-blue-50 rounded-lg">
                  <p className="text-sm text-gray-600 mb-1">Market {revenueReq.metric_name}</p>
                  <p className="text-2xl font-bold text-blue-600">
                    {formatters.currency(revenueReq.market_value)}
                  </p>
                </div>
              </div>
              
              <div className={`p-4 rounded-lg ${
                (revenueReq.feasibility?.status || revenueReq.feasibility) === 'Feasible' 
                  ? 'bg-green-50 border border-green-200' 
                  : 'bg-amber-50 border border-amber-200'
              }`}>
                <div className="flex items-center justify-between">
                  <span className="font-semibold">Project Feasibility:</span>
                  <span className={`font-bold ${
                    (revenueReq.feasibility?.status || revenueReq.feasibility) === 'Feasible' ? 'text-green-600' : 'text-amber-600'
                  }`}>
                    {revenueReq.feasibility?.status || revenueReq.feasibility}
                  </span>
                </div>
                {(revenueReq.gap !== undefined || revenueReq.feasibility?.gap !== undefined) && (
                  <p className="text-sm mt-2">
                    {(revenueReq.gap || revenueReq.feasibility?.gap || 0) > 0 
                      ? `Market rate is ${formatters.currency(Math.abs(revenueReq.gap || revenueReq.feasibility?.gap || 0))} (${Math.abs(revenueReq.gap_percentage || 0).toFixed(1)}%) above requirement ✓`
                      : `Need to achieve ${formatters.currency(Math.abs(revenueReq.gap || revenueReq.feasibility?.gap || 0))} (${Math.abs(revenueReq.gap_percentage || 0).toFixed(1)}%) above market rate`
                    }
                  </p>
                )}
                {revenueReq.feasibility?.recommendation && (
                  <p className="text-sm mt-2 text-gray-600">
                    {revenueReq.feasibility.recommendation}
                  </p>
                )}
              </div>
              
              <div className="pt-4 border-t">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Simple Payback Period</span>
                  <span className="text-lg font-bold">{formatters.years(displayData.paybackPeriod)}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Financial Requirements removed - was only implemented for hospital */}

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
                <div className="w-full bg-gradient-to-r from-green-100 via-yellow-100 to-red-100 rounded-full h-4 relative">
                  <div 
                    className="absolute top-1/2 transform -translate-y-1/2 w-6 h-6 bg-blue-600 rounded-full border-2 border-white shadow-lg z-10"
                    style={{ left: '59%', marginLeft: '-12px' }}
                  >
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
    </>
  );
};
