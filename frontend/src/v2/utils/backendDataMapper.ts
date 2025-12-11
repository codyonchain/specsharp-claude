/**
 * Maps backend data to frontend display fields
 * Single source of truth for where data lives in backend response
 */

import { safeGet } from './displayFormatters';

// Shared modifiers fallback so downstream access remains safe even when an
// analysis payload omits modifier metadata.
// eslint-disable-next-line @typescript-eslint/no-explicit-any
let modifiers: any = {};

interface FacilityMetricEntry {
  id: string;
  label: string;
  value?: number;
  unit?: string;
}

interface FacilityMetrics {
  units?: number;
  costPerUnit?: number;
  revenuePerUnit?: number;
  monthlyRevenuePerUnit?: number;
  unitLabel?: string;
  buildingSize?: number;
  costPerSf?: number;
  revenuePerSf?: number;
  noiPerSf?: number;
  rooms?: number;
  adr?: number;
  occupancy?: number;
  revpar?: number;
  costPerKey?: number;
  officeRentPerSf?: number;
  officeNoiPerSf?: number;
  type?: string;
  entries?: FacilityMetricEntry[];
  restaurantSalesPerSf?: number;
  restaurantNoiPerSf?: number;
  restaurantCostPerSf?: number;
}

export interface DisplayData {
  // Financial metrics
  roi: number;
  npv: number;
  irr: number;
  paybackPeriod: number;
  dscr: number;
  
  // Revenue metrics
  annualRevenue: number;
  monthlyRevenue: number;
  noi: number;
  operatingMargin: number;
  operatingExpenses: number;
  camCharges: number;
  yieldOnCost: number;
  marketCapRate: number | null;
  capRateSpreadBps: number | null;
  targetYield?: number | null;
  targetDscr?: number | null;
  operatingExpenses?: number;
  camCharges?: number;
  
  // Investment decision
  investmentDecision: 'GO' | 'NO-GO' | 'PENDING';
  feasible?: boolean;
  decisionReason: string;
  suggestions: string[];
  improvementsNeeded: Array<{
    metric: string;
    current: number;
    required: number;
    gap: number;
    suggestion: string;
  }>;
  failedCriteria?: Array<{
    metric: string;
    current: string;
    required: string;
    gap: string;
    fix: string;
  }>;
  metricsTable?: Array<{
    metric: string;
    current: string;
    required: string;
    status: 'pass' | 'fail';
  }>;
  feasibilityScore?: number;
  
  // Building-specific metrics
  unitCount: number;
  unitLabel: string;
  unitType: string;
  revenuePerUnit: number;
  costPerUnit: number;
  units?: number;
  annualRevenuePerUnit?: number;
  monthlyRevenuePerUnit?: number;

  // Underwriting refinements
  yieldGapBps?: number | null;
  breakEvenOccupancyForTargetYield?: number | null;
  sensitivity?: {
    baseYieldOnCost?: number | null;
    revenueUp10YieldOnCost?: number | null;
    revenueDown10YieldOnCost?: number | null;
    costUp10YieldOnCost?: number | null;
    costDown10YieldOnCost?: number | null;
    scenarios?: any[] | null;
  };
  
  // Operational metrics
  breakEvenOccupancy: number;
  targetOccupancy: number;
  requiredRent: number;
  facilityMetrics?: FacilityMetrics;
  projectTimeline?: {
    groundbreaking?: string;
    structureComplete?: string;
    substantialCompletion?: string;
    grandOpening?: string;
  };
  
  // Department allocations
  departments: Array<{
    name: string;
    percent: number;
    amount: number;
    square_footage: number;
    cost_per_sf: number;
    gradient?: string;
    icon_name?: string;
  }>;
  
  // Staffing metrics
  staffingMetrics: Array<{
    label: string;
    value: number | string;
  }>;
  
  // Revenue efficiency metrics
  revenueMetrics: { [key: string]: string };
  
  // Target KPIs
  kpis: Array<{
    label: string;
    value: string;
    color: string;
  }>;
  
  // Core project data
  totalProjectCost: number;
  constructionCost: number;
  softCosts: number;
  costPerSF: number;
  squareFootage: number;
  buildingType: string;
  buildingSubtype: string;
  location: string;
  floors: number;
  constructionCostBuildUp: Array<{
    label: string;
    value_per_sf?: number;
    multiplier?: number;
  }>;
  finishLevel: string;
  finishLevelSource: 'explicit' | 'description' | 'default';
  costFactor?: number;
  revenueFactor?: number;
  // Derived market comparison helpers
  costPerSf?: number;
  marketCostPerSF?: number;
  marketCostPerSf?: number;
  costPerSFDeltaPct?: number;
  costPerSfDeltaPct?: number;
  requiredNoiPerKey?: number;
  currentNoiPerKey?: number;
  requiredRevpar?: number;
  currentRevpar?: number;
  impliedAdrForTargetRevpar?: number;
  impliedOccupancyForTargetRevpar?: number;
  requiredNoiPerSf?: number;
  currentNoiPerSf?: number;
}

