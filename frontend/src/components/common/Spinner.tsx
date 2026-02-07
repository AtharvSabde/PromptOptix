import React from 'react';
import clsx from 'clsx';
import { Loader2 } from 'lucide-react';

interface SpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

export const Spinner: React.FC<SpinnerProps> = ({ size = 'md', className }) => {
  const sizeStyles = {
    sm: 'h-4 w-4',
    md: 'h-8 w-8',
    lg: 'h-12 w-12',
  };

  return (
    <Loader2
      className={clsx(
        'animate-spin text-blue-600',
        sizeStyles[size],
        className
      )}
    />
  );
};

interface LoadingProps {
  message?: string;
  subMessage?: string;
}

export const Loading: React.FC<LoadingProps> = ({ message = 'Loading...', subMessage }) => {
  return (
    <div className="flex flex-col items-center justify-center py-12">
      <Spinner size="lg" />
      <p className="mt-4 text-lg font-medium text-gray-700">{message}</p>
      {subMessage && (
        <p className="mt-2 text-sm text-gray-500">{subMessage}</p>
      )}
    </div>
  );
};
