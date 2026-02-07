import { apiClient } from './client';
import type { Technique, TechniquesListResponse } from '../types/technique.types';

export const techniquesService = {
  /**
   * Get all available prompt engineering techniques
   * @returns List of all techniques organized by category
   */
  getAllTechniques: async (): Promise<TechniquesListResponse> => {
    const response = await apiClient.get<TechniquesListResponse>('/api/techniques');
    return response.data;
  },

  /**
   * Get details for a specific technique
   * @param techniqueId Technique ID (T001-T015)
   * @returns Detailed information about the technique
   */
  getTechniqueById: async (techniqueId: string): Promise<Technique> => {
    const response = await apiClient.get<Technique>(`/api/techniques/${techniqueId}`);
    return response.data;
  },
};
