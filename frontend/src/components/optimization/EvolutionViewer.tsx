import React from 'react';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  ResponsiveContainer
} from 'recharts';
import { Card } from '../common/Card';
import type { DGEOGeneration, DGEOVariant } from '../../types/advanced.types';

interface EvolutionViewerProps {
  generations: DGEOGeneration[];
  finalPopulation?: DGEOVariant[];
}

export const EvolutionViewer: React.FC<EvolutionViewerProps> = ({
  generations,
  finalPopulation,
}) => {
  if (!generations || generations.length === 0) return null;

  const chartData = generations.map((gen) => ({
    generation: `Gen ${gen.generation}`,
    best: gen.best_score,
    avg: gen.avg_score,
  }));

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
        <span className="text-2xl">🧬</span> DGEO Evolution History
      </h3>

      {/* Score Chart */}
      <Card padding="lg">
        <h4 className="text-sm font-medium text-gray-700 mb-4">Score Progression</h4>
        <ResponsiveContainer width="100%" height={250}>
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="generation" fontSize={12} />
            <YAxis domain={[0, 10]} fontSize={12} />
            <Tooltip />
            <Legend />
            <Line
              type="monotone"
              dataKey="best"
              stroke="#22c55e"
              strokeWidth={2}
              name="Best Score"
              dot={{ r: 4 }}
            />
            <Line
              type="monotone"
              dataKey="avg"
              stroke="#3b82f6"
              strokeWidth={2}
              strokeDasharray="5 5"
              name="Avg Score"
              dot={{ r: 3 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </Card>

      {/* Generation Details */}
      <div className="space-y-3">
        {generations.map((gen) => (
          <Card key={gen.generation} padding="md">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-semibold text-gray-900">
                Generation {gen.generation}
              </span>
              <span className="text-xs text-gray-500">
                {gen.variants.length} variants
              </span>
            </div>
            <div className="flex flex-wrap gap-2">
              {gen.variants
                .sort((a, b) => b.score - a.score)
                .map((v) => (
                  <div
                    key={v.id}
                    className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-gray-50 text-xs"
                  >
                    <span className="font-mono font-medium text-gray-700">{v.id}</span>
                    <span className={`font-bold ${v.score >= 7 ? 'text-green-600' : v.score >= 5 ? 'text-yellow-600' : 'text-red-600'}`}>
                      {v.score.toFixed(1)}
                    </span>
                    <span className="text-gray-500">{v.focus}</span>
                    {v.defects_remaining > 0 && (
                      <span className="text-red-400">{v.defects_remaining} defects</span>
                    )}
                  </div>
                ))}
            </div>
          </Card>
        ))}
      </div>

      {/* Final Population */}
      {finalPopulation && finalPopulation.length > 0 && (
        <Card padding="lg">
          <h4 className="text-sm font-medium text-gray-700 mb-3">Final Population (Top Variants)</h4>
          <div className="space-y-2">
            {finalPopulation
              .sort((a, b) => b.score - a.score)
              .slice(0, 5)
              .map((v, i) => (
                <div
                  key={v.id}
                  className="flex items-center gap-3 p-3 rounded-lg bg-gray-50"
                >
                  <span className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold ${i === 0 ? 'bg-yellow-100 text-yellow-700' : 'bg-gray-200 text-gray-600'}`}>
                    {i + 1}
                  </span>
                  <span className="font-mono text-sm text-gray-700">{v.id}</span>
                  <span className="text-lg font-bold text-green-600">{v.score.toFixed(1)}</span>
                  <span className="text-sm text-gray-500 flex-1">{v.focus}</span>
                  {v.parent_ids && v.parent_ids.length > 0 && (
                    <span className="text-xs text-gray-400">
                      Parents: {v.parent_ids.join(', ')}
                    </span>
                  )}
                </div>
              ))}
          </div>
        </Card>
      )}
    </div>
  );
};
