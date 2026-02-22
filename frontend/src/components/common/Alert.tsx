import React from 'react';
import clsx from 'clsx';
import { AlertCircle, CheckCircle, Info, XCircle, X } from 'lucide-react';

interface AlertProps {
  variant?: 'info' | 'success' | 'warning' | 'error';
  title?: string;
  children: React.ReactNode;
  onClose?: () => void;
  className?: string;
}

export const Alert: React.FC<AlertProps> = ({
  variant = 'info',
  title,
  children,
  onClose,
  className,
}) => {
  const variantStyles = {
    info: {
      container: 'bg-accent-cyan/10 border-l-4 border-l-accent-cyan',
      icon: 'text-accent-cyan',
      title: 'text-white',
      text: 'text-gray-300',
      Icon: Info,
    },
    success: {
      container: 'bg-green-500/10 border-l-4 border-l-green-500',
      icon: 'text-green-500',
      title: 'text-white',
      text: 'text-gray-300',
      Icon: CheckCircle,
    },
    warning: {
      container: 'bg-yellow-500/10 border-l-4 border-l-yellow-500',
      icon: 'text-yellow-500',
      title: 'text-white',
      text: 'text-gray-300',
      Icon: AlertCircle,
    },
    error: {
      container: 'bg-red-500/10 border-l-4 border-l-red-500',
      icon: 'text-red-500',
      title: 'text-white',
      text: 'text-gray-300',
      Icon: XCircle,
    },
  };

  const styles = variantStyles[variant];
  const Icon = styles.Icon;

  return (
    <div
      className={clsx(
        'rounded-xl p-4 backdrop-blur-sm',
        styles.container,
        className
      )}
    >
      <div className="flex">
        <div className="flex-shrink-0">
          <Icon className={clsx('h-5 w-5', styles.icon)} />
        </div>
        <div className="ml-3 flex-1">
          {title && (
            <h3 className={clsx('text-sm font-semibold', styles.title)}>
              {title}
            </h3>
          )}
          <div className={clsx('text-sm', title ? 'mt-1' : '', styles.text)}>
            {children}
          </div>
        </div>
        {onClose && (
          <div className="ml-auto pl-3">
            <button
              onClick={onClose}
              className={clsx(
                'inline-flex rounded-md p-1.5 hover:bg-white/10 transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-dark-bg',
                styles.icon
              )}
            >
              <span className="sr-only">Dismiss</span>
              <X className="h-5 w-5" />
            </button>
          </div>
        )}
      </div>
    </div>
  );
};
