import React from 'react';

interface FloatingOrbProps {
  size?: 'sm' | 'md' | 'lg';
  color?: 'purple' | 'cyan' | 'pink';
  className?: string;
  delay?: number;
}

/**
 * FloatingOrb component - Decorative floating circle with blur effect
 * Used for background decoration
 */
export const FloatingOrb: React.FC<FloatingOrbProps> = ({
  size = 'md',
  color = 'purple',
  className = '',
  delay = 0,
}) => {
  const sizeClasses = {
    sm: 'w-32 h-32',
    md: 'w-48 h-48',
    lg: 'w-64 h-64',
  };

  const colorClasses = {
    purple: 'bg-primary-from',
    cyan: 'bg-accent-cyan',
    pink: 'bg-primary-to',
  };

  return (
    <div
      className={`${sizeClasses[size]} ${colorClasses[color]} rounded-full blur-3xl opacity-20 absolute animate-float ${className}`}
      style={{ animationDelay: `${delay}s` }}
    />
  );
};
