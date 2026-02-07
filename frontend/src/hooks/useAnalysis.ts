import { useState, useCallback } from 'react';
import { analysisService } from '../api/analysis.service';
import type { AnalyzeRequest, AnalysisResponse } from '../types/analysis.types';
import type { ApiError } from '../api/client';

export const useAnalysis = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<ApiError | null>(null);
  const [data, setData] = useState<AnalysisResponse | null>(null);

  const analyzePrompt = useCallback(async (request: AnalyzeRequest) => {
    setIsLoading(true);
    setError(null);

    try {
      const result = await analysisService.analyzePrompt(request);
      setData(result);
      return result;
    } catch (err) {
      const apiError = err as ApiError;
      setError(apiError);
      throw apiError;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const reset = useCallback(() => {
    setData(null);
    setError(null);
    setIsLoading(false);
  }, []);

  return {
    analyzePrompt,
    isLoading,
    error,
    data,
    reset,
  };
};
