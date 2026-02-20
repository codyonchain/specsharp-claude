/**
 * V2 Type Definitions
 * Single source of truth - matches backend exactly
 * NO divergence allowed
 */

// ============================================================================
// ENUMS - Must match backend exactly
// ============================================================================

export enum BuildingType {
  HEALTHCARE = 'healthcare',
  MULTIFAMILY = 'multifamily',
  OFFICE = 'office',
  RETAIL = 'retail',
  INDUSTRIAL = 'industrial',
  HOSPITALITY = 'hospitality',
  EDUCATIONAL = 'educational',
  CIVIC = 'civic',
  RECREATION = 'recreation',
  MIXED_USE = 'mixed_use',
  PARKING = 'parking',
  RESTAURANT = 'restaurant',
  SPECIALTY = 'specialty'
}

export enum ProjectClass {
  GROUND_UP = 'ground_up',
  ADDITION = 'addition',
  RENOVATION = 'renovation',
  TENANT_IMPROVEMENT = 'tenant_improvement'
}

export enum OwnershipType {
  FOR_PROFIT = 'for_profit',
  NON_PROFIT = 'non_profit',
  GOVERNMENT = 'government',
  PPP = 'public_private_partnership'
}

// ============================================================================
// BUILDING SUBTYPES - Complete mapping
// ============================================================================

export const BUILDING_SUBTYPES: Record<BuildingType, Array<{value: string, label: string}>> = {
  [BuildingType.HEALTHCARE]: [
    { value: 'hospital', label: 'Hospital' },
    { value: 'medical_office', label: 'Medical Office Building' },
    { value: 'urgent_care', label: 'Urgent Care Center' }
  ],
  [BuildingType.MULTIFAMILY]: [
    { value: 'luxury_apartments', label: 'Class A / Luxury Apartments' },
    { value: 'market_rate_apartments', label: 'Class B / Market Rate' },
    { value: 'affordable_housing', label: 'Affordable Housing' }
  ],
  [BuildingType.OFFICE]: [
    { value: 'class_a', label: 'Class A Office' },
    { value: 'class_b', label: 'Class B Office' }
  ],
  [BuildingType.RETAIL]: [
    { value: 'shopping_center', label: 'Shopping Center' },
    { value: 'big_box', label: 'Big Box Retail' }
  ],
  [BuildingType.INDUSTRIAL]: [
    { value: 'warehouse', label: 'Warehouse' },
    { value: 'distribution_center', label: 'Distribution Center' },
    { value: 'manufacturing', label: 'Manufacturing Facility' },
    { value: 'flex_space', label: 'Flex Space' },
    { value: 'cold_storage', label: 'Cold Storage' }
  ],
  [BuildingType.HOSPITALITY]: [
    { value: 'full_service_hotel', label: 'Full Service Hotel' },
    { value: 'limited_service_hotel', label: 'Limited Service Hotel' }
  ],
  [BuildingType.EDUCATIONAL]: [
    { value: 'elementary_school', label: 'Elementary School' },
    { value: 'middle_school', label: 'Middle School' },
    { value: 'high_school', label: 'High School' },
    { value: 'university', label: 'University' },
    { value: 'community_college', label: 'Community College' }
  ],
  [BuildingType.CIVIC]: [
    { value: 'government_building', label: 'Government Building' },
    { value: 'public_safety', label: 'Public Safety Facility' },
    { value: 'library', label: 'Library' },
    { value: 'community_center', label: 'Community Center' },
    { value: 'courthouse', label: 'Courthouse' }
  ],
  [BuildingType.RECREATION]: [
    { value: 'fitness_center', label: 'Fitness Center' },
    { value: 'sports_complex', label: 'Sports Complex' },
    { value: 'aquatic_center', label: 'Aquatic Center' },
    { value: 'recreation_center', label: 'Recreation Center' },
    { value: 'stadium', label: 'Stadium / Arena' }
  ],
  [BuildingType.MIXED_USE]: [
    { value: 'retail_residential', label: 'Retail with Residential' },
    { value: 'office_residential', label: 'Office with Residential' },
    { value: 'hotel_retail', label: 'Hotel with Retail' },
    { value: 'urban_mixed', label: 'Urban Mixed Use' },
    { value: 'transit_oriented', label: 'Transit-Oriented Development' }
  ],
  [BuildingType.PARKING]: [
    { value: 'surface_parking', label: 'Surface Parking' },
    { value: 'parking_garage', label: 'Parking Garage' },
    { value: 'underground_parking', label: 'Underground Parking' },
    { value: 'automated_parking', label: 'Automated Parking' }
  ],
  [BuildingType.RESTAURANT]: [
    { value: 'quick_service', label: 'Quick Service Restaurant' },
    { value: 'full_service', label: 'Full Service Restaurant' }
  ],
  [BuildingType.SPECIALTY]: [
    { value: 'data_center', label: 'Data Center' },
    { value: 'laboratory', label: 'Laboratory' },
    { value: 'self_storage', label: 'Self Storage' },
    { value: 'car_dealership', label: 'Car Dealership' },
    { value: 'broadcast_facility', label: 'Broadcast Facility' }
  ]
};