export class BackendDataMapper {
  /**
   * Map backend response to standardized display data
   * Handles all building types dynamically
   */
  static mapToDisplay(analysis: any): DisplayData {
    if (!analysis) {
      return this.getEmptyDisplayData();
    }
    
    const calculations = analysis?.calculations || analysis?.calculation_data || {};
    const rawTimeline =
      calculations?.project_timeline ||
      analysis?.project_timeline ||
      analysis?.engine_output?.project_timeline ||
      analysis?.result?.project_timeline ||
      null;
    modifiers =
      (calculations as any)?.modifiers ||
      (calculations as any)?.calculations?.modifiers ||
      {};
    
    // Add comprehensive tracing for ROI and financial metrics
    console.log('=== ROI & FINANCIAL METRICS TRACE ===');
    console.log('Full analysis object:', analysis);
    console.log('Full calculations object:', calculations);
    
    // Check both possible paths due to double-nested structure
    const path1_roi = calculations?.ownership_analysis?.return_metrics?.estimated_roi;
    const path2_roi = calculations?.calculations?.ownership_analysis?.return_metrics?.estimated_roi;
    
    console.log('1. ROI at calculations.ownership_analysis:', path1_roi);
    console.log('2. ROI at calculations.calculations.ownership_analysis:', path2_roi);
    
    // Check where other metrics are - backend uses 'npv' not 'ten_year_npv'
    const path1_npv = calculations?.ownership_analysis?.return_metrics?.npv;
    const path2_npv = calculations?.calculations?.ownership_analysis?.return_metrics?.npv;
    
    console.log('3. NPV at path1:', path1_npv);
    console.log('4. NPV at path2:', path2_npv);
    
    // Check payback period
    const path1_payback = calculations?.ownership_analysis?.return_metrics?.payback_period;
    const path2_payback = calculations?.calculations?.ownership_analysis?.return_metrics?.payback_period;
    
    console.log('5. Payback at path1:', path1_payback);
    console.log('6. Payback at path2:', path2_payback);
    
    // Check IRR
    const path1_irr = calculations?.ownership_analysis?.return_metrics?.irr;
    const path2_irr = calculations?.calculations?.ownership_analysis?.return_metrics?.irr;
    
    console.log('7. IRR at path1:', path1_irr);
    console.log('8. IRR at path2:', path2_irr);
    
    // Check DSCR
    const path1_dscr = calculations?.ownership_analysis?.debt_metrics?.calculated_dscr;
    const path2_dscr = calculations?.calculations?.ownership_analysis?.debt_metrics?.calculated_dscr;
    
    console.log('9. DSCR at path1:', path1_dscr);
    console.log('10. DSCR at path2:', path2_dscr);
    
    // Show actual vs expected structure
    console.log('11. Full ownership_analysis at level 1:', calculations?.ownership_analysis);
    console.log('12. Full ownership_analysis at level 2:', calculations?.calculations?.ownership_analysis);
    
    // Check for annual revenue
    const path1_revenue = calculations?.ownership_analysis?.annual_revenue;
    const path2_revenue = calculations?.calculations?.ownership_analysis?.annual_revenue;
    
    console.log('13. Annual revenue at path1:', path1_revenue);
    console.log('14. Annual revenue at path2:', path2_revenue);
    
    // Check NOI
    const path1_noi = calculations?.ownership_analysis?.return_metrics?.estimated_annual_noi;
    const path2_noi = calculations?.calculations?.ownership_analysis?.return_metrics?.estimated_annual_noi;
    
    console.log('15. NOI at path1:', path1_noi);
    console.log('16. NOI at path2:', path2_noi);
    
    console.log('=== END ROI & FINANCIAL METRICS TRACE ===');
    
    // Now extract with proper fallback to both paths
    const ownership = calculations?.ownership_analysis || calculations?.calculations?.ownership_analysis || {};
    const revenueAnalysis = ownership?.revenue_analysis || {};
    const returnMetrics = ownership?.return_metrics || {};
    const debtMetrics = ownership?.debt_metrics || {};
    const investmentAnalysis = ownership?.investment_analysis || {};
    const projectInfo = ownership?.project_info || calculations?.project_info || calculations?.calculations?.project_info || {};
    // Backend sends operational_efficiency, not operational_metrics
    const operationalEfficiency = ownership?.operational_efficiency || calculations?.operational_efficiency || calculations?.calculations?.operational_efficiency || {};
    const operatingExpensesValue =
      safeGet(revenueAnalysis, 'operating_expenses', undefined) ??
      safeGet(operationalEfficiency, 'total_expenses', 0);
    const camChargesValue =
      safeGet(revenueAnalysis, 'cam_charges', undefined) ??
      safeGet(operationalEfficiency, 'cam_charges', 0);
    const parsedInputRaw = analysis?.parsed_input || {};
    const parsedInput: Record<string, any> = { ...parsedInputRaw };
    const constructionCosts = calculations?.construction_costs || {};
    const nestedCalculations = calculations?.calculations || {};
    const profile = calculations?.profile ||
      nestedCalculations?.profile ||
      analysis?.profile ||
      {};

    const rawBuildingTypeValue =
      calculations?.building_type ||
      calculations?.buildingType ||
      parsedInput?.building_type ||
      projectInfo?.building_type ||
      '';
    const buildingTypeName =
      typeof rawBuildingTypeValue === 'string'
        ? rawBuildingTypeValue
        : rawBuildingTypeValue?.name ?? String(rawBuildingTypeValue ?? '');
    const buildingTypeString = (buildingTypeName || '').toString();
    const lowerBuildingType = buildingTypeString.toLowerCase();
    const isIndustrialFacility =
      buildingTypeString.toUpperCase().includes('INDUSTRIAL') ||
      lowerBuildingType.includes('warehouse') ||
      lowerBuildingType.includes('manufacturing');
    const isHospitalityFacility =
      buildingTypeString.toUpperCase().includes('HOSPITALITY') ||
      lowerBuildingType.includes('hotel');
    const isOfficeFacility =
      buildingTypeString.toUpperCase().includes('OFFICE');
    const isRestaurantFacility =
      buildingTypeString.toUpperCase().includes('RESTAURANT');

    if (!parsedInput.square_footage || Number(parsedInput.square_footage) === 0) {
      const fallbackSF =
        Number(constructionCosts?.square_footage) ||
        Number(calculations?.totals?.square_footage) ||
        Number(calculations?.calculations?.totals?.square_footage) ||
        undefined;
      if (fallbackSF) {
        parsedInput.square_footage = fallbackSF;
      }
    }

    if (!parsedInput.building_type) {
      const inferredType = (projectInfo?.building_type || parsedInputRaw?.subtype || 'General')
        .toString()
        .trim();
      parsedInput.building_type = inferredType.toLowerCase().replace(/\s+/g, '_') || 'general';
      parsedInput.__display_type = inferredType || 'General';
    } else if (!parsedInput.__display_type) {
      parsedInput.__display_type = String(parsedInput.building_type)
        .replace(/_/g, ' ')
        .replace(/\b\w/g, c => c.toUpperCase());
    }
    const totals = calculations?.totals || calculations?.calculations?.totals || {};
    const calculationTrace = Array.isArray(calculations?.calculation_trace)
      ? calculations.calculation_trace.filter((entry: any) => entry && typeof entry === 'object' && 'step' in entry)
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

    const modifiersTrace = getLatestTrace('modifiers_applied');
    const finishSourceTrace = getLatestTrace('finish_level_source');

    const normalizeFinishLevel = (value: any): string | undefined => {
      if (typeof value !== 'string') {
        return undefined;
      }
      const trimmed = value.trim();
      if (!trimmed) {
        return undefined;
      }
      return trimmed.charAt(0).toUpperCase() + trimmed.slice(1).toLowerCase();
    };

    const finishLevelFromInfo = normalizeFinishLevel(projectInfo?.finish_level);
    const finishLevelFromParsed = normalizeFinishLevel(parsedInput?.finish_level);
    const finishLevelFromTrace = normalizeFinishLevel(modifiersTrace?.data?.finish_level);
    const finishLevel =
      finishLevelFromInfo ||
      finishLevelFromParsed ||
      finishLevelFromTrace ||
      'Standard';

    const isFinishSource = (value: any): value is 'explicit' | 'description' | 'default' =>
      value === 'explicit' || value === 'description' || value === 'default';

    const finishLevelSourceTrace = finishSourceTrace?.data?.source;
    const parsedFinishSource = parsedInput?.finish_level_source;
    const finishLevelSource: 'explicit' | 'description' | 'default' =
      (isFinishSource(finishLevelSourceTrace) && finishLevelSourceTrace) ||
      (isFinishSource(parsedFinishSource) && parsedFinishSource) ||
      'default';

    const costFactorFromTrace = typeof modifiersTrace?.data?.cost_factor === 'number' ? modifiersTrace.data.cost_factor : undefined;
    const revenueFactorFromTrace = typeof modifiersTrace?.data?.revenue_factor === 'number' ? modifiersTrace.data.revenue_factor : undefined;
    const fallbackCostFactor = typeof modifiers?.cost_factor === 'number' ? modifiers.cost_factor : undefined;
    const fallbackRevenueFactor = typeof modifiers?.revenue_factor === 'number' ? modifiers.revenue_factor : undefined;
    const costFactor = costFactorFromTrace ?? fallbackCostFactor;
    const revenueFactor = revenueFactorFromTrace ?? fallbackRevenueFactor;
    
    // TRACE DATA MAPPING
    console.log('=== BACKEND DATA MAPPER TRACE ===');
    console.log('Mapper input analysis:', analysis);
    console.log('Calculations extracted:', calculations);
    console.log('Totals object:', totals);
    console.log('Looking for hard_costs at totals.hard_costs:', totals?.hard_costs);
    console.log('Looking for soft_costs at totals.soft_costs:', totals?.soft_costs);
    console.log('Looking for total_project_cost at totals.total_project_cost:', totals?.total_project_cost);
    console.log('=== END MAPPER TRACE ===');
    
    // Extract financial metrics with proper paths - backend uses 'npv' not 'ten_year_npv'
    const roi = this.extractROI(returnMetrics);
    const npv = safeGet(returnMetrics, 'npv', 0);
    const irr = safeGet(returnMetrics, 'irr', 0);
    const paybackPeriod = this.extractPaybackPeriod(returnMetrics, calculations);
    const dscr = safeGet(debtMetrics, 'calculated_dscr', 1.0);
    
    // Extract revenue metrics - pass calculations to include roi_analysis
    const annualRevenue = this.extractAnnualRevenue(returnMetrics, projectInfo, calculations);
    const noi = safeGet(returnMetrics, 'estimated_annual_noi', 0) || 
                safeGet(ownership, 'noi', 0);
    const operatingMargin = operationalEfficiency?.operating_margin || 
                           safeGet(ownership, 'operational_efficiency.operating_margin', 0.6);
    
    // Extract investment analysis
    const backendFeasible = safeGet(returnMetrics, 'feasible', undefined);
    const fallbackFeasible = roi >= 0.08 && npv > 0;
    const hasFinancialSignals = !!roi || !!npv;
    const feasible = typeof backendFeasible === 'boolean'
      ? backendFeasible
      : hasFinancialSignals
        ? fallbackFeasible
        : undefined;
    const investmentDecision = feasible === undefined ? 'PENDING' : feasible ? 'GO' : 'NO-GO';
    
    // Extract unit metrics
    const totalCost = safeGet(totals, 'total_project_cost', 0);
    const unitLabel = safeGet(projectInfo, 'unit_label', safeGet(calculations, 'unit_label', 'Units'));
    const unitType = safeGet(projectInfo, 'unit_type', safeGet(calculations, 'unit_type', 'units'));
    
    // Extract operational metrics
    const breakEvenOccupancy = safeGet(investmentAnalysis, 'breakeven_metrics.occupancy', 0.85);
    const targetOccupancy = safeGet(projectInfo, 'target_occupancy', 0.93);
    const requiredRent = safeGet(investmentAnalysis, 'breakeven_metrics.required_rent', 0);
    
    // Extract departments with fallback
    const departments = this.extractDepartments(calculations, ownership);
    
    // Get operational metrics from backend (already formatted for display)
    const operationalMetrics = ownership?.operational_metrics || 
                              calculations?.operational_metrics ||
                              { staffing: [], revenue: {}, kpis: [] };
    const perUnitMetrics = operationalMetrics?.per_unit ||
                           ownership?.operational_metrics?.per_unit ||
                           calculations?.operational_metrics?.per_unit ||
                           {};
    const sensitivityAnalysis = ownership?.sensitivity_analysis || {};
    const sensitivityBase = sensitivityAnalysis.base || {};
    const sensitivityRevenueUp = sensitivityAnalysis.revenue_up_10 || {};
    const sensitivityRevenueDown = sensitivityAnalysis.revenue_down_10 || {};
    const sensitivityCostUp = sensitivityAnalysis.cost_up_10 || {};
    const sensitivityCostDown = sensitivityAnalysis.cost_down_10 || {};
    const sensitivityScenarios = Array.isArray(sensitivityAnalysis.scenarios)
      ? sensitivityAnalysis.scenarios
      : null;
    if (sensitivityScenarios && calculations && typeof calculations === 'object') {
      const existingSensitivityAnalysis =
        calculations.sensitivity_analysis && typeof calculations.sensitivity_analysis === 'object'
          ? calculations.sensitivity_analysis
          : {};
      calculations.sensitivity_analysis = {
        ...existingSensitivityAnalysis,
        scenarios: sensitivityScenarios,
      };
    }
    
    // Extract metrics for backward compatibility
    const staffingMetrics = operationalMetrics.staffing || [];
    const revenueMetrics = operationalMetrics.revenue || {};
    const kpis = operationalMetrics.kpis || [];

    // Consolidated unit/per-unit metrics using backend payload first
    const backendUnits = typeof perUnitMetrics.units === 'number' ? perUnitMetrics.units : undefined;
    const fallbackUnitCount = this.extractUnitCount(projectInfo, parsedInput);
    const unitCount = backendUnits && backendUnits > 0 ? backendUnits : fallbackUnitCount;
    const backendCostPerUnit = typeof perUnitMetrics.cost_per_unit === 'number' ? perUnitMetrics.cost_per_unit : undefined;
    const backendAnnualRevenuePerUnit = typeof perUnitMetrics.annual_revenue_per_unit === 'number'
      ? perUnitMetrics.annual_revenue_per_unit
      : undefined;
    const backendMonthlyRevenuePerUnit = typeof perUnitMetrics.monthly_revenue_per_unit === 'number'
      ? perUnitMetrics.monthly_revenue_per_unit
      : undefined;
    const fallbackCostPerUnit = safeGet(projectInfo, 'cost_per_unit', 0);
    const fallbackProjectRevenuePerUnit = safeGet(projectInfo, 'revenue_per_unit', 0);
    const fallbackOperationalRevenuePerUnit = safeGet(operationalEfficiency, 'revenue_per_unit', 0);
    const annualRevenuePerUnit =
      (typeof backendAnnualRevenuePerUnit === 'number' ? backendAnnualRevenuePerUnit : undefined) ??
      (typeof fallbackProjectRevenuePerUnit === 'number' && fallbackProjectRevenuePerUnit > 0 ? fallbackProjectRevenuePerUnit : undefined) ??
      (typeof fallbackOperationalRevenuePerUnit === 'number' && fallbackOperationalRevenuePerUnit > 0 ? fallbackOperationalRevenuePerUnit : undefined) ??
      (unitCount > 0 ? annualRevenue / unitCount : 0);
    const revenuePerUnit = annualRevenuePerUnit;
    const costPerUnit =
      backendCostPerUnit ??
      (typeof fallbackCostPerUnit === 'number' && fallbackCostPerUnit > 0 ? fallbackCostPerUnit : undefined) ??
      (totalCost / Math.max(unitCount, 1));
    const monthlyRevenuePerUnit =
      backendMonthlyRevenuePerUnit ??
      (annualRevenuePerUnit > 0 ? annualRevenuePerUnit / 12 : 0);
    
    // Extract core project data
    const squareFootage = safeGet(parsedInput, 'square_footage', 0);
    const costPerSF = safeGet(totals, 'cost_per_sf', 0);
    const derivedCostPerSf =
      totalCost > 0 && squareFootage > 0
        ? totalCost / squareFootage
        : (typeof costPerSF === 'number' ? costPerSF : 0);
    const marketFactor =
      typeof modifiers?.market_factor === 'number' &&
      Number.isFinite(modifiers.market_factor) &&
      modifiers.market_factor > 0
        ? modifiers.market_factor
        : undefined;
    const marketCostPerSF =
      typeof marketFactor === 'number'
        ? derivedCostPerSf / marketFactor
        : undefined;
    const costPerSFDeltaPct =
      typeof marketCostPerSF === 'number' &&
      marketCostPerSF !== 0
        ? ((derivedCostPerSf - marketCostPerSF) / marketCostPerSF) * 100
        : undefined;
    const profileMarketCapRate = typeof profile?.market_cap_rate === 'number' ? profile.market_cap_rate : null;
    const profileTargetYield = typeof profile?.target_yield === 'number' ? profile.target_yield : undefined;
    const profileTargetDscr = typeof profile?.target_dscr === 'number' ? profile.target_dscr : undefined;
    const targetYieldValue = profileTargetYield;
    const debtTargetDscrValue = typeof debtMetrics?.target_dscr === 'number' ? debtMetrics.target_dscr : undefined;
    const targetDscrValue = debtTargetDscrValue ?? profileTargetDscr;
    const marketCapRateValue = typeof ownership?.market_cap_rate === 'number'
      ? ownership.market_cap_rate
      : profileMarketCapRate;

    const pickPositiveNumber = (...values: Array<unknown>): number | undefined => {
      for (const value of values) {
        const num = typeof value === 'number' ? value : Number(value);
        if (Number.isFinite(num) && num > 0) {
          return num;
        }
      }
      return undefined;
    };

    const resolvedSquareFootage =
      typeof squareFootage === 'number' && squareFootage > 0
        ? squareFootage
        : pickPositiveNumber(
            totals?.square_footage,
            calculations?.square_footage,
            projectInfo?.square_footage,
            parsedInputRaw?.square_footage
          );

    const resolvedTotalCost =
      typeof totalCost === 'number' && totalCost > 0
        ? totalCost
        : pickPositiveNumber(
            totals?.total_project_cost,
            calculations?.total_project_cost,
            calculations?.total_cost
          );

    const resolvedAnnualRevenue =
      typeof annualRevenue === 'number' && annualRevenue > 0
        ? annualRevenue
        : pickPositiveNumber(revenueAnalysis?.annual_revenue, projectInfo?.annual_revenue);

    const resolvedNoi =
      typeof noi === 'number' && noi > 0
        ? noi
        : pickPositiveNumber(returnMetrics?.estimated_annual_noi, ownership?.noi);

    const toFiniteNumber = (value: unknown): number | undefined => {
      if (typeof value === 'number' && Number.isFinite(value)) {
        return value;
      }
      const parsed = Number(value);
      return Number.isFinite(parsed) ? parsed : undefined;
    };

    const hotelRooms =
      toFiniteNumber(calculations?.rooms) ??
      toFiniteNumber(calculations?.room_count) ??
      toFiniteNumber(calculations?.hotel_rooms) ??
      toFiniteNumber(calculations?.hospitality_rooms) ??
      toFiniteNumber(projectInfo?.rooms) ??
      undefined;
    const hotelAdr =
      toFiniteNumber(calculations?.adr) ??
      toFiniteNumber(calculations?.average_daily_rate) ??
      toFiniteNumber(calculations?.hotel_adr) ??
      toFiniteNumber(calculations?.hospitality_adr) ??
      toFiniteNumber(projectInfo?.adr) ??
      undefined;
    let hotelOccupancy =
      toFiniteNumber(calculations?.occupancy) ??
      toFiniteNumber(calculations?.hotel_occupancy) ??
      toFiniteNumber(calculations?.hospitality_occupancy) ??
      toFiniteNumber(calculations?.occ) ??
      toFiniteNumber(projectInfo?.occupancy_rate) ??
      undefined;
    if (typeof hotelOccupancy === 'number' && hotelOccupancy > 1 && hotelOccupancy <= 100) {
      hotelOccupancy = hotelOccupancy / 100;
    }
    let hotelRevpar =
      toFiniteNumber(calculations?.revpar) ??
      toFiniteNumber(calculations?.hotel_revpar) ??
      toFiniteNumber(calculations?.hospitality_revpar) ??
      toFiniteNumber(projectInfo?.revpar) ??
      undefined;
    if ((hotelRevpar === undefined || hotelRevpar === 0) && typeof hotelAdr === 'number' && typeof hotelOccupancy === 'number') {
      hotelRevpar = hotelAdr * hotelOccupancy;
    }
    const hotelTotalCostOverride =
      toFiniteNumber(calculations?.total_project_cost) ??
      toFiniteNumber(calculations?.total_cost) ??
      toFiniteNumber(calculations?.investment_required) ??
      toFiniteNumber(calculations?.hotel_total_cost) ??
      toFiniteNumber(analysis?.total_project_cost) ??
      toFiniteNumber(analysis?.total_cost) ??
      toFiniteNumber(analysis?.investment_required) ??
      undefined;
    const hotelCostPerKey =
      toFiniteNumber(calculations?.cost_per_key) ??
      toFiniteNumber(calculations?.hotel_cost_per_key) ??
      (
        typeof hotelRooms === 'number' &&
        hotelRooms > 0 &&
        typeof hotelTotalCostOverride === 'number' &&
        hotelTotalCostOverride > 0
          ? hotelTotalCostOverride / hotelRooms
          : undefined
      );

    const hospitalityFacilityMetrics: FacilityMetrics | undefined = isHospitalityFacility
      ? {
          rooms: hotelRooms,
          adr: hotelAdr,
          occupancy: hotelOccupancy,
          revpar: hotelRevpar,
          costPerKey: hotelCostPerKey,
        }
      : undefined;
    const officeBuildingSize =
      toFiniteNumber(calculations?.total_gross_sf) ??
      toFiniteNumber(calculations?.total_building_area) ??
      toFiniteNumber(calculations?.square_footage) ??
      toFiniteNumber(parsedInput?.square_footage) ??
      toFiniteNumber(projectInfo?.square_footage) ??
      undefined;
    const officeTotalCost =
      toFiniteNumber(calculations?.total_project_cost) ??
      toFiniteNumber(calculations?.total_cost) ??
      toFiniteNumber(calculations?.investment_required) ??
      undefined;
    const officeRentPerSf =
      toFiniteNumber(calculations?.rent_per_sf) ??
      toFiniteNumber(calculations?.office_rent_per_sf) ??
      toFiniteNumber(ownership?.rent_per_sf) ??
      undefined;
    const officeNoiPerSf =
      toFiniteNumber(calculations?.noi_per_sf) ??
      toFiniteNumber(calculations?.office_noi_per_sf) ??
      toFiniteNumber(ownership?.noi_per_sf) ??
      undefined;
    const officeCostPerSf =
      typeof officeBuildingSize === 'number' &&
      officeBuildingSize > 0 &&
      typeof officeTotalCost === 'number' &&
      officeTotalCost > 0
        ? officeTotalCost / officeBuildingSize
        : undefined;
    const officeFacilityMetrics: FacilityMetrics | undefined = isOfficeFacility
      ? {
          buildingSize: officeBuildingSize,
          costPerSf: officeCostPerSf,
          revenuePerSf: officeRentPerSf,
          noiPerSf: officeNoiPerSf,
          officeRentPerSf,
          officeNoiPerSf
        }
      : undefined;

    const requiredNoiResolved =
      toFiniteNumber(calculations?.revenue_requirements?.required_value) ??
      toFiniteNumber(ownership?.revenue_requirements?.required_value) ??
      (typeof totalCost === 'number' && typeof targetYieldValue === 'number'
        ? totalCost * targetYieldValue
        : undefined);
    const currentNoiResolved =
      typeof noi === 'number' && Number.isFinite(noi)
        ? noi
        : toFiniteNumber(returnMetrics?.estimated_annual_noi);
    const hospitalityRequiredNoiPerKey =
      isHospitalityFacility && typeof hotelRooms === 'number' && hotelRooms > 0 && typeof requiredNoiResolved === 'number'
        ? requiredNoiResolved / hotelRooms
        : undefined;
    const hospitalityCurrentNoiPerKey =
      isHospitalityFacility && typeof hotelRooms === 'number' && hotelRooms > 0 && typeof currentNoiResolved === 'number'
        ? currentNoiResolved / hotelRooms
        : undefined;
    const hospitalityCurrentRevpar =
      isHospitalityFacility && typeof hotelRevpar === 'number'
        ? hotelRevpar
        : isHospitalityFacility && typeof hotelAdr === 'number' && typeof hotelOccupancy === 'number'
          ? hotelAdr * hotelOccupancy
          : undefined;
    let hospitalityRequiredRevpar =
      isHospitalityFacility
        ? toFiniteNumber(calculations?.required_revpar ?? calculations?.hotel_required_revpar)
        : undefined;
    const hospitalityMargin = typeof operatingMargin === 'number' && operatingMargin > 0 ? operatingMargin : undefined;
    if (
      isHospitalityFacility &&
      hospitalityRequiredRevpar === undefined &&
      typeof requiredNoiResolved === 'number' &&
      typeof hospitalityMargin === 'number' &&
      typeof hotelRooms === 'number' &&
      hotelRooms > 0
    ) {
      hospitalityRequiredRevpar = (requiredNoiResolved / hospitalityMargin) / (hotelRooms * 365);
    }
    let impliedAdrForTargetRevpar: number | undefined;
    let impliedOccupancyForTargetRevpar: number | undefined;
    if (isHospitalityFacility && typeof hospitalityRequiredRevpar === 'number') {
      if (typeof hotelOccupancy === 'number' && hotelOccupancy > 0) {
        impliedAdrForTargetRevpar = hospitalityRequiredRevpar / hotelOccupancy;
      }
      if (typeof hotelAdr === 'number' && hotelAdr > 0) {
        impliedOccupancyForTargetRevpar = hospitalityRequiredRevpar / hotelAdr;
      }
    }

    const industrialFacilityMetrics: FacilityMetrics | undefined = isIndustrialFacility
      ? {
          buildingSize: resolvedSquareFootage,
          costPerSf:
            resolvedSquareFootage && resolvedTotalCost
              ? resolvedTotalCost / resolvedSquareFootage
              : undefined,
          revenuePerSf:
            resolvedSquareFootage && resolvedAnnualRevenue
              ? resolvedAnnualRevenue / resolvedSquareFootage
              : undefined,
          noiPerSf:
            resolvedSquareFootage && resolvedNoi ? resolvedNoi / resolvedSquareFootage : undefined,
        }
      : undefined;

    const facilityMetricsPayload = calculations?.facility_metrics;
    const payloadUnits = toFiniteNumber(
      facilityMetricsPayload?.units ??
      facilityMetricsPayload?.scan_rooms ??
      facilityMetricsPayload?.scanRooms
    );
    const payloadCostPerUnit = toFiniteNumber(
      facilityMetricsPayload?.cost_per_unit ?? facilityMetricsPayload?.costPerUnit
    );
    const payloadRevenuePerUnit = toFiniteNumber(
      facilityMetricsPayload?.revenue_per_unit ?? facilityMetricsPayload?.revenuePerUnit
    );
    const payloadMonthlyRevenuePerUnit = toFiniteNumber(
      facilityMetricsPayload?.monthly_revenue_per_unit ?? facilityMetricsPayload?.monthlyRevenuePerUnit
    );
    const payloadUnitLabel =
      typeof facilityMetricsPayload?.unit_label === 'string'
        ? facilityMetricsPayload.unit_label
        : undefined;
    const restaurantFacilityMetrics: FacilityMetrics | undefined = isRestaurantFacility
      ? (() => {
          const metricEntries = Array.isArray(facilityMetricsPayload?.metrics)
            ? facilityMetricsPayload?.metrics
            : [];
          const metricMap: Record<string, number | undefined> = {};
          for (const entry of metricEntries) {
            const id = typeof entry?.id === 'string' ? entry.id : '';
            if (!id) {
              continue;
            }
            const numericValue = toFiniteNumber(entry?.value);
            if (numericValue !== undefined) {
              metricMap[id] = numericValue;
            }
          }
          const salesPerSfValue =
            metricMap['sales_per_sf'] ??
            (typeof resolvedSquareFootage === 'number' &&
            resolvedSquareFootage > 0 &&
            typeof resolvedAnnualRevenue === 'number'
              ? resolvedAnnualRevenue / resolvedSquareFootage
              : undefined);
          const noiPerSfValue =
            metricMap['noi_per_sf'] ??
            (typeof resolvedSquareFootage === 'number' &&
            resolvedSquareFootage > 0 &&
            typeof resolvedNoi === 'number'
              ? resolvedNoi / resolvedSquareFootage
              : undefined);
          const costPerSfValue =
            metricMap['cost_per_sf'] ??
            (typeof resolvedSquareFootage === 'number' &&
            resolvedSquareFootage > 0 &&
            typeof resolvedTotalCost === 'number'
              ? resolvedTotalCost / resolvedSquareFootage
              : undefined);
          if (
            salesPerSfValue === undefined &&
            noiPerSfValue === undefined &&
            costPerSfValue === undefined
          ) {
            return undefined;
          }
          return {
            type: 'restaurant',
            restaurantSalesPerSf: salesPerSfValue,
            restaurantNoiPerSf: noiPerSfValue,
            restaurantCostPerSf: costPerSfValue,
            revenuePerSf: salesPerSfValue,
            noiPerSf: noiPerSfValue,
            costPerSf: costPerSfValue,
            entries: metricEntries.length > 0 ? metricEntries : undefined,
          };
        })()
      : undefined;

    const standardFacilityMetrics: FacilityMetrics | undefined = !isIndustrialFacility && !isRestaurantFacility
      ? {
          units:
            payloadUnits ??
            (unitCount > 0 ? unitCount : undefined),
          costPerUnit:
            payloadCostPerUnit ??
            (typeof costPerUnit === 'number' ? costPerUnit : undefined),
          revenuePerUnit:
            payloadRevenuePerUnit ??
            (typeof revenuePerUnit === 'number' ? revenuePerUnit : undefined),
          monthlyRevenuePerUnit:
            payloadMonthlyRevenuePerUnit ??
            (typeof payloadRevenuePerUnit === 'number'
              ? payloadRevenuePerUnit / 12
              : typeof monthlyRevenuePerUnit === 'number'
                ? monthlyRevenuePerUnit
                : undefined),
          unitLabel: payloadUnitLabel ?? unitLabel,
        }
      : undefined;

    const facilityMetrics =
      restaurantFacilityMetrics ??
      hospitalityFacilityMetrics ??
      officeFacilityMetrics ??
      industrialFacilityMetrics ??
      standardFacilityMetrics;
    const revenueRequirementsTotalSf =
      officeBuildingSize ??
      resolvedSquareFootage ??
      squareFootage;
    let officeRequiredNoiPerSf: number | undefined;
    let officeCurrentNoiPerSf: number | undefined;
    if (
      isOfficeFacility &&
      typeof revenueRequirementsTotalSf === 'number' &&
      revenueRequirementsTotalSf > 0
    ) {
      if (typeof requiredNoiResolved === 'number') {
        officeRequiredNoiPerSf = requiredNoiResolved / revenueRequirementsTotalSf;
      }
      if (typeof currentNoiResolved === 'number') {
        officeCurrentNoiPerSf = currentNoiResolved / revenueRequirementsTotalSf;
      }
    }
    
    return {
      roi,
      npv,
      irr,
      paybackPeriod,
      dscr,
      annualRevenue,
      monthlyRevenue: safeGet(operationalEfficiency, 'monthly_revenue', 0) || 
                     safeGet(projectInfo, 'monthly_revenue', 0) || 
                     (annualRevenue / 12),
      noi,
      operatingMargin,
      operatingExpenses: typeof operatingExpensesValue === 'number' ? operatingExpensesValue : 0,
      camCharges: typeof camChargesValue === 'number' ? camChargesValue : 0,
      yieldOnCost: typeof ownership?.yield_on_cost === 'number' ? ownership.yield_on_cost : 0,
      marketCapRate: marketCapRateValue,
      capRateSpreadBps: typeof ownership?.cap_rate_spread_bps === 'number' ? ownership.cap_rate_spread_bps : null,
      targetYield: targetYieldValue,
      targetDscr: targetDscrValue,
      investmentDecision,
      feasible,
      decisionReason: investmentAnalysis.summary || investmentAnalysis.reason || this.generateDecisionReason(roi, npv, dscr),
      suggestions: Array.isArray(investmentAnalysis.suggestions) ? investmentAnalysis.suggestions : [],
      improvementsNeeded: Array.isArray(investmentAnalysis.improvements_needed) ? investmentAnalysis.improvements_needed : [],
      failedCriteria: Array.isArray(investmentAnalysis.failed_criteria) ? investmentAnalysis.failed_criteria : [],
      metricsTable: Array.isArray(investmentAnalysis.metrics_table) ? investmentAnalysis.metrics_table : [],
      feasibilityScore: investmentAnalysis.feasibility_score,
      unitCount,
      unitLabel,
      unitType,
      revenuePerUnit,
      costPerUnit,
      units: unitCount > 0 ? unitCount : undefined,
      annualRevenuePerUnit,
      monthlyRevenuePerUnit,
      breakEvenOccupancy,
      targetOccupancy,
      requiredRent,
      facilityMetrics,
      projectTimeline: rawTimeline
        ? {
            groundbreaking: rawTimeline.groundbreaking,
            structureComplete: rawTimeline.structure_complete,
            substantialCompletion: rawTimeline.substantial_completion,
            grandOpening: rawTimeline.grand_opening,
          }
        : undefined,
      departments,
      staffingMetrics,
      revenueMetrics,
      kpis,
      totalProjectCost: totalCost,
      constructionCost: safeGet(totals, 'hard_costs', 0),
      softCosts: safeGet(totals, 'soft_costs', 0),
      costPerSF,
      costPerSf: derivedCostPerSf,
      marketCostPerSF,
      marketCostPerSf: marketCostPerSF,
      costPerSFDeltaPct,
      costPerSfDeltaPct: costPerSFDeltaPct,
      requiredNoiPerKey: isHospitalityFacility ? hospitalityRequiredNoiPerKey : undefined,
      currentNoiPerKey: isHospitalityFacility ? hospitalityCurrentNoiPerKey : undefined,
      requiredRevpar: isHospitalityFacility ? hospitalityRequiredRevpar : undefined,
      currentRevpar: isHospitalityFacility ? hospitalityCurrentRevpar : undefined,
      impliedAdrForTargetRevpar: isHospitalityFacility ? impliedAdrForTargetRevpar : undefined,
      impliedOccupancyForTargetRevpar: isHospitalityFacility ? impliedOccupancyForTargetRevpar : undefined,
      requiredNoiPerSf: isOfficeFacility ? officeRequiredNoiPerSf : undefined,
      currentNoiPerSf: isOfficeFacility ? officeCurrentNoiPerSf : undefined,
      squareFootage,
      buildingType: safeGet(parsedInput, 'building_type', 'office'),
      buildingSubtype: safeGet(parsedInput, 'building_subtype', safeGet(parsedInput, 'subtype', 'standard')),
      location: safeGet(parsedInput, 'location', 'Nashville'),
      floors: safeGet(parsedInput, 'floors', 1),
      constructionCostBuildUp: Array.isArray(calculations?.construction_costs?.cost_build_up)
        ? calculations.construction_costs.cost_build_up
        : [],
      finishLevel,
      finishLevelSource,
      costFactor,
      revenueFactor,
      yieldGapBps: typeof ownership.yield_gap_bps === 'number' ? ownership.yield_gap_bps : undefined,
      breakEvenOccupancyForTargetYield:
        typeof ownership.break_even_occupancy_for_target_yield === 'number'
          ? ownership.break_even_occupancy_for_target_yield
          : undefined,
      sensitivity: {
        baseYieldOnCost:
          typeof sensitivityBase.yield_on_cost === 'number' ? sensitivityBase.yield_on_cost : undefined,
        revenueUp10YieldOnCost:
          typeof sensitivityRevenueUp.yield_on_cost === 'number' ? sensitivityRevenueUp.yield_on_cost : undefined,
        revenueDown10YieldOnCost:
          typeof sensitivityRevenueDown.yield_on_cost === 'number' ? sensitivityRevenueDown.yield_on_cost : undefined,
        costUp10YieldOnCost:
          typeof sensitivityCostUp.yield_on_cost === 'number' ? sensitivityCostUp.yield_on_cost : undefined,
        costDown10YieldOnCost:
          typeof sensitivityCostDown.yield_on_cost === 'number' ? sensitivityCostDown.yield_on_cost : undefined,
        scenarios: sensitivityScenarios ?? undefined,
      }
    };
  }
  
