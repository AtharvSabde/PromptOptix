import { useState, useCallback, useEffect } from 'react';
import { historyService } from '../api/history.service';
import type { HistoryEntry, HistoryStats } from '../types/advanced.types';
import type { ApiError } from '../api/client';

export const useHistory = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<ApiError | null>(null);
  const [records, setRecords] = useState<HistoryEntry[]>([]);
  const [stats, setStats] = useState<HistoryStats | null>(null);
  const [total, setTotal] = useState(0);

  const fetchHistory = useCallback(async (params?: {
    strategy?: string;
    limit?: number;
    offset?: number;
  }) => {
    setIsLoading(true);
    setError(null);

    try {
      const result = await historyService.getHistory(params);
      setRecords(result.records);
      setStats(result.stats);
      setTotal(result.total);
      return result;
    } catch (err) {
      const apiError = err as ApiError;
      setError(apiError);
      throw apiError;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const fetchStats = useCallback(async () => {
    try {
      const result = await historyService.getStats();
      setStats(result);
      return result;
    } catch (err) {
      // Stats fetch is non-critical, silently fail
      console.error('Failed to fetch stats:', err);
    }
  }, []);

  // Load on mount
  useEffect(() => {
    fetchHistory();
  }, [fetchHistory]);

  return {
    records,
    stats,
    total,
    isLoading,
    error,
    fetchHistory,
    fetchStats,
  };
};
