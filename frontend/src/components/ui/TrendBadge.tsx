import React from 'react';
import { TrendingUp, TrendingDown } from 'lucide-react';

interface TrendBadgeProps {
  value: number;
  label?: string;
  className?: string;
}

/**
 * TrendBadge component - Shows trend indicator with arrow and percentage
 * Positive trends are green, negative trends are red
 */
export const TrendBadge: React.FC<TrendBadgeProps> = ({
  value,
  label,
  className = ''
}) => {
  const isPositive = value >= 0;
  const Icon = isPositive ? TrendingUp : TrendingDown;
  const colorClass = isPositive ? 'text-green-500 bg-green-500/10' : 'text-red-500 bg-red-500/10';

  return (
    <div className={`flex items-center gap-1 px-2 py-1 rounded-lg ${colorClass} ${className}`}>
      <Icon className="w-3 h-3" />
      <span className="text-xs font-semibold">
        {Math.abs(value)}%
      </span>
      {label && (
        <span className="text-xs text-gray-400">
          {label}
        </span>
      )}
    </div>
  );
};
