import React, { useEffect, useRef, useState } from 'react';
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

// Local title casing to avoid depending on missing formatters.titleCase
const toTitleCase = (value?: string): string => {
  if (!value) return '';
  return value
    .toString()
    .replace(/_/g, ' ')
    .toLowerCase()
    .replace(/\b\w/g, c => c.toUpperCase());
};

type AnyRecord = Record<string, any>;

const toRecord = (value: unknown): AnyRecord =>
  value && typeof value === 'object' && !Array.isArray(value)
    ? (value as AnyRecord)
    : {};

const coalesceRecord = (...candidates: unknown[]): AnyRecord => {
  for (const candidate of candidates) {
    if (candidate && typeof candidate === 'object' && !Array.isArray(candidate)) {
      return candidate as AnyRecord;
    }
  }
  return {};
};

const buildSafeAnalysis = (project?: Project | null): AnyRecord => {
  const projectRecord = toRecord(project);
  const rawAnalysis = toRecord(projectRecord.analysis);
  const calculations = coalesceRecord(
    rawAnalysis.calculations,
    projectRecord.calculation_data,
    projectRecord.calculations,
    projectRecord
  );
  const parsedInput = coalesceRecord(
    rawAnalysis.parsed_input,
    rawAnalysis.request_payload?.parsed_input,
    projectRecord.parsed_input,
    projectRecord.form_state,
    projectRecord.form_inputs
  );

  return {
    ...rawAnalysis,
    parsed_input: parsedInput,
    calculations
  };
};

interface SectionCardProps {
  title: React.ReactNode;
  subtitle?: React.ReactNode;
  className?: string;
  children: React.ReactNode;
}

const SectionCard: React.FC<SectionCardProps> = ({ title, subtitle, className, children }) => (
  <div className={`rounded-2xl border border-slate-200 bg-white shadow-sm ${className ?? ''}`}>
    <div className="px-6 py-5 border-b border-slate-100 space-y-2">
      {typeof title === 'string' ? (
        <h3 className="text-xl font-semibold text-slate-900">{title}</h3>
      ) : (
        title
      )}
      {subtitle ? <p className="text-sm text-slate-500">{subtitle}</p> : null}
    </div>
    <div className="p-6">{children}</div>
  </div>
);

