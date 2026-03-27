import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import clsx from 'clsx';
import { Sparkles, Home, ScanSearch, Zap, BookOpen, History as HistoryIcon } from 'lucide-react';

export const Header: React.FC = () => {
  const location = useLocation();

  const navLinks = [
    { path: '/', label: 'Home', icon: Home },
    { path: '/analyze', label: 'Analyze', icon: ScanSearch },
    { path: '/optimize', label: 'Optimizer', icon: Zap },
    { path: '/history', label: 'History', icon: HistoryIcon },
  ];

  return (
    <header className="bg-dark-bg/90 backdrop-blur-md border-b border-dark-border sticky top-0 z-50">
      <div className="max-w-[1400px] mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center space-x-2 group">
            <div className="bg-gradient-primary p-2 rounded-xl">
              <Sparkles className="h-5 w-5 text-white" />
            </div>
            <span className="text-lg font-bold text-white">
              PromptOptix
            </span>
          </Link>

          {/* Navigation Pills */}
          <nav className="flex items-center space-x-2">
            {navLinks.map(link => {
              const Icon = link.icon;
              const isActive = location.pathname === link.path;

              return (
                <Link
                  key={link.path}
                  to={link.path}
                  className={clsx(
                    'flex items-center gap-2 px-4 py-2 rounded-full text-sm font-medium transition-all duration-300',
                    isActive
                      ? 'bg-gradient-primary text-white shadow-glow'
                      : 'text-gray-400 hover:text-white hover:bg-dark-card'
                  )}
                >
                  <Icon className="w-4 h-4" />
                  {link.label}
                </Link>
              );
            })}

            {/* Get Started Button */}
            <Link
              to="/optimize"
              className="ml-4 px-6 py-2 rounded-full bg-gradient-primary text-white text-sm font-semibold hover:shadow-glow-lg transition-all duration-300 hover:scale-105"
            >
              Get Started
            </Link>
          </nav>
        </div>
      </div>
    </header>
  );
};
