/**
 * API configuration for the Kids Book Generator
 * 
 * Contains base URLs and endpoints for API communication
 */

// Base API URL
export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

// Authentication endpoints
export const AUTH_ENDPOINTS = {
  LOGIN: `${API_BASE_URL}/auth/token`,
  REGISTER: `${API_BASE_URL}/users`,
  CURRENT_USER: `${API_BASE_URL}/users/me`,
};

// Book management endpoints
export const BOOKS_ENDPOINTS = {
  LIST: `${API_BASE_URL}/books`,
  DETAIL: (id: string) => `${API_BASE_URL}/books/${id}`,
  CREATE: `${API_BASE_URL}/books`,
  UPDATE: (id: string) => `${API_BASE_URL}/books/${id}`,
  DELETE: (id: string) => `${API_BASE_URL}/books/${id}`,
};

// Batch processing endpoints
export const BATCH_ENDPOINTS = {
  LIST: `${API_BASE_URL}/batch`,
  DETAIL: (id: string) => `${API_BASE_URL}/batch/${id}`,
  CREATE: `${API_BASE_URL}/batch`,
  STATUS: (id: string) => `${API_BASE_URL}/batch/${id}/status`,
};

// Canva integration endpoints
export const CANVA_ENDPOINTS = {
  TEMPLATES: `${API_BASE_URL}/canva/templates`,
  PREVIEW: (designId: string) => `${API_BASE_URL}/canva/preview/${designId}`,
  EXPORT: (designId: string) => `${API_BASE_URL}/canva/export/${designId}`,
};