  private static getEmptyDisplayData(): DisplayData {
    return {
      roi: 0,
      npv: 0,
      irr: 0,
      paybackPeriod: 0,
      dscr: 1.0,
      annualRevenue: 0,
      monthlyRevenue: 0,
      noi: 0,
      operatingMargin: 0,
      operatingExpenses: 0,
      camCharges: 0,
      yieldOnCost: 0,
      marketCapRate: null,
      capRateSpreadBps: null,
      targetYield: undefined,
      targetDscr: undefined,
      investmentDecision: 'PENDING',
      feasible: undefined,
      decisionReason: 'Awaiting analysis...',
      suggestions: [],
      improvementsNeeded: [],
      unitCount: 0,
      unitLabel: 'Units',
      unitType: 'units',
      revenuePerUnit: 0,
      costPerUnit: 0,
      units: 0,
      annualRevenuePerUnit: 0,
      monthlyRevenuePerUnit: 0,
      breakEvenOccupancy: 0,
      targetOccupancy: 0,
      requiredRent: 0,
      facilityMetrics: undefined,
      departments: [],
      staffingMetrics: [],
      revenueMetrics: {},
      kpis: [],
      yieldGapBps: undefined,
      breakEvenOccupancyForTargetYield: undefined,
      sensitivity: {
        baseYieldOnCost: undefined,
        revenueUp10YieldOnCost: undefined,
        revenueDown10YieldOnCost: undefined,
        costUp10YieldOnCost: undefined,
        costDown10YieldOnCost: undefined,
        scenarios: undefined,
      },
      totalProjectCost: 0,
      constructionCost: 0,
      softCosts: 0,
      costPerSF: 0,
      costPerSf: 0,
      marketCostPerSF: undefined,
      marketCostPerSf: undefined,
      costPerSFDeltaPct: undefined,
      costPerSfDeltaPct: undefined,
      impliedAdrForTargetRevpar: undefined,
      impliedOccupancyForTargetRevpar: undefined,
      squareFootage: 0,
      buildingType: '',
      buildingSubtype: '',
      location: '',
      floors: 1,
      constructionCostBuildUp: [],
      finishLevel: 'Standard',
      finishLevelSource: 'default',
      costFactor: undefined,
      revenueFactor: undefined
    };
  }
  
