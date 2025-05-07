import axios from 'axios';
import { BATCH_ENDPOINTS } from '../config/api';
import { BookCreationRequest } from './booksService';

/**
 * Batch job interface
 */
export interface BatchJob {
  id: string;
  name: string;
  description: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  owner: string;
  created_at: string;
  updated_at: string;
  total_books: number;
  completed_books: number;
  failed_books: number;
  results: BatchBookResult[];
}

/**
 * Batch book result interface
 */
export interface BatchBookResult {
  id: string | null;
  metadata: {
    title: string;
    author: string;
    age_group: string;
    book_type: string;
    theme: string;
    educational_focus: string | null;
    trim_size: string;
    page_count: number;
  };
  status: 'pending' | 'processing' | 'completed' | 'failed';
  error: string | null;
  preview_url: string | null;
  download_url: string | null;
}

/**
 * Batch job creation request interface
 */
export interface BatchJobCreationRequest {
  name: string;
  description: string;
  books: BookCreationRequest[];
}

/**
 * Batch service for managing batch job operations
 */
const batchService = {
  /**
   * Get all batch jobs
   * 
   * @returns List of batch jobs
   */
  getBatchJobs: async (): Promise<BatchJob[]> => {
    const token = localStorage.getItem('token');
    
    if (!token) {
      throw new Error('No authentication token found');
    }
    
    const response = await axios.get<BatchJob[]>(BATCH_ENDPOINTS.LIST, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
    
    return response.data;
  },
  
  /**
   * Get a specific batch job by ID
   * 
   * @param id Batch job ID
   * @returns Batch job data
   */
  getBatchJob: async (id: string): Promise<BatchJob> => {
    const token = localStorage.getItem('token');
    
    if (!token) {
      throw new Error('No authentication token found');
    }
    
    const response = await axios.get<BatchJob>(BATCH_ENDPOINTS.DETAIL(id), {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
    
    return response.data;
  },
  
  /**
   * Create a new batch job
   * 
   * @param batchJob Batch job creation data
   * @returns Created batch job
   */
  createBatchJob: async (batchJob: BatchJobCreationRequest): Promise<BatchJob> => {
    const token = localStorage.getItem('token');
    
    if (!token) {
      throw new Error('No authentication token found');
    }
    
    const response = await axios.post<BatchJob>(BATCH_ENDPOINTS.CREATE, batchJob, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });
    
    return response.data;
  },
  
  /**
   * Check batch job status
   * 
   * @param id Batch job ID
   * @returns Batch job status
   */
  checkBatchJobStatus: async (id: string): Promise<{ status: string; progress: number }> => {
    const token = localStorage.getItem('token');
    
    if (!token) {
      throw new Error('No authentication token found');
    }
    
    const response = await axios.get<{ status: string; progress: number }>(
      BATCH_ENDPOINTS.STATUS(id),
      {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      }
    );
    
    return response.data;
  },
  
  /**
   * Cancel a batch job
   * 
   * @param id Batch job ID
   * @returns Success message
   */
  cancelBatchJob: async (id: string): Promise<void> => {
    const token = localStorage.getItem('token');
    
    if (!token) {
      throw new Error('No authentication token found');
    }
    
    await axios.delete(BATCH_ENDPOINTS.DETAIL(id), {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
  },
};

export default batchService;
