import React from 'react';

interface GradientTextProps {
  children: React.ReactNode;
  className?: string;
  variant?: 'primary' | 'secondary' | 'text';
}

/**
 * GradientText component - Renders text with gradient color effect
 * Used for hero headlines and emphasis text
 */
export const GradientText: React.FC<GradientTextProps> = ({
  children,
  className = '',
  variant = 'text'
}) => {
  const variantClasses = {
    primary: 'bg-gradient-primary',
    secondary: 'bg-gradient-secondary',
    text: 'bg-gradient-text',
  };

  return (
    <span
      className={`${variantClasses[variant]} bg-clip-text text-transparent bg-[length:200%_200%] animate-gradient ${className}`}
    >
      {children}
    </span>
  );
};
