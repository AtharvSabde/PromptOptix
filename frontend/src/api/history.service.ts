import { apiClient } from './client';
import type {
  HistoryResponse,
  HistoryEntry,
  HistoryStats,
  TechniqueEffectiveness,
} from '../types/advanced.types';

export const historyService = {
  getHistory: async (params?: {
    strategy?: string;
    limit?: number;
    offset?: number;
  }): Promise<HistoryResponse> => {
    const response = await apiClient.get<HistoryResponse>('/api/history', { params });
    return response.data;
  },

  getHistoryById: async (id: number): Promise<HistoryEntry> => {
    const response = await apiClient.get<HistoryEntry>(`/api/history/${id}`);
    return response.data;
  },

  getStats: async (): Promise<HistoryStats> => {
    const response = await apiClient.get<HistoryStats>('/api/history/stats');
    return response.data;
  },

  getTechniqueEffectiveness: async (): Promise<TechniqueEffectiveness[]> => {
    const response = await apiClient.get<TechniqueEffectiveness[]>('/api/techniques/effectiveness');
    return response.data;
  },
};
