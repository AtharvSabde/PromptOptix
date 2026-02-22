import React from 'react';
import type { LucideIcon } from 'lucide-react';
import { TrendBadge } from './TrendBadge';

interface StatCardProps {
  icon: LucideIcon;
  value: string | number;
  label: string;
  trend?: number;
  trendLabel?: string;
  iconColor?: string;
  className?: string;
}

/**
 * StatCard component - Displays a statistic with icon, value, and optional trend
 * Used for dashboard metrics and key performance indicators
 */
export const StatCard: React.FC<StatCardProps> = ({
  icon: Icon,
  value,
  label,
  trend,
  trendLabel,
  iconColor = 'bg-gradient-primary',
  className = '',
}) => {
  return (
    <div
      className={`
        bg-dark-card border border-dark-border rounded-2xl p-6
        hover:scale-[1.02] hover:shadow-glow
        transition-all duration-300
        ${className}
      `}
    >
      <div className="flex items-start justify-between mb-4">
        <div className={`${iconColor} p-3 rounded-xl`}>
          <Icon className="w-6 h-6 text-white" />
        </div>
        {trend !== undefined && (
          <TrendBadge value={trend} label={trendLabel} />
        )}
      </div>

      <div className="mt-4">
        <div className="text-4xl font-bold text-white mb-1">
          {value}
        </div>
        <div className="text-gray-400 text-sm font-medium">
          {label}
        </div>
      </div>
    </div>
  );
};