export const ExecutiveViewComplete: React.FC<Props> = ({ project }) => {
  const navigate = useNavigate();
  const [isScenarioOpen, setIsScenarioOpen] = useState(false);
  
  // Early return if no project data - check multiple paths for data
  if (!project?.analysis && !project?.calculation_data) {
    return (
      <div className="p-8 text-center text-gray-500">
        <p>Loading project data...</p>
      </div>
    );
  }

  // Normalize analysis payload so downstream consumers always receive objects
  const analysis = buildSafeAnalysis(project);
  
  // Map backend data through our mapper
  const displayData = BackendDataMapper.mapToDisplay(analysis || {});
  let { buildingType, facilityMetrics } = displayData;
  const projectTimeline = displayData.projectTimeline;
  const dscrFromDisplay = typeof displayData.dscr === 'number' ? displayData.dscr : undefined;
  const dscrFromOwnership = typeof (analysis as AnyRecord)?.calculations?.ownership_analysis?.debt_metrics?.calculated_dscr === 'number'
    ? (analysis as AnyRecord).calculations.ownership_analysis.debt_metrics.calculated_dscr
    : undefined;
  const targetDscrFromOwnership = typeof (analysis as AnyRecord)?.calculations?.ownership_analysis?.debt_metrics?.target_dscr === 'number'
    ? (analysis as AnyRecord).calculations.ownership_analysis.debt_metrics.target_dscr
    : undefined;
  const dscr = dscrFromDisplay ?? dscrFromOwnership;
  const targetDscr = targetDscrFromOwnership;
  const resolvedTargetDscr = typeof targetDscr === 'number' && Number.isFinite(targetDscr) ? targetDscr : 1.25;
  const yieldOnCost = typeof displayData.yieldOnCost === 'number' && Number.isFinite(displayData.yieldOnCost)
    ? displayData.yieldOnCost
    : undefined;
  const stabilizedYield = typeof yieldOnCost === 'number'
    ? yieldOnCost
    : (typeof displayData.roi === 'number' ? displayData.roi : 0);
  const marketCapRateDisplay = typeof displayData.marketCapRate === 'number' && Number.isFinite(displayData.marketCapRate)
    ? displayData.marketCapRate
    : undefined;
  const capRateSpreadBps = typeof displayData.capRateSpreadBps === 'number' && Number.isFinite(displayData.capRateSpreadBps)
    ? displayData.capRateSpreadBps
    : undefined;
  const effectiveYield = typeof yieldOnCost === 'number'
    ? yieldOnCost
    : (typeof displayData.roi === 'number' && Number.isFinite(displayData.roi) ? displayData.roi : undefined);
  const marketCapRateValue = marketCapRateDisplay;
  const computedYieldCapSpreadPct = typeof effectiveYield === 'number' && typeof marketCapRateValue === 'number'
    ? effectiveYield - marketCapRateValue
    : undefined;
  const yieldCapSpreadPct = typeof capRateSpreadBps === 'number'
    ? capRateSpreadBps / 10000
    : computedYieldCapSpreadPct;
  const yieldCapSpreadBps = typeof capRateSpreadBps === 'number'
    ? capRateSpreadBps
    : (typeof computedYieldCapSpreadPct === 'number' ? computedYieldCapSpreadPct * 10000 : undefined);
  const equityReturn = typeof displayData.roi === 'number' && Number.isFinite(displayData.roi)
    ? displayData.roi
    : undefined;
  const investmentDecisionFromDisplay = displayData.investmentDecision;
  const feasibilityFlag = typeof displayData.feasible === 'boolean' ? displayData.feasible : undefined;
  type DecisionStatus = 'GO' | 'Needs Work' | 'NO-GO' | 'PENDING';
  const normalizeBackendDecision = (value: unknown): DecisionStatus | undefined => {
    if (typeof value === 'string') {
      if (value.toLowerCase().includes('go')) return 'GO';
      if (value.toLowerCase().includes('no-go') || value.toLowerCase().includes('no_go')) return 'NO-GO';
      if (value.toLowerCase().includes('work') || value.toLowerCase().includes('near')) return 'Needs Work';
    }
    return undefined;
  };
  const backendDecision = normalizeBackendDecision(
    typeof investmentDecisionFromDisplay === 'string'
      ? investmentDecisionFromDisplay
      : investmentDecisionFromDisplay?.recommendation
  );
  const fallbackDecisionStatus: DecisionStatus =
    backendDecision ??
    (feasibilityFlag === true
      ? 'GO'
      : feasibilityFlag === false
        ? 'NO-GO'
        : 'PENDING');
  const spreadBpsValue =
    typeof yieldOnCost === 'number' &&
    Number.isFinite(yieldOnCost) &&
    typeof marketCapRateDisplay === 'number' &&
    Number.isFinite(marketCapRateDisplay)
      ? (yieldOnCost - marketCapRateDisplay) * 10000
      : undefined;
  const dscrValue = typeof dscr === 'number' && Number.isFinite(dscr) ? dscr : undefined;
  const spreadPctValue = typeof spreadBpsValue === 'number' ? spreadBpsValue / 100 : undefined;
  const derivedDecisionStatus: DecisionStatus | undefined = (() => {
    if (
      typeof spreadBpsValue === 'number' &&
      typeof marketCapRateDisplay === 'number' &&
      typeof yieldOnCost === 'number' &&
      Number.isFinite(yieldOnCost) &&
      typeof dscrValue === 'number'
    ) {
      if (spreadBpsValue >= 200 && dscrValue >= resolvedTargetDscr) {
        return 'GO';
      }
      if (spreadBpsValue >= 0 && dscrValue >= resolvedTargetDscr) {
        return 'Needs Work';
      }
      return 'NO-GO';
    }
    return undefined;
  })();
  let decisionStatus: DecisionStatus = derivedDecisionStatus ?? fallbackDecisionStatus;
  // Industrial override: evaluate directly against target yield and DSCR so a
  // 7+% warehouse at 1.25x+ DSCR is a clear GO.
  (() => {
    const bt = (buildingType || '').toLowerCase();
    if (bt !== 'industrial') return;

    const yoc =
      typeof displayData.yieldOnCost === 'number' && Number.isFinite(displayData.yieldOnCost)
        ? displayData.yieldOnCost
        : undefined;
    const targetYieldFromDisplay =
      typeof displayData.targetYield === 'number' && Number.isFinite(displayData.targetYield)
        ? displayData.targetYield
        : undefined;
    const dscrOk =
      typeof dscrValue === 'number' &&
      typeof resolvedTargetDscr === 'number' &&
      Number.isFinite(dscrValue) &&
      Number.isFinite(resolvedTargetDscr)
        ? dscrValue >= resolvedTargetDscr
        : false;

    if (typeof yoc !== 'number' || typeof targetYieldFromDisplay !== 'number') {
      return;
    }

    if (dscrOk && yoc >= targetYieldFromDisplay) {
      decisionStatus = 'GO';
      return;
    }

    if (dscrOk && yoc >= targetYieldFromDisplay * 0.95) {
      decisionStatus = 'Needs Work';
      return;
    }

    decisionStatus = 'NO-GO';
  })();
  const decisionStatusLabel =
    decisionStatus === 'Needs Work'
      ? 'Needs Work'
      : decisionStatus === 'NO-GO'
        ? 'NO-GO'
        : decisionStatus === 'PENDING'
          ? 'Under Review'
          : 'GO';
  const feasibilityChipLabel =
    decisionStatus === 'Needs Work'
      ? 'Needs Work'
      : decisionStatus === 'NO-GO'
        ? 'NO-GO'
        : decisionStatus === 'GO'
          ? 'GO'
          : 'Needs Review';
  const decisionReasonText = displayData.decisionReason || (
    typeof investmentDecisionFromDisplay === 'object'
      ? investmentDecisionFromDisplay?.summary
    : undefined
  ) || 'Debt coverage and yield metrics are still loading.';
  const formatPct = (value?: number) =>
    typeof value === 'number' && Number.isFinite(value) ? `${value.toFixed(1)}%` : '—';
  const yieldPctValue = typeof yieldOnCost === 'number' && Number.isFinite(yieldOnCost)
    ? yieldOnCost * 100
    : undefined;
  const marketCapPctValue = typeof marketCapRateDisplay === 'number' && Number.isFinite(marketCapRateDisplay)
    ? marketCapRateDisplay * 100
    : undefined;
  const dscrText = typeof dscrValue === 'number' ? `${dscrValue.toFixed(2)}×` : undefined;
  const dscrTargetText = `${resolvedTargetDscr.toFixed(2)}×`;
  const decisionCopy = (() => {
    const yieldText = formatPct(yieldPctValue);
    const marketText = formatPct(marketCapPctValue);
    const spreadText = typeof spreadPctValue === 'number'
      ? `${spreadPctValue >= 0 ? '+' : ''}${spreadPctValue.toFixed(1)}%`
      : undefined;
    if (decisionStatus === 'GO') {
      return {
        body: 'Project meets underwriting criteria with strong returns and healthy debt coverage.',
        detail: `${yieldPctValue !== undefined ? `Yield on cost ${yieldText}` : 'Yield on cost'}${marketCapPctValue !== undefined ? ` vs market cap ${marketText}` : ''}${spreadText ? ` (${spreadText})` : ''}${dscrText ? ` and DSCR ${dscrText} meets the ${dscrTargetText} requirement.` : '.'}`
      };
    }
    if (decisionStatus === 'Needs Work') {
      return {
        body: 'Project is close to the yield hurdle but still needs improvement.',
        detail: `${yieldPctValue !== undefined ? `Yield on cost ${yieldText}` : 'Yield on cost'} is roughly in line with the market cap${spreadText ? ` (${spreadText})` : ''}. Keep DSCR ${dscrText ?? '—'}× at or above ${dscrTargetText} while lifting NOI or trimming costs to add at least 200 bp of spread.`
      };
    }
    if (decisionStatus === 'NO-GO') {
      return {
        body: 'Project currently falls below underwriting thresholds.',
        detail: `${yieldPctValue !== undefined ? `Yield on cost ${yieldText}` : 'Yield on cost'}${marketCapPctValue !== undefined ? ` vs market cap ${marketText}` : ''}${spreadText ? ` (${spreadText})` : ''} and/or DSCR ${dscrText ?? '—'}× are below the ${dscrTargetText} requirement. Improve rents, cut scope, or rework the capital stack before advancing.`
      };
    }
    return {
      body: 'Investment analysis is still running.',
      detail: 'Once NOI, yield on cost, and DSCR metrics are available, this banner will classify the deal automatically.'
    };
  })();
  const decisionBodyClass = `mt-1 text-sm ${
    decisionStatus === 'GO' ? 'text-green-700' : decisionStatus === 'NO-GO' ? 'text-red-700' : 'text-amber-700'
  }`;
  const decisionDetailClass = `mt-1 text-xs ${
    decisionStatus === 'GO' ? 'text-green-600' : decisionStatus === 'NO-GO' ? 'text-red-600' : 'text-amber-600'
  }`;
  
  // Extract additional raw data we need - check multiple paths for data
  const parsed = analysis?.parsed_input || {};
  // Look for calculations in multiple places due to data mapping
  const calculations = analysis?.calculations || {};
  const projectInfo = calculations?.project_info || {};
  const totals = calculations?.totals || {};
  const construction_costs = calculations?.construction_costs || {};
  const soft_costs = calculations?.soft_costs || {};
  const ownership = calculations?.ownership_analysis || {};
  const investmentAnalysis = ownership?.investment_analysis || {};
  const debtMetrics = ownership?.debt_metrics || calculations?.debt_metrics || {};
  const annualDebtService = typeof debtMetrics?.annual_debt_service === 'number' && Number.isFinite(debtMetrics.annual_debt_service)
    ? debtMetrics.annual_debt_service
    : undefined;
  const hasDebt = typeof debtMetrics?.annual_debt_service === 'number' && debtMetrics.annual_debt_service > 0;
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
  const finishLevelFromProject = normalizeFinishLevel(projectInfo?.finish_level);
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

  const costPerSFValue = typeof displayData.costPerSF === 'number' && Number.isFinite(displayData.costPerSF)
    ? displayData.costPerSF
    : undefined;
  const marketCostPerSFField = (displayData as AnyRecord)?.marketCostPerSF;
  const inferredMarketCostPerSF = typeof costPerSFValue === 'number' && typeof costFactor === 'number' && costFactor > 0
    ? costPerSFValue / costFactor
    : undefined;
  const marketCostPerSF = typeof marketCostPerSFField === 'number' && Number.isFinite(marketCostPerSFField)
    ? marketCostPerSFField
    : inferredMarketCostPerSF;
  const costPerSFDeltaPct = typeof costPerSFValue === 'number' && typeof marketCostPerSF === 'number' && marketCostPerSF !== 0
    ? ((costPerSFValue - marketCostPerSF) / marketCostPerSF) * 100
    : undefined;
  const costPerSFGaugePosition = (() => {
    if (typeof costPerSFDeltaPct === 'number') {
      const clamped = Math.max(-20, Math.min(20, costPerSFDeltaPct));
      return ((clamped + 20) / 40) * 100;
    }
    return 50;
  })();
  const softCostRatio = typeof displayData.softCosts === 'number' &&
    typeof displayData.totalProjectCost === 'number' &&
    displayData.totalProjectCost > 0
      ? displayData.softCosts / displayData.totalProjectCost
      : undefined;

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
  const enrichedParsed: any = analysis?.parsed_input || {};
  const squareFootage =
    Number(enrichedParsed?.square_footage) ||
    Number(calculations?.construction_costs?.square_footage) ||
    Number(calculations?.totals?.square_footage) ||
    0;
  if (!buildingType) {
    buildingType = (enrichedParsed?.building_type || parsed?.building_type || 'general') as string;
  }
  const buildingSubtype = parsed?.building_subtype || parsed?.subtype || 'general';
  const location = parsed?.location || 'Nashville';
  const friendlyType =
    (enrichedParsed?.__display_type as string) ||
    toTitleCase(
      (projectInfo?.subtype as string) ||
      (projectInfo?.display_name as string) ||
      buildingSubtype ||
      buildingType ||
      'general'
    ) ||
    'General';
  // For multifamily and other building types, use typical_floors if available (more accurate)
  const floors = projectInfo?.typical_floors || parsed?.floors || 1;
  const headerSquareFootage =
    Number(projectInfo?.square_footage) ||
    Number(totals?.square_footage) ||
    squareFootage;
  const headerFriendlyType =
    toTitleCase(
      (projectInfo?.subtype as string) ||
      (projectInfo?.display_name as string) ||
      friendlyType
    ) || friendlyType;
  const heroTitle =
    headerSquareFootage > 0
      ? `${formatters.squareFeet(headerSquareFootage)} ${headerFriendlyType}`
      : headerFriendlyType;
  const normalizedOfficeSquareFootage = Math.max(headerSquareFootage || squareFootage || 1, 1);
  const operatingExpensesTotal = typeof displayData.operatingExpenses === 'number' ? displayData.operatingExpenses : 0;
  const camChargesTotal = typeof displayData.camCharges === 'number' ? displayData.camCharges : 0;
  
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
  const normalizeRate = (value?: number | null) => {
    if (typeof value !== 'number' || !Number.isFinite(value) || value <= 0) {
      return undefined;
    }
    return value > 1 ? value / 100 : value;
  };
  const targetYieldRate =
    normalizeRate(revenueReq?.target_yield) ||
    normalizeRate(investmentAnalysis?.target_yield) ||
    normalizeRate(calculations?.ownership_analysis?.return_metrics?.target_roi) ||
    normalizeRate((ownership as AnyRecord)?.return_metrics?.target_yield) ||
    normalizeRate((displayData as AnyRecord)?.targetYield) ||
    normalizeRate((displayData as AnyRecord)?.targetYieldPct) ||
    normalizeRate((displayData as AnyRecord)?.yieldTarget) ||
    0.08;
  const requiredNoi = typeof totalProjectCost === 'number' && Number.isFinite(totalProjectCost)
    ? totalProjectCost * targetYieldRate
    : (typeof revenueReq?.required_value === 'number' ? revenueReq.required_value : undefined);
  const currentNoi = typeof noi === 'number' && Number.isFinite(noi)
    ? noi
    : (typeof revenueReq?.actual_net_income === 'number' ? revenueReq.actual_net_income : undefined);
  const noiGap = typeof currentNoi === 'number' && typeof requiredNoi === 'number'
    ? currentNoi - requiredNoi
    : undefined;
  const noiGapPct = typeof noiGap === 'number' && typeof requiredNoi === 'number' && requiredNoi !== 0
    ? (noiGap / requiredNoi) * 100
    : undefined;
  const currentRevenuePerSf =
    typeof annualRevenue === 'number' &&
    Number.isFinite(annualRevenue) &&
    typeof squareFootage === 'number' &&
    squareFootage > 0
      ? annualRevenue / squareFootage
      : (typeof revenueReq?.actual_revenue_per_sf === 'number' ? revenueReq.actual_revenue_per_sf : undefined);
  const requiredRevenuePerSf = (() => {
    if (
      typeof requiredNoi === 'number' &&
      typeof operatingMargin === 'number' &&
      operatingMargin > 0 &&
      typeof squareFootage === 'number' &&
      squareFootage > 0
    ) {
      return (requiredNoi / operatingMargin) / squareFootage;
    }
    if (
      typeof revenueReq?.required_revenue === 'number' &&
      typeof squareFootage === 'number' &&
      squareFootage > 0
    ) {
      return revenueReq.required_revenue / squareFootage;
    }
    if (typeof revenueReq?.required_revenue_per_sf === 'number') {
      return revenueReq.required_revenue_per_sf;
    }
    return undefined;
  })();
  const revenuePerSfGap = typeof currentRevenuePerSf === 'number' && typeof requiredRevenuePerSf === 'number'
    ? currentRevenuePerSf - requiredRevenuePerSf
    : undefined;
  const revenuePerSfGapPct = typeof revenuePerSfGap === 'number' && typeof requiredRevenuePerSf === 'number' && requiredRevenuePerSf !== 0
    ? (revenuePerSfGap / requiredRevenuePerSf) * 100
    : undefined;
  const normalizedFacilityType = (buildingType || '').toUpperCase();
  const showHotelFacilityMetrics =
    normalizedFacilityType === 'HOSPITALITY' || normalizedFacilityType === 'HOTEL';
  const showIndustrialFacilityMetrics =
    normalizedFacilityType === 'INDUSTRIAL' || normalizedFacilityType === 'WAREHOUSE';
  const isHospitalityProject = showHotelFacilityMetrics;
  const hospitalityRooms =
    typeof facilityMetrics?.rooms === 'number' ? facilityMetrics.rooms : undefined;
  const hospitalityAdr =
    typeof facilityMetrics?.adr === 'number' ? facilityMetrics.adr : undefined;
  const hospitalityOccupancy =
    typeof facilityMetrics?.occupancy === 'number' ? facilityMetrics.occupancy : undefined;
  const hospitalityRevpar =
    typeof facilityMetrics?.revpar === 'number' ? facilityMetrics.revpar : undefined;
  const hospitalityCostPerKey =
    typeof facilityMetrics?.costPerKey === 'number' ? facilityMetrics.costPerKey : undefined;
  const hospitalityAdrText = hospitalityAdr !== undefined ? `$${hospitalityAdr.toFixed(0)}` : 'ADR pending';
  const hospitalityOccupancyText =
    hospitalityOccupancy !== undefined ? `${(hospitalityOccupancy * 100).toFixed(0)}% occupancy` : 'stabilized occupancy';
  const hospitalityRevparText =
    hospitalityRevpar !== undefined ? `$${hospitalityRevpar.toFixed(0)} RevPAR` : 'RevPAR loading';
  const hospitalityMarginText =
    typeof operatingMargin === 'number'
      ? `${(operatingMargin * 100).toFixed(1)}% NOI margin`
      : 'NOI margin pending';

  const hospitalityRequiredNoiPerKeyValue =
    displayData.requiredNoiPerKey ??
    (isHospitalityProject &&
    typeof requiredNoi === 'number' &&
    typeof hospitalityRooms === 'number' &&
    hospitalityRooms > 0
      ? requiredNoi / hospitalityRooms
      : undefined);
  const hospitalityCurrentNoiPerKeyValue =
    displayData.currentNoiPerKey ??
    (isHospitalityProject &&
    typeof currentNoi === 'number' &&
    typeof hospitalityRooms === 'number' &&
    hospitalityRooms > 0
      ? currentNoi / hospitalityRooms
      : undefined);
  const hospitalityRequiredRevparValue =
    displayData.requiredRevpar ??
    (isHospitalityProject &&
    typeof requiredNoi === 'number' &&
    typeof operatingMargin === 'number' &&
    operatingMargin > 0 &&
    typeof hospitalityRooms === 'number' &&
    hospitalityRooms > 0
      ? (requiredNoi / operatingMargin) / (hospitalityRooms * 365)
      : undefined);
  const fallbackCurrentRevpar =
    hospitalityRevpar !== undefined
      ? hospitalityRevpar
      : isHospitalityProject &&
        typeof hospitalityRooms === 'number' &&
        hospitalityRooms > 0 &&
        typeof annualRevenue === 'number'
        ? annualRevenue / (hospitalityRooms * 365)
        : undefined;
  const hospitalityCurrentRevparValue = displayData.currentRevpar ?? fallbackCurrentRevpar;
  const hospitalityRevparGap =
    typeof hospitalityRequiredRevparValue === 'number' && typeof hospitalityCurrentRevparValue === 'number'
      ? hospitalityRequiredRevparValue - hospitalityCurrentRevparValue
      : undefined;
  const hospitalityRevparGapPct =
    typeof hospitalityRevparGap === 'number' &&
    typeof hospitalityRequiredRevparValue === 'number' &&
    hospitalityRequiredRevparValue !== 0
      ? (hospitalityRevparGap / hospitalityRequiredRevparValue) * 100
      : undefined;
  const feasibilityGapCopy = (() => {
    if (typeof noiGap !== 'number') {
      return 'Feasibility update pending NOI inputs.';
    }
    const gapCurrency = formatters.currency(Math.abs(noiGap));
    const pctText = `${Math.abs(noiGapPct ?? 0).toFixed(1)}%`;
    if (noiGap >= 0) {
      return `Current NOI is ${gapCurrency} (${pctText}) ahead of requirement.`;
    }
    return `Need ${gapCurrency} (${pctText}) more NOI to meet the yield target.`;
  })();

  const isIndustrialProject = (buildingType || '').toLowerCase() === 'industrial';
  // Enhanced, context-aware Executive Decision Points
  const decisionBullets: string[] = (() => {
    const bullets: string[] = [];
    if (isHospitalityProject) {
      const basisSnippets: string[] = [];
      if (typeof costPerSFValue === 'number') {
        basisSnippets.push(formatters.costPerSF(costPerSFValue));
      }
      if (typeof facilityMetrics?.costPerKey === 'number') {
        basisSnippets.push(`${formatters.currencyExact(facilityMetrics.costPerKey)} per key`);
      }
      const basisCopy = basisSnippets.length
        ? basisSnippets.join(' | ')
        : 'basis inputs still populating';
      bullets.push(
        `Basis & keys: ${basisCopy}. Benchmark this against recent select-service trades so site, flag, and amenity mix justify the spend.`
      );

      const hotelAdr = typeof facilityMetrics?.adr === 'number' ? `$${facilityMetrics.adr.toFixed(0)}` : 'ADR inputs';
      const hotelOcc =
        typeof facilityMetrics?.occupancy === 'number'
          ? `${(facilityMetrics.occupancy * 100).toFixed(0)}% occupancy`
          : 'stabilized occupancy';
      const hotelRevpar =
        typeof facilityMetrics?.revpar === 'number' ? `$${facilityMetrics.revpar.toFixed(0)} RevPAR` : 'RevPAR inputs';
      const marginText =
        typeof operatingMargin === 'number'
          ? `${(operatingMargin * 100).toFixed(1)}% NOI margin`
          : 'NOI margin pending';

      const capRate = marketCapRateValue;
      const spreadBps = yieldCapSpreadBps;
      const dscrValue = typeof dscr === 'number' ? dscr : undefined;
      const dscrTarget = resolvedTargetDscr;
      const returnParts: string[] = [`ADR ${hotelAdr}`, hotelOcc, hotelRevpar, marginText];
      if (typeof effectiveYield === 'number' && typeof capRate === 'number' && typeof spreadBps === 'number') {
        returnParts.push(
          `yield ${(effectiveYield * 100).toFixed(1)}% vs ${(capRate * 100).toFixed(1)}% cap (${Math.abs(spreadBps).toFixed(0)} bp ${spreadBps >= 0 ? 'above' : 'below'})`
        );
      }
      if (typeof dscrValue === 'number') {
        const delta = dscrValue - dscrTarget;
        returnParts.push(`DSCR ${dscrValue.toFixed(2)}× ${delta >= 0 ? '≥' : '<'} ${dscrTarget.toFixed(2)}×`);
      }
      bullets.push(
        `Returns: ${returnParts.join(' · ')}. Stress ADR/occupancy against the comp set so RevPAR, DSCR, and IRR stay inside the acceptable hotel range.`
      );

      if (typeof softCostRatio === 'number') {
        const softPct = (softCostRatio * 100).toFixed(1);
        bullets.push(
          `Soft costs & reserves: ${softPct}% of total. Confirm franchise fees, management fees, FF&E/PIP reserves, and pre-opening spend align with brand standards so RevPAR doesn't erode.`
        );
      } else {
        bullets.push(
          'Soft costs & reserves: finalize FF&E, franchise, and management agreements to protect RevPAR and lender covenants.'
        );
      }

      return bullets;
    }

    // Non-hospitality branch preserves existing logic
    // 1) Cost positioning - cost/SF vs market benchmarks
    if (
      typeof costPerSFValue === 'number' &&
      typeof marketCostPerSF === 'number' &&
      typeof costPerSFDeltaPct === 'number'
    ) {
      const deltaPct = Math.abs(costPerSFDeltaPct).toFixed(1);
      const direction = costPerSFDeltaPct >= 0 ? 'above' : 'below';
      const implication =
        costPerSFDeltaPct >= 0 ? 'stretching the basis' : 'leaving cushion vs peers';
      bullets.push(
        `Basis risk: ${formatters.costPerSF(costPerSFValue)} sits ${deltaPct}% ${direction} market ${formatters.costPerSF(marketCostPerSF)} — ${implication}.`
      );
    } else if (typeof costPerSFValue === 'number') {
      bullets.push(
        `Basis check: ${formatters.costPerSF(costPerSFValue)} with no peer benchmarks loaded yet.`
      );
    } else {
      bullets.push('Basis check pending: total project cost still reconciling; confirm scope and inputs.');
    }

    // 2) Return positioning - yield vs cap + DSCR vs target
    const capRate = marketCapRateValue;
    const spreadBps = yieldCapSpreadBps;
    const dscrValue = typeof dscr === 'number' ? dscr : undefined;
    const dscrTarget = resolvedTargetDscr;

    if (typeof effectiveYield === 'number' || typeof dscrValue === 'number') {
      const parts: string[] = [];
      if (typeof effectiveYield === 'number' && typeof capRate === 'number' && typeof spreadBps === 'number') {
        const yieldPct = (effectiveYield * 100).toFixed(1);
        const capPct = (capRate * 100).toFixed(1);
        const spreadText = `${Math.abs(spreadBps).toFixed(0)} bp ${spreadBps >= 0 ? 'above' : 'below'}`;
        parts.push(`yield ${yieldPct}% vs ${capPct}% cap (${spreadText})`);
      } else if (typeof effectiveYield === 'number') {
        parts.push(`yield ${(effectiveYield * 100).toFixed(1)}% (cap TBD)`);
      } else if (typeof capRate === 'number') {
        parts.push(`market cap ${(capRate * 100).toFixed(1)}% (yield TBD)`);
      }

      if (typeof dscrValue === 'number') {
        const delta = dscrValue - dscrTarget;
        const meetsTarget = delta >= 0;
        parts.push(
          `DSCR ${dscrValue.toFixed(2)}× ${meetsTarget ? '≥' : '<'} ${dscrTarget.toFixed(2)}× target (${delta >= 0 ? '+' : ''}${delta.toFixed(2)}×)`
        );
      }

      let returnsText = `Returns: ${parts.join('; ')}.`;
      returnsText += isIndustrialProject
        ? ' For industrial, this signals whether the rent roll, dock configuration, and truck flow can clear both equity and lender hurdles.'
        : ' Together these determine whether the project clears both equity and lender hurdles.';
      bullets.push(returnsText);
    } else {
      bullets.push('Returns: yield and DSCR metrics are still populating from the latest underwriting run.');
    }

    // 3) Soft-cost positioning - compare to 18-25% band
    if (typeof softCostRatio === 'number') {
      const softPct = (softCostRatio * 100).toFixed(1);
      let posture = 'within the 18-25% guardrail; balanced owner costs.';
      if (softCostRatio > 0.25) {
        posture = 'high vs the 18-25% band — trim VE or contingency.';
      } else if (softCostRatio < 0.18) {
        posture = 'below the band — confirm allowances and contingency.';
      }
      if (isIndustrialProject) {
        bullets.push(
          `Scope & sitework: ${softPct}% of total — prioritize slab thickness, dock count, ESFR coverage, and truck court design with your GC to keep the budget aligned.`
        );
      } else {
        bullets.push(`Soft costs: ${softPct}% of total — ${posture}`);
      }
    } else {
      bullets.push(
        isIndustrialProject
          ? 'Scope & sitework: awaiting detailed estimates to validate slab, dock, ESFR, and sitework allowances.'
          : 'Soft costs: awaiting latest estimates to benchmark against the 18-25% guidance band.'
      );
    }

    // 4) Optional “what needs to change” bullet when gaps are material
    const yieldShortfallBps =
      typeof spreadBps === 'number' && spreadBps < 0 ? Math.abs(spreadBps) : undefined;
    const dscrShortfall =
      typeof dscrValue === 'number' && dscrValue < dscrTarget ? dscrTarget - dscrValue : undefined;
    const revenueLiftNeeded =
      typeof requiredRevenuePerSf === 'number' &&
      typeof currentRevenuePerSf === 'number' &&
      requiredRevenuePerSf > currentRevenuePerSf
        ? requiredRevenuePerSf - currentRevenuePerSf
        : undefined;
    const noiLiftNeeded =
      typeof requiredNoi === 'number' &&
      typeof currentNoi === 'number' &&
      requiredNoi > currentNoi
        ? requiredNoi - currentNoi
        : undefined;
    const needsRemedy =
      (yieldShortfallBps ?? 0) >= 40 ||
      (dscrShortfall ?? 0) >= 0.05;

    if (needsRemedy) {
      const gapDetails: string[] = [];
      if (yieldShortfallBps) gapDetails.push(`${yieldShortfallBps.toFixed(0)} bp yield shortfall`);
      if (dscrShortfall) gapDetails.push(`${dscrShortfall.toFixed(2)}× DSCR gap`);

      const actionHints: string[] = [];
      if (typeof revenueLiftNeeded === 'number' && revenueLiftNeeded > 0) {
        actionHints.push(`~$${revenueLiftNeeded.toFixed(2)}/SF/yr revenue lift`);
      }
      if (typeof noiLiftNeeded === 'number' && noiLiftNeeded > 0) {
        actionHints.push(`${formatters.currency(noiLiftNeeded)} NOI improvement`);
      }

      const remedyText =
        actionHints.length > 0
          ? actionHints.join(' or ')
          : 'rent growth, scope reductions, or cheaper capital';
      bullets.push(`Adjustments: ${gapDetails.join(' and ')} flagged; plan for ${remedyText} to hit targets.`);
    }

    return bullets;
  })();

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
        ['DECISION', decisionStatusLabel],
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
              {heroTitle}
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
              <button
                onClick={() => setIsScenarioOpen(true)}
                className="px-4 py-2 border border-white/30 text-white rounded-lg hover:bg-white/10 transition flex items-center gap-2"
              >
                <Target className="h-4 w-4" />
                Scenario
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
        
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-6 pt-6 mt-6 border-t border-white/20">
          <div>
            <p className="text-blue-200 text-xs uppercase tracking-wider mb-2 font-medium">CONSTRUCTION</p>
            <p className="text-3xl font-bold">{formatters.currency(constructionTotal)}</p>
          </div>
          <div>
            <p className="text-blue-200 text-xs uppercase tracking-wider mb-2 font-medium">SOFT COSTS</p>
            <p className="text-3xl font-bold">{formatters.currency(softCostsTotal)}</p>
          </div>
          <div>
            <p className="text-blue-200 text-xs uppercase tracking-wider mb-2 font-medium">STABILIZED YIELD (NOI / COST)</p>
            <p className="text-3xl font-bold">
              {formatters.percentage(stabilizedYield)}
            </p>
            {typeof yieldOnCost === 'number' && typeof marketCapRateDisplay === 'number' && (
              <p className="text-xs text-blue-200 mt-1">
                vs cap {(marketCapRateDisplay * 100).toFixed(1)}% ({((yieldOnCost - marketCapRateDisplay) * 100).toFixed(1)}% Δ)
              </p>
            )}
            <p className="text-[11px] text-blue-200/80 mt-1">
              Yield on total project cost at stabilization.
            </p>
          </div>
          <div>
            <p className="text-blue-200 text-xs uppercase tracking-wider mb-2 font-medium">DSCR VS TARGET</p>
            <p className="text-3xl font-bold">
              {typeof dscr === 'number' ? `${dscr.toFixed(2)}×` : '—'}
            </p>
            <p className="text-xs text-blue-200 mt-1">
              target {resolvedTargetDscr.toFixed(2)}×
            </p>
            <p className="text-[11px] text-blue-200/80 mt-1">
              Lender sizing based on NOI and annual debt service.
            </p>
          </div>
          <div>
            <p className="text-blue-200 text-xs uppercase tracking-wider mb-2 font-medium">Simple Payback (yrs)</p>
            <p className="text-3xl font-bold">{formatters.years(displayData.paybackPeriod)}</p>
          </div>
        </div>
      </div>

      {/* Investment Decision Section with Enhanced Feedback */}
      {/* Patch 12F: legacy static NO-GO banner removed; the dynamic 3-state component below now owns all decision copy. */}
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
                Investment Decision: {decisionStatusLabel}
              </h3>
              {isHospitalityProject ? (
                <>
                  <p className={decisionBodyClass}>
                    Hotel clears underwriting at {hospitalityAdrText}, {hospitalityOccupancyText}, and {hospitalityRevparText}, generating {hospitalityMarginText} to support the flagged room count and debt sizing.
                  </p>
                  <p className="mt-1 text-xs text-slate-600">
                    Hospitality memo: validate ADR and RevPAR against comp sets, keep DSCR comfortably above lender hotel hurdles, and confirm franchise, management, and FF&E reserves stay in sync with brand requirements.
                  </p>
                  {decisionReasonText && (
                    <p className="mt-2 text-xs text-slate-600">
                      Analyst context: {decisionReasonText}
                    </p>
                  )}
                </>
              ) : (
                <>
                  <p className={decisionBodyClass}>
                    {decisionCopy.body}
                  </p>
                  {decisionCopy.detail && (
                    <p className={decisionDetailClass}>
                      {decisionCopy.detail}
                    </p>
                  )}
                  {decisionReasonText && (
                    <p className="mt-2 text-xs text-slate-600">
                      Analyzer note: {decisionReasonText}
                    </p>
                  )}
                </>
              )}
              {hasDebt &&
                typeof dscr === 'number' &&
                Number.isFinite(dscr) &&
                dscr < resolvedTargetDscr && (
                  <p className="text-xs md:text-sm opacity-80 mt-0.5 text-red-700">
                    DSCR {dscr.toFixed(2)}× vs target {resolvedTargetDscr.toFixed(2)}×: coverage is below lender sizing.
                  </p>
                )}
              {typeof yieldOnCost === 'number' && yieldOnCost > 0 && (
                <p className="text-xs md:text-sm opacity-90 mt-0.5">
                  Yield on cost of {(yieldOnCost * 100).toFixed(1)}%
                  {typeof marketCapRateDisplay === 'number' && (
                    <> vs market cap {(marketCapRateDisplay * 100).toFixed(1)}%</>
                  )}
                  {typeof capRateSpreadBps === 'number' && (
                    <> ({capRateSpreadBps >= 0 ? '+' : ''}{(capRateSpreadBps / 100).toFixed(1)} bp)</>
                  )}
                </p>
              )}
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
            {showHotelFacilityMetrics ? (
              <div className="grid gap-4 md:grid-cols-3 text-xs text-slate-700">
                <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-md shadow-slate-100 space-y-1">
                  <div className="text-[11px] font-semibold uppercase tracking-wide text-slate-400">
                    Rooms
                  </div>
                  <div className="text-2xl font-semibold">
                    {typeof facilityMetrics?.rooms === 'number'
                      ? facilityMetrics.rooms.toLocaleString()
                      : '—'}
                  </div>
                  <div className="text-[11px] text-slate-500">Keys in the hotel</div>
                </div>
                <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-md shadow-slate-100 space-y-1">
                  <div className="text-[11px] font-semibold uppercase tracking-wide text-slate-400">
                    ADR
                  </div>
                  <div className="text-lg font-semibold">
                    {typeof facilityMetrics?.adr === 'number'
                      ? `$${facilityMetrics.adr.toFixed(0)}`
                      : '—'}
                  </div>
                  <div className="text-[11px] text-slate-500">Average daily rate</div>
                </div>
                <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-md shadow-slate-100 space-y-1">
                  <div className="text-[11px] font-semibold uppercase tracking-wide text-slate-400">
                    Occupancy
                  </div>
                  <div className="text-lg font-semibold">
                    {typeof facilityMetrics?.occupancy === 'number'
                      ? `${(facilityMetrics.occupancy * 100).toFixed(0)}%`
                      : '—'}
                  </div>
                  <div className="text-[11px] text-slate-500">Stabilized occupancy</div>
                </div>
                <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-md shadow-slate-100 space-y-1">
                  <div className="text-[11px] font-semibold uppercase tracking-wide text-slate-400">
                    RevPAR
                  </div>
                  <div className="text-lg font-semibold">
                    {typeof facilityMetrics?.revpar === 'number'
                      ? `$${facilityMetrics.revpar.toFixed(0)}`
                      : '—'}
                  </div>
                  <div className="text-[11px] text-slate-500">Revenue per available room</div>
                </div>
                <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-md shadow-slate-100 space-y-1 md:col-span-2">
                  <div className="text-[11px] font-semibold uppercase tracking-wide text-slate-400">
                    Cost per Key
                  </div>
                  <div className="text-lg font-semibold">
                    {typeof facilityMetrics?.costPerKey === 'number'
                      ? `$${facilityMetrics.costPerKey.toLocaleString(undefined, { maximumFractionDigits: 0 })}`
                      : '—'}
                  </div>
                  <div className="text-[11px] text-slate-500">Total project cost per room</div>
                </div>
              </div>
            ) : showIndustrialFacilityMetrics ? (
              <div className="grid gap-4 md:grid-cols-3 text-xs text-slate-700">
                <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-md shadow-slate-100 space-y-1">
                  <div className="text-[11px] font-semibold uppercase tracking-wide text-slate-400">
                    Building Size
                  </div>
                  <div className="text-2xl font-semibold">
                    {typeof facilityMetrics?.buildingSize === 'number'
                      ? `${facilityMetrics.buildingSize.toLocaleString()} SF`
                      : '—'}
                  </div>
                  <div className="text-[11px] text-slate-500">Total gross building area</div>
                </div>
                <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-md shadow-slate-100 space-y-1">
                  <div className="text-[11px] font-semibold uppercase tracking-wide text-slate-400">
                    Cost per SF
                  </div>
                  <div className="text-lg font-semibold">
                    {typeof facilityMetrics?.costPerSf === 'number'
                      ? formatters.currencyExact(facilityMetrics.costPerSf)
                      : '—'}
                  </div>
                  <div className="text-[11px] text-slate-500">Total project cost divided by SF</div>
                </div>
                <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-md shadow-slate-100 space-y-1">
                  <div className="text-[11px] font-semibold uppercase tracking-wide text-slate-400">
                    Revenue & NOI per SF
                  </div>
                  <div className="mt-2 space-y-1">
                    <div className="flex items-baseline justify-between">
                      <span className="text-[11px] text-slate-500">Revenue</span>
                      <span className="text-sm font-semibold">
                        {typeof facilityMetrics?.revenuePerSf === 'number'
                          ? `$${facilityMetrics.revenuePerSf.toFixed(1)} /SF`
                          : '—'}
                      </span>
                    </div>
                    <div className="flex items-baseline justify-between">
                      <span className="text-[11px] text-slate-500">NOI</span>
                      <span className="text-sm font-semibold">
                        {typeof facilityMetrics?.noiPerSf === 'number'
                          ? `$${facilityMetrics.noiPerSf.toFixed(1)} /SF`
                          : '—'}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            ) : (
              <>
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
              </>
            )}
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

      {/* Target Yield Prescription */}
      <div className="bg-white rounded-xl border border-slate-200/70 shadow-lg shadow-slate-200/50 mb-8">
        <div className="px-6 py-5 border-b border-slate-100">
          <div className="inline-flex items-center text-[11px] font-semibold uppercase mb-4 px-3 py-1 rounded-full bg-gradient-to-r from-indigo-50 to-purple-50 text-indigo-700 tracking-wide shadow-sm border border-indigo-200/50">
            Prescriptive Playbook
          </div>
          <h3 className="text-xl font-semibold text-slate-900">What It Would Take to Hit Target Yield</h3>
          <p className="text-sm text-slate-500 mt-1">See how much NOI or cost needs to move for this project to hit its underwriting hurdle.</p>
        </div>
        <div className="p-6 md:p-8">
        {(() => {
          const formatMoney = (value?: number) =>
              typeof value === 'number' && Number.isFinite(value) ? formatters.currency(value) : '—';
            const formatPercent = (value?: number) =>
              typeof value === 'number' && Number.isFinite(value) ? `${(value * 100).toFixed(1)}%` : '—';
            const formatMultiplier = (value?: number) =>
              typeof value === 'number' && Number.isFinite(value) ? `${value.toFixed(2)}x` : '—';

            const totalCostValue =
              typeof totalProjectCost === 'number' && Number.isFinite(totalProjectCost) && totalProjectCost > 0
                ? totalProjectCost
                : undefined;
            const currentNoiValue = typeof currentNoi === 'number' && Number.isFinite(currentNoi) ? currentNoi : undefined;
            const requiredNoiValue = typeof requiredNoi === 'number' && Number.isFinite(requiredNoi) ? requiredNoi : undefined;
            const currentYieldValue = typeof stabilizedYield === 'number' && Number.isFinite(stabilizedYield) ? stabilizedYield : undefined;
            const targetYieldValue =
              typeof targetYieldRate === 'number' && Number.isFinite(targetYieldRate) && targetYieldRate > 0 ? targetYieldRate : undefined;
            const dscrValue = typeof dscr === 'number' && Number.isFinite(dscr) ? dscr : undefined;
            const targetDscrValue =
              typeof resolvedTargetDscr === 'number' && Number.isFinite(resolvedTargetDscr) ? resolvedTargetDscr : undefined;

            const noiShortfall =
              typeof requiredNoiValue === 'number' && typeof currentNoiValue === 'number'
                ? requiredNoiValue - currentNoiValue
                : undefined;
            const noiShortfallPct =
              typeof noiShortfall === 'number' && typeof currentNoiValue === 'number' && currentNoiValue !== 0
                ? noiShortfall / currentNoiValue
                : undefined;

            const maxCostForTarget =
              typeof currentNoiValue === 'number' &&
              typeof targetYieldValue === 'number' &&
              targetYieldValue > 0
                ? currentNoiValue / targetYieldValue
                : undefined;
            const costReductionNeeded =
              typeof totalCostValue === 'number' && typeof maxCostForTarget === 'number'
                ? totalCostValue - maxCostForTarget
                : undefined;

            const gapBps =
              typeof targetYieldValue === 'number' && typeof currentYieldValue === 'number'
                ? Math.round((targetYieldValue - currentYieldValue) * 10000)
                : undefined;

            let yieldSummary = 'Yield-on-cost data is still loading.';
            if (typeof currentYieldValue === 'number' && typeof targetYieldValue === 'number') {
              const direction =
                typeof gapBps === 'number'
                  ? gapBps > 0
                    ? `${Math.abs(gapBps)} bps below target`
                    : `${Math.abs(gapBps)} bps above target`
                  : null;
              yieldSummary = `Current yield is ${formatPercent(currentYieldValue)} vs ${formatPercent(targetYieldValue)}${
                direction ? ` (${direction})` : ''
              }.`;
            }

            let dscrSummary = 'Debt coverage metrics are still loading. Use lender sizing once available.';
            if (typeof dscrValue === 'number' && typeof targetDscrValue === 'number') {
              dscrSummary =
                dscrValue >= targetDscrValue
                  ? `Debt coverage is solid at ${formatMultiplier(dscrValue)} vs ${formatMultiplier(targetDscrValue)} — equity returns are the main limiter.`
                  : `Debt coverage is ${formatMultiplier(dscrValue)} vs ${formatMultiplier(
                      targetDscrValue
                    )}; expect lenders to require NOI lift, lower leverage, or added credit support.`;
            } else if (typeof dscrValue === 'number') {
              dscrSummary = `Debt coverage is ${formatMultiplier(dscrValue)}. Target DSCR not provided.`;
            }

          return (
              <div className="grid gap-6 md:gap-8 md:grid-cols-3 text-sm text-slate-700">
                <div className="space-y-3">
                  <p className="text-xs font-semibold text-slate-500 uppercase tracking-[0.2em]">Path 1 · Increase NOI</p>
                    <div className="rounded-lg border border-slate-200 bg-white p-4 space-y-2 shadow-md shadow-slate-100">
                    <div className="flex justify-between">
                      <span className="text-slate-500">Current NOI</span>
                      <span className="font-semibold text-slate-900">{formatMoney(currentNoiValue)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-500">NOI needed</span>
                      <span className="font-semibold text-slate-900">{formatMoney(requiredNoiValue)}</span>
                    </div>
                    <p className="text-[12px] text-slate-500 leading-relaxed border-t border-slate-100 pt-2">
                      {typeof noiShortfall === 'number' && noiShortfall > 0 ? (
                        <>
                          Increase annual NOI by <span className="font-semibold text-slate-900">{formatMoney(noiShortfall)}</span>
                          {typeof noiShortfallPct === 'number' && Number.isFinite(noiShortfallPct)
                            ? ` (${(noiShortfallPct * 100).toFixed(1)}% lift)`
                            : ''}{' '}
                          to reach {formatPercent(targetYieldValue)}.
                        </>
                      ) : requiredNoiValue && currentNoiValue ? (
                        'Current NOI already meets the target yield — keep this level of performance through stabilization.'
                      ) : (
                        'Once NOI and target yield metrics load, this path highlights the lift required.'
                      )}
                    </p>
                  </div>
                </div>

                <div className="space-y-3">
                  <p className="text-xs font-semibold text-slate-500 uppercase tracking-[0.2em]">Path 2 · Reduce Project Cost</p>
                    <div className="rounded-lg border border-slate-200 bg-white p-4 space-y-2 shadow-md shadow-slate-100">
                    <div className="flex justify-between">
                      <span className="text-slate-500">Current total cost</span>
                      <span className="font-semibold text-slate-900">{formatMoney(totalCostValue)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-500">Max cost supported</span>
                      <span className="font-semibold text-slate-900">{formatMoney(maxCostForTarget)}</span>
                    </div>
                    <p className="text-[12px] text-slate-500 leading-relaxed border-t border-slate-100 pt-2">
                      {typeof costReductionNeeded === 'number' && costReductionNeeded > 0 ? (
                        <>
                          Value engineer roughly <span className="font-semibold text-slate-900">{formatMoney(costReductionNeeded)}</span> from the budget or
                          source grants/equity to close the gap.
                        </>
                      ) : totalCostValue && maxCostForTarget ? (
                        'Today’s cost basis already supports the target yield at current NOI.'
                      ) : (
                        'Cost stack guidance appears once current NOI and target yield inputs are ready.'
                      )}
                    </p>
                  </div>
                </div>

                <div className="space-y-3">
                  <p className="text-xs font-semibold text-slate-500 uppercase tracking-[0.2em]">Summary & Perspective</p>
                  <div className="rounded-lg border border-slate-200 bg-white p-4 space-y-3 shadow-md shadow-slate-100">
                    <p className="text-sm text-slate-600 leading-relaxed">{yieldSummary}</p>
                    <p className="text-sm text-slate-600 leading-relaxed">{dscrSummary}</p>
                    <p className="text-sm text-slate-500 leading-relaxed">
                      Use this as the talking track for lease-up assumptions, cost value engineering, or capital-stack tweaks.
                    </p>
                  </div>
                </div>
              </div>
          );
        })()}
        </div>
      </div>

      {/* Revenue Requirements Card */}
      {revenueReq && (
        <div className="bg-white rounded-xl shadow-lg overflow-hidden">
          <div className="bg-gradient-to-r from-emerald-500 to-teal-600 px-6 py-4">
            <h3 className="text-lg font-bold text-white">Revenue Required to Hit Target Yield</h3>
            <p className="text-sm text-emerald-100">
              {isHospitalityProject
                ? 'Benchmark NOI per key and RevPAR against the brand’s underwriting targets.'
                : 'Compare required NOI and revenue per SF against current performance.'}
            </p>
          </div>
          <div className="p-6 space-y-5">
            {isHospitalityProject ? (
              <div className="grid gap-4 md:grid-cols-2">
                <div className="p-4 bg-gray-50 rounded-lg">
                  <p className="text-sm text-gray-600 mb-1">Required NOI (target yield)</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {formatters.currency(requiredNoi ?? revenueReq.required_value)}
                  </p>
                  <p className="text-xs text-gray-600 mt-2">
                    Current NOI:{' '}
                    <span className="font-semibold text-gray-900">
                      {formatters.currency(currentNoi ?? revenueReq.market_value)}
                    </span>
                  </p>
                  {typeof noiGap === 'number' && (
                    <p className={`text-xs mt-1 ${noiGap >= 0 ? 'text-green-600' : 'text-amber-600'}`}>
                      Gap: {formatters.currency(Math.abs(noiGap))} ({Math.abs(noiGapPct || 0).toFixed(1)}%)&nbsp;
                      {noiGap >= 0 ? 'surplus vs target' : 'shortfall vs target'}
                    </p>
                  )}
                  <div className="mt-3 text-xs text-gray-600 space-y-1">
                    <div>
                      Required NOI per key:{' '}
                      <span className="font-semibold text-gray-900">
                        {typeof hospitalityRequiredNoiPerKeyValue === 'number'
                          ? formatters.currency(hospitalityRequiredNoiPerKeyValue)
                          : '—'}
                      </span>
                    </div>
                    <div>
                      Current NOI per key:{' '}
                      <span className="font-semibold text-gray-900">
                        {typeof hospitalityCurrentNoiPerKeyValue === 'number'
                          ? formatters.currency(hospitalityCurrentNoiPerKeyValue)
                          : '—'}
                      </span>
                    </div>
                  </div>
                </div>
                <div className="p-4 bg-blue-50 rounded-lg">
                  <p className="text-sm text-blue-900/80 mb-1">Required RevPAR</p>
                  <p className="text-2xl font-bold text-blue-700">
                    {typeof hospitalityRequiredRevparValue === 'number'
                      ? `$${hospitalityRequiredRevparValue.toFixed(0)}`
                      : '—'}
                  </p>
                  <p className="text-xs text-blue-900/80 mt-2">
                    Current RevPAR:{' '}
                    <span className="font-semibold">
                      {typeof hospitalityCurrentRevparValue === 'number'
                        ? `$${hospitalityCurrentRevparValue.toFixed(0)}`
                        : '—'}
                    </span>
                  </p>
                  {typeof hospitalityRevparGap === 'number' && (
                    <p className={`text-xs mt-1 ${hospitalityRevparGap <= 0 ? 'text-green-700' : 'text-amber-600'}`}>
                      Gap: ${Math.abs(hospitalityRevparGap).toFixed(0)} ({Math.abs(hospitalityRevparGapPct || 0).toFixed(1)}%)&nbsp;
                      {hospitalityRevparGap <= 0 ? 'above requirement' : 'needed to reach target'}
                    </p>
                  )}
                </div>
              </div>
            ) : (
              <>
            <div className="flex items-center justify-between mb-3">
              <div className="text-xs font-semibold uppercase tracking-wide text-slate-400">
                Feasibility vs Target Yield
              </div>
              {(() => {
                const label =
                  decisionStatus === 'GO'
                    ? 'GO'
                    : decisionStatus === 'NO-GO'
                      ? 'Not Feasible'
                      : 'Marginal';
                const baseClasses =
                  'rounded-full px-3 py-1 text-[11px] font-semibold uppercase tracking-wide';
                const colorClasses =
                  decisionStatus === 'GO'
                    ? 'bg-emerald-100 text-emerald-900'
                    : decisionStatus === 'NO-GO'
                      ? 'bg-red-100 text-red-900'
                      : 'bg-amber-100 text-amber-900';
                return <div className={`${baseClasses} ${colorClasses}`}>{label}</div>;
              })()}
            </div>
            <div className="grid gap-4 md:grid-cols-2">
              <div className="p-4 bg-gray-50 rounded-lg">
                <p className="text-sm text-gray-600 mb-1">Required NOI (target yield)</p>
                <p className="text-2xl font-bold text-gray-900">
                  {formatters.currency(requiredNoi ?? revenueReq.required_value)}
                </p>
                <p className="text-xs text-gray-600 mt-2">
                  Current NOI:{' '}
                  <span className="font-semibold text-gray-900">
                    {formatters.currency(currentNoi ?? revenueReq.market_value)}
                  </span>
                </p>
                {typeof noiGap === 'number' && (
                  <p className={`text-xs mt-1 ${noiGap >= 0 ? 'text-green-600' : 'text-amber-600'}`}>
                    Gap: {formatters.currency(Math.abs(noiGap))} ({Math.abs(noiGapPct || 0).toFixed(1)}%)&nbsp;
                    {noiGap >= 0 ? 'surplus vs target' : 'shortfall vs target'}
                  </p>
                )}
              </div>
              <div className="p-4 bg-blue-50 rounded-lg">
                <p className="text-sm text-blue-900/80 mb-1">Required Revenue per SF</p>
                <p className="text-2xl font-bold text-blue-700">
                  {typeof requiredRevenuePerSf === 'number' ? formatters.currency(requiredRevenuePerSf) : '—'}
                </p>
                <p className="text-xs text-blue-900/80 mt-2">
                  Current Revenue per SF:{' '}
                  <span className="font-semibold">
                    {typeof currentRevenuePerSf === 'number' ? formatters.currency(currentRevenuePerSf) : '—'}
                  </span>
                </p>
                {typeof revenuePerSfGap === 'number' && (
                  <p className={`text-xs mt-1 ${revenuePerSfGap >= 0 ? 'text-green-700' : 'text-amber-600'}`}>
                    Gap: {formatters.currency(Math.abs(revenuePerSfGap))} ({Math.abs(revenuePerSfGapPct || 0).toFixed(1)}%)&nbsp;
                    {revenuePerSfGap >= 0 ? 'above requirement' : 'needed to reach target'}
                  </p>
                )}
              </div>
            </div>
              </>
            )}

            <div className={`p-4 rounded-lg ${
              (revenueReq.feasibility?.status || revenueReq.feasibility) === 'Feasible' 
                ? 'bg-green-50 border border-green-200' 
                : 'bg-amber-50 border border-amber-200'
            }`}>
              <div className="flex flex-wrap items-center justify-between gap-3">
                <div>
                  <p className="text-xs font-semibold uppercase tracking-wider text-gray-500">
                    Feasibility vs Target Yield
                  </p>
                  <p className="text-sm text-gray-800 leading-snug mt-1">
                    {feasibilityGapCopy}
                  </p>
                </div>
                <span className={`font-bold ${
                  (revenueReq.feasibility?.status || revenueReq.feasibility) === 'Feasible' ? 'text-green-600' : 'text-amber-600'
                }`}>
                  {revenueReq.feasibility?.status || revenueReq.feasibility}
                </span>
              </div>
              {revenueReq.feasibility?.recommendation && (
                <p className="text-sm mt-3 text-gray-600">
                  {revenueReq.feasibility.recommendation}
                </p>
              )}
            </div>
            
            <div className="flex justify-between items-center pt-4 border-t">
              <span className="text-sm text-gray-600">Simple Payback (yrs)</span>
              <span className="text-lg font-bold">{formatters.years(displayData.paybackPeriod)}</span>
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
          <div className="p-6 space-y-4 text-sm">
            {(() => {
              const formatCost = (value?: number) =>
                typeof value === 'number' && Number.isFinite(value)
                  ? formatters.costPerSF(value)
                  : 'n/a';
              const basisCopy = typeof costPerSFDeltaPct === 'number'
                ? `${Math.abs(costPerSFDeltaPct).toFixed(1)}% ${costPerSFDeltaPct >= 0 ? 'above' : 'below'} benchmark`
                : 'Benchmark comparison pending additional market data.';
              return (
                <div className="bg-white rounded-lg p-4 shadow-sm space-y-1">
                  <div className="flex justify-between items-center">
                    <span className="text-sm font-medium text-gray-600">Your cost basis</span>
                    <span className="text-xl font-bold text-blue-600">
                      {formatCost(costPerSFValue ?? totals.cost_per_sf)}
                    </span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-500">Market benchmark</span>
                    <span className="font-medium text-gray-700">
                      {formatCost(marketCostPerSF)}
                    </span>
                  </div>
                  <p className="text-xs text-gray-500 mt-2">{basisCopy}</p>
                </div>
              );
            })()}

            <div className="relative">
              <div className="w-full bg-gradient-to-r from-green-100 via-yellow-100 to-red-100 rounded-full h-4 relative">
                <div
                  className="absolute top-1/2 transform -translate-y-1/2 w-6 h-6 bg-blue-600 rounded-full border-2 border-white shadow-lg z-10 transition-all"
                  style={{ left: `calc(${costPerSFGaugePosition}% - 12px)` }}
                />
              </div>
              <div className="flex justify-between text-xs text-gray-500 mt-2">
                <span>-20%</span>
                <span>Market Avg</span>
                <span>+20%</span>
              </div>
              <div className="mt-4 p-3 bg-blue-50 rounded-lg text-center text-blue-800 text-sm font-semibold">
                {typeof costPerSFDeltaPct === 'number'
                  ? `${Math.abs(costPerSFDeltaPct).toFixed(1)}% ${costPerSFDeltaPct >= 0 ? 'above' : 'below'} market`
                  : 'Waiting on market cost inputs'}
              </div>
            </div>

            <div className="bg-slate-900/40 border border-slate-800/50 rounded-lg p-4 text-slate-100">
              {(() => {
                const formatPct = (value?: number) =>
                  typeof value === 'number' && Number.isFinite(value)
                    ? `${(value * 100).toFixed(1)}%`
                    : 'n/a';
                const spreadCopy = typeof yieldCapSpreadBps === 'number' && typeof yieldCapSpreadPct === 'number'
                  ? `Spread: ${yieldCapSpreadBps >= 0 ? '+' : '-'}${Math.abs(yieldCapSpreadBps).toFixed(0)} bp (${formatPct(Math.abs(yieldCapSpreadPct))}) ${yieldCapSpreadBps >= 0 ? 'above' : 'below'} market`
                  : 'Add a market cap benchmark to calculate spread.';
                return (
                  <>
                    <p className="text-xs uppercase tracking-wider text-slate-400 mb-2">Yield vs market cap</p>
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span className="text-slate-300">Yield on cost</span>
                        <span className="font-semibold">{formatPct(effectiveYield)}</span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span className="text-slate-300">Market cap rate</span>
                        <span className="font-semibold">{formatPct(marketCapRateValue)}</span>
                      </div>
                      <p className="text-xs text-amber-200 mt-1">{spreadCopy}</p>
                    </div>
                  </>
                );
              })()}
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
            {(() => {
              const sensitivity = displayData?.sensitivity || {};

              // Prefer backend-supplied base; fallback to the mapped yield so cards always have context.
              const baseYOC =
                typeof sensitivity.baseYieldOnCost === 'number' && Number.isFinite(sensitivity.baseYieldOnCost)
                  ? sensitivity.baseYieldOnCost
                  : typeof displayData.yieldOnCost === 'number' && Number.isFinite(displayData.yieldOnCost)
                    ? displayData.yieldOnCost
                    : undefined;

              const fmt = (value?: number) =>
                typeof value === 'number' && Number.isFinite(value)
                  ? formatters.percentage(value)
                  : '—';
              const breakEvenOcc =
                typeof displayData.breakEvenOccupancyForTargetYield === 'number'
                  ? displayData.breakEvenOccupancyForTargetYield
                  : typeof displayData.breakEvenOccupancy === 'number'
                    ? displayData.breakEvenOccupancy
                    : undefined;
              const occLabel =
                typeof breakEvenOcc === 'number'
                  ? breakEvenOcc > 1.02
                    ? '> 100% (not achievable)'
                    : formatters.percentage(breakEvenOcc)
                  : 'N/A';

              // Return backend scenario metric when present; otherwise fall back to naive +/-10% adjustments.
              const scenarioValue = (
                backendValue: number | undefined,
                fallbackFn: (base: number) => number
              ): string => {
                if (typeof backendValue === 'number' && Number.isFinite(backendValue)) {
                  return fmt(backendValue);
                }
                if (typeof baseYOC === 'number') {
                  return fmt(fallbackFn(baseYOC));
                }
                return '—';
              };

              const cards = [
                {
                  label: 'If costs +10%',
                  icon: <TrendingDown className="h-5 w-5 text-red-500" />,
                  value: scenarioValue(sensitivity.costUp10YieldOnCost, (base) => base / 1.1),
                  color: 'text-red-600'
                },
                {
                  label: 'If costs -10%',
                  icon: <TrendingUp className="h-5 w-5 text-green-500" />,
                  value: scenarioValue(sensitivity.costDown10YieldOnCost, (base) => base / 0.9),
                  color: 'text-green-600'
                },
                {
                  label: 'If revenue +10%',
                  icon: <TrendingUp className="h-5 w-5 text-green-500" />,
                  value: scenarioValue(sensitivity.revenueUp10YieldOnCost, (base) => base * 1.1),
                  color: 'text-green-600'
                },
                {
                  label: 'If revenue -10%',
                  icon: <TrendingDown className="h-5 w-5 text-red-500" />,
                  value: scenarioValue(sensitivity.revenueDown10YieldOnCost, (base) => base * 0.9),
                  color: 'text-red-600'
                }
              ];

              return (
                <>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    {cards.map(({ label, icon, value, color }) => (
                      <div key={label} className="bg-white rounded-lg p-4 shadow-sm">
                        <p className="text-xs text-gray-500 uppercase tracking-wider mb-2">{label}</p>
                        <div className="flex items-center justify-between">
                          {icon}
                          <span className={`text-lg font-bold ${color}`}>
                            {value !== '—' ? `${value} yield` : '—'}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                  <div className="p-4 bg-gradient-to-r from-purple-100 to-pink-100 rounded-lg">
                    <p className="text-xs text-gray-600 uppercase tracking-wider mb-2">Break-even needs:</p>
                    <span className="text-xl font-bold text-purple-700">{occLabel}</span>
                  </div>
                </>
              );
            })()}
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
              {
                icon: CheckCircle,
                color: 'green',
                title: 'Groundbreaking',
                date: projectTimeline?.groundbreaking ?? 'TBD'
              },
              {
                icon: Building,
                color: 'blue',
                title: 'Structure Complete',
                date: projectTimeline?.structureComplete ?? 'TBD'
              },
              {
                icon: Users,
                color: 'purple',
                title: 'Substantial Completion',
                date: projectTimeline?.substantialCompletion ?? 'TBD'
              },
              {
                icon: Target,
                color: 'orange',
                title: buildingType === 'multifamily' ? 'First Tenant Move-in' : 'Grand Opening',
                date: projectTimeline?.grandOpening ?? 'TBD'
              }
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

            {buildingType === 'office' && (
              <div className="mb-4">
                <h4 className="text-sm font-bold text-gray-700 mb-3 uppercase tracking-wider">Office Opex & CAM</h4>
                <div className="bg-white rounded-lg p-3 shadow-sm space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Operating Expenses</span>
                    <span className="font-bold text-gray-900">
                      {formatters.currency(operatingExpensesTotal)}
                      {' '}
                      ({formatters.currencyExact(operatingExpensesTotal / normalizedOfficeSquareFootage)}/SF)
                    </span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Recoverable CAM</span>
                    <span className="font-bold text-gray-900">
                      {camChargesTotal > 0
                        ? `${formatters.currency(camChargesTotal)} (${formatters.currencyExact(camChargesTotal / normalizedOfficeSquareFootage)}/SF)`
                        : 'Included in rent'}
                    </span>
                  </div>
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
        <div className="space-y-3">
          {decisionBullets.length > 0 ? (
            decisionBullets.slice(0, 3).map((point, idx) => (
              <div key={idx} className="flex items-start gap-3 bg-white rounded-lg p-3 shadow-sm">
                <div className="w-6 h-6 bg-amber-200 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                  <span className="text-amber-700 text-xs font-bold">{idx + 1}</span>
                </div>
                <span className="text-sm text-gray-700">{point}</span>
              </div>
            ))
          ) : (
            <p className="text-sm text-gray-700">Cost, yield, and soft cost metrics are loading.</p>
          )}
        </div>
      </div>

      {/* Executive Financial Summary Footer */}
        <div className="bg-gradient-to-r from-slate-900 via-indigo-900 to-slate-900 rounded-xl p-8 shadow-2xl">
          <div className="grid grid-cols-1 gap-8 sm:grid-cols-2 xl:grid-cols-4 2xl:grid-cols-5">
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
              INVESTMENT PER UNIT
            </p>
            <p className="text-3xl font-bold text-white">
              {displayData.costPerUnit > 0 ? formatters.currencyExact(displayData.costPerUnit) : 'N/A'}
            </p>
            <p className="text-sm text-slate-500">Total project cost divided by units</p>
          </div>
            <div className="text-center">
              <p className="text-xs text-slate-400 uppercase tracking-wider mb-3">DEBT COVERAGE</p>
              <p className="text-3xl font-bold text-white">{formatters.multiplier(displayData.dscr)}</p>
              <p className="text-sm text-slate-500">DSCR (Target: 1.25x)</p>
            </div>
          {(() => {
            const showTotalUnitsFooter =
              (buildingType || '').toLowerCase() !== 'industrial' &&
              typeof displayData.units === 'number' &&
              displayData.units > 0;
            if (!showTotalUnitsFooter) return null;
            return (
            <div className="text-center">
              <p className="text-xs text-slate-400 uppercase tracking-wider mb-3">TOTAL UNITS</p>
              <p className="text-3xl font-bold text-white">{displayData.units.toLocaleString()}</p>
              <p className="text-sm text-slate-500">Derived from square footage and density</p>
            </div>
            );
          })()}
          </div>
        </div>
      </div>

      {/* Scenario Comparison Modal */}
      {isScenarioOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 px-4 py-8" onClick={() => setIsScenarioOpen(false)}>
          <div className="w-full max-w-6xl rounded-2xl border border-slate-800 bg-slate-950 shadow-2xl" onClick={event => event.stopPropagation()}>
            <div className="flex items-center justify-between gap-4 border-b border-slate-800 px-6 py-4">
              <div>
                <p className="text-sm font-semibold text-white">Scenario Comparison – Current vs Target Yield</p>
                <p className="text-xs text-slate-400">Shows the current case alongside the target yield requirements.</p>
              </div>
              <button
                className="inline-flex items-center gap-2 rounded-full border border-slate-700 px-3 py-1 text-xs font-semibold text-slate-200 hover:bg-slate-800"
                onClick={() => setIsScenarioOpen(false)}
              >
                <XCircle className="h-4 w-4" />
                Close
              </button>
            </div>
            <div className="px-6 py-6">
              {(() => {
                const formatPct = (value?: number) => (typeof value === 'number' && Number.isFinite(value) ? `${(value * 100).toFixed(1)}%` : '—');
                const formatCurrency0 = (value?: number) =>
                  typeof value === 'number' && Number.isFinite(value)
                    ? value.toLocaleString('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 })
                    : '—';
                const formatPerSf = (value?: number) => (typeof value === 'number' && Number.isFinite(value) ? `$${value.toFixed(0)}/SF` : '—');
                const formatDscrValue = (value?: number) => (typeof value === 'number' && Number.isFinite(value) ? `${value.toFixed(2)}×` : '—');

                const currentYieldValue = typeof stabilizedYield === 'number' && Number.isFinite(stabilizedYield) ? stabilizedYield : undefined;
                const targetYieldValue = typeof targetYieldRate === 'number' && Number.isFinite(targetYieldRate) ? targetYieldRate : undefined;

                const currentNoiValue = typeof noi === 'number' && Number.isFinite(noi) ? noi : undefined;
                const requiredNoiValue = typeof requiredNoi === 'number' && Number.isFinite(requiredNoi) ? requiredNoi : undefined;

                const currentRevenuePerSfValue =
                  typeof currentRevenuePerSf === 'number' && Number.isFinite(currentRevenuePerSf) ? currentRevenuePerSf : undefined;
                const requiredRevenuePerSfValue =
                  typeof requiredRevenuePerSf === 'number' && Number.isFinite(requiredRevenuePerSf) ? requiredRevenuePerSf : undefined;

                const currentDscrValue =
                  typeof dscr === 'number' && Number.isFinite(dscr)
                    ? dscr
                    : typeof annualDebtService === 'number' && annualDebtService > 0 && typeof currentNoiValue === 'number'
                      ? currentNoiValue / annualDebtService
                      : undefined;
                const targetDscrValue =
                  typeof requiredNoiValue === 'number' && typeof annualDebtService === 'number' && annualDebtService > 0
                    ? requiredNoiValue / annualDebtService
                    : undefined;

                const yieldGap = typeof targetYieldValue === 'number' && typeof currentYieldValue === 'number' ? targetYieldValue - currentYieldValue : undefined;
                const noiDelta =
                  typeof requiredNoiValue === 'number' && typeof currentNoiValue === 'number' ? requiredNoiValue - currentNoiValue : undefined;
                const noiDeltaPct =
                  typeof noiDelta === 'number' && typeof requiredNoiValue === 'number' && requiredNoiValue !== 0 ? noiDelta / requiredNoiValue : undefined;
                const revenueDeltaPerSf =
                  typeof requiredRevenuePerSfValue === 'number' && typeof currentRevenuePerSfValue === 'number'
                    ? requiredRevenuePerSfValue - currentRevenuePerSfValue
                    : undefined;
                const revenueDeltaPct =
                  typeof revenueDeltaPerSf === 'number' &&
                  typeof requiredRevenuePerSfValue === 'number' &&
                  requiredRevenuePerSfValue !== 0
                    ? revenueDeltaPerSf / requiredRevenuePerSfValue
                    : undefined;

                return (
                  <div className="space-y-4 text-xs md:text-sm text-slate-100">
                    <div className="rounded-lg border border-slate-800/60 bg-slate-900/70 px-4 py-3 flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
                      <div>
                        <div className="text-xs font-semibold text-slate-200">Gaps to target</div>
                        <div className="text-xs text-slate-300 mt-1">
                          Yield gap:{' '}
                          <span className="font-semibold">
                            {typeof yieldGap === 'number' ? formatPct(yieldGap) : 'n/a'}
                          </span>
                          {targetYieldValue != null && currentYieldValue != null && (
                            <span className="text-slate-400">
                              {' '}
                              (current {formatPct(currentYieldValue)} vs target {formatPct(targetYieldValue)})
                            </span>
                          )}
                        </div>
                      </div>
                      <div className="text-xs text-slate-300">
                        NOI gap:{' '}
                        <span className="font-semibold">
                          {formatCurrency0(noiDelta)}
                          {typeof noiDeltaPct === 'number' ? ` (${(noiDeltaPct * 100).toFixed(1)}%)` : ''}
                        </span>
                        <span className="mx-3 text-slate-700">|</span>
                        Revenue gap:{' '}
                        <span className="font-semibold">
                          {formatPerSf(revenueDeltaPerSf)}
                          {typeof revenueDeltaPct === 'number' ? ` (${(revenueDeltaPct * 100).toFixed(1)}%)` : ''}
                        </span>
                      </div>
                    </div>

                    <div className="grid gap-4 md:grid-cols-2">
                      <div className="rounded-lg border border-slate-800 bg-slate-900/40 p-4">
                        <p className="text-xs font-semibold uppercase tracking-wider text-slate-400">Current scenario</p>
                        <div className="mt-3 space-y-2 text-sm text-slate-200">
                          <div className="flex justify-between">
                            <span>Yield on cost</span>
                            <span className="font-semibold">{formatPct(currentYieldValue)}</span>
                          </div>
                          <div className="flex justify-between">
                            <span>NOI</span>
                            <span className="font-semibold">{formatCurrency0(currentNoiValue)}</span>
                          </div>
                          <div className="flex justify-between">
                            <span>Revenue per SF</span>
                            <span className="font-semibold">{formatPerSf(currentRevenuePerSfValue)}</span>
                          </div>
                          <div className="flex justify-between">
                            <span>DSCR</span>
                            <span className="font-semibold">{formatDscrValue(currentDscrValue)}</span>
                          </div>
                        </div>
                      </div>
                      <div className="rounded-lg border border-slate-800 bg-slate-900/40 p-4">
                        <p className="text-xs font-semibold uppercase tracking-wider text-slate-400">Target yield scenario</p>
                        <div className="mt-3 space-y-2 text-sm text-slate-200">
                          <div className="flex justify-between">
                            <span>Yield on cost (target)</span>
                            <span className="font-semibold">{formatPct(targetYieldValue)}</span>
                          </div>
                          <div className="flex justify-between">
                            <span>Required NOI</span>
                            <span className="font-semibold">{formatCurrency0(requiredNoiValue)}</span>
                          </div>
                          <div className="flex justify-between">
                            <span>Required revenue per SF</span>
                            <span className="font-semibold">{formatPerSf(requiredRevenuePerSfValue)}</span>
                          </div>
                          <div className="flex justify-between">
                            <span>DSCR at target NOI</span>
                            <span className="font-semibold">{formatDscrValue(targetDscrValue)}</span>
                          </div>
                        </div>
                      </div>
                    </div>

                    <div className="text-xs text-slate-300">
                      {typeof yieldGap === 'number' && typeof targetYieldValue === 'number' && yieldGap > 0 ? (
                        <>
                          To reach a yield on cost of <span className="font-semibold">{formatPct(targetYieldValue)}</span>, the project needs roughly{' '}
                          <span className="font-semibold">{formatCurrency0(noiDelta)}</span> more NOI and{' '}
                          <span className="font-semibold">{formatPerSf(revenueDeltaPerSf)}</span> more revenue per SF (or equivalent cost savings).
                        </>
                      ) : (
                        <>Target yield isn’t configured for this asset yet—showing the current snapshot only.</>
                      )}
                    </div>
                  </div>
                );
              })()}
            </div>
          </div>
        </div>
      )}
    </>
  );
};
