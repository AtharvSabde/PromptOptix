import { DefectSeverity } from '../types/analysis.types';

// Severity color coding for Tailwind CSS
export const SEVERITY_COLORS = {
  [DefectSeverity.CRITICAL]: {
    bg: 'bg-red-100',
    text: 'text-red-800',
    border: 'border-red-500',
    badge: 'bg-red-500 text-white',
  },
  [DefectSeverity.HIGH]: {
    bg: 'bg-orange-100',
    text: 'text-orange-800',
    border: 'border-orange-500',
    badge: 'bg-orange-500 text-white',
  },
  [DefectSeverity.MEDIUM]: {
    bg: 'bg-yellow-100',
    text: 'text-yellow-800',
    border: 'border-yellow-500',
    badge: 'bg-yellow-500 text-white',
  },
  [DefectSeverity.LOW]: {
    bg: 'bg-blue-100',
    text: 'text-blue-800',
    border: 'border-blue-500',
    badge: 'bg-blue-500 text-white',
  },
};

// Agent icons
export const AGENT_ICONS = {
  ClarityAgent: '👁️',
  StructureAgent: '📋',
  ContextAgent: '🧠',
  SecurityAgent: '🛡️',
};

// Agent names mapping
export const AGENT_NAMES = {
  ClarityAgent: 'Clarity Agent',
  StructureAgent: 'Structure Agent',
  ContextAgent: 'Context Agent',
  SecurityAgent: 'Security Agent',
};

// Score color gradient
export const getScoreColor = (score: number): string => {
  if (score >= 8) return 'text-green-600';
  if (score >= 6) return 'text-yellow-600';
  if (score >= 4) return 'text-orange-600';
  return 'text-red-600';
};

export const getScoreBgColor = (score: number): string => {
  if (score >= 8) return 'bg-green-100';
  if (score >= 6) return 'bg-yellow-100';
  if (score >= 4) return 'bg-orange-100';
  return 'bg-red-100';
};

// Validation limits
export const VALIDATION_LIMITS = {
  MIN_PROMPT_LENGTH: 10,
  MAX_PROMPT_LENGTH: 50000,
};

// API endpoints
export const API_ENDPOINTS = {
  ANALYZE: '/api/analyze',
  OPTIMIZE: '/api/optimize',
  TECHNIQUES: '/api/techniques',
  HEALTH: '/api/health',
};