// ============================================================================
// API RESPONSE TYPES
// ============================================================================

export interface ParsedInput {
  building_type: BuildingType;
  subtype: string;
  square_footage: number;
  location: string;
  project_class: ProjectClass;
  floors: number;
  confidence: number;
}

export interface ConstructionCosts {
  base_cost_per_sf: number;
  class_multiplier: number;
  regional_multiplier: number;
  final_cost_per_sf: number;
  construction_total: number;
  equipment_total: number;
  special_features_total: number;
  special_features_breakdown?: Array<{
    id: string;
    cost_per_sf: number;
    total_cost: number;
    label: string;
  }>;
}

export interface RegionalContext {
  city?: string | null;
  state?: string | null;
  source?: string | null;
  multiplier: number;
  cost_factor?: number | null;
  market_factor?: number | null;
  location_display?: string | null;
}

export interface ProjectTotals {
  hard_costs: number;
  soft_costs: number;
  total_project_cost: number;
  cost_per_sf: number;
}

export interface TraceEntry {
  step: string;
  data: Record<string, any>;
  timestamp: string;
}

export interface OwnershipAnalysis {
  financing_sources: {
    debt_amount: number;
    equity_amount: number;
    philanthropy_amount: number;
    grants_amount: number;
    total_sources: number;
  };
  debt_metrics: {
    debt_rate: number;
    annual_debt_service: number;
    monthly_debt_service: number;
    target_dscr: number;
    calculated_dscr: number;
    dscr_meets_target: boolean;
  };
  return_metrics: {
    target_roi: number;
    estimated_annual_noi: number;
    cash_on_cash_return: number;
    feasible?: boolean;
  };
}

export interface CalculationResult {
  project_info: {
    building_type: string;
    subtype: string;
    display_name: string;
    project_class: string;
    square_footage: number;
    location: string;
    floors: number;
    typical_floors: number;
  };
  regional?: RegionalContext;
  regional_applied?: boolean;
  construction_costs: ConstructionCosts;
  trade_breakdown: Record<string, number>;
  scope_items?: Array<{
    trade: string;
    systems: Array<{
      name?: string;
      description?: string;
      quantity?: number;
      unit?: string;
      unit_cost?: number;
      total_cost?: number;
    }>;
  }>;
  soft_costs: Record<string, number>;
  totals: ProjectTotals;
  ownership_analysis?: OwnershipAnalysis;
  calculation_trace: TraceEntry[];
  timestamp: string;
}

export interface ProjectAnalysis {
  parsed_input: ParsedInput;
  calculations: CalculationResult;
  confidence: number;
  debug?: {
    engine_version: string;
    config_version: string;
    trace_count: number;
  };
}

// ============================================================================
// FRONTEND TYPES
// ============================================================================

export interface Project {
  id: string;
  name: string;
  description: string;
  analysis: ProjectAnalysis;
  created_at: string;
  updated_at: string;
  createdAt?: string; // For compatibility with Dashboard
  user_id: string;
  is_shared: boolean;
  share_token?: string;
}

export interface User {
  id: string;
  email: string;
  name: string;
  company?: string;
  role?: string;
}

export interface APIError {
  message: string;
  code?: string;
  status?: number;
  details?: any;
}

