/**
 * V2 API Client
 * Single source of truth for all API calls
 * NO other file should make fetch calls
 */

import {
  BuildingType,
  ProjectClass,
  OwnershipType,
  ProjectAnalysis,
  CalculationResult,
  APIError,
  Project,
  ComparisonScenario,
  ParsedInput
} from '../types';
import { tracer } from '../utils/traceSystem';

class V2APIClient {
  private baseURL: string;
  private headers: HeadersInit;

  constructor() {
    this.baseURL = import.meta.env.VITE_API_URL || 'http://localhost:8001';
    this.headers = {
      'Content-Type': 'application/json',
    };
  }

  /**
   * Generic request handler with error handling
   */
  private async request<T>(
    endpoint: string,
    options?: RequestInit,
    apiVersion: 'v1' | 'v2' = 'v2'
  ): Promise<T> {
    const url = `${this.baseURL}/api/${apiVersion}${endpoint}`;
    
    try {
      const response = await fetch(url, {
        ...options,
        headers: {
          ...this.headers,
          ...options?.headers,
        },
      });

      // Handle non-JSON responses
      const contentType = response.headers.get('content-type');
      if (!contentType?.includes('application/json')) {
        if (!response.ok) {
          throw new Error(`API Error: ${response.status} ${response.statusText}`);
        }
        return {} as T;
      }

      const data = await response.json();

      if (!response.ok) {
        const error: APIError = {
          message: data.message || data.detail || response.statusText,
          status: response.status,
          code: data.code,
          details: data
        };
        throw error;
      }

      // Handle V2 API wrapper format
      if ('success' in data && 'data' in data) {
        if (!data.success) {
          throw new Error(data.errors?.[0] || 'Request failed');
        }
        return data.data;
      }

      return data;
    } catch (error) {
      // Network errors or other failures
      if (error instanceof Error) {
        console.error(`API Error [${endpoint}]:`, error);
        throw error;
      }
      throw new Error('An unexpected error occurred');
    }
  }

  /**
   * Set authorization token
   */
  setAuthToken(token: string) {
    this.headers = {
      ...this.headers,
      'Authorization': `Bearer ${token}`,
    };
  }

  /**
   * Clear authorization token
   */
  clearAuthToken() {
    const { Authorization, ...headers } = this.headers as any;
    this.headers = headers;
  }

  // ============================================================================
  // CORE API METHODS
  // ============================================================================

  /**
   * Analyze natural language project description
   */
  async analyzeProject(text: string): Promise<ProjectAnalysis> {
    tracer.trace('API_REQUEST', 'Sending analysis request', { description: text });
    
    const result = await this.request<ProjectAnalysis>('/analyze', {
      method: 'POST',
      body: JSON.stringify({ description: text }),
    });
    
    tracer.trace('API_RESPONSE', 'Received analysis response', {
      building_type: result?.parsed_input?.building_type,
      subtype: result?.parsed_input?.building_subtype,
      square_footage: result?.parsed_input?.square_footage,
      full_result: result
    });
    
    return result;
  }

  /**
   * Calculate project with specific parameters
   */
  async calculateProject(params: {
    building_type: BuildingType;
    subtype: string;
    square_footage: number;
    location: string;
    project_class?: ProjectClass;
    ownership_type?: OwnershipType;
    floors?: number;
    special_features?: string[];
    finishLevel?: 'Standard' | 'Premium' | 'Luxury';
  }): Promise<CalculationResult> {
    const finishSource = params.finishLevel;
    const normalized = finishSource ? finishSource.toLowerCase() : undefined;
    const finishLevel = normalized
      ? normalized.charAt(0).toUpperCase() + normalized.slice(1)
      : undefined;

    return this.request<CalculationResult>('/calculate', {
      method: 'POST',
      body: JSON.stringify({
        ...params,
        finishLevel,
      }),
    });
  }

