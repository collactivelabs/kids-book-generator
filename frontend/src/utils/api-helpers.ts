import axios, { AxiosError, AxiosRequestConfig, AxiosResponse } from 'axios';

/**
 * Error response from the API
 */
export interface ApiError {
  detail: string;
  status_code: number;
}

/**
 * Setup axios interceptors for handling auth tokens and errors
 */
export const setupAxiosInterceptors = (): void => {
  // Request interceptor
  axios.interceptors.request.use(
    (config) => {
      const token = localStorage.getItem('token');
      
      // If token exists and Authorization header is not already set, add it
      if (token && !config.headers.Authorization) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      
      return config;
    },
    (error) => Promise.reject(error)
  );
  
  // Response interceptor
  axios.interceptors.response.use(
    (response) => response,
    (error: AxiosError) => {
      // Handle token expiration
      if (error.response?.status === 401) {
        // Clear token if it's expired
        localStorage.removeItem('token');
        
        // Redirect to login page if not already there
        if (window.location.pathname !== '/login') {
          window.location.href = `/login?returnUrl=${encodeURIComponent(window.location.pathname)}`;
        }
      }
      
      return Promise.reject(error);
    }
  );
};

/**
 * Format error message from API response
 */
export const formatErrorMessage = (error: unknown): string => {
  if (axios.isAxiosError(error)) {
    const axiosError = error as AxiosError<ApiError>;
    
    if (axiosError.response?.data) {
      if (typeof axiosError.response.data === 'string') {
        return axiosError.response.data;
      }
      
      if (axiosError.response.data.detail) {
        return axiosError.response.data.detail;
      }
    }
    
    if (axiosError.message) {
      return axiosError.message;
    }
  }
  
  if (error instanceof Error) {
    return error.message;
  }
  
  return 'An unknown error occurred';
};

/**
 * Make an API request with proper error handling
 */
export const apiRequest = async <T>(
  config: AxiosRequestConfig
): Promise<T> => {
  try {
    const response: AxiosResponse<T> = await axios(config);
    return response.data;
  } catch (error) {
    throw new Error(formatErrorMessage(error));
  }
};
