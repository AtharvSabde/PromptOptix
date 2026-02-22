import React from 'react';
import { Header } from './Header';
import { FloatingOrb } from '../ui/FloatingOrb';
import { FloatingActionButton } from '../ui/FloatingActionButton';

interface PageLayoutProps {
  children: React.ReactNode;
  maxWidth?: 'sm' | 'md' | 'lg' | 'xl' | '2xl' | '7xl' | 'full';
  showFAB?: boolean;
}

export const PageLayout: React.FC<PageLayoutProps> = ({
  children,
  maxWidth = '7xl',
  showFAB = true,
}) => {
  const maxWidthClasses = {
    sm: 'max-w-sm',
    md: 'max-w-md',
    lg: 'max-w-lg',
    xl: 'max-w-xl',
    '2xl': 'max-w-2xl',
    '7xl': 'max-w-7xl',
    full: 'max-w-[1400px]',
  };

  return (
    <div className="min-h-screen bg-dark-bg relative overflow-hidden">
      {/* Floating Decorative Orbs */}
      <FloatingOrb
        size="lg"
        color="purple"
        className="top-20 -left-32"
        delay={0}
      />
      <FloatingOrb
        size="md"
        color="cyan"
        className="top-1/3 right-10"
        delay={2}
      />
      <FloatingOrb
        size="md"
        color="pink"
        className="bottom-32 left-1/4"
        delay={4}
      />
      <FloatingOrb
        size="sm"
        color="purple"
        className="bottom-20 right-1/4"
        delay={1}
      />

      {/* Header */}
      <Header />

      {/* Main Content */}
      <main className={`${maxWidthClasses[maxWidth]} mx-auto px-4 sm:px-6 lg:px-8 py-8 relative z-10`}>
        {children}
      </main>

      {/* Floating Action Button */}
      {showFAB && <FloatingActionButton />}
    </div>
  );
};
