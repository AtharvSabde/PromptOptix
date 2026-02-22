/**
 * Advanced Optimization Types
 * Types for DGEO, SHDT, CDRAF strategies and history
 */

// ============================================================
// Strategy Types
// ============================================================

export type OptimizationStrategy = 'standard' | 'dgeo' | 'shdt' | 'cdraf' | 'auto';

export interface StrategyInfo {
  id: OptimizationStrategy;
  name: string;
  description: string;
  estimatedTime: string;
  estimatedCalls: string;
  bestFor: string;
  icon: string;
}

export const STRATEGIES: StrategyInfo[] = [
  {
    id: 'standard',
    name: 'Standard',
    description: 'Quick single-pass optimization using LLM rewriting',
    estimatedTime: '~30s',
    estimatedCalls: '2-3 LLM calls',
    bestFor: 'Simple improvements',
    icon: '⚡'
  },
  {
    id: 'dgeo',
    name: 'DGEO',
    description: 'Defect-Guided Evolutionary Optimization — generates multiple variants and evolves the best through crossover and mutation',
    estimatedTime: '~2 min',
    estimatedCalls: '10+ LLM calls',
    bestFor: 'Complex multi-defect prompts',
    icon: '🧬'
  },
  {
    id: 'shdt',
    name: 'SHDT',
    description: 'Scored History with Defect Trajectories — iteratively improves using causal learning from what changes helped',
    estimatedTime: '~1 min',
    estimatedCalls: '6+ LLM calls',
    bestFor: 'Iterative refinement',
    icon: '📈'
  },
  {
    id: 'cdraf',
    name: 'CDRAF',
    description: 'Critic-Driven Refinement with Agent Feedback — uses 4 specialist agents as critics for targeted fixes',
    estimatedTime: '~1 min',
    estimatedCalls: '4+ LLM calls',
    bestFor: 'Targeted improvement',
    icon: '🔍'
  }
];

// ============================================================
// DGEO Types
// ============================================================

export interface DGEOVariant {
  id: string;
  score: number;
  focus: string;
  defects_remaining: number;
  parent_ids?: string[];
}

export interface DGEOGeneration {
  generation: number;
  variants: DGEOVariant[];
  best_score: number;
  avg_score: number;
}

export interface DGEOEvolutionHistory {
  generations: DGEOGeneration[];
}

// ============================================================
// SHDT Types
// ============================================================

export interface SHDTTrajectoryVersion {
  version: number;
  prompt: string;
  score: number;
  defects_fixed: string[];
  defects_remaining: string[];
  defects_introduced: string[];
  improvement: number;
}

// ============================================================
// CDRAF Types
// ============================================================

export interface CritiqueIssue {
  defect_id: string;
  name: string;
  description: string;
  remediation: string;
  confidence: number;
  severity: string;
}

export interface AgentCritique {
  agent: string;
  focus_area: string;
  issues: CritiqueIssue[];
}

export interface CritiqueRound {
  round: number;
  score_before?: number;
  agent_feedback: AgentCritique[];
  issues_found: number;
  issues_addressed?: Array<{
    issue_number: number;
    agent: string;
    fix_applied: string;
  }>;
  prompt_before?: string;
  prompt_after?: string;
}

// ============================================================
// Advanced Optimization Response
// ============================================================

export type LLMProvider = 'anthropic' | 'groq' | 'openai' | 'gemini';

export const LLM_PROVIDERS: { id: LLMProvider; name: string; description: string }[] = [
  { id: 'groq', name: 'Groq (Llama 3.3)', description: 'Fast & free — great for testing' },
  { id: 'anthropic', name: 'Anthropic (Claude)', description: 'Best quality analysis' },
  { id: 'openai', name: 'OpenAI (GPT-4o)', description: 'Versatile & reliable' },
  { id: 'gemini', name: 'Google (Gemini)', description: 'Large context window' },
];

export interface AdvancedOptimizeRequest {
  prompt: string;
  analysis?: Record<string, unknown>;
  strategy: OptimizationStrategy;
  optimization_level?: string;
  max_techniques?: number;
  population_size?: number;
  generations?: number;
  max_iterations?: number;
  target_score?: number;
  max_rounds?: number;
  task_type?: string;
  domain?: string;
  provider?: LLMProvider;
  user_issues?: string[];
}

export interface AdvancedOptimizeResponse {
  original_prompt: string;
  optimized_prompt: string;
  strategy: OptimizationStrategy;
  score_before: number;
  score_after: number;
  improvement: number;
  // Strategy-specific data
  techniques_applied?: Array<{
    technique_id: string;
    technique_name: string;
    target_defects: string[];
    modification: string;
  }>;
  evolution_history?: DGEOGeneration[];
  population_final?: DGEOVariant[];
  trajectory?: SHDTTrajectoryVersion[];
  critique_rounds?: CritiqueRound[];
  standard_result?: {
    optimized_prompt: string;
    score: number;
    techniques_applied: unknown[];
  };
  before_analysis: Record<string, unknown>;
  after_analysis: Record<string, unknown>;
  metadata: Record<string, unknown>;
}

// ============================================================
// History Types
// ============================================================

export interface HistoryEntry {
  id: number;
  original_prompt: string;
  optimized_prompt: string;
  strategy: OptimizationStrategy;
  score_before: number;
  score_after: number;
  improvement: number;
  defects_before?: unknown[];
  defects_after?: unknown[];
  techniques_applied?: unknown[];
  evolution_history?: unknown;
  trajectory_history?: unknown;
  critique_history?: unknown;
  metadata?: Record<string, unknown>;
  task_type: string;
  domain: string;
  created_at: string;
}

export interface HistoryStats {
  total_optimizations: number;
  by_strategy: Record<string, {
    count: number;
    avg_improvement: number;
    best_improvement: number;
    avg_final_score: number;
  }>;
  avg_improvement: number;
  best_improvement: number;
}

export interface HistoryResponse {
  records: HistoryEntry[];
  total: number;
  stats: HistoryStats;
}

export interface TechniqueEffectiveness {
  technique_id: string;
  defect_id: string;
  times_applied: number;
  avg_improvement: number;
  success_count: number;
}
