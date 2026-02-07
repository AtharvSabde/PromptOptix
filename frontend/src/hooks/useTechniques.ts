import { useState, useCallback, useEffect } from 'react';
import { techniquesService } from '../api/techniques.service';
import type { Technique, TechniquesListResponse } from '../types/technique.types';
import type { ApiError } from '../api/client';

export const useTechniques = (loadOnMount: boolean = false) => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<ApiError | null>(null);
  const [techniques, setTechniques] = useState<TechniquesListResponse | null>(null);

  const loadTechniques = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const result = await techniquesService.getAllTechniques();
      setTechniques(result);
      return result;
    } catch (err) {
      const apiError = err as ApiError;
      setError(apiError);
      throw apiError;
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    if (loadOnMount) {
      loadTechniques();
    }
  }, [loadOnMount, loadTechniques]);

  return {
    loadTechniques,
    isLoading,
    error,
    techniques,
  };
};

export const useTechniqueDetails = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<ApiError | null>(null);
  const [technique, setTechnique] = useState<Technique | null>(null);

  const loadTechniqueDetails = useCallback(async (techniqueId: string) => {
    setIsLoading(true);
    setError(null);

    try {
      const result = await techniquesService.getTechniqueById(techniqueId);
      setTechnique(result);
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
    setTechnique(null);
    setError(null);
    setIsLoading(false);
  }, []);

  return {
    loadTechniqueDetails,
    isLoading,
    error,
    technique,
    reset,
  };
};