  private static extractROI(returnMetrics: any): number {
    // Try multiple possible locations for ROI
    return safeGet(returnMetrics, 'estimated_roi', 0) ||
           safeGet(returnMetrics, 'cash_on_cash_return', 0) ||
           safeGet(returnMetrics, 'roi', 0);
  }
  
  private static extractPaybackPeriod(returnMetrics: any, calculations: any): number {
    // Try multiple locations and calculate if needed
    const directValue = safeGet(returnMetrics, 'payback_period', 0);
    if (directValue && directValue !== Infinity && directValue < 999) return directValue;
    
    // Calculate from NOI if available
    const noi = safeGet(returnMetrics, 'estimated_annual_noi', 0);
    const totalCost = safeGet(calculations, 'totals.total_project_cost', 0);
    
    if (noi > 0 && totalCost > 0) {
      const period = totalCost / noi;
      return period < 999 ? period : 999;
    }
    
    return 0;
  }
  
  private static extractAnnualRevenue(returnMetrics: any, projectInfo: any, calculations: any): number {
    // Try multiple possible locations including roi_analysis path
    const roiAnalysis = calculations?.roi_analysis || {};
    const financialMetrics = roiAnalysis?.financial_metrics || {};
    const ownership = calculations?.ownership_analysis || {};
    
    console.log('=== EXTRACT ANNUAL REVENUE DEBUG ===');
    console.log('calculations passed:', calculations);
    console.log('roi_analysis found:', !!roiAnalysis);
    console.log('financial_metrics found:', !!financialMetrics);
    console.log('annual_revenue in financial_metrics:', financialMetrics?.annual_revenue);
    console.log('=== END EXTRACT DEBUG ===');
    
    return financialMetrics?.annual_revenue ||
           safeGet(ownership, 'annual_revenue', 0) ||
           safeGet(returnMetrics, 'annual_revenue', 0) ||
           safeGet(projectInfo, 'annual_revenue', 0) ||
           safeGet(returnMetrics, 'estimated_annual_revenue', 0) ||
           (safeGet(returnMetrics, 'estimated_annual_noi', 0) / 0.6); // Derive from NOI if needed
  }
  
