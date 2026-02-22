import React from 'react';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer
} from 'recharts';
import { Card } from '../common/Card';
import type { SHDTTrajectoryVersion } from '../../types/advanced.types';

interface TrajectoryViewerProps {
  trajectory: SHDTTrajectoryVersion[];
}

export const TrajectoryViewer: React.FC<TrajectoryViewerProps> = ({ trajectory }) => {
  if (!trajectory || trajectory.length === 0) return null;

  const chartData = trajectory.map((v) => ({
    version: `v${v.version}`,
    score: v.score,
    defectsRemaining: v.defects_remaining.length,
  }));

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
        <span className="text-2xl">📈</span> SHDT Trajectory
      </h3>

      {/* Score Chart */}
      <Card padding="lg">
        <h4 className="text-sm font-medium text-gray-700 mb-4">Score Over Iterations</h4>
        <ResponsiveContainer width="100%" height={220}>
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="version" fontSize={12} />
            <YAxis domain={[0, 10]} fontSize={12} />
            <Tooltip />
            <Line
              type="monotone"
              dataKey="score"
              stroke="#8b5cf6"
              strokeWidth={2}
              dot={{ r: 5, fill: '#8b5cf6' }}
              name="Score"
            />
          </LineChart>
        </ResponsiveContainer>
      </Card>

      {/* Version Timeline */}
      <div className="relative">
        <div className="absolute left-4 top-0 bottom-0 w-0.5 bg-purple-200" />
        <div className="space-y-4">
          {trajectory.map((v, i) => (
            <div key={v.version} className="relative pl-10">
              <div className={`absolute left-2.5 w-4 h-4 rounded-full border-2 ${
                i === trajectory.length - 1
                  ? 'bg-purple-500 border-purple-500'
                  : 'bg-white border-purple-300'
              }`} />

              <Card padding="md">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-semibold text-gray-900">
                    Version {v.version}
                  </span>
                  <div className="flex items-center gap-3">
                    <span className="text-sm font-bold text-purple-600">
                      {v.score.toFixed(1)}/10
                    </span>
                    {v.improvement > 0 && (
                      <span className="text-xs font-medium text-green-600 bg-green-50 px-2 py-0.5 rounded">
                        +{v.improvement.toFixed(1)}
                      </span>
                    )}
                  </div>
                </div>

                <div className="space-y-2 text-xs">
                  {v.defects_fixed.length > 0 && (
                    <div>
                      <span className="font-medium text-green-700">Fixed: </span>
                      <span className="text-gray-600">{v.defects_fixed.join(', ')}</span>
                    </div>
                  )}
                  {v.defects_introduced.length > 0 && (
                    <div>
                      <span className="font-medium text-red-700">Introduced: </span>
                      <span className="text-gray-600">{v.defects_introduced.join(', ')}</span>
                    </div>
                  )}
                  {v.defects_remaining.length > 0 && (
                    <div>
                      <span className="font-medium text-gray-500">Remaining: </span>
                      <span className="text-gray-400">{v.defects_remaining.join(', ')}</span>
                    </div>
                  )}
                </div>
              </Card>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
