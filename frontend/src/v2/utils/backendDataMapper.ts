/**
 * Maps backend data to frontend display fields
 * Single source of truth for where data lives in backend response
 */

import { safeGet } from './displayFormatters';

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
  
  // Operational metrics
  breakEvenOccupancy: number;
  targetOccupancy: number;
  requiredRent: number;
  
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
    
    const calculations = analysis?.calculations || {};
    
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
    const returnMetrics = ownership?.return_metrics || {};
    const debtMetrics = ownership?.debt_metrics || {};
    const investmentAnalysis = ownership?.investment_analysis || {};
    const projectInfo = ownership?.project_info || calculations?.project_info || calculations?.calculations?.project_info || {};
    // Backend sends operational_efficiency, not operational_metrics
    const operationalEfficiency = ownership?.operational_efficiency || calculations?.operational_efficiency || calculations?.calculations?.operational_efficiency || {};
    const parsedInput = analysis?.parsed_input || {};
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
    const fallbackCostFactor = typeof calculations?.modifiers?.cost_factor === 'number' ? calculations.modifiers.cost_factor : undefined;
    const fallbackRevenueFactor = typeof calculations?.modifiers?.revenue_factor === 'number' ? calculations.modifiers.revenue_factor : undefined;
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
    const unitCount = this.extractUnitCount(projectInfo, parsedInput);
    const unitLabel = safeGet(projectInfo, 'unit_label', 'Units');
    const unitType = safeGet(projectInfo, 'unit_type', 'units');
    const totalCost = safeGet(totals, 'total_project_cost', 0);
    const revenuePerUnit = safeGet(projectInfo, 'revenue_per_unit', 0) || 
                          safeGet(operationalEfficiency, 'revenue_per_unit', 0) || 
                          (annualRevenue / Math.max(unitCount, 1));
    const costPerUnit = safeGet(projectInfo, 'cost_per_unit', 0) || 
                       (totalCost / Math.max(unitCount, 1));
    
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
    
    // Extract metrics for backward compatibility
    const staffingMetrics = operationalMetrics.staffing || [];
    const revenueMetrics = operationalMetrics.revenue || {};
    const kpis = operationalMetrics.kpis || [];
    
    // Extract core project data
    const squareFootage = safeGet(parsedInput, 'square_footage', 0);
    const costPerSF = safeGet(totals, 'cost_per_sf', 0);
    
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
      breakEvenOccupancy,
      targetOccupancy,
      requiredRent,
      departments,
      staffingMetrics,
      revenueMetrics,
      kpis,
      totalProjectCost: totalCost,
      constructionCost: safeGet(totals, 'hard_costs', 0),
      softCosts: safeGet(totals, 'soft_costs', 0),
      costPerSF,
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
      revenueFactor
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
      breakEvenOccupancy: 0,
      targetOccupancy: 0,
      requiredRent: 0,
      departments: [],
      staffingMetrics: [],
      revenueMetrics: {},
      kpis: [],
      totalProjectCost: 0,
      constructionCost: 0,
      softCosts: 0,
      costPerSF: 0,
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
      return 'Project meets all investment criteria with strong returns and debt coverage.';
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
