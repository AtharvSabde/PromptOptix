import { apiClient } from './client';
import type { AnalyzeRequest, AnalysisResponse } from '../types/analysis.types';

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface AgentStreamEvent {
  type: 'agent_start' | 'agent_complete' | 'final' | 'error';
  agent?: string;
  focus_area?: string;
  score?: number;
  defects_count?: number;
  summary?: string;
  status?: string;
  error?: string;
  // final event includes full AnalysisResponse fields
  overall_score?: number;
  defects?: AnalysisResponse['defects'];
  consensus?: number;
  agent_results?: AnalysisResponse['agent_results'];
  disagreements?: AnalysisResponse['disagreements'];
  metadata?: AnalysisResponse['metadata'];
}

export const analysisService = {
  /**
   * Analyze a prompt for defects using multi-agent consensus system
   */
  analyzePrompt: async (request: AnalyzeRequest): Promise<AnalysisResponse> => {
    const response = await apiClient.post<AnalysisResponse>('/api/analyze', request);
    return response.data;
  },

  /**
   * Stream analysis results via SSE — agents report in as they complete
   */
  analyzePromptStream: async (
    request: AnalyzeRequest,
    onEvent: (event: AgentStreamEvent) => void,
    signal?: AbortSignal
  ): Promise<void> => {
    const response = await fetch(`${BASE_URL}/api/analyze/stream`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request),
      signal,
    });

    if (!response.ok) {
      throw new Error(`Analysis stream failed: ${response.status}`);
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
            const event = JSON.parse(line.slice(6)) as AgentStreamEvent;
            onEvent(event);
          } catch {
            // skip malformed events
          }
        }
      }
    }
  },
};
