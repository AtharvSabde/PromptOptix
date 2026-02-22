import { DefectSeverity } from '../types/analysis.types';

// Severity color coding for Tailwind CSS (Dark Theme)
export const SEVERITY_COLORS = {
  [DefectSeverity.CRITICAL]: {
    bg: 'bg-red-500/10',
    text: 'text-red-400',
    border: 'border-red-500',
    badge: 'bg-red-500 text-white shadow-[0_0_15px_rgba(239,68,68,0.4)]',
  },
  [DefectSeverity.HIGH]: {
    bg: 'bg-orange-500/10',
    text: 'text-orange-400',
    border: 'border-orange-500',
    badge: 'bg-orange-500 text-white shadow-[0_0_15px_rgba(249,115,22,0.4)]',
  },
  [DefectSeverity.MEDIUM]: {
    bg: 'bg-yellow-500/10',
    text: 'text-yellow-400',
    border: 'border-yellow-500',
    badge: 'bg-yellow-500 text-white shadow-[0_0_15px_rgba(234,179,8,0.4)]',
  },
  [DefectSeverity.LOW]: {
    bg: 'bg-green-500/10',
    text: 'text-green-400',
    border: 'border-green-500',
    badge: 'bg-green-500 text-white shadow-[0_0_15px_rgba(16,185,129,0.4)]',
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

// Score color gradient (Dark Theme)
export const getScoreColor = (score: number): string => {
  if (score >= 8) return 'text-green-400';
  if (score >= 6) return 'text-yellow-400';
  if (score >= 4) return 'text-orange-400';
  return 'text-red-400';
};

export const getScoreBgColor = (score: number): string => {
  if (score >= 8) return 'bg-green-500/10';
  if (score >= 6) return 'bg-yellow-500/10';
  if (score >= 4) return 'bg-orange-500/10';
  return 'bg-red-500/10';
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
