import React from 'react';
import clsx from 'clsx';

interface CardProps {
  children: React.ReactNode;
  className?: string;
  padding?: 'none' | 'sm' | 'md' | 'lg';
  shadow?: 'none' | 'sm' | 'md' | 'lg';
  variant?: 'default' | 'glass' | 'gradient';
  hover?: boolean;
}

export const Card: React.FC<CardProps> = ({
  children,
  className,
  padding = 'md',
  shadow = 'md',
  variant = 'default',
  hover = true,
}) => {
  const paddingStyles = {
    none: '',
    sm: 'p-3',
    md: 'p-5',
    lg: 'p-6',
  };

  const shadowStyles = {
    none: '',
    sm: 'shadow-sm',
    md: 'shadow-md',
    lg: 'shadow-lg',
  };

  const variantStyles = {
    default: 'bg-dark-card border border-dark-border',
    glass: 'bg-dark-card/80 backdrop-blur-md border border-dark-border',
    gradient: 'bg-gradient-card border border-dark-border',
  };

  const hoverStyles = hover ? 'hover:scale-[1.01] hover:shadow-glow transition-all duration-300' : '';

  return (
    <div
      className={clsx(
        'rounded-2xl',
        variantStyles[variant],
        paddingStyles[padding],
        shadowStyles[shadow],
        hoverStyles,
        className
      )}
    >
      {children}
    </div>
  );
};
