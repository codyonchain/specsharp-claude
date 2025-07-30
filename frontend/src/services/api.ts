import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL 
  ? `${import.meta.env.VITE_API_URL}/api/v1`
  : 'http://localhost:8001/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true, // Include cookies in requests
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Add response interceptor to handle blob errors
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    // If we expected a blob but got an error, try to parse the JSON error message
    if (error.response && error.config.responseType === 'blob' && error.response.data instanceof Blob) {
      try {
        const text = await error.response.data.text();
        const json = JSON.parse(text);
        error.response.data = json;
      } catch (e) {
        // If parsing fails, keep the original error
      }
    }
    return Promise.reject(error);
  }
);


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
  building_mix?: { [key: string]: number };
  service_level?: string;
  building_features?: string[];
  finish_level?: 'basic' | 'standard' | 'premium';
}

export const authService = {
  logout: async () => {
    // Call backend logout to clear cookies
    try {
      await api.post('/auth/logout');
    } catch (error) {
      // Still clear local storage even if backend call fails
    }
    localStorage.removeItem('token');
  },

  isAuthenticated: () => {
    // Check for token in localStorage or cookie presence
    return !!localStorage.getItem('token') || document.cookie.includes('access_token');
  },

  getCurrentUser: async () => {
    const response = await api.get('/oauth/user/info');
    return response.data;
  },
};

export const scopeService = {
  generate: async (data: ScopeRequest) => {
    const response = await api.post('/scope/generate', data);
    return response.data;
  },

  getProjects: async () => {
    const response = await api.get('/scope/projects');
    // Handle new paginated response format
    if (response.data && response.data.items) {
      return response.data.items;
    }
    return response.data;
  },

  getProject: async (projectId: string) => {
    const response = await api.get(`/scope/projects/${projectId}`);
    return response.data;
  },

  deleteProject: async (projectId: string) => {
    const response = await api.delete(`/scope/projects/${projectId}`);
    return response.data;
  },

  duplicateProject: async (projectId: string, name?: string) => {
    const response = await api.post(`/scope/projects/${projectId}/duplicate`, {
      duplicate_name: name
    });
    return response.data;
  },

  updateProjectName: async (projectId: string, name: string) => {
    const response = await api.put(`/scope/projects/${projectId}`, {
      project_name: name
    });
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

export const demoService = {
  generateDemoScope: async (data: { description: string; is_demo: boolean }) => {
    // Create a separate axios instance without auth headers for demo
    const demoApi = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
      withCredentials: true
    });
    
    const response = await demoApi.post('/demo/generate', data);
    return response.data;
  },
  
  quickSignup: async (data: { email?: string; password?: string; demo_project_id?: string }) => {
    // Create a separate axios instance without auth headers for demo signup
    const demoApi = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
      withCredentials: true
    });
    
    const response = await demoApi.post('/demo/quick-signup', data);
    
    // Store the token
    if (response.data.access_token) {
      localStorage.setItem('token', response.data.access_token);
    }
    
    return response.data;
  },
};

// Add to scopeService for demo compatibility
scopeService.generateDemoScope = demoService.generateDemoScope;
scopeService.quickSignup = demoService.quickSignup;

export const markupService = {
  getUserSettings: async () => {
    const response = await api.get('/markup/user/settings');
    return response.data;
  },

  updateUserSettings: async (settings: any) => {
    const response = await api.put('/markup/user/settings', settings);
    return response.data;
  },

  getProjectOverrides: async (projectId: string) => {
    const response = await api.get(`/markup/project/${projectId}/overrides`);
    return response.data;
  },

  updateProjectOverrides: async (projectId: string, overrides: any) => {
    const response = await api.put(`/markup/project/${projectId}/overrides`, overrides);
    return response.data;
  },

  applyMarkupsToProject: async (projectId: string) => {
    const response = await api.post(`/markup/project/${projectId}/apply-markups`);
    return response.data;
  },

  getAvailableTrades: async () => {
    const response = await api.get('/markup/trades');
    return response.data;
  },
};

export const excelService = {
  exportProject: async (projectId: string, includeMarkups: boolean = true) => {
    const response = await api.get(`/excel/project/${projectId}`, {
      params: { include_markups: includeMarkups },
      responseType: 'blob'
    });
    return response;
  },

  exportProfessional: async (projectId: string, clientName?: string) => {
    const response = await api.get(`/excel/project/${projectId}/excel-pro`, {
      params: { client_name: clientName },
      responseType: 'blob'
    });
    return response;
  },

  exportTrade: async (projectId: string, tradeName: string) => {
    const response = await api.get(`/excel/project/${projectId}/trade/${tradeName}`, {
      responseType: 'blob'
    });
    return response;
  },

  extractForSubs: async (projectId: string, tradeName: string) => {
    const response = await api.get(`/excel/extract/${projectId}/${tradeName}`, {
      responseType: 'blob'
    });
    return response;
  },
};

export const pdfService = {
  exportProject: async (projectId: string, clientName?: string) => {
    const response = await api.get(`/pdf/project/${projectId}/pdf`, {
      params: { client_name: clientName },
      responseType: 'blob'
    });
    return response;
  },
};

export const subscriptionService = {
  getStatus: async () => {
    const response = await api.get('/subscription/status');
    return response.data;
  },

  createSubscription: async () => {
    const response = await api.post('/subscription/create');
    return response.data;
  },

  confirmSubscription: async (subscriptionId: string) => {
    const response = await api.post('/subscription/confirm', { subscription_id: subscriptionId });
    return response.data;
  },

  cancelSubscription: async () => {
    const response = await api.post('/subscription/cancel');
    return response.data;
  },
};

export const teamService = {
  createTeam: async (name: string) => {
    const response = await api.post('/team/create', null, { params: { name } });
    return response.data;
  },

  getCurrentTeam: async () => {
    const response = await api.get('/team/current');
    return response.data;
  },

  getTeamMembers: async () => {
    const response = await api.get('/team/members');
    return response.data;
  },

  inviteTeamMember: async (email: string, role: 'admin' | 'member' = 'member') => {
    const response = await api.post('/team/invite', null, { 
      params: { email, role } 
    });
    return response.data;
  },

  acceptInvitation: async (token: string) => {
    const response = await api.post(`/team/accept-invitation/${token}`);
    return response.data;
  },

  updateMemberRole: async (memberId: number, newRole: 'admin' | 'member') => {
    const response = await api.put(`/team/members/${memberId}/role`, null, {
      params: { new_role: newRole }
    });
    return response.data;
  },

  addSeats: async (seatsToAdd: number) => {
    const response = await api.post('/team/add-seats', null, {
      params: { seats_to_add: seatsToAdd }
    });
    return response.data;
  },
};

export const shareService = {
  createShareLink: async (projectId: string) => {
    const response = await api.post(`/project/${projectId}/share`);
    return response.data;
  },

  getSharedProject: async (shareId: string) => {
    // This endpoint doesn't require auth, so we make a direct request
    const response = await axios.get(`${API_BASE_URL}/share/${shareId}`);
    return response.data;
  },

  listProjectShares: async (projectId: string) => {
    const response = await api.get(`/project/${projectId}/shares`);
    return response.data;
  },

  deactivateShare: async (shareId: string) => {
    const response = await api.delete(`/share/${shareId}`);
    return response.data;
  },
};

export default api;