import React from 'react';
import { Card } from '../common/Card';
import { formatScore } from '../../utils/formatters';
import { getScoreColor } from '../../utils/constants';

interface ScoreDisplayProps {
  score: number;
  title?: string;
}

export const ScoreDisplay: React.FC<ScoreDisplayProps> = ({
  score,
  title = 'Overall Prompt Quality',
}) => {
  const percentage = (score / 10) * 100;
  const scoreColor = getScoreColor(score);

  return (
    <Card padding="lg" className="text-center">
      <h3 className="text-sm font-medium text-gray-300 mb-4">{title}</h3>

      {/* Circular progress indicator */}
      <div className="relative inline-flex items-center justify-center">
        <svg className="transform -rotate-90 w-32 h-32">
          {/* Background circle */}
          <circle
            className="text-gray-200"
            strokeWidth="8"
            stroke="currentColor"
            fill="transparent"
            r="56"
            cx="64"
            cy="64"
          />
          {/* Progress circle */}
          <circle
            className={scoreColor}
            strokeWidth="8"
            strokeDasharray={351.86}
            strokeDashoffset={351.86 - (351.86 * percentage) / 100}
            strokeLinecap="round"
            stroke="currentColor"
            fill="transparent"
            r="56"
            cx="64"
            cy="64"
          />
        </svg>

        {/* Score text */}
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className={`text-4xl font-bold ${scoreColor}`}>
            {formatScore(score)}
          </span>
          <span className="text-sm text-gray-500">/ 10</span>
        </div>
      </div>

      {/* Score interpretation */}
      <div className="mt-4">
        <p className="text-sm text-gray-300">
          {score >= 8 && 'Excellent! Your prompt is well-structured.'}
          {score >= 6 && score < 8 && 'Good prompt with minor improvements possible.'}
          {score >= 4 && score < 6 && 'Fair prompt. Several issues need attention.'}
          {score < 4 && 'Poor prompt. Significant improvements required.'}
        </p>
      </div>
    </Card>
  );
};
