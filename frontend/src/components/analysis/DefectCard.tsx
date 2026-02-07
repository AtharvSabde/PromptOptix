import React, { useState } from 'react';
import { Card } from '../common/Card';
import { Badge } from '../common/Badge';
import type { Defect } from '../../types/analysis.types';
import { AGENT_ICONS, SEVERITY_COLORS } from '../../utils/constants';
import { formatConfidence } from '../../utils/formatters';
import { ChevronDown, ChevronUp } from 'lucide-react';
import clsx from 'clsx';

interface DefectCardProps {
  defect: Defect;
}

export const DefectCard: React.FC<DefectCardProps> = ({ defect }) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const colors = SEVERITY_COLORS[defect.severity];

  return (
    <Card
      padding="md"
      shadow="sm"
      className={clsx('border-l-4', colors.border)}
    >
      {/* Header */}
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-2">
            <span className="text-sm font-mono text-gray-500">{defect.id}</span>
            <h3 className="text-lg font-semibold text-gray-900">{defect.name}</h3>
            <Badge severity={defect.severity}>{defect.severity.toUpperCase()}</Badge>
          </div>

          {/* Confidence */}
          <div className="flex items-center gap-4 mb-3">
            <div className="flex-1">
              <div className="flex justify-between text-xs text-gray-600 mb-1">
                <span>Confidence</span>
                <span className="font-medium">{formatConfidence(defect.confidence)}</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-blue-600 h-2 rounded-full transition-all"
                  style={{ width: `${defect.confidence * 100}%` }}
                />
              </div>
            </div>

            {defect.consensus !== undefined && (
              <div className="text-xs text-gray-600">
                <span className="font-medium">Consensus:</span> {formatConfidence(defect.consensus)}
                <span className="text-gray-500 ml-1">
                  ({defect.detected_by.length}/{4})
                </span>
              </div>
            )}
          </div>

          {/* Description */}
          <p className="text-sm text-gray-700 mb-3">{defect.description}</p>

          {/* Detected by agents */}
          <div className="flex flex-wrap gap-2 mb-3">
            {defect.detected_by.map(agent => (
              <span
                key={agent}
                className="inline-flex items-center px-2 py-1 rounded-md bg-gray-100 text-xs font-medium text-gray-700"
              >
                <span className="mr-1">{AGENT_ICONS[agent as keyof typeof AGENT_ICONS]}</span>
                {agent}
              </span>
            ))}
          </div>
        </div>

        {/* Expand/Collapse button */}
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="ml-4 p-1 rounded-md hover:bg-gray-100 transition-colors"
        >
          {isExpanded ? (
            <ChevronUp className="h-5 w-5 text-gray-500" />
          ) : (
            <ChevronDown className="h-5 w-5 text-gray-500" />
          )}
        </button>
      </div>

      {/* Expanded details */}
      {isExpanded && (
        <div className="mt-4 pt-4 border-t border-gray-200 space-y-3">
          {/* Evidence */}
          <div>
            <h4 className="text-sm font-medium text-gray-700 mb-1 flex items-center gap-1">
              📝 Evidence
            </h4>
            <div className="bg-gray-50 p-3 rounded-md">
              <p className="text-sm text-gray-800 font-mono">{defect.evidence}</p>
            </div>
          </div>

          {/* Explanation */}
          {defect.explanation && (
            <div>
              <h4 className="text-sm font-medium text-gray-700 mb-1 flex items-center gap-1">
                💭 Explanation
              </h4>
              <p className="text-sm text-gray-700">{defect.explanation}</p>
            </div>
          )}

          {/* Remediation */}
          <div>
            <h4 className="text-sm font-medium text-gray-700 mb-1 flex items-center gap-1">
              💡 How to Fix
            </h4>
            <p className="text-sm text-gray-700">{defect.remediation}</p>
          </div>
        </div>
      )}
    </Card>
  );
};
