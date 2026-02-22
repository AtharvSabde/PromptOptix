import React from 'react';

interface LiveIndicatorProps {
  text?: string;
  className?: string;
}

/**
 * LiveIndicator component - Shows a pulsing green dot with "Live" text
 * Used to indicate real-time processing or active status
 */
export const LiveIndicator: React.FC<LiveIndicatorProps> = ({
  text = 'Live Processing',
  className = ''
}) => {
  return (
    <div className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-green-500/10 ${className}`}>
      <span className="relative flex h-2 w-2">
        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-500 opacity-75"></span>
        <span className="relative inline-flex rounded-full h-2 w-2 bg-green-500"></span>
      </span>
      <span className="text-xs font-medium text-green-500">
        {text}
      </span>
    </div>
  );
};