  private static extractUnitCount(projectInfo: any, parsedInput: any): number {
    // Try backend first, then calculate based on building type
    const backendCount = safeGet(projectInfo, 'unit_count', 0);
    if (backendCount > 0) return backendCount;
    
    const buildingType = safeGet(parsedInput, 'building_type', '');
    const squareFootage = safeGet(parsedInput, 'square_footage', 0);
    const subtype = safeGet(parsedInput, 'building_subtype', safeGet(parsedInput, 'subtype', ''));
    
    // Calculate based on building type
    switch (buildingType) {
      case 'multifamily': {
        // Vary by subtype
        let avgUnitSize = 950;
        if (subtype === 'luxury_apartments') avgUnitSize = 1100;
        else if (subtype === 'affordable_housing') avgUnitSize = 750;
        else if (subtype === 'student_housing') avgUnitSize = 650;
        else if (subtype === 'senior_living') avgUnitSize = 900;
        
        return Math.round(squareFootage / avgUnitSize);
      }
      case 'healthcare':
        return Math.round(squareFootage / 1333); // beds
      case 'educational':
        return Math.round(squareFootage / 900); // classrooms
      case 'office':
        return Math.max(1, Math.round(squareFootage / 15000)); // floors
      default:
        return 1;
    }
  }
  