// ============================================================================
// FORM TYPES
// ============================================================================

export interface ProjectFormData {
  description: string;
  building_type?: BuildingType;
  subtype?: string;
  square_footage?: number;
  location?: string;
  project_class?: ProjectClass;
  floors?: number;
  ownership_type?: OwnershipType;
  special_features?: string[];
}

export interface ComparisonScenario {
  name: string;
  building_type: BuildingType;
  subtype: string;
  square_footage: number;
  location: string;
  project_class?: ProjectClass;
  ownership_type?: OwnershipType;
}

// ============================================================================
// UTILITY TYPES
// ============================================================================

export type LoadingState = 'idle' | 'loading' | 'success' | 'error';

export interface AsyncState<T> {
  data: T | null;
  loading: boolean;
  error: APIError | null;
}

// ============================================================================
// FINANCIAL REQUIREMENTS TYPES
// ============================================================================

export interface FinancialRequirementsMetric {
  label: string;
  value: string;
  status?: 'green' | 'yellow' | 'red';
  tooltip?: string;
}

export interface FinancialRequirementsSection {
  title: string;
  metrics: FinancialRequirementsMetric[];
}

export interface FinancialRequirements {
  primary_metrics: FinancialRequirementsSection;
  performance_targets: FinancialRequirementsSection;
  market_analysis: FinancialRequirementsSection;
}

// ============================================================================
// DEALSHIELD TYPES
// ============================================================================

export interface DealShieldControls {
  stress_band_pct: 10 | 7 | 5 | 3;
  anchor_total_project_cost: number | null;
  use_cost_anchor: boolean;
  anchor_annual_revenue: number | null;
  use_revenue_anchor: boolean;
}

export interface DecisionInsurancePrimaryControlVariable {
  tile_id?: string | null;
  label?: string | null;
  metric_ref?: string | null;
  impact_pct?: number | null;
  delta_cost?: number | null;
  severity?: 'Low' | 'Med' | 'High' | 'Unknown' | string | null;
}

export interface DecisionInsuranceFirstBreakCondition {
  scenario_id?: string | null;
  scenario_label?: string | null;
  break_metric?: string | null;
  operator?: string | null;
  threshold?: number | null;
  observed_value?: number | null;
  observed_value_pct?: number | null;
}

export interface DecisionInsuranceRankedLikelyWrongItem {
  id?: string | null;
  text?: string | null;
  why?: string | null;
  driver_tile_id?: string | null;
  impact_pct?: number | null;
  severity?: 'Low' | 'Med' | 'High' | 'Unknown' | string | null;
}

export interface DecisionInsuranceProvenanceEntry {
  status?: 'available' | 'unavailable' | string;
  reason?: string | null;
  band?: string | null;
  [key: string]: any;
}

export interface DecisionInsuranceFlexBandPolicy {
  tight_lt?: number;
  moderate_lt?: number;
  labels?: {
    tight?: string;
    moderate?: string;
    comfortable?: string;
  };
}

export interface DecisionInsuranceProvenance {
  enabled?: boolean;
  profile_id?: string | null;
  primary_control_variable?: DecisionInsuranceProvenanceEntry;
  first_break_condition?: DecisionInsuranceProvenanceEntry;
  flex_before_break_pct?: DecisionInsuranceProvenanceEntry;
  flex_before_break_bands?: DecisionInsuranceFlexBandPolicy;
  exposure_concentration_pct?: DecisionInsuranceProvenanceEntry;
  ranked_likely_wrong?: DecisionInsuranceProvenanceEntry;
  [key: string]: any;
}

export interface DealShieldDecisionInsuranceFields {
  primary_control_variable?: DecisionInsurancePrimaryControlVariable | null;
  first_break_condition?: DecisionInsuranceFirstBreakCondition | null;
  flex_before_break_pct?: number | null;
  flex_before_break_band?: string | null;
  exposure_concentration_pct?: number | null;
  ranked_likely_wrong?: DecisionInsuranceRankedLikelyWrongItem[];
  decision_insurance_provenance?: DecisionInsuranceProvenance;
}

export type DealShieldViewModel = Record<string, any> & Partial<DealShieldDecisionInsuranceFields>;
