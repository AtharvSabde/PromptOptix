import React, { useState } from 'react';
import { PageLayout } from '../components/layout/PageLayout';
import { Card } from '../components/common/Card';
import { Button } from '../components/common/Button';
import { useHistory } from '../hooks/useHistory';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell
} from 'recharts';
import { Clock, TrendingUp, Filter, RefreshCw } from 'lucide-react';


const STRATEGY_COLORS: Record<string, string> = {
  standard: '#3b82f6',
  dgeo: '#22c55e',
  shdt: '#8b5cf6',
  cdraf: '#f59e0b',
};

const STRATEGY_LABELS: Record<string, string> = {
  standard: 'Standard',
  dgeo: 'DGEO',
  shdt: 'SHDT',
  cdraf: 'CDRAF',
};

export const HistoryPage: React.FC = () => {
  const { records, stats, total, isLoading, fetchHistory } = useHistory();
  const [strategyFilter, setStrategyFilter] = useState<string>('all');

  const handleFilterChange = (strategy: string) => {
    setStrategyFilter(strategy);
    const params = strategy === 'all' ? {} : { strategy };
    fetchHistory(params);
  };

  // Prepare chart data from stats
  const strategyChartData = stats?.by_strategy
    ? Object.entries(stats.by_strategy).map(([key, val]) => ({
        name: STRATEGY_LABELS[key] || key,
        count: val.count,
        avgImprovement: val.avg_improvement,
        avgScore: val.avg_final_score,
        fill: STRATEGY_COLORS[key] || '#9ca3af',
      }))
    : [];

  const pieData = strategyChartData.filter(d => d.count > 0);

  return (
    <PageLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-white mb-2">Optimization History</h1>
            <p className="text-gray-400">
              Track past optimizations and performance across strategies
            </p>
          </div>
          <Button
            variant="outline"
            onClick={() => fetchHistory(strategyFilter === 'all' ? {} : { strategy: strategyFilter })}
            disabled={isLoading}
          >
            <RefreshCw className={`w-4 h-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
        </div>

        {/* Stats Overview */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Card padding="lg">
              <div className="text-center">
                <p className="text-3xl font-bold text-blue-600">{stats.total_optimizations}</p>
                <p className="text-sm text-gray-400 mt-1">Total Optimizations</p>
              </div>
            </Card>
            <Card padding="lg">
              <div className="text-center">
                <p className="text-3xl font-bold text-green-600">
                  +{stats.avg_improvement.toFixed(1)}
                </p>
                <p className="text-sm text-gray-400 mt-1">Avg Improvement</p>
              </div>
            </Card>
            <Card padding="lg">
              <div className="text-center">
                <p className="text-3xl font-bold text-purple-600">
                  +{stats.best_improvement.toFixed(1)}
                </p>
                <p className="text-sm text-gray-400 mt-1">Best Improvement</p>
              </div>
            </Card>
            <Card padding="lg">
              <div className="text-center">
                <p className="text-3xl font-bold text-white">
                  {Object.keys(stats.by_strategy).length}
                </p>
                <p className="text-sm text-gray-400 mt-1">Strategies Used</p>
              </div>
            </Card>
          </div>
        )}

        {/* Charts */}
        {stats && strategyChartData.length > 0 && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Bar Chart - Avg Improvement by Strategy */}
            <Card padding="lg">
              <h3 className="text-sm font-semibold text-gray-300 mb-4 flex items-center gap-2">
                <TrendingUp className="w-4 h-4" />
                Avg Improvement by Strategy
              </h3>
              <ResponsiveContainer width="100%" height={220}>
                <BarChart data={strategyChartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" fontSize={12} />
                  <YAxis fontSize={12} />
                  <Tooltip />
                  <Bar dataKey="avgImprovement" name="Avg Improvement" radius={[4, 4, 0, 0]}>
                    {strategyChartData.map((entry, i) => (
                      <Cell key={i} fill={entry.fill} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </Card>

            {/* Pie Chart - Usage Distribution */}
            <Card padding="lg">
              <h3 className="text-sm font-semibold text-gray-300 mb-4 flex items-center gap-2">
                <Clock className="w-4 h-4" />
                Strategy Usage Distribution
              </h3>
              <ResponsiveContainer width="100%" height={220}>
                <PieChart>
                  <Pie
                    data={pieData}
                    dataKey="count"
                    nameKey="name"
                    cx="50%"
                    cy="50%"
                    outerRadius={80}
                    label={({ name, percent }) => `${name} ${((percent ?? 0) * 100).toFixed(0)}%`}
                  >
                    {pieData.map((entry, i) => (
                      <Cell key={i} fill={entry.fill} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </Card>
          </div>
        )}

        {/* Filter */}
        <Card padding="md">
          <div className="flex items-center gap-3">
            <Filter className="w-4 h-4 text-gray-500" />
            <span className="text-sm font-medium text-gray-300">Filter:</span>
            {['all', 'standard', 'dgeo', 'shdt', 'cdraf'].map((s) => (
              <button
                key={s}
                onClick={() => handleFilterChange(s)}
                className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                  strategyFilter === s
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-300 hover:bg-gray-700'
                }`}
              >
                {s === 'all' ? 'All' : STRATEGY_LABELS[s] || s.toUpperCase()}
              </button>
            ))}
            <span className="ml-auto text-sm text-gray-400">{total} records</span>
          </div>
        </Card>

        {/* Records Table */}
        {isLoading ? (
          <Card padding="lg">
            <div className="text-center py-8">
              <div className="animate-spin h-8 w-8 border-4 border-blue-500 border-t-transparent rounded-full mx-auto mb-4" />
              <p className="text-gray-400">Loading history...</p>
            </div>
          </Card>
        ) : records.length === 0 ? (
          <Card padding="lg">
            <div className="text-center py-12">
              <Clock className="w-12 h-12 text-gray-300 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-300 mb-2">No optimization history yet</h3>
              <p className="text-sm text-gray-400">
                Run some optimizations to see them tracked here.
              </p>
            </div>
          </Card>
        ) : (
          <Card padding="none">
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-gray-200 bg-gray-50">
                    <th className="text-left px-4 py-3 font-medium text-gray-600">Prompt</th>
                    <th className="text-center px-4 py-3 font-medium text-gray-600">Strategy</th>
                    <th className="text-center px-4 py-3 font-medium text-gray-600">Before</th>
                    <th className="text-center px-4 py-3 font-medium text-gray-600">After</th>
                    <th className="text-center px-4 py-3 font-medium text-gray-600">Improvement</th>
                    <th className="text-center px-4 py-3 font-medium text-gray-600">Date</th>
                  </tr>
                </thead>
                <tbody>
                  {records.map((record) => (
                    <tr key={record.id} className="border-b border-gray-100 hover:bg-gray-50">
                      <td className="px-4 py-3 max-w-xs">
                        <p className="text-gray-900 truncate" title={record.original_prompt}>
                          {record.original_prompt.substring(0, 80)}
                          {record.original_prompt.length > 80 ? '...' : ''}
                        </p>
                      </td>
                      <td className="px-4 py-3 text-center">
                        <span
                          className="inline-block px-2.5 py-1 rounded-full text-xs font-medium text-white"
                          style={{ backgroundColor: STRATEGY_COLORS[record.strategy] || '#9ca3af' }}
                        >
                          {STRATEGY_LABELS[record.strategy] || record.strategy}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-center text-gray-600">
                        {record.score_before.toFixed(1)}
                      </td>
                      <td className="px-4 py-3 text-center font-medium text-green-600">
                        {record.score_after.toFixed(1)}
                      </td>
                      <td className="px-4 py-3 text-center">
                        <span className={`font-medium ${record.improvement > 0 ? 'text-green-600' : 'text-gray-500'}`}>
                          {record.improvement > 0 ? '+' : ''}{record.improvement.toFixed(1)}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-center text-gray-500 text-xs">
                        {new Date(record.created_at).toLocaleDateString()}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>
        )}
      </div>
    </PageLayout>
  );
};