  private static extractDepartments(calculations: any, ownership: any): any[] {
    // Try multiple locations for department data
    let departments = safeGet(ownership, 'department_allocation', []) ||
                     safeGet(calculations, 'department_allocation', []);
    
    if (!Array.isArray(departments)) departments = [];
    
    // Ensure all departments have required fields
    return departments.map(dept => ({
      name: dept.name || 'Department',
      percent: dept.percent || 0,
      amount: dept.amount || 0,
      square_footage: dept.square_footage || dept.squareFootage || 0,
      cost_per_sf: dept.cost_per_sf || dept.costPerSF || 0,
      gradient: dept.gradient || 'from-blue-600 to-blue-700',
      icon_name: dept.icon_name || 'Building'
    }));
  }
  
  private static generateDecisionReason(roi: number, npv: number, dscr: number): string {
    if (roi >= 0.08 && npv > 0 && dscr >= 1.25) {
      return 'Debt coverage and returns appear to meet underwriting targets, but confirm DSCR, NOI gap, and yield on cost before proceeding.';
    } else if (roi < 0.06) {
      return `ROI of ${(roi * 100).toFixed(1)}% is below the 8% minimum threshold.`;
    } else if (npv < 0) {
      return 'Negative NPV indicates project will not generate sufficient returns over 10 years.';
    } else if (dscr < 1.25) {
      return `DSCR of ${dscr.toFixed(2)}x is below lender requirements of 1.25x minimum.`;
    }
    return 'Project is marginal. Consider optimization strategies to improve returns.';
  }
}
