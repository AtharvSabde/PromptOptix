import { useState, useCallback, useRef } from 'react';
import { optimizationService } from '../api/optimize.service';
import type { PhaseStreamEvent } from '../api/optimize.service';
import type { AdvancedOptimizeRequest, AdvancedOptimizeResponse } from '../types/advanced.types';
import type { ApiError } from '../api/client';

export interface PipelinePhase {
  phase: number;
  name: string;
  status: 'pending' | 'running' | 'complete' | 'failed';
  score?: number;
  skipped?: boolean;
  error?: string;
}

const INITIAL_PHASES: PipelinePhase[] = [
  { phase: 1, name: 'Standard Optimization', status: 'pending' },
  { phase: 2, name: 'DGEO Evolutionary Search', status: 'pending' },
  { phase: 3, name: 'SHDT Trajectory Refinement', status: 'pending' },
  { phase: 4, name: 'CDRAF Agent Critique', status: 'pending' },
];

export const useAdvancedOptimization = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<ApiError | null>(null);
  const [data, setData] = useState<AdvancedOptimizeResponse | null>(null);
  const [pipelinePhases, setPipelinePhases] = useState<PipelinePhase[]>(INITIAL_PHASES);
  const [isStreaming, setIsStreaming] = useState(false);
  const abortRef = useRef<AbortController | null>(null);

  const advancedOptimize = useCallback(async (request: AdvancedOptimizeRequest) => {
    setIsLoading(true);
    setError(null);

    try {
      const result = await optimizationService.advancedOptimize(request);
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

  const streamOptimize = useCallback(async (request: AdvancedOptimizeRequest) => {
    setIsLoading(true);
    setIsStreaming(true);
    setError(null);
    setData(null);
    setPipelinePhases(INITIAL_PHASES);

    abortRef.current = new AbortController();

    try {
      await optimizationService.advancedOptimizeStream(
        request,
        (event: PhaseStreamEvent) => {
          if (event.type === 'phase') {
            setPipelinePhases(prev =>
              prev.map(p =>
                p.phase === event.phase
                  ? {
                      ...p,
                      status: (event.status as PipelinePhase['status']) || p.status,
                      score: event.score ?? p.score,
                      skipped: event.skipped,
                      error: event.error,
                    }
                  : p
              )
            );
          } else if (event.type === 'final') {
            const result = event as unknown as AdvancedOptimizeResponse;
            setData(result);
          } else if (event.type === 'error') {
            setError({ error: 'Optimization failed', message: (event.error || event.message || 'Unknown error') as string });
          }
        },
        abortRef.current.signal
      );
    } catch (err) {
      if ((err as Error).name !== 'AbortError') {
        setError({ error: 'Stream failed', message: (err as Error).message });
      }
    } finally {
      setIsLoading(false);
      setIsStreaming(false);
    }
  }, []);

  const reset = useCallback(() => {
    abortRef.current?.abort();
    setData(null);
    setError(null);
    setIsLoading(false);
    setIsStreaming(false);
    setPipelinePhases(INITIAL_PHASES);
  }, []);

  return {
    advancedOptimize,
    streamOptimize,
    isLoading,
    isStreaming,
    error,
    data,
    pipelinePhases,
    reset,
  };
};
