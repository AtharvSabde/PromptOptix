import React from 'react';
import clsx from 'clsx';
import { DefectSeverity } from '../../types/analysis.types';
import { SEVERITY_COLORS } from '../../utils/constants';

interface BadgeProps {
  severity: DefectSeverity;
  children: React.ReactNode;
  className?: string;
}

export const Badge: React.FC<BadgeProps> = ({ severity, children, className }) => {
  const colors = SEVERITY_COLORS[severity];

  return (
    <span
      className={clsx(
        'inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold',
        colors.badge,
        className
      )}
    >
      {children}
    </span>
  );
};
