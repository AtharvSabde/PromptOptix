import React from 'react';
import { Card } from '../common/Card';

interface PromptDiffProps {
  original: string;
  optimized: string;
  scoreBefore: number;
  scoreAfter: number;
}

export const PromptDiff: React.FC<PromptDiffProps> = ({
  original,
  optimized,
  scoreBefore,
  scoreAfter,
}) => {
  const improvement = scoreAfter - scoreBefore;

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Original */}
        <Card padding="lg">
          <div className="flex items-center justify-between mb-3">
            <h4 className="text-sm font-semibold text-gray-300">Original Prompt</h4>
            <span className="text-sm font-bold text-gray-400">{scoreBefore.toFixed(1)}/10</span>
          </div>
          <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-4 max-h-80 overflow-y-auto">
            <pre className="text-sm text-gray-300 whitespace-pre-wrap font-mono leading-relaxed">
              {original}
            </pre>
          </div>
        </Card>

        {/* Optimized */}
        <Card padding="lg">
          <div className="flex items-center justify-between mb-3">
            <h4 className="text-sm font-semibold text-gray-300">Optimized Prompt</h4>
            <div className="flex items-center gap-2">
              <span className="text-sm font-bold text-green-400">{scoreAfter.toFixed(1)}/10</span>
              {improvement > 0 && (
                <span className="text-xs font-medium text-green-400 bg-green-500/20 px-2 py-0.5 rounded">
                  +{improvement.toFixed(1)}
                </span>
              )}
            </div>
          </div>
          <div className="bg-green-500/10 border border-green-500/20 rounded-lg p-4 max-h-80 overflow-y-auto">
            <pre className="text-sm text-gray-300 whitespace-pre-wrap font-mono leading-relaxed">
              {optimized}
            </pre>
          </div>
        </Card>
      </div>
    </div>
  );
};
