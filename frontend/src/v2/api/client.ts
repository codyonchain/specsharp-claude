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
    options?: RequestInit
  ): Promise<T> {
    const url = `${this.baseURL}/api/v2${endpoint}`;
    
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
  }): Promise<CalculationResult> {
    return this.request<CalculationResult>('/calculate', {
      method: 'POST',
      body: JSON.stringify(params),
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
   * Save project to local storage (later: backend)
   */
  async saveProject(project: Omit<Project, 'id' | 'created_at' | 'updated_at'>): Promise<Project> {
    tracer.trace('STORAGE_CREATE', 'Creating project object', {
      building_type: project.analysis?.parsed_input?.building_type,
      subtype: project.analysis?.parsed_input?.building_subtype,
      has_analysis: !!project.analysis,
      has_calculations: !!project.analysis?.calculations
    });
    
    const newProject: Project = {
      ...project,
      id: `proj_${Date.now()}`,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };
    
    tracer.trace('STORAGE_BEFORE_SAVE', 'Project object created', newProject);
    
    // Save to localStorage with correct key
    const projects = this.getStoredProjects();
    projects.push(newProject);
    localStorage.setItem('specsharp_projects', JSON.stringify(projects));
    
    tracer.trace('STORAGE_AFTER_SAVE', 'Saved to localStorage', {
      id: newProject.id,
      total_projects: projects.length,
      building_type: newProject.analysis?.parsed_input?.building_type
    });
    
    return newProject;
  }

  /**
   * Get all projects
   */
  async getProjects(): Promise<Project[]> {
    // From localStorage for now
    return this.getStoredProjects();
  }

  /**
   * Get single project
   */
  async getProject(id: string): Promise<Project | null> {
    tracer.trace('STORAGE_GET_PROJECT', 'Fetching project by ID', { id });
    
    const projects = this.getStoredProjects();
    const project = projects.find(p => p.id === id) || null;
    
    tracer.trace('STORAGE_FOUND_PROJECT', 'Project retrieved', {
      found: !!project,
      id: project?.id,
      building_type: project?.analysis?.parsed_input?.building_type,
      subtype: project?.analysis?.parsed_input?.building_subtype,
      has_analysis: !!project?.analysis,
      has_calculations: !!project?.analysis?.calculations
    });
    
    return project;
  }

  /**
   * Delete project
   */
  async deleteProject(id: string): Promise<void> {
    const projects = this.getStoredProjects();
    const filtered = projects.filter(p => p.id !== id);
    localStorage.setItem('specsharp_projects', JSON.stringify(filtered));
  }

  /**
   * Helper to get projects from localStorage
   */
  private getStoredProjects(): Project[] {
    const stored = localStorage.getItem('specsharp_projects');
    return stored ? JSON.parse(stored) : [];
  }
}

// Export singleton instance
export const api = new V2APIClient();

// Export class for testing
export { V2APIClient };