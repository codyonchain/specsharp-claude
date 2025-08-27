/**
 * V2 API service for project scenario management
 * This handles scenarios for V2 projects that exist in localStorage
 */

import api from './api';

export interface V2ScenarioModification {
  square_footage?: number;
  finish_level?: string;
  parking_type?: string;
  floors?: number;
  project_classification?: string;
}

export interface V2Scenario {
  id: string;
  projectId: string;
  name: string;
  description: string;
  modifications: V2ScenarioModification;
  results: any;
  createdAt: string;
  isBase?: boolean;
}

class ScenarioV2Api {
  private STORAGE_KEY = 'specsharp_scenarios';

  /**
   * Get all scenarios from localStorage
   */
  private getAllScenarios(): Record<string, V2Scenario[]> {
    const stored = localStorage.getItem(this.STORAGE_KEY);
    return stored ? JSON.parse(stored) : {};
  }

  /**
   * Save scenarios to localStorage
   */
  private saveAllScenarios(scenarios: Record<string, V2Scenario[]>): void {
    localStorage.setItem(this.STORAGE_KEY, JSON.stringify(scenarios));
  }

  /**
   * Create a new scenario for a V2 project
   */
  async createScenario(
    projectId: string,
    name: string,
    description: string,
    modifications: V2ScenarioModification,
    baseProjectData?: any
  ): Promise<V2Scenario> {
    try {
      // Use provided baseProject data or get from localStorage
      let baseProject = baseProjectData;
      
      if (!baseProject) {
        const projectsStr = localStorage.getItem('specsharp_projects');
        const projects = projectsStr ? JSON.parse(projectsStr) : [];
        baseProject = projects.find((p: any) => p.id === projectId || p.project_id === projectId);
      }
      
      if (!baseProject) {
        throw new Error(`Project ${projectId} not found`);
      }

      // For V2 projects, calculate locally without API call to avoid auth issues
      // This uses the same calculation logic but runs client-side
      // Check all possible locations for the total cost
      const baseCost = baseProject.total_project_cost || 
                       baseProject.totalCost || 
                       baseProject.total_cost ||
                       baseProject.cost_breakdown?.total ||
                       baseProject.costBreakdown?.total ||
                       1000000;
      const baseSqft = baseProject.square_footage || 5000;
      const newSqft = modifications.square_footage || baseSqft;
      
      // Calculate base cost per square foot
      let costPerSqft = baseCost / baseSqft;
      
      // Apply finish level adjustments
      const finishMultipliers: Record<string, number> = {
        'economy': 0.85,
        'standard': 1.0,
        'premium': 1.15,
        'luxury': 1.30
      };
      costPerSqft *= finishMultipliers[modifications.finish_level?.toLowerCase() || 'standard'] || 1.0;
      
      // Apply parking adjustments
      const parkingMultipliers: Record<string, number> = {
        'none': 0.90,
        'surface': 1.0,
        'garage': 1.10,
        'underground': 1.20
      };
      costPerSqft *= parkingMultipliers[modifications.parking_type?.toLowerCase() || 'surface'] || 1.0;
      
      // Apply project classification multipliers
      const classificationMultipliers: Record<string, number> = {
        'ground_up': 1.0,
        'addition': 1.15,
        'renovation': 1.35
      };
      costPerSqft *= classificationMultipliers[modifications.project_classification || 'ground_up'] || 1.0;
      
      // Calculate total costs
      const constructionCost = costPerSqft * newSqft;
      const softCosts = constructionCost * 0.20; // 20% soft costs
      const contingency = constructionCost * 0.10; // 10% contingency
      const totalProjectCost = constructionCost + softCosts + contingency;
      
      // Calculate financial metrics
      const roi = 0.08 * (baseCost / totalProjectCost); // Simplified ROI
      const paybackPeriod = totalProjectCost / (totalProjectCost * 0.12); // Simplified payback
      
      // Create response in the same format as the API
      const response = {
        data: {
          project_id: `scenario_${Date.now()}`,
          project_name: `${baseProject.name} - ${name}`,
          building_type: baseProject.building_type || 'office',
          square_footage: newSqft,
          location: baseProject.location || 'Nashville, TN',
          total_cost: totalProjectCost,
          total_project_cost: totalProjectCost,
          construction_cost: constructionCost,
          soft_costs: softCosts,
          contingency_amount: contingency,
          cost_per_sqft: costPerSqft,
          roi: roi,
          payback_period: paybackPeriod,
          cost_breakdown: {
            site_work: constructionCost * 0.05,
            foundation: constructionCost * 0.08,
            structure: constructionCost * 0.15,
            envelope: constructionCost * 0.12,
            interiors: constructionCost * 0.25,
            mechanical: constructionCost * 0.20,
            electrical: constructionCost * 0.15
          }
        }
      };

      // Create the scenario object
      const scenario: V2Scenario = {
        id: `scenario_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        projectId,
        name,
        description,
        modifications,
        results: response.data,
        createdAt: new Date().toISOString(),
        isBase: false
      };

      // Save to localStorage
      const allScenarios = this.getAllScenarios();
      if (!allScenarios[projectId]) {
        allScenarios[projectId] = [];
        
        // Create base scenario if it doesn't exist
        // Ensure the base project has all required cost fields
        // Get the actual total cost with all possible fallbacks
        const actualTotalCost = baseProject.total_project_cost || 
                               baseProject.totalCost || 
                               baseProject.total_cost ||
                               baseProject.cost_breakdown?.total ||
                               baseProject.costBreakdown?.total ||
                               0;
        
        const actualSqft = baseProject.square_footage || 4200; // Default to restaurant size
        
        const baseResults = {
          project_id: baseProject.id || baseProject.project_id,
          project_name: baseProject.name,
          building_type: baseProject.building_type || baseProject.project_type,
          square_footage: actualSqft,
          location: baseProject.location,
          total_project_cost: actualTotalCost,
          total_cost: actualTotalCost,
          construction_cost: baseProject.construction_cost || baseProject.constructionCost || (actualTotalCost * 0.77),
          soft_costs: baseProject.soft_costs || baseProject.softCosts || (actualTotalCost * 0.20),
          contingency_amount: baseProject.contingency_amount || baseProject.contingency || (actualTotalCost * 0.10),
          cost_per_sqft: baseProject.cost_per_sqft || baseProject.costPerSqft || (actualTotalCost / actualSqft),
          roi: baseProject.roi || 0.08,
          payback_period: baseProject.payback_period || baseProject.paybackPeriod || 8.3,
          cost_breakdown: baseProject.cost_breakdown || baseProject.costBreakdown || {}
        };
        
        const baseScenario: V2Scenario = {
          id: `scenario_base_${projectId}`,
          projectId,
          name: 'Base Project',
          description: 'Original project configuration',
          modifications: {},
          results: baseResults,
          createdAt: baseProject.createdAt || new Date().toISOString(),
          isBase: true
        };
        allScenarios[projectId].push(baseScenario);
      }
      
      allScenarios[projectId].push(scenario);
      this.saveAllScenarios(allScenarios);

      return scenario;
    } catch (error) {
      console.error('Error creating V2 scenario:', error);
      throw error;
    }
  }

  /**
   * Get all scenarios for a V2 project
   */
  async listScenarios(projectId: string, baseProjectData?: any): Promise<V2Scenario[]> {
    const allScenarios = this.getAllScenarios();
    const projectScenarios = allScenarios[projectId] || [];
    
    // If no scenarios exist, create the base scenario
    if (projectScenarios.length === 0) {
      // Use provided baseProject data or get from localStorage
      let baseProject = baseProjectData;
      
      if (!baseProject) {
        const projectsStr = localStorage.getItem('specsharp_projects');
        const projects = projectsStr ? JSON.parse(projectsStr) : [];
        baseProject = projects.find((p: any) => p.id === projectId || p.project_id === projectId);
      }
      
      if (baseProject) {
        // Ensure the base project has all required cost fields
        // Get the actual total cost with all possible fallbacks
        const actualTotalCost = baseProject.total_project_cost || 
                               baseProject.totalCost || 
                               baseProject.total_cost ||
                               baseProject.cost_breakdown?.total ||
                               baseProject.costBreakdown?.total ||
                               0;
        
        const actualSqft = baseProject.square_footage || 4200; // Default to restaurant size
        
        const baseResults = {
          project_id: baseProject.id || baseProject.project_id,
          project_name: baseProject.name,
          building_type: baseProject.building_type || baseProject.project_type,
          square_footage: actualSqft,
          location: baseProject.location,
          total_project_cost: actualTotalCost,
          total_cost: actualTotalCost,
          construction_cost: baseProject.construction_cost || baseProject.constructionCost || (actualTotalCost * 0.77),
          soft_costs: baseProject.soft_costs || baseProject.softCosts || (actualTotalCost * 0.20),
          contingency_amount: baseProject.contingency_amount || baseProject.contingency || (actualTotalCost * 0.10),
          cost_per_sqft: baseProject.cost_per_sqft || baseProject.costPerSqft || (actualTotalCost / actualSqft),
          roi: baseProject.roi || 0.08,
          payback_period: baseProject.payback_period || baseProject.paybackPeriod || 8.3,
          cost_breakdown: baseProject.cost_breakdown || baseProject.costBreakdown || {}
        };
        
        const baseScenario: V2Scenario = {
          id: `scenario_base_${projectId}`,
          projectId,
          name: 'Base Project',
          description: 'Original project configuration',
          modifications: {},
          results: baseResults,
          createdAt: baseProject.createdAt || new Date().toISOString(),
          isBase: true
        };
        
        const scenarios = { ...allScenarios };
        scenarios[projectId] = [baseScenario];
        this.saveAllScenarios(scenarios);
        
        return [baseScenario];
      }
    }
    
    return projectScenarios;
  }

  /**
   * Delete a scenario
   */
  async deleteScenario(scenarioId: string): Promise<void> {
    const allScenarios = this.getAllScenarios();
    
    // Find and remove the scenario
    for (const projectId in allScenarios) {
      const index = allScenarios[projectId].findIndex(s => s.id === scenarioId);
      if (index !== -1 && !allScenarios[projectId][index].isBase) {
        allScenarios[projectId].splice(index, 1);
        this.saveAllScenarios(allScenarios);
        return;
      }
    }
  }

  /**
   * Compare multiple scenarios
   */
  async compareScenarios(
    projectId: string,
    scenarioIds: string[],
    name?: string
  ): Promise<any> {
    const scenarios = await this.listScenarios(projectId);
    const selectedScenarios = scenarios.filter(s => scenarioIds.includes(s.id));
    
    if (selectedScenarios.length < 2) {
      throw new Error('Need at least 2 scenarios to compare');
    }

    // Build comparison data
    const comparison = {
      comparison_name: name || 'Scenario Comparison',
      scenario_ids: scenarioIds,
      scenario_names: selectedScenarios.map(s => s.name),
      metrics_comparison: {} as Record<string, number[]>,
      best_overall_scenario: '',
      best_roi_scenario: '',
      lowest_cost_scenario: '',
      fastest_payback_scenario: ''
    };

    // Extract metrics for comparison with multiple fallbacks for field names
    const metricMappings: Record<string, string[]> = {
      'total_project_cost': ['total_project_cost', 'totalCost', 'total_cost'],
      'cost_per_sqft': ['cost_per_sqft', 'costPerSqft'],
      'construction_cost': ['construction_cost', 'constructionCost'],
      'soft_costs': ['soft_costs', 'softCosts'],
      'contingency': ['contingency_amount', 'contingency'],
      'roi': ['roi'],
      'payback_period': ['payback_period', 'paybackPeriod']
    };

    Object.keys(metricMappings).forEach(metricKey => {
      comparison.metrics_comparison[metricKey] = selectedScenarios.map(s => {
        // Try each possible field name
        for (const field of metricMappings[metricKey]) {
          const value = s.results[field] || s.results.cost_breakdown?.[field];
          if (value !== undefined && value !== null) {
            return typeof value === 'number' ? value : 0;
          }
        }
        return 0;
      });
    });

    // Determine best scenarios
    const costs = selectedScenarios.map((s, i) => ({
      name: s.name,
      cost: s.results.total_project_cost || s.results.totalCost || 0,
      roi: s.results.roi || 0,
      payback: s.results.payback_period || 999,
      index: i
    }));

    comparison.lowest_cost_scenario = costs.reduce((prev, curr) => 
      curr.cost < prev.cost ? curr : prev
    ).name;

    comparison.best_roi_scenario = costs.reduce((prev, curr) => 
      curr.roi > prev.roi ? curr : prev
    ).name;

    comparison.fastest_payback_scenario = costs.reduce((prev, curr) => 
      curr.payback < prev.payback ? curr : prev
    ).name;

    // Best overall (balanced score)
    const scores = costs.map(c => {
      const costScore = 1 - (c.cost - Math.min(...costs.map(x => x.cost))) / 
                        (Math.max(...costs.map(x => x.cost)) - Math.min(...costs.map(x => x.cost)) || 1);
      const roiScore = (c.roi - Math.min(...costs.map(x => x.roi))) / 
                       (Math.max(...costs.map(x => x.roi)) - Math.min(...costs.map(x => x.roi)) || 1);
      return { name: c.name, score: (costScore + roiScore) / 2 };
    });

    comparison.best_overall_scenario = scores.reduce((prev, curr) => 
      curr.score > prev.score ? curr : prev
    ).name;

    return comparison;
  }

  /**
   * Calculate scenario impact without saving
   */
  async calculateScenarioImpact(
    projectId: string,
    modifications: V2ScenarioModification
  ): Promise<any> {
    try {
      // Get the base project
      const projectsStr = localStorage.getItem('specsharp_projects');
      const projects = projectsStr ? JSON.parse(projectsStr) : [];
      const baseProject = projects.find((p: any) => p.id === projectId || p.project_id === projectId);
      
      if (!baseProject) {
        throw new Error(`Project ${projectId} not found`);
      }

      // Calculate locally without API call to avoid auth issues
      const baseCost = baseProject.total_project_cost || baseProject.totalCost || 1000000;
      const baseSqft = baseProject.square_footage || 5000;
      const newSqft = modifications.square_footage || baseSqft;
      
      // Calculate base cost per square foot
      let costPerSqft = baseCost / baseSqft;
      
      // Apply finish level adjustments
      const finishMultipliers: Record<string, number> = {
        'economy': 0.85,
        'standard': 1.0,
        'premium': 1.15,
        'luxury': 1.30
      };
      costPerSqft *= finishMultipliers[modifications.finish_level?.toLowerCase() || 'standard'] || 1.0;
      
      // Apply parking adjustments
      const parkingMultipliers: Record<string, number> = {
        'none': 0.90,
        'surface': 1.0,
        'garage': 1.10,
        'underground': 1.20
      };
      costPerSqft *= parkingMultipliers[modifications.parking_type?.toLowerCase() || 'surface'] || 1.0;
      
      // Apply project classification multipliers
      const classificationMultipliers: Record<string, number> = {
        'ground_up': 1.0,
        'addition': 1.15,
        'renovation': 1.35
      };
      costPerSqft *= classificationMultipliers[modifications.project_classification || 'ground_up'] || 1.0;
      
      // Calculate total costs
      const constructionCost = costPerSqft * newSqft;
      const softCosts = constructionCost * 0.20;
      const contingency = constructionCost * 0.10;
      const totalProjectCost = constructionCost + softCosts + contingency;
      
      // Calculate financial metrics
      const roi = 0.08 * (baseCost / totalProjectCost);
      const paybackPeriod = totalProjectCost / (totalProjectCost * 0.12);
      
      return {
        project_id: `impact_${Date.now()}`,
        project_name: `${baseProject.name} - Impact Analysis`,
        building_type: baseProject.building_type || 'office',
        square_footage: newSqft,
        location: baseProject.location || 'Nashville, TN',
        total_cost: totalProjectCost,
        total_project_cost: totalProjectCost,
        construction_cost: constructionCost,
        soft_costs: softCosts,
        contingency_amount: contingency,
        cost_per_sqft: costPerSqft,
        roi: roi,
        payback_period: paybackPeriod,
        cost_breakdown: {
          site_work: constructionCost * 0.05,
          foundation: constructionCost * 0.08,
          structure: constructionCost * 0.15,
          envelope: constructionCost * 0.12,
          interiors: constructionCost * 0.25,
          mechanical: constructionCost * 0.20,
          electrical: constructionCost * 0.15
        }
      };
    } catch (error) {
      console.error('Error calculating scenario impact:', error);
      throw error;
    }
  }
}

export default new ScenarioV2Api();