import React from 'react';
import { Plus } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

interface FloatingActionButtonProps {
  onClick?: () => void;
  icon?: React.ReactNode;
  to?: string;
  className?: string;
}

/**
 * FloatingActionButton (FAB) - Fixed position button at bottom-right
 * Used for primary actions like "Create New" or "Start Optimizing"
 */
export const FloatingActionButton: React.FC<FloatingActionButtonProps> = ({
  onClick,
  icon,
  to = '/optimize',
  className = ''
}) => {
  const navigate = useNavigate();

  const handleClick = () => {
    if (onClick) {
      onClick();
    } else if (to) {
      navigate(to);
    }
  };

  return (
    <button
      onClick={handleClick}
      className={`
        fixed bottom-8 right-8 z-50
        w-14 h-14
        bg-gradient-primary
        rounded-full
        flex items-center justify-center
        shadow-glow-lg
        hover:scale-110 hover:rotate-90
        transition-all duration-300
        group
        ${className}
      `}
      aria-label="Quick action"
    >
      {icon || <Plus className="w-6 h-6 text-white" />}
    </button>
  );
};
