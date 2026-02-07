import { useState, useCallback } from 'react';
import { optimizationService } from '../api/optimize.service';
import type { OptimizeRequest, OptimizationResponse } from '../types/optimization.types';
import type { ApiError } from '../api/client';

export const useOptimization = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<ApiError | null>(null);
  const [data, setData] = useState<OptimizationResponse | null>(null);

  const optimizePrompt = useCallback(async (request: OptimizeRequest) => {
    setIsLoading(true);
    setError(null);

    try {
      const result = await optimizationService.optimizePrompt(request);
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
    optimizePrompt,
    isLoading,
    error,
    data,
    reset,
  };
};
