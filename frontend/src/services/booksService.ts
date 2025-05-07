import axios from 'axios';
import { BOOKS_ENDPOINTS, API_BASE_URL } from '../config/api';
import { apiRequest } from '../utils/api-helpers';

/**
 * Book metadata interface
 */
export interface BookMetadata {
  title: string;
  author: string;
  age_group: string; // '0-3', '3-5', '5-7', or '7-12'
  book_type: string; // 'story' or 'coloring'
  theme: string;
  educational_focus?: string;
  trim_size: string; // '8.5x11' or '8.5x8.5'
  page_count: number;
}

/**
 * Book interface
 */
export interface Book {
  id: string;
  metadata: BookMetadata;
  template_id: string;
  canva_design_id: string | null;
  created_at: string;
  updated_at: string;
  owner: string;
  status: string;
  preview_url: string | null;
  download_url: string | null;
}

/**
 * Book creation request interface
 */
export interface BookCreationRequest {
  metadata: BookMetadata;
  template_id: string;
}

/**
 * Book update request interface
 */
export interface BookUpdateRequest {
  metadata?: Partial<BookMetadata>;
  status?: string;
}

/**
 * Generation parameters interface
 */
export interface GenerationParams {
  prompt?: string;
  settings?: {
    style?: string;
    characters?: string[];
    additionalDetails?: string;
  };
}

/**
 * Generation status response interface
 */
export interface GenerationStatus {
  status: 'pending' | 'in_progress' | 'completed' | 'failed';
  progress: number;
  message?: string;
  estimated_completion_time?: string;
}

/**
 * Books service for handling book-related API operations
 */
export const booksService = {
  /**
   * Fetch all books for the current user
   */
  getBooks: async (): Promise<Book[]> => {
    return apiRequest<Book[]>({
      method: 'GET',
      url: BOOKS_ENDPOINTS.LIST,
    });
  },

  /**
   * Get a specific book by ID
   */
  getBook: async (bookId: string): Promise<Book> => {
    return apiRequest<Book>({
      method: 'GET',
      url: BOOKS_ENDPOINTS.DETAIL(bookId),
    });
  },

  /**
   * Create a new book
   */
  createBook: async (bookData: BookCreationRequest): Promise<Book> => {
    return apiRequest<Book>({
      method: 'POST',
      url: BOOKS_ENDPOINTS.CREATE,
      data: bookData,
    });
  },

  /**
   * Update a book's metadata or status
   */
  updateBook: async (bookId: string, bookData: BookUpdateRequest): Promise<Book> => {
    return apiRequest<Book>({
      method: 'PATCH',
      url: BOOKS_ENDPOINTS.UPDATE(bookId),
      data: bookData,
    });
  },

  /**
   * Delete a book
   */
  deleteBook: async (bookId: string): Promise<void> => {
    return apiRequest<void>({
      method: 'DELETE',
      url: BOOKS_ENDPOINTS.DELETE(bookId),
    });
  },

  /**
   * Start book generation
   */
  generateBook: async (bookId: string, params: GenerationParams): Promise<Book> => {
    return apiRequest<Book>({
      method: 'POST',
      url: `${API_BASE_URL}/books/${bookId}/generate`,
      data: params,
    });
  },

  /**
   * Get book generation status
   */
  getGenerationStatus: async (bookId: string): Promise<GenerationStatus> => {
    return apiRequest<GenerationStatus>({
      method: 'GET',
      url: `${API_BASE_URL}/books/${bookId}/status`,
    });
  },

  /**
   * Get book preview as a blob
   */
  getBookPreview: async (bookId: string): Promise<Blob> => {
    const response = await axios.get(`${API_BASE_URL}/books/${bookId}/preview`, {
      responseType: 'blob',
      headers: {
        Authorization: `Bearer ${localStorage.getItem('token')}`,
      },
    });
    return response.data;
  },

  /**
   * Download book in specified format
   */
  downloadBook: async (bookId: string, format: 'pdf' | 'epub' | 'zip'): Promise<Blob> => {
    const response = await axios.get(`${API_BASE_URL}/books/${bookId}/download?format=${format}`, {
      responseType: 'blob',
      headers: {
        Authorization: `Bearer ${localStorage.getItem('token')}`,
      },
    });
    return response.data;
  },

  /**
   * Send book to Canva for editing
   */
  sendToCanva: async (bookId: string): Promise<{ redirect_url: string }> => {
    return apiRequest<{ redirect_url: string }>({
      method: 'POST',
      url: `${API_BASE_URL}/books/${bookId}/canva`,
    });
  }
};

export default booksService;
