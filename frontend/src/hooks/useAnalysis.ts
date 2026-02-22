import { useState, useCallback, useRef } from 'react';
import { analysisService } from '../api/analysis.service';
import type { AgentStreamEvent } from '../api/analysis.service';
import type { AnalyzeRequest, AnalysisResponse } from '../types/analysis.types';
import type { ApiError } from '../api/client';

export interface AgentStatus {
  name: string;
  focusArea: string;
  status: 'pending' | 'running' | 'complete' | 'failed';
  score?: number;
  defectsCount?: number;
  summary?: string;
  error?: string;
}

const INITIAL_AGENTS: AgentStatus[] = [
  { name: 'ClarityAgent', focusArea: 'Specification & Intent', status: 'pending' },
  { name: 'StructureAgent', focusArea: 'Structure & Formatting', status: 'pending' },
  { name: 'ContextAgent', focusArea: 'Context & Memory', status: 'pending' },
  { name: 'SecurityAgent', focusArea: 'Security & Safety', status: 'pending' },
];

export const useAnalysis = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<ApiError | null>(null);
  const [data, setData] = useState<AnalysisResponse | null>(null);
  const [agentStatuses, setAgentStatuses] = useState<AgentStatus[]>(INITIAL_AGENTS);
  const [isStreaming, setIsStreaming] = useState(false);
  const abortRef = useRef<AbortController | null>(null);

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

  const streamAnalyze = useCallback(async (request: AnalyzeRequest) => {
    setIsLoading(true);
    setIsStreaming(true);
    setError(null);
    setData(null);
    setAgentStatuses(INITIAL_AGENTS.map(a => ({ ...a, status: 'running' as const })));

    abortRef.current = new AbortController();

    try {
      await analysisService.analyzePromptStream(
        request,
        (event: AgentStreamEvent) => {
          if (event.type === 'agent_start') {
            setAgentStatuses(prev =>
              prev.map(a =>
                a.name === event.agent ? { ...a, status: 'running' as const } : a
              )
            );
          } else if (event.type === 'agent_complete') {
            setAgentStatuses(prev =>
              prev.map(a =>
                a.name === event.agent
                  ? {
                      ...a,
                      status: (event.status === 'complete' ? 'complete' : 'failed') as AgentStatus['status'],
                      score: event.score,
                      defectsCount: event.defects_count,
                      summary: event.summary,
                      error: event.error,
                    }
                  : a
              )
            );
          } else if (event.type === 'final') {
            const result: AnalysisResponse = {
              overall_score: event.overall_score!,
              defects: event.defects!,
              consensus: event.consensus!,
              agent_results: event.agent_results,
              disagreements: event.disagreements,
              summary: (event as Record<string, unknown>).summary as string || '',
              metadata: event.metadata!,
            };
            setData(result);
          } else if (event.type === 'error') {
            setError({ error: 'Analysis failed', message: event.error || event.message || 'Unknown error' });
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
    setAgentStatuses(INITIAL_AGENTS);
  }, []);

  return {
    analyzePrompt,
    streamAnalyze,
    isLoading,
    isStreaming,
    error,
    data,
    agentStatuses,
    reset,
  };
};