  /**
   * Compare multiple project scenarios
   */
  async compareScenarios(scenarios: ComparisonScenario[]): Promise<{
    scenarios: Array<{
      scenario_name: string;
      calculations?: CalculationResult;
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
  }> {
    return this.request('/compare', {
      method: 'POST',
      body: JSON.stringify({ scenarios }),
    });
  }

  /**
   * Get all building types and subtypes
   */
  async getBuildingTypes(): Promise<{
    building_types: Array<{
      type: BuildingType;
      display_name: string;
      subtypes: Array<{
        value: string;
        display_name: string;
        base_cost_per_sf: number;
        cost_range: [number, number];
      }>;
    }>;
  }> {
    return this.request('/building-types');
  }

  /**
   * Get specific building configuration
   */
  async getBuildingDetails(
    buildingType: BuildingType,
    subtype: string
  ): Promise<any> {
    return this.request(`/building-details/${buildingType}/${subtype}`);
  }

  /**
   * Test NLP parsing without calculation
   */
  async testNLP(text: string): Promise<ParsedInput> {
    const params = new URLSearchParams({ text });
    return this.request(`/test-nlp?${params}`);
  }

  /**
   * Health check
   */
  async health(): Promise<{
    status: string;
    version: string;
    building_types_loaded: number;
    subtypes_loaded: number;
  }> {
    return this.request('/health');
  }

  // ============================================================================
  // PROJECT MANAGEMENT (Frontend state - could be backend later)
  // ============================================================================
  
  /**
   * V1/V2 Endpoint Architecture:
   * 
   * V1 endpoints: Project CRUD operations (storage)
   * - GET /api/v2/scope/projects/{id} - fetch stored project
   * - POST /api/v2/scope/projects - save project
   * - DELETE /api/v2/scope/projects/{id} - delete project
   * 
   * V2 endpoints: Calculations only (no storage)
   * - POST /api/v2/analyze - analyze new input
   * - POST /api/v2/calculate - detailed calculations
   * - POST /api/v2/compare - scenario comparison
   */
  
  /**
   * Transform V1 project response to V2 structure expected by frontend
   */
  private adaptV1ToV2Structure(project: any): Project {
    // Preserve the ENTIRE original structure first
    let adaptedProject = { ...project };
    
    // Only fix the double-nested calculations.calculations issue if it exists
    if (project?.analysis?.calculations?.calculations) {
      console.log('🔧 Fixing double-nested calculations structure');
      
      // Merge the nested calculations level up while preserving ALL other data
      adaptedProject = {
        ...project,
        analysis: {
          ...project.analysis,
          calculations: {
            // First, preserve everything from the original calculations level
            ...project.analysis.calculations,
            // Then merge in the double-nested calculations content
            ...project.analysis.calculations.calculations,
            // Explicitly preserve critical top-level objects that might get overwritten
            ownership_analysis: 
              project.analysis.calculations.ownership_analysis || 
              project.analysis.calculations.calculations.ownership_analysis,
            revenue_analysis: 
              project.analysis.calculations.revenue_analysis || 
              project.analysis.calculations.calculations.revenue_analysis,
            revenue_requirements: 
              project.analysis.calculations.revenue_requirements || 
              project.analysis.calculations.calculations.revenue_requirements,
            project_info: 
              project.analysis.calculations.project_info || 
              project.analysis.calculations.calculations.project_info,
            operational_metrics:
              project.analysis.calculations.operational_metrics ||
              project.analysis.calculations.calculations.operational_metrics,
            department_allocation:
              project.analysis.calculations.department_allocation ||
              project.analysis.calculations.calculations.department_allocation,
            // Ensure totals exists
            totals: 
              project.analysis.calculations.calculations.totals ||
              project.analysis.calculations.totals || {
                hard_costs: project.total_cost || project.subtotal || 0,
                soft_costs: project.soft_costs || 0,
                total_project_cost: project.total_cost || 0,
                cost_per_sf: project.cost_per_sqft || 0
              }
          }
        }
      };
      
      // Remove the nested calculations property to avoid confusion
      if (adaptedProject.analysis?.calculations?.calculations) {
        delete adaptedProject.analysis.calculations.calculations;
      }
    }
    
    // Ensure basic V2 structure exists even for V1 projects
    if (!adaptedProject?.analysis?.calculations) {
      console.log('📦 Creating V2 structure for V1 project');
      adaptedProject = {
        ...adaptedProject,
        analysis: {
          ...adaptedProject.analysis,
          parsed_input: adaptedProject.request_data || adaptedProject.parsed_input || {
            square_footage: adaptedProject.square_footage || 0,
            building_type: adaptedProject.building_type || '',
            building_subtype: adaptedProject.building_subtype || '',
            location: adaptedProject.location || '',
            floors: adaptedProject.floors || 1
          },
          calculations: {
            totals: {
              hard_costs: adaptedProject.total_cost || adaptedProject.subtotal || 0,
              soft_costs: adaptedProject.soft_costs || 0,
              total_project_cost: adaptedProject.total_cost || 0,
              cost_per_sf: adaptedProject.cost_per_sqft || 0
            },
            construction_costs: {
              total: adaptedProject.subtotal || adaptedProject.total_cost || 0,
              base_cost_per_sf: adaptedProject.base_cost_per_sf || adaptedProject.cost_per_sqft || 0,
              breakdown: adaptedProject.calculation_breakdown || {}
            },
            soft_costs: {
              total: adaptedProject.soft_costs || 0,
              breakdown: adaptedProject.soft_cost_breakdown || {}
            },
            trade_breakdown: adaptedProject.trades || adaptedProject.categories || [],
            confidence_score: adaptedProject.confidence_score || 95
          }
        }
      };
    }
    
    return adaptedProject;
  }

  /**
   * Save project to backend
   */
  async saveProject(project: Omit<Project, 'id' | 'created_at' | 'updated_at'>): Promise<Project> {
    // Apply adapter to incoming project to fix any structure issues BEFORE saving
    const cleanProject = this.adaptV1ToV2Structure(project);
    
    tracer.trace('API_CREATE_PROJECT', 'Creating project via API', {
      building_type: cleanProject.analysis?.parsed_input?.building_type,
      subtype: cleanProject.analysis?.parsed_input?.building_subtype,
      has_analysis: !!cleanProject.analysis,
      has_calculations: !!cleanProject.analysis?.calculations,
      has_totals: !!cleanProject.analysis?.calculations?.totals
    });
    
    try {
      console.log('📡 Saving project to backend API...');
      console.log('Original project:', project);
      console.log('Cleaned project:', cleanProject);
      
      const v1SavedProject = await this.request<any>('/scope/projects', {
        method: 'POST',
        body: JSON.stringify(cleanProject),
      }, 'v1');
      
      console.log('Backend response:', v1SavedProject);
      
      // Transform V1 response to V2 structure
      const v2SavedProject = this.adaptV1ToV2Structure(v1SavedProject);
      
      console.log('✅ Project saved to backend with ID:', v2SavedProject.id);
      console.log('Adapted project structure:', {
        has_totals: !!v2SavedProject.analysis?.calculations?.totals,
        hard_costs: v2SavedProject.analysis?.calculations?.totals?.hard_costs,
        total_cost: v2SavedProject.analysis?.calculations?.totals?.total_project_cost
      });
      
      tracer.trace('API_PROJECT_SAVED', 'Saved to backend', {
        id: v2SavedProject.id,
        building_type: v2SavedProject.analysis?.parsed_input?.building_type
      });
      
      // Also save to localStorage as backup (save V2 structure)
      // Note: Don't use getStoredProjects here as it applies adapter and we want to save the clean structure
      const stored = localStorage.getItem('specsharp_projects');
      const projects = stored ? JSON.parse(stored) : [];
      projects.push(v2SavedProject);
      localStorage.setItem('specsharp_projects', JSON.stringify(projects));
      
      return v2SavedProject;
    } catch (error) {
      console.error('❌ Failed to save to backend, saving to localStorage only:', error);
      
      // Fallback to localStorage if API fails
      const newProject: Project = {
        ...cleanProject,
        id: `proj_${Date.now()}`,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      };
      
      // Project is already clean from the start of this function
      const finalProject = newProject;
      
      // Don't use getStoredProjects as it applies adapter
      const stored = localStorage.getItem('specsharp_projects');
      const projects = stored ? JSON.parse(stored) : [];
      projects.push(finalProject);
      localStorage.setItem('specsharp_projects', JSON.stringify(projects));
      
      console.log('📦 Saved to localStorage with ID:', finalProject.id);
      console.log('Final project structure:', {
        has_totals: !!finalProject.analysis?.calculations?.totals,
        hard_costs: finalProject.analysis?.calculations?.totals?.hard_costs,
        total_cost: finalProject.analysis?.calculations?.totals?.total_project_cost
      });
      
      return finalProject;
    }
  }

  /**
   * Get all projects
   */
  async getProjects(): Promise<Project[]> {
    try {
      console.log('📡 Fetching all projects from V2 backend API...');
      const v2Response = await this.request<any>('/scope/projects', {}, 'v2');
      
      // Handle V2 response structure - might be wrapped in data key
      const projectsData = v2Response.data || v2Response;
      const projectsList = Array.isArray(projectsData) ? projectsData : [projectsData];
      
      console.log(`✅ Received ${projectsList.length} projects from V2 backend`);
      
      // Map V2 projects to expected structure
      const v2Projects = projectsList.map(project => ({
        ...project,
        analysis: {
          calculations: project.calculation_data || project
        },
        calculation_data: project.calculation_data,
        roi_analysis: project.calculation_data?.roi_analysis,
        revenue_analysis: project.calculation_data?.revenue_analysis
      }));
      
      // Debug dashboard data
      console.log('=== DASHBOARD PROJECT LIST DEBUG ===');
      v2Projects.forEach((project, index) => {
        const hardCosts = project.analysis?.calculations?.totals?.hard_costs;
        const totalCost = project.analysis?.calculations?.totals?.total_project_cost;
        
        console.log(`Project ${index + 1} (${project.id}):`, project.name);
        console.log('  - Has analysis:', !!project.analysis);
        console.log('  - Has calculations:', !!project.analysis?.calculations);
        console.log('  - Has totals:', !!project.analysis?.calculations?.totals);
        console.log('  - Hard costs:', hardCosts);
        console.log('  - Total cost:', totalCost);
        console.log('  - Has ownership_analysis:', !!project.analysis?.calculations?.ownership_analysis);
        
        if (hardCosts === 0 || hardCosts === null || hardCosts === undefined) {
          console.log('  ⚠️ ZERO COST DETECTED! Full structure:');
          console.log('  - Full analysis:', project.analysis);
          console.log('  - Full calculations:', project.analysis?.calculations);
          console.log('  - Raw project:', project);
        }
      });
      console.log('=== END DASHBOARD DEBUG ===');
      
      return v2Projects;
    } catch (error) {
      console.error('❌ Failed to fetch projects from backend:', error);
      
      // Fallback to localStorage if API fails
      console.log('⚠️ Falling back to localStorage...');
      const v1Projects = this.getStoredProjects();
      console.log(`📦 Found ${v1Projects.length} projects in localStorage`);
      
      // Note: getStoredProjects now applies the adapter internally
      console.log('=== DASHBOARD PROJECT LIST DEBUG (localStorage) ===');
      v1Projects.forEach((project, index) => {
        console.log(`Project ${index + 1} (${project.id}):`);
        console.log('  - Has analysis:', !!project.analysis);
        console.log('  - Has calculations:', !!project.analysis?.calculations);
        console.log('  - Has totals:', !!project.analysis?.calculations?.totals);
        console.log('  - Hard costs:', project.analysis?.calculations?.totals?.hard_costs);
        console.log('  - Total cost:', project.analysis?.calculations?.totals?.total_project_cost);
        console.log('  - Has ownership_analysis:', !!project.analysis?.calculations?.ownership_analysis);
      });
      console.log('=== END DASHBOARD DEBUG ===');
      
      return v1Projects;
    }
  }

  /**
   * Get single project
   */
  async getProject(id: string): Promise<Project | null> {
    console.log('🔍 DEBUG: getProject called with ID:', id);
    tracer.trace('API_GET_PROJECT', 'Fetching project by ID from backend', { id });
    
    try {
      console.log('📡 Making API call to V2 backend for project:', id);
      const v2Project = await this.request<any>(`/scope/projects/${id}`, {}, 'v2');
      
      // Handle V2 response structure
      const projectData = v2Project.data || v2Project;
      
      console.log('✅ Received V2 project from backend:', v2Project);
      console.log('📊 Project data structure:', projectData);
      tracer.trace('API_PROJECT_RETRIEVED', 'Project retrieved from V2 backend', {
        found: !!projectData,
        id: projectData?.id,
        building_type: projectData?.building_type,
        subtype: projectData?.subtype,
        has_calculation_data: !!projectData?.calculation_data,
        has_revenue_analysis: !!projectData?.calculation_data?.revenue_analysis
      });
      
      // Map V2 response to expected frontend structure
      const mappedProject = {
        ...projectData,
        analysis: {
          // Map calculation_data to where frontend expects it
          calculations: projectData.calculation_data || projectData
        },
        // Also preserve at top level for compatibility
        calculation_data: projectData.calculation_data,
        roi_analysis: projectData.calculation_data?.roi_analysis,
        revenue_analysis: projectData.calculation_data?.revenue_analysis
      };
      
      console.log('🔧 Mapped V2 project structure:', mappedProject);
      return mappedProject;
    } catch (error) {
      console.error('❌ Failed to fetch project from backend:', error);
      
      // Fallback to localStorage if API fails
      console.log('⚠️ Falling back to localStorage...');
      const projects = this.getStoredProjects();
      const v1Project = projects.find(p => p.id === id) || null;
      
      if (v1Project) {
        console.log('📦 Found project in localStorage');
        
        // Debug: Show full structure of localStorage project
        console.log('=== FULL PROJECT STRUCTURE ===');
        console.log('Full project:', JSON.stringify(v1Project, null, 2));
        
        // Debug: Find all cost-related values in the structure
        console.log('=== SEARCHING FOR COST VALUES ===');
        const findCosts = (obj: any, path = '') => {
          for (const key in obj) {
            if (obj[key] && typeof obj[key] === 'object' && !Array.isArray(obj[key])) {
              findCosts(obj[key], path ? `${path}.${key}` : key);
            } else if (typeof obj[key] === 'number' && obj[key] > 1000) {
              console.log(`Found large number at ${path ? path + '.' : ''}${key}:`, obj[key]);
            }
            // Also look for any key containing 'cost', 'total', or 'subtotal'
            if (key.toLowerCase().includes('cost') || 
                key.toLowerCase().includes('total') || 
                key.toLowerCase().includes('subtotal')) {
              console.log(`Found cost-related field at ${path ? path + '.' : ''}${key}:`, obj[key]);
            }
          }
        };
        findCosts(v1Project);
        console.log('=== END COST SEARCH ===');
        
        // Transform V1 structure to V2 if needed
        const v2Project = this.adaptV1ToV2Structure(v1Project);
        
        console.log('=== LOCALSTORAGE PROJECT DATA TRACE ===');
        console.log('1. Original V1 project:', v1Project);
        console.log('2. Transformed V2 project:', v2Project);
        console.log('3. Has analysis?', !!v2Project?.analysis);
        console.log('4. Has calculations?', !!v2Project?.analysis?.calculations);
        console.log('5. Has totals?', !!v2Project?.analysis?.calculations?.totals);
        console.log('6. Hard costs value:', v2Project?.analysis?.calculations?.totals?.hard_costs);
        console.log('7. Soft costs value:', v2Project?.analysis?.calculations?.totals?.soft_costs);
        console.log('8. Total project cost:', v2Project?.analysis?.calculations?.totals?.total_project_cost);
        console.log('=== END LOCALSTORAGE TRACE ===');
        
        return v2Project;
      } else {
        console.log('❌ Project not found in localStorage either');
        return null;
      }
    }
  }

  /**
   * Delete project
   */
  async deleteProject(id: string): Promise<void> {
    try {
      console.log('📡 Deleting project from backend:', id);
      await this.request(`/scope/projects/${id}`, {
        method: 'DELETE',
      }, 'v1');
      console.log('✅ Project deleted from backend');
      
      // Also remove from localStorage
      // Don't use getStoredProjects as it applies adapter unnecessarily
      const stored = localStorage.getItem('specsharp_projects');
      const projects = stored ? JSON.parse(stored) : [];
      const filtered = projects.filter((p: any) => p.id !== id);
      localStorage.setItem('specsharp_projects', JSON.stringify(filtered));
    } catch (error) {
      console.error('❌ Failed to delete from backend:', error);
      
      // Still remove from localStorage
      // Don't use getStoredProjects as it applies adapter unnecessarily
      const stored = localStorage.getItem('specsharp_projects');
      const projects = stored ? JSON.parse(stored) : [];
      const filtered = projects.filter((p: any) => p.id !== id);
      localStorage.setItem('specsharp_projects', JSON.stringify(filtered));
      console.log('📦 Removed from localStorage');
    }
  }

  /**
   * Helper to get projects from localStorage
   */
  private getStoredProjects(): Project[] {
    const stored = localStorage.getItem('specsharp_projects');
    if (!stored) return [];
    
    const projects = JSON.parse(stored);
    // Apply adapter to each project to fix any structure issues
    return projects.map(p => this.adaptV1ToV2Structure(p));
  }
}

// Export singleton instance
export const api = new V2APIClient();

// Export class for testing
export { V2APIClient };
