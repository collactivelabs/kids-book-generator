import axios, { InternalAxiosRequestConfig, AxiosResponse, AxiosError } from 'axios';
import { AUTH_ENDPOINTS } from '../config/api';

/**
 * User registration data interface
 */
export interface RegisterData {
  username: string;
  email: string;
  password: string;
  full_name: string;
}

/**
 * Login data interface
 */
export interface LoginData {
  username: string;
  password: string;
}

/**
 * Token response interface
 */
export interface TokenResponse {
  access_token: string;
  token_type: string;
  expires_at: string;
  scopes: string[];
}

/**
 * User interface
 */
export interface User {
  username: string;
  email: string;
  full_name: string;
  created_at: string;
  last_login: string | null;
  scopes: string[];
}

/**
 * Authentication service for managing user registration, login, and token handling
 */
const authService = {
  /**
   * Register a new user
   * 
   * @param userData User registration data
   * @returns Created user data
   */
  register: async (userData: RegisterData): Promise<User> => {
    const response = await axios.post<User>(AUTH_ENDPOINTS.REGISTER, userData);
    return response.data;
  },

  /**
   * Setup axios request/response interceptors for authentication
   * @param onSessionExpired callback to execute when session has expired
   * @returns interceptor id for cleanup
   */
  setupAuthInterceptors: (onSessionExpired: () => void): number => {
    // Request interceptor to add token to all requests
    axios.interceptors.request.use(
      (config: InternalAxiosRequestConfig) => {
        const token = localStorage.getItem('token');
        if (token && config.headers) {
          config.headers['Authorization'] = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor to handle 401 errors
    const responseInterceptor = axios.interceptors.response.use(
      (response: AxiosResponse) => response,
      (error: AxiosError) => {
        // Handle 401 Unauthorized errors
        if (error.response && error.response.status === 401) {
          // Remove token and notify about session expiration
          localStorage.removeItem('token');
          onSessionExpired();
        }
        return Promise.reject(error);
      }
    );

    // Return the interceptor id for cleanup
    return responseInterceptor;
  },

  /**
   * Remove axios interceptor
   * @param interceptorId Id of the interceptor to remove
   */
  removeAuthInterceptor: (interceptorId: number): void => {
    axios.interceptors.response.eject(interceptorId);
  },
  
  /**
   * Log in a user
   * 
   * @param loginData User login credentials
   * @returns Token response
   */
  login: async (loginData: LoginData): Promise<TokenResponse> => {
    // Use form-urlencoded format as required by OAuth2 spec
    const formData = new URLSearchParams();
    formData.append('username', loginData.username);
    formData.append('password', loginData.password);
    
    const response = await axios.post<TokenResponse>(
      AUTH_ENDPOINTS.LOGIN,
      formData.toString(),
      {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      }
    );
    
    return response.data;
  },
  
  /**
   * Get current user data
   * 
   * @returns Current user data
   */
  getCurrentUser: async (): Promise<User> => {
    const token = localStorage.getItem('token');
    
    if (!token) {
      throw new Error('No authentication token found');
    }
    
    const response = await axios.get<User>(AUTH_ENDPOINTS.CURRENT_USER, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
    
    return response.data;
  },
  
  /**
   * Check if user is authenticated
   * 
   * @returns Boolean indicating if user is authenticated
   */
  isAuthenticated: (): boolean => {
    return !!localStorage.getItem('token');
  },
  
  /**
   * Log out user by removing token
   */
  logout: (): void => {
    localStorage.removeItem('token');
  },
  
  /**
   * Set authentication token
   * 
   * @param token JWT token
   */
  setToken: (token: string): void => {
    localStorage.setItem('token', token);
  },
  
  /**
   * Get authentication token
   * 
   * @returns JWT token or null if not authenticated
   */
  getToken: (): string | null => {
    return localStorage.getItem('token');
  },
};

export default authService;
