export const API_CONFIG = {
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8001',
  timeout: 30000, // 30 seconds
  retryAttempts: 3,
  retryDelay: 1000, // 1 second
};

export const getApiUrl = (endpoint: string): string => {
  return `${API_CONFIG.baseURL}${endpoint}`;
};
