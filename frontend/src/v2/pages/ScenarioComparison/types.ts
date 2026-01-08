// Use the existing Project type from v2/types
import { Project as V2Project } from '../../types';

// Extend the V2 Project type with additional fields we need
export interface Project extends V2Project {
  building_type?: string;
  subtype?: string;
  square_footage?: number;
  location?: string;
  project_class?: string;
  ownership_type?: string;
  floors?: number;
  total_cost?: number;
  cost_per_sqft?: number;
  scope_data?: any;
}

export interface Scenario {
  id: string;
  name: string;
  isBase?: boolean;
  building_type: string;
  subtype: string;
  square_footage: number;
  location: string;
  project_class: string;
  ownership_type: string;
  floors: number;
  special_features?: string[];
  modifications: Record<string, any>;
  totalCost: number;
  costPerSF: number;
}

export interface ComparisonResult {
  scenarios: Array<{
    scenario_name: string;
    project_info?: {
      building_type: string;
      subtype: string;
      square_footage: number;
      location: string;
      project_class: string;
    };
    totals?: {
      total_project_cost: number;
      cost_per_sf: number;
      hard_costs: number;
      soft_costs: number;
    };
    ownership_analysis?: {
      estimated_roi: number;
      payback_years?: number;
      dscr?: number;
      cash_on_cash_return?: number;
    };
    revenue_requirements?: {
      annual_revenue_required: number;
      monthly_revenue_required: number;
    };
    error?: string;
  }>;
  summary: {
    total_scenarios: number;
    successful_calculations: number;
    lowest_cost_scenario: string | null;
    highest_cost_scenario: string | null;
    cost_range: {
      min: number;
      max: number;
    };
  };
  timestamp: string;
}