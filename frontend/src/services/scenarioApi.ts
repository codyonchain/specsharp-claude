/**
 * API service for project scenario management
 */

import api from './api';

export interface ScenarioModification {
  parameter: string;
  original_value: any;
  new_value: any;
  cost_impact?: number;
  timeline_impact?: number;
  roi_impact?: number;
  impact_description?: string;
}

export interface ProjectScenario {
  id: string;
  project_id: number;
  name: string;
  description?: string;
  modifications: Record<string, any>;
  is_base: boolean;
  
  // Financial metrics
  total_cost: number;
  construction_cost: number;
  soft_costs: number;
  cost_per_sqft: number;
  roi: number;
  npv: number;
  irr: number;
  payback_period: number;
  dscr: number;
  
  // Revenue metrics
  annual_revenue: number;
  monthly_revenue: number;
  noi: number;
  
  // Building metrics
  square_footage: number;
  unit_count?: number;
  finish_level?: string;
  
  // Metadata
  created_at: string;
  updated_at: string;
}

export interface ScenarioComparison {
  comparison_name?: string;
  scenario_ids: string[];
  scenario_names: string[];
  
  // Metric comparisons
  metrics_comparison: Record<string, number[]>;
  winner_by_metric: Record<string, string>;
  
  // Delta analysis
  cost_deltas: Record<string, number>;
  roi_deltas: Record<string, number>;
  timeline_deltas: Record<string, number>;
  
  // Summary insights
  best_overall_scenario: string;
  best_roi_scenario: string;
  lowest_cost_scenario: string;
  fastest_payback_scenario: string;
  
  // Detailed comparisons
  metric_details: Array<{
    metric_name: string;
    values: number[];
    winner_scenario_id: string;
    winner_scenario_name: string;
    best_value: number;
    worst_value: number;
    delta_from_base: number[];
  }>;
}

export interface ModificationOptions {
  building_type: string;
  modification_options: Record<string, any>;
}

class ScenarioApi {
  /**
   * Create a new scenario
   */
  async createScenario(
    projectId: string,
    name: string,
    description: string,
    modifications: Record<string, any>
  ): Promise<ProjectScenario> {
    const response = await api.post(`/projects/${projectId}/scenarios`, {
      name,
      description,
      modifications
    });
    return response.data;
  }
  
  /**
   * Get all scenarios for a project
   */
  async listScenarios(projectId: string): Promise<ProjectScenario[]> {
    const response = await api.get(`/projects/${projectId}/scenarios`);
    return response.data;
  }
  
  /**
   * Get a specific scenario
   */
  async getScenario(scenarioId: string): Promise<ProjectScenario> {
    const response = await api.get(`/scenarios/${scenarioId}`);
    return response.data;
  }
  
  /**
   * Update a scenario
   */
  async updateScenario(
    scenarioId: string,
    updates: {
      name?: string;
      description?: string;
      modifications?: Record<string, any>;
    }
  ): Promise<ProjectScenario> {
    const response = await api.put(`/scenarios/${scenarioId}`, updates);
    return response.data;
  }
  
  /**
   * Delete a scenario
   */
  async deleteScenario(scenarioId: string): Promise<void> {
    await api.delete(`/scenarios/${scenarioId}`);
  }
  
  /**
   * Compare multiple scenarios
   */
  async compareScenarios(
    projectId: string,
    scenarioIds: string[],
    name?: string
  ): Promise<ScenarioComparison> {
    const response = await api.post(`/projects/${projectId}/compare`, {
      scenario_ids: scenarioIds,
      name
    });
    return response.data;
  }
  
  /**
   * Export scenario comparison
   */
  async exportComparison(
    projectId: string,
    scenarioIds: string[],
    format: 'pdf' | 'excel' | 'pptx',
    includeCharts: boolean = true,
    includeDetails: boolean = true
  ): Promise<{ data: string; content_type: string; filename: string }> {
    const response = await api.post(`/projects/${projectId}/export-comparison`, {
      scenario_ids: scenarioIds,
      format,
      include_charts: includeCharts,
      include_details: includeDetails
    });
    return response.data;
  }
  
  /**
   * Get modification options for a project's building type
   */
  async getModificationOptions(projectId: string): Promise<ModificationOptions> {
    const response = await api.get(`/projects/${projectId}/modification-options`);
    return response.data;
  }
}

export default new ScenarioApi();