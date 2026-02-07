// TypeScript types for analysis - must match backend Pydantic models exactly

export enum DefectSeverity {
  CRITICAL = 'critical',
  HIGH = 'high',
  MEDIUM = 'medium',
  LOW = 'low'
}

export enum DefectCategory {
  SPECIFICATION_AND_INTENT = 'specification_and_intent',
  STRUCTURE_AND_FORMATTING = 'structure_and_formatting',
  CONTEXT_AND_MEMORY = 'context_and_memory',
  OUTPUT_GUIDANCE = 'output_guidance',
  EXAMPLES_AND_DEMONSTRATIONS = 'examples_and_demonstrations',
  SECURITY_AND_SAFETY = 'security_and_safety'
}

export interface Defect {
  id: string;                    // D001-D028
  name: string;                  // "Ambiguity"
  category: DefectCategory;
  severity: DefectSeverity;
  confidence: number;            // 0.0-1.0
  consensus?: number;            // 0.0-1.0 (% of agents that detected it)
  description: string;
  evidence: string;              // Specific text from prompt showing defect
  explanation?: string;
  remediation: string;           // How to fix
  detected_by: string[];         // ["ClarityAgent", "StructureAgent"]
}

export interface AgentResult {
  agent: string;                 // Agent name
  focus_area: string;            // "specification_and_intent"
  defects: Defect[];
  score: number;                 // 0.0-10.0
  confidence: number;            // 0.0-1.0
  summary: string;
  metadata?: {
    provider?: string;
    model?: string;
    usage?: {
      input_tokens?: number;
      output_tokens?: number;
    };
    cost?: {
      total_cost?: number;
    };
  };
}

export interface Disagreement {
  defect_id: string;
  defect_name?: string;
  consensus: number;
  detected_by: string[];
  not_detected_by: string[];
  reason?: string;
}

export interface AnalysisMetadata {
  num_agents: number;
  total_defects_raw?: number;
  total_defects_after_dedup?: number;
  total_disagreements?: number;
  consensus_threshold?: number;
  processing_time_ms: number;
  total_cost: number;
  total_tokens: number;
  timestamp?: string;
}

export interface AnalysisResponse {
  overall_score: number;         // 0.0-10.0
  defects: Defect[];
  consensus: number;             // 0.0-1.0 (agent agreement level)
  agent_results?: Record<string, AgentResult>;
  disagreements?: Disagreement[];
  summary: string;
  metadata: AnalysisMetadata;
}

export interface AnalyzeRequest {
  prompt: string;                // 10-50,000 chars
  task_type?: string;            // Default: "general"
  domain?: string;               // Default: "general"
  include_agent_breakdown?: boolean;
}

// Task types and domains
export const TASK_TYPES = [
  'code_generation',
  'reasoning',
  'creative_writing',
  'information_extraction',
  'classification',
  'conversation',
  'summarization',
  'question_answering',
  'translation',
  'general'
] as const;

export const DOMAINS = [
  'software_engineering',
  'mathematics',
  'science',
  'business',
  'education',
  'healthcare',
  'legal',
  'creative',
  'general'
] as const;

export type TaskType = typeof TASK_TYPES[number];
export type Domain = typeof DOMAINS[number];
