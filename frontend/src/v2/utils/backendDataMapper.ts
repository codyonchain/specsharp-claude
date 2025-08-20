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
  decisionReason: string;
  suggestions: string[];
  
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
    const ownership = calculations?.ownership_analysis || {};
    const returnMetrics = ownership?.return_metrics || {};
    const debtMetrics = ownership?.debt_metrics || {};
    const investmentAnalysis = ownership?.investment_analysis || {};
    const projectInfo = ownership?.project_info || calculations?.project_info || {};
    const operationalMetrics = ownership?.operational_metrics || calculations?.operational_metrics || {};
    const parsedInput = analysis?.parsed_input || {};
    const totals = calculations?.totals || {};
    
    // Extract financial metrics with proper paths
    const roi = this.extractROI(returnMetrics);
    const npv = safeGet(returnMetrics, 'ten_year_npv', 0);
    const irr = safeGet(returnMetrics, 'irr', 0);
    const paybackPeriod = this.extractPaybackPeriod(returnMetrics, calculations);
    const dscr = safeGet(debtMetrics, 'calculated_dscr', 1.0);
    
    // Extract revenue metrics
    const annualRevenue = this.extractAnnualRevenue(returnMetrics, projectInfo, ownership);
    const noi = safeGet(returnMetrics, 'estimated_annual_noi', 0) || 
                safeGet(ownership, 'noi', 0);
    const operatingMargin = annualRevenue > 0 ? (noi / annualRevenue) : 0.6;
    
    // Extract investment analysis
    const investmentDecision = investmentAnalysis.decision || 
                               (roi >= 0.08 && npv > 0 ? 'GO' : 'NO-GO');
    
    // Extract unit metrics
    const unitCount = this.extractUnitCount(projectInfo, parsedInput);
    const unitLabel = safeGet(projectInfo, 'unit_label', 'Units');
    const unitType = safeGet(projectInfo, 'unit_type', 'units');
    const totalCost = safeGet(totals, 'total_project_cost', 0);
    const revenuePerUnit = annualRevenue / Math.max(unitCount, 1);
    const costPerUnit = totalCost / Math.max(unitCount, 1);
    
    // Extract operational metrics
    const breakEvenOccupancy = safeGet(investmentAnalysis, 'breakeven_metrics.occupancy', 0.85);
    const targetOccupancy = safeGet(projectInfo, 'target_occupancy', 0.93);
    const requiredRent = safeGet(investmentAnalysis, 'breakeven_metrics.required_rent', 0);
    
    // Extract departments with fallback
    const departments = this.extractDepartments(calculations, ownership);
    
    // Extract staffing metrics
    const staffingMetrics = Array.isArray(operationalMetrics?.staffing) ? 
                           operationalMetrics.staffing : [];
    
    // Extract revenue metrics
    const revenueMetrics = operationalMetrics?.revenue || {};
    
    // Extract KPIs
    const kpis = Array.isArray(operationalMetrics?.kpis) ? 
                 operationalMetrics.kpis : [];
    
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
      monthlyRevenue: annualRevenue / 12,
      noi,
      operatingMargin,
      investmentDecision,
      decisionReason: investmentAnalysis.reason || this.generateDecisionReason(roi, npv, dscr),
      suggestions: Array.isArray(investmentAnalysis.suggestions) ? investmentAnalysis.suggestions : [],
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
      floors: safeGet(parsedInput, 'floors', 1)
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
      decisionReason: 'Awaiting analysis...',
      suggestions: [],
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
      floors: 1
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
  
  private static extractAnnualRevenue(returnMetrics: any, projectInfo: any, ownership: any): number {
    // Try multiple possible locations
    return safeGet(ownership, 'annual_revenue', 0) ||
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