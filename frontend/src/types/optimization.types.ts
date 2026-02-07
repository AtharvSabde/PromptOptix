// TypeScript types for optimization - must match backend Pydantic models

import { AnalysisResponse } from './analysis.types';

export enum OptimizationLevel {
  MINIMAL = 'minimal',
  BALANCED = 'balanced',
  AGGRESSIVE = 'aggressive'
}

export interface TechniqueApplication {
  technique_id: string;          // T001-T015
  technique_name: string;        // "Role Prompting"
  target_defects: string[];      // ["D002", "D005"]
  modification: string;          // Description of changes
  before_snippet?: string;
  after_snippet?: string;
}

export interface OptimizationMetadata {
  original_tokens?: number;
  optimized_tokens?: number;
  optimization_level: string;
  techniques_considered: number;
  techniques_applied?: number;
  defects_before?: number;
  defects_after?: number;
  total_cost: number;
  defects_fixed: number;
  processing_time_ms?: number;
  timestamp?: string;
}

export interface OptimizationResponse {
  original_prompt: string;
  optimized_prompt: string;
  techniques_applied: TechniqueApplication[];
  improvement_score: number;     // Score delta (can be negative)
  before_analysis: AnalysisResponse;
  after_analysis: AnalysisResponse;
  metadata: OptimizationMetadata;
}

export interface OptimizeRequest {
  prompt: string;                // 10-50,000 chars
  analysis: {                    // Analysis results from /api/analyze
    defects: any[];
    overall_score: number;
  };
  optimization_level?: OptimizationLevel;
  max_techniques?: number;       // 1-10, default: 5
  preserve_intent?: boolean;     // Default: true
}

export const OPTIMIZATION_LEVELS = [
  'minimal',
  'balanced',
  'aggressive'
] as const;

export type OptimizationLevelType = typeof OPTIMIZATION_LEVELS[number];
