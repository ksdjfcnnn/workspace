import axios from 'axios';
import { LoginRequest, Token } from '../types/auth';

// Create axios instance with base URL
const api = axios.create({
  baseURL: window.location.hostname.includes('all-hands.dev') 
    ? 'https://work-2-mjergotjfrqnqigl.prod-runtime.all-hands.dev/api/v1' 
    : 'http://localhost:12001/api/v1',
});

// Add request interceptor to add auth token to requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Auth API
export const authApi = {
  login: (data: LoginRequest) => api.post<Token>('/auth/login', data),
};

// User API
export const userApi = {
  getProfile: () => api.get('/user/profile'),
  getStats: () => api.get('/user/stats'),
};

// Admin API
export const adminApi = {
  getProjectTimeAnalytics: (params: {
    start: number;
    end: number;
    employeeId?: string;
    teamId?: string;
    projectId?: string;
    taskId?: string;
    shiftId?: string;
  }) => api.get('/analytics/project-time', { params }),
  
  getScreenshots: (params: {
    start: number;
    end: number;
    limit?: number;
    employeeId?: string;
    teamId?: string;
    projectId?: string;
    taskId?: string;
    shiftId?: string;
  }) => api.get('/analytics/screenshots', { params }),
};

export default api;