import axios from 'axios';

const API_BASE_URL = 'http://localhost:8001/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface RegisterData {
  email: string;
  full_name: string;
  password: string;
}

export interface ScopeRequest {
  project_name: string;
  project_type: 'residential' | 'commercial' | 'industrial' | 'mixed_use';
  square_footage: number;
  location: string;
  climate_zone?: string;
  num_floors?: number;
  ceiling_height?: number;
  occupancy_type?: string;
  special_requirements?: string;
  budget_constraint?: number;
}

export const authService = {
  login: async (credentials: LoginCredentials) => {
    const formData = new FormData();
    formData.append('username', credentials.username);
    formData.append('password', credentials.password);
    const response = await api.post('/auth/token', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    localStorage.setItem('token', response.data.access_token);
    return response.data;
  },

  register: async (data: RegisterData) => {
    const response = await api.post('/auth/register', data);
    return response.data;
  },

  logout: () => {
    localStorage.removeItem('token');
  },
};

export const scopeService = {
  generate: async (data: ScopeRequest) => {
    const response = await api.post('/scope/generate', data);
    return response.data;
  },

  getProjects: async () => {
    const response = await api.get('/scope/projects');
    return response.data;
  },

  getProject: async (projectId: string) => {
    const response = await api.get(`/scope/projects/${projectId}`);
    return response.data;
  },
};

export const costService = {
  getRegionalMultipliers: async () => {
    const response = await api.get('/cost/regional-multipliers');
    return response.data;
  },

  getMaterials: async (location?: string) => {
    const params = location ? { location } : {};
    const response = await api.get('/cost/materials', { params });
    return response.data;
  },

  calculateBreakdown: async (scopeData: any) => {
    const response = await api.post('/cost/calculate-breakdown', scopeData);
    return response.data;
  },
};

export const floorPlanService = {
  generate: async (data: any) => {
    const response = await api.post('/floor-plan/generate', data);
    return response.data;
  },

  getFloorPlan: async (floorPlanId: string) => {
    const response = await api.get(`/floor-plan/plans/${floorPlanId}`);
    return response.data;
  },
};

export default api;

// Re-export types to ensure they're available
export type { LoginCredentials, RegisterData, ScopeRequest };