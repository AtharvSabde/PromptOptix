import { apiClient } from './client';
import type { OptimizeRequest, OptimizationResponse } from '../types/optimization.types';
import type { AdvancedOptimizeRequest, AdvancedOptimizeResponse } from '../types/advanced.types';

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface PhaseStreamEvent {
  type: 'phase' | 'final' | 'error';
  phase?: number;
  name?: string;
  status?: string;
  score?: number;
  skipped?: boolean;
  error?: string;
  // final event includes full AdvancedOptimizeResponse fields
  [key: string]: unknown;
}

export const optimizationService = {
  /**
   * Optimize a prompt by applying prompt engineering techniques
   */
  optimizePrompt: async (request: OptimizeRequest): Promise<OptimizationResponse> => {
    const response = await apiClient.post<OptimizationResponse>('/api/optimize', request);
    return response.data;
  },

  /**
   * Advanced optimization using DGEO, SHDT, or CDRAF strategies
   */
  advancedOptimize: async (request: AdvancedOptimizeRequest): Promise<AdvancedOptimizeResponse> => {
    const response = await apiClient.post<AdvancedOptimizeResponse>(
      '/api/optimize/advanced',
      request,
      { timeout: 180000 }
    );
    return response.data;
  },

  /**
   * Stream advanced optimization progress via SSE — phases report as they complete
   */
  advancedOptimizeStream: async (
    request: AdvancedOptimizeRequest,
    onEvent: (event: PhaseStreamEvent) => void,
    signal?: AbortSignal
  ): Promise<void> => {
    const response = await fetch(`${BASE_URL}/api/optimize/advanced/stream`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request),
      signal,
    });

    if (!response.ok) {
      throw new Error(`Optimization stream failed: ${response.status}`);
    }

    const reader = response.body?.getReader();
    if (!reader) throw new Error('No response body');

    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop() || '';

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const event = JSON.parse(line.slice(6)) as PhaseStreamEvent;
            onEvent(event);
          } catch {
            // skip malformed events
          }
        }
      }
    }
  },
};
