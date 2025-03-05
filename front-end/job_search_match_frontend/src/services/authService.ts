import api from './api';
import { AuthResponse, LoginCredentials, RegisterData, User } from '@/types';

const AUTH_ENDPOINTS = {
  LOGIN: '/auth/login',
  REGISTER: '/auth/register',
  REFRESH: '/auth/refresh',
  ME: '/auth/me',
};

export const authService = {
  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    // Convert to form data for compatibility with OAuth2 backend 
    const formData = new FormData();
    formData.append('username', credentials.email);
    formData.append('password', credentials.password);
    
    const response = await api.post<AuthResponse>(AUTH_ENDPOINTS.LOGIN, formData, {
        // This is necessary for the backend to parse the form data correctly since it's not a JSON request
        // This is a workaround for the OAuth2 backend not being able to parse the form data correctly
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
    
    // Store tokens
    localStorage.setItem('token', response.data.access_token);
    localStorage.setItem('refreshToken', response.data.refresh_token);
    
    return response.data;
  },
  
  async register(userData: RegisterData): Promise<{ userId: string; message: string }> {
    const response = await api.post<{ userId: string; message: string }>(
      AUTH_ENDPOINTS.REGISTER,
      userData
    );
    return response.data;
  },
  
  async refreshToken(refreshToken: string): Promise<AuthResponse> {
    const response = await api.post<AuthResponse>(AUTH_ENDPOINTS.REFRESH, {
      refreshToken,
    });
    
    localStorage.setItem('token', response.data.access_token);
    localStorage.setItem('refreshToken', response.data.refresh_token);
    
    return response.data;
  },
  
  async getCurrentUser(): Promise<User> {
    const response = await api.get<User>(AUTH_ENDPOINTS.ME);
    return response.data;
  },
  
  logout(): void {
    localStorage.removeItem('token');
    localStorage.removeItem('refreshToken');
  },
  
  isAuthenticated(): boolean {
    return !!localStorage.getItem('token');
  },
};