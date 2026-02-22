import React from 'react';

interface GlassCardProps {
  children: React.ReactNode;
  className?: string;
  hover?: boolean;
  glow?: boolean;
}

/**
 * GlassCard component - Card with glassmorphism effect
 * Features backdrop blur and subtle borders
 */
export const GlassCard: React.FC<GlassCardProps> = ({
  children,
  className = '',
  hover = true,
  glow = false,
}) => {
  const hoverClass = hover ? 'hover:scale-[1.02] hover:shadow-glow' : '';
  const glowClass = glow ? 'shadow-glow' : '';

  return (
    <div
      className={`
        bg-dark-card/80 backdrop-blur-md
        border border-dark-border
        rounded-2xl p-6
        transition-all duration-300
        ${hoverClass}
        ${glowClass}
        ${className}
      `}
    >
      {children}
    </div>
  );
};
