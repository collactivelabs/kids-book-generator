// Import required dependencies
import { API_BASE_URL } from '../config/api';
import { apiRequest } from '../utils/api-helpers';
import { Book, BookMetadata } from './booksService';

// Generation endpoints
const GENERATION_ENDPOINTS = {
  START: `${API_BASE_URL}/generation/start`,
  STATUS: `${API_BASE_URL}/generation/status`,
  CANCEL: `${API_BASE_URL}/generation/cancel`,
};

/**
 * Generation Settings interface - matches the components
 */
export interface GenerationSettingsData {
  storyType: string;
  ageRange: string;
  language: string;
  theme: string;
  characters: string;
  illustrationStyle: string;
  additionalNotes: string;
  pagesCount: number;
}

/**
 * Generation request payload
 */
export interface GenerationRequest {
  bookId?: string; // Optional - if updating an existing book
  settings: GenerationSettingsData;
}

// Export generation status type
export type GenerationStatus = 'idle' | 'preparing' | 'generating' | 'completed' | 'failed';

/**
 * Generation status response
 */
export interface GenerationStatusResponse {
  status: GenerationStatus;
  currentStep: string;
  progress: number;
  error?: string;
  estimatedTimeRemaining?: number;
  bookId?: string;
}

/**
 * Generation service for handling book generation
 */
const generationService = {
  /**
   * Start the generation process for a book
   */
  async startGeneration(request: GenerationRequest): Promise<{ bookId: string; status: GenerationStatusResponse }> {
    try {
      const response = await apiRequest<{ bookId: string; status: GenerationStatusResponse }>({
        method: 'POST',
        url: GENERATION_ENDPOINTS.START,
        data: request
      });
      return response;
    } catch (error) {
      console.error('Error starting generation:', error);
      throw error;
    }
  },

  /**
   * Get the status of a generation process
   */
  async getGenerationStatus(bookId: string): Promise<GenerationStatusResponse> {
    try {
      const response = await apiRequest<GenerationStatusResponse>({
        method: 'GET',
        url: `${GENERATION_ENDPOINTS.STATUS}/${bookId}`
      });
      return response;
    } catch (error) {
      console.error('Error getting generation status:', error);
      throw error;
    }
  },

  /**
   * Cancel an ongoing generation process
   */
  async cancelGeneration(bookId: string): Promise<void> {
    try {
      await apiRequest({
        method: 'POST',
        url: `${GENERATION_ENDPOINTS.CANCEL}/${bookId}`
      });
    } catch (error) {
      console.error('Error canceling generation:', error);
      throw error;
    }
  },

  /**
   * Convert generation settings to book metadata
   * This helps convert between our frontend model and the API model
   */
  convertToBookMetadata: (settings: GenerationSettingsData): BookMetadata => {
    return {
      title: settings.theme,
      author: "AI Generated", // Default author for generated books
      age_group: settings.ageRange,
      book_type: settings.storyType === 'coloring' ? 'coloring' : 'story',
      theme: settings.theme,
      educational_focus: settings.additionalNotes || undefined,
      trim_size: "8.5x11", // Default trim size
      page_count: settings.pagesCount
    };
  },

  /**
   * Convert book metadata to generation settings
   * For editing existing books
   */
  convertFromBookMetadata: (metadata: BookMetadata): GenerationSettingsData => {
    return {
      storyType: metadata.book_type,
      ageRange: metadata.age_group,
      language: 'english', // Default if not specified
      theme: metadata.theme,
      characters: '', // Not directly mapped
      illustrationStyle: 'cartoon', // Default style
      additionalNotes: metadata.educational_focus || '',
      pagesCount: metadata.page_count
    };
  },

  /**
   * Mock generation for testing (simulates the generation process)
   */
  mockGeneration: async function(settings: GenerationSettingsData): Promise<Book> {
    // This is a mock function that simulates the generation process
    // for development and testing without making actual API calls
    
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 5000));
    
    // Generate a mock book
    const bookId = 'mock-' + Date.now();
    const metadata = generationService.convertToBookMetadata(settings);
    
    return {
      id: bookId,
      metadata: metadata,
      template_id: 'template-123',
      canva_design_id: null,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      owner: 'current-user',
      status: 'completed',
      preview_url: 'https://placekitten.com/800/1000',
      download_url: null,
      pages: Array(settings.pagesCount).fill(0).map((_, i) => ({
        id: `page-${i}`,
        page_number: i + 1,
        content: i === 0 ? settings.theme : `Page content for page ${i + 1}`,
        image_url: `https://placekitten.com/800/600?image=${i}` // Placeholder images
      }))
    } as Book;
  }
};

export default generationService;
