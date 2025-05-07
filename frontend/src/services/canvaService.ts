import axios from 'axios';
import { CANVA_ENDPOINTS } from '../config/api';

/**
 * Canva template interface
 */
export interface CanvaTemplate {
  template_id: string;
  name: string;
  description: string;
  book_type: string;
  age_groups: string[];
  properties: {
    layout: string;
    font_family: string;
    title_font: string;
    body_font: string;
    caption_font: string;
    color_scheme: {
      primary: string;
      secondary: string;
      text: string;
    };
    info_boxes: boolean;
    title_alignment: string;
    body_alignment: string;
    image_placement: string;
    page_numbering: boolean;
    educational_notes: boolean;
  };
  preview_image: string | null;
  created_at: string;
  updated_at: string;
}

/**
 * Canva service for managing Canva API integrations
 */
const canvaService = {
  /**
   * Get all Canva templates
   * 
   * @returns List of Canva templates
   */
  getTemplates: async (): Promise<CanvaTemplate[]> => {
    const token = localStorage.getItem('token');
    
    if (!token) {
      throw new Error('No authentication token found');
    }
    
    const response = await axios.get<CanvaTemplate[]>(CANVA_ENDPOINTS.TEMPLATES, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
    
    return response.data;
  },
  
  /**
   * Get Canva design preview
   * 
   * @param designId Canva design ID
   * @returns Preview URL
   */
  getDesignPreview: async (designId: string): Promise<{ preview_url: string }> => {
    const token = localStorage.getItem('token');
    
    if (!token) {
      throw new Error('No authentication token found');
    }
    
    const response = await axios.get<{ preview_url: string }>(
      CANVA_ENDPOINTS.PREVIEW(designId),
      {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      }
    );
    
    return response.data;
  },
  
  /**
   * Export Canva design to PDF
   * 
   * @param designId Canva design ID
   * @returns Download URL
   */
  exportDesign: async (designId: string): Promise<{ download_url: string }> => {
    const token = localStorage.getItem('token');
    
    if (!token) {
      throw new Error('No authentication token found');
    }
    
    const response = await axios.post<{ download_url: string }>(
      CANVA_ENDPOINTS.EXPORT(designId),
      {},
      {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      }
    );
    
    return response.data;
  },
};

export default canvaService;
