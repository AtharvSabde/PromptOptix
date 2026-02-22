import React from 'react';
import clsx from 'clsx';
import { motion } from 'framer-motion';
import { STRATEGIES, type OptimizationStrategy } from '../../types/advanced.types';

interface StrategySelectorProps {
  selected: OptimizationStrategy;
  onSelect: (strategy: OptimizationStrategy) => void;
  disabled?: boolean;
}

export const StrategySelector: React.FC<StrategySelectorProps> = ({
  selected,
  onSelect,
  disabled = false,
}) => {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {STRATEGIES.map((strategy) => {
        const isSelected = selected === strategy.id;

        return (
          <motion.button
            key={strategy.id}
            whileHover={disabled ? {} : { scale: 1.02 }}
            whileTap={disabled ? {} : { scale: 0.98 }}
            onClick={() => !disabled && onSelect(strategy.id)}
            disabled={disabled}
            className={clsx(
              'relative text-left p-4 rounded-xl border-2 transition-colors',
              'focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2',
              isSelected
                ? 'border-blue-500 bg-blue-50 shadow-md'
                : 'border-gray-200 bg-white hover:border-gray-300',
              disabled && 'opacity-50 cursor-not-allowed'
            )}
          >
            {isSelected && (
              <div className="absolute top-2 right-2 w-3 h-3 rounded-full bg-blue-500" />
            )}

            <div className="text-2xl mb-2">{strategy.icon}</div>
            <h3 className="text-lg font-semibold text-gray-900 mb-1">
              {strategy.name}
            </h3>
            <p className="text-xs text-gray-500 mb-3 leading-relaxed">
              {strategy.description}
            </p>

            <div className="space-y-1 text-xs">
              <div className="flex justify-between text-gray-500">
                <span>Time</span>
                <span className="font-medium text-gray-700">{strategy.estimatedTime}</span>
              </div>
              <div className="flex justify-between text-gray-500">
                <span>LLM Calls</span>
                <span className="font-medium text-gray-700">{strategy.estimatedCalls}</span>
              </div>
              <div className="flex justify-between text-gray-500">
                <span>Best for</span>
                <span className="font-medium text-gray-700">{strategy.bestFor}</span>
              </div>
            </div>
          </motion.button>
        );
      })}
    </div>
  );
};
