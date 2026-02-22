import React from 'react';
import { Card } from '../common/Card';
import type { CritiqueRound } from '../../types/advanced.types';

interface CritiqueViewerProps {
  rounds: CritiqueRound[];
}

const agentColors: Record<string, string> = {
  clarity: 'blue',
  structure: 'green',
  context: 'purple',
  security: 'red',
};

const getColor = (agent: string) => {
  const key = agent.toLowerCase().replace('_agent', '').replace('agent', '');
  return agentColors[key] || 'gray';
};

export const CritiqueViewer: React.FC<CritiqueViewerProps> = ({ rounds }) => {
  if (!rounds || rounds.length === 0) return null;

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
        <span className="text-2xl">🔍</span> CDRAF Agent Critiques
      </h3>

      {rounds.map((round) => (
        <Card key={round.round} padding="lg">
          <div className="flex items-center justify-between mb-4">
            <h4 className="text-sm font-semibold text-gray-900">
              Round {round.round}
            </h4>
            <div className="flex items-center gap-3 text-xs">
              <span className="text-gray-500">
                {round.issues_found} issues found
              </span>
              {round.score_before !== undefined && (
                <span className="text-gray-500">
                  Score: {round.score_before.toFixed(1)}
                </span>
              )}
            </div>
          </div>

          {/* Agent Feedback */}
          <div className="space-y-3">
            {round.agent_feedback.map((critique) => {
              const color = getColor(critique.agent);
              return (
                <div
                  key={critique.agent}
                  className={`border-l-4 pl-4 py-2 border-${color}-400`}
                  style={{ borderLeftColor: color === 'blue' ? '#60a5fa' : color === 'green' ? '#4ade80' : color === 'purple' ? '#a78bfa' : color === 'red' ? '#f87171' : '#9ca3af' }}
                >
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-sm font-medium text-gray-900 capitalize">
                      {critique.agent.replace('_', ' ')}
                    </span>
                    <span className="text-xs text-gray-500">
                      ({critique.focus_area})
                    </span>
                  </div>

                  {critique.issues.length === 0 ? (
                    <p className="text-xs text-green-600">No issues found</p>
                  ) : (
                    <div className="space-y-1.5">
                      {critique.issues.map((issue) => (
                        <div key={issue.defect_id} className="text-xs">
                          <div className="flex items-center gap-2">
                            <span className="font-mono text-gray-500">{issue.defect_id}</span>
                            <span className="font-medium text-gray-800">{issue.name}</span>
                            <span className={`px-1.5 py-0.5 rounded text-xs ${
                              issue.severity === 'high'
                                ? 'bg-red-100 text-red-700'
                                : issue.severity === 'medium'
                                ? 'bg-yellow-100 text-yellow-700'
                                : 'bg-gray-100 text-gray-600'
                            }`}>
                              {issue.severity}
                            </span>
                            <span className="text-gray-400">
                              {(issue.confidence * 100).toFixed(0)}% confidence
                            </span>
                          </div>
                          <p className="text-gray-600 mt-0.5">{issue.description}</p>
                          <p className="text-blue-600 mt-0.5">Fix: {issue.remediation}</p>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              );
            })}
          </div>

          {/* Issues Addressed */}
          {round.issues_addressed && round.issues_addressed.length > 0 && (
            <div className="mt-4 pt-3 border-t border-gray-100">
              <h5 className="text-xs font-medium text-gray-700 mb-2">Issues Addressed</h5>
              <div className="space-y-1">
                {round.issues_addressed.map((item) => (
                  <div key={item.issue_number} className="flex items-center gap-2 text-xs">
                    <span className="text-green-500">✓</span>
                    <span className="text-gray-500 capitalize">{item.agent}</span>
                    <span className="text-gray-700">{item.fix_applied}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </Card>
      ))}
    </div>
  );
};
