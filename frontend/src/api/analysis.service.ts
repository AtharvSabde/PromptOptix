import { apiClient } from './client';
import type { AnalyzeRequest, AnalysisResponse } from '../types/analysis.types';

export const analysisService = {
  /**
   * Analyze a prompt for defects using multi-agent consensus system
   * @param request Analysis request with prompt, task_type, and domain
   * @returns Analysis response with defects, scores, and agent results
   */
  analyzePrompt: async (request: AnalyzeRequest): Promise<AnalysisResponse> => {
    const response = await apiClient.post<AnalysisResponse>('/api/analyze', request);
    return response.data;
  },
};
