// TypeScript types for prompt engineering techniques

export const TechniqueCategory = {
  ZERO_SHOT: 'zero_shot',
  FEW_SHOT: 'few_shot',
  CHAIN_OF_THOUGHT: 'chain_of_thought',
  STRUCTURED: 'structured',
  ROLE_BASED: 'role_based',
  ITERATIVE: 'iterative',
  DECOMPOSITION: 'decomposition',
  CONTEXT_ENHANCEMENT: 'context_enhancement',
} as const;
export type TechniqueCategory = typeof TechniqueCategory[keyof typeof TechniqueCategory];

export interface Technique {
  id: string;                    // T001-T015
  name: string;
  category: TechniqueCategory;
  description: string;
  when_to_use: string;
  example: string;               // Code example with syntax highlighting
  fixes_defects: string[];       // Defect IDs this technique addresses
  effectiveness_score: number;   // 0.0-1.0
  template?: string;
}

export interface TechniquesListResponse {
  total: number;
  categories: Record<string, number>;
  techniques: Technique[];
}

export const TECHNIQUE_CATEGORIES = [
  'zero_shot',
  'few_shot',
  'chain_of_thought',
  'structured',
  'role_based',
  'iterative',
  'decomposition',
  'context_enhancement'
] as const;

export type TechniqueCategoryType = typeof TECHNIQUE_CATEGORIES[number];
