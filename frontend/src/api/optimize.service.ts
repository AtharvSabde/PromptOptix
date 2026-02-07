import { apiClient } from './client';
import type { OptimizeRequest, OptimizationResponse } from '../types/optimization.types';

export const optimizationService = {
  /**
   * Optimize a prompt by applying prompt engineering techniques
   * @param request Optimization request with prompt, analysis, and optimization level
   * @returns Optimization response with before/after comparison and applied techniques
   */
  optimizePrompt: async (request: OptimizeRequest): Promise<OptimizationResponse> => {
    const response = await apiClient.post<OptimizationResponse>('/api/optimize', request);
    return response.data;
  },
};
