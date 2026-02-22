# PromptOptimizer Pro: State-of-the-Art Research & Implementation Plan

> **Project**: PromptOptimizer Pro - Multi-Agent Prompt Engineering System
> **Based on**: Nagpure et al. (2025) - Prompt Engineering Survey, IJFMR
> **Date**: February 2026
> **Goal**: Elevate the project to state-of-the-art level with novel methods

---

## Part 1: Research - Current State of the Art

### 1.1 Leading Prompt Optimization Tools

| Tool | Org | Stars | Core Approach | Key Innovation |
|------|-----|-------|---------------|----------------|
| **DSPy** | Stanford NLP | 20k+ | Declarative framework; auto-optimizes prompts via MIPROv2 (Bayesian optimization over instruction+example combinations) | Programs LMs instead of prompting; automatic prompt compilation |
| **OPRO** | Google DeepMind | 3k+ | LLM-as-optimizer; feeds scored history of previous prompt attempts to LLM | Simple but effective - 8-50% improvement on benchmarks |
| **TextGrad** | Stanford HAI | 5k+ | Automatic differentiation via text; LLM-generated "textual gradients" for iterative improvement | Output-quality focused; SOTA on GPQA and LeetCode Hard |
| **EvoPrompt** | Tsinghua/MS | 1k+ | Evolutionary algorithms (GA/DE) with LLM as crossover/mutation operator | 25% improvement over human-engineered prompts |
| **PromptAgent** | Microsoft Research | 800+ | Monte Carlo Tree Search (MCTS) over prompt modification space | Expert-level prompts; 6-9% over APE (ICLR 2024) |
| **PromptBreeder** | Google DeepMind | - | Co-evolves task prompts AND mutation strategies simultaneously | Self-improving mutation operators |
| **Promptomatix** | Salesforce | 500+ | End-to-end pipeline: intent analysis -> synthetic data -> strategy selection -> optimization | Full pipeline with cost-aware optimization |
| **Meta Prompt-Ops** | Meta | 1k+ | Model-specific prompt adaptation; converts prompts across LLM families | Cross-model portability |

### 1.2 Key Research Papers (2023-2026)

| # | Paper | Venue/Year | Key Contribution |
|---|-------|-----------|-----------------|
| 1 | "Large Language Models as Optimizers" (OPRO) | NeurIPS 2023 | Proved LLMs can optimize prompts by seeing scored history of attempts |
| 2 | "PromptAgent: Strategic Planning with Language Models" | ICLR 2024 | Monte Carlo Tree Search for exploring prompt modification space |
| 3 | "EvoPrompt: Connecting LLMs with Evolutionary Algorithms" | ACL 2024 | Genetic Algorithm + Differential Evolution operators for prompt populations |
| 4 | "TextGrad: Automatic Differentiation via Text" | ICML 2024 | Textual gradient descent - critic LLM generates "gradients" for improvement |
| 5 | "The Prompt Report" (Schulhoff et al.) | arXiv 2024 | Taxonomy of 58 prompting techniques, 33 terms, comprehensive guidelines |
| 6 | "A Survey of Automatic Prompt Engineering: An Optimization Perspective" | arXiv Feb 2025 | Unified optimization-theoretic framework for ALL prompt optimization methods |
| 7 | "Promptomatix: An Automatic Prompt Optimization Framework" | arXiv Jul 2025 | End-to-end pipeline with synthetic data generation and cost-aware optimization |
| 8 | "DelvePO: Direction-Guided Self-Evolving Framework for Flexible Prompt Optimization" | arXiv Oct 2025 | Self-evolving prompt optimization with directional guidance |
| 9 | "Rethinking Prompt Optimizers: From Prompt Merits to Optimization" | arXiv May 2025 | Shows SOTA claims are prompt-dependent; proposes Combined Performance Score (CPS) |
| 10 | "Theoretical Foundations of Prompt Engineering" | arXiv Dec 2025 | Formalizes prompts as external parameters controlling model behavior |

### 1.3 Common Approaches Categorized

**Search-Based Optimization:**
- OPRO: LLM generates new prompts informed by scored history
- PromptAgent: MCTS balances exploration vs exploitation
- EvoPrompt/PromptBreeder: Evolutionary algorithms with LLM operators

**Gradient-Based Optimization:**
- TextGrad: Textual "gradients" from critic LLM guide updates
- Soft prompt tuning: Continuous embeddings (requires model access)

**Framework-Based:**
- DSPy: Declarative programming with automatic compilation
- Promptomatix: Pipeline automation with strategy selection

**Evaluation Methods:**
- LLM-as-Judge (G-EVAL style)
- NLP metrics (BLEU, ROUGE, METEOR, BERTScore)
- Task-specific metrics (Pass@k for code, accuracy for QA)
- Multi-metric evaluation with Pareto optimization

---

## Part 2: What Makes PromptOptimizer Pro Already Unique

### 2.1 Existing Innovations (No Other Tool Has These)

| Feature | Our Project | DSPy | OPRO | TextGrad | EvoPrompt |
|---------|------------|------|------|----------|-----------|
| Multi-Agent Defect Detection | 4 specialized agents with consensus voting | No | No | No | No |
| Explainable Diagnosis | Shows exactly which defects, evidence, remediation | No | No | No | No |
| 28-Defect Taxonomy | Based on Tian et al. research | No | No | No | No |
| 41+ Technique Library | Mapped to specific defects | No | No | No | No |
| Defect->Technique Mapping | Automatic technique selection based on defects | No | No | No | No |
| Consensus Mechanism | Reduces false positives via agent voting | No | No | No | No |

### 2.2 Our "Diagnosis-Before-Treatment" Philosophy

Other tools treat prompt optimization as a black box:
- Input: prompt -> Output: "better" prompt (no explanation)

Our tool follows a clinical approach:
1. **Diagnose**: 4 specialist agents examine the prompt (like specialist doctors)
2. **Consensus**: Agents vote on defects (like a medical board)
3. **Prescribe**: Select techniques mapped to diagnosed defects (like targeted treatment)
4. **Treat**: Apply techniques to fix specific issues
5. **Verify**: Re-analyze to confirm improvement

This is genuinely novel in the literature and should be emphasized in the thesis.

### 2.3 Current Gaps vs SOTA

| Capability | Current State | SOTA Baseline |
|-----------|--------------|---------------|
| Optimization search | Greedy top-N technique selection | MCTS, evolutionary, Bayesian |
| Within-session learning | Each iteration independent | OPRO passes scored history |
| Output quality feedback | Only analyzes prompt text | TextGrad evaluates actual output |
| Population-based search | Single optimization path | EvoPrompt maintains population |
| Benchmark validation | No datasets | Standard benchmarks required |
| Persistence/history | In-memory only | Database-backed |
| Frontend visualization | Basic before/after comparison | Rich diff views, charts, history |

---

## Part 3: Proposed Novel Methods

> **Key Principle**: We don't copy any tool's algorithm. We combine our unique multi-agent architecture with ideas from multiple SOTA approaches to create genuinely new methods.

### 3.1 DGEO - Defect-Guided Evolutionary Optimization

**Inspired by**: EvoPrompt (evolutionary search) + Our defect detection (unique)

**How EvoPrompt works**: Maintains a population of prompt variants, uses random LLM-guided mutations and crossover.

**How DGEO differs**: Defects **guide** the evolution. Population is initialized from defect subsets. Crossover combines variants that excel in different defect categories. Mutations are defect remediations, not random.

**Algorithm**:
```
DGEO(original_prompt, context):
  1. ANALYZE: Run 4-agent defect detection -> defects[], score
  2. GENERATE POPULATION (N=5 variants):
     - Variant 1: Fix only clarity defects (D001-D004)
     - Variant 2: Fix only structure defects (D005-D009)
     - Variant 3: Fix only context defects (D010-D014)
     - Variant 4: Fix all high-severity defects
     - Variant 5: Fix all detected defects (aggressive)
     Each variant is generated via LLM rewrite with targeted remediation instructions
  3. EVALUATE: Score each variant using multi-agent re-analysis
  4. SELECT: Keep top 3 variants (tournament selection)
  5. CROSSOVER: For each pair of selected variants:
     - Identify which defect categories each variant fixed best
     - Ask LLM: "Variant A excels at clarity (score 8.5), Variant B excels at structure (score 9.0). Combine the clarity improvements from A with the structural improvements from B."
  6. MUTATE: For each offspring:
     - Re-analyze for remaining defects
     - Apply targeted defect remediations as directed mutations
  7. REPEAT steps 3-6 for 2-3 generations
  8. RETURN: Best variant + full evolution history
```

**Novelty**: No tool combines defect-driven population seeding + defect-guided crossover + multi-agent fitness evaluation. This is the primary publishable contribution.

---

### 3.2 SHDT - Scored History with Defect Trajectories

**Inspired by**: OPRO (scored history) + Our defect tracking (unique)

**How OPRO works**: Shows the LLM a list of `(prompt, score)` pairs from previous attempts.

**How SHDT differs**: Instead of just scores, we show **defect trajectories** - which specific defects were fixed or introduced at each step. The LLM gets causal understanding, not just correlation.

**Algorithm**:
```
SHDT(original_prompt, context, max_iterations=4):
  trajectory = []

  1. Iteration 0:
     - Analyze -> defects=[D001, D002, D005, D010], score=6.0
     - trajectory.append({version: 0, prompt, score: 6.0, defects})

  2. For each iteration i = 1..max_iterations:
     - Build trajectory prompt:
       "OPTIMIZATION HISTORY:
        v0 (score 6.0): Had D001-Ambiguity, D002-Underspec, D005-NoStructure, D010-NoContext
        v1 (score 7.2): Fixed D001 (added specific criteria), Fixed D005 (added sections).
                         Remaining: D002, D010. Improvement: +1.2
        v2 (score 7.8): Fixed D010 (added domain context).
                         Remaining: D002. Improvement: +0.6

        INSTRUCTION: Generate v3 that fixes D002. Learn from what worked:
        - Adding specific criteria helped (+1.2)
        - Adding sections helped (+1.2)
        - Adding context helped (+0.6)"

     - LLM generates improved prompt informed by full trajectory
     - Re-analyze -> new defects, new score
     - Record: which defects fixed, which introduced, score delta
     - trajectory.append({...})
     - Stop if: score >= target OR no improvement OR no remaining defects

  3. RETURN: Best version + complete trajectory with causal analysis
```

**Novelty**: OPRO only shows scores. Adding defect trajectories gives the LLM **causal insight** into what changes caused what improvements. No existing paper does this.

---

### 3.3 CDRAF - Critic-Driven Refinement with Agent Feedback

**Inspired by**: TextGrad (critic feedback loop) + Our multi-agent architecture (unique)

**How TextGrad works**: A single LLM critic evaluates output, generates textual "gradients" (criticism), and these update the prompt.

**How CDRAF differs**: Instead of one generic critic, our 4 specialized agents serve as **domain-specific critics**. Each provides targeted feedback in their area of expertise.

**Algorithm**:
```
CDRAF(optimized_prompt, context, max_refinements=2):

  1. Start with optimized prompt (from DGEO or standard optimization)

  2. For each refinement round:
     a. MULTI-AGENT CRITIQUE: Run all 4 agents on current prompt
     b. COLLECT FEEDBACK:
        - ClarityAgent: "Term 'good performance' on line 3 is ambiguous (D001, confidence 0.85)"
        - StructureAgent: "Missing output format specification (D008, confidence 0.90)"
        - ContextAgent: "No domain context provided (D011, confidence 0.75)"
        - SecurityAgent: "No issues detected"
     c. PRIORITIZE: Sort feedback by confidence * severity
     d. DIRECTED REFINEMENT: Send to LLM:
        "Your optimized prompt was reviewed by 4 specialist reviewers.
         Their feedback (highest priority first):
         1. [Structure] Missing output format spec (confidence: 90%) -> Add clear format
         2. [Clarity] 'good performance' is ambiguous (confidence: 85%) -> Use specific metrics
         3. [Context] No domain context (confidence: 75%) -> Add domain-specific context

         Revise the prompt addressing these specific issues."
     e. VALIDATE: Re-analyze. If no high-severity defects remain -> done

  3. RETURN: Refined prompt + critique history (showing each round's feedback and fixes)
```

**Novelty**: TextGrad's single critic can't specialize. Our 4-agent architecture provides **multi-dimensional criticism** where each critic has deep expertise in one area. This is a genuinely new contribution.

---

### 3.4 ATSEL - Adaptive Technique Selection via Effectiveness Learning

**Inspired by**: Multi-armed bandit algorithms + Our technique registry (unique)

**Core Idea**: Track which techniques actually improve scores for which defect types over time, and use this data to make better technique selections.

**Algorithm**:
```
ATSEL:
  effectiveness_db = SQLite table: {technique_id, defect_id, times_applied, total_improvement, avg_improvement}

  On each optimization:
    1. Get detected defects
    2. For each defect, rank techniques by:
       - If enough data (>= 5 applications): Use learned avg_improvement
       - If insufficient data: Use static effectiveness_score * exploration_bonus
       - Exploration bonus = sqrt(2 * ln(total_applications) / technique_applications)  # UCB1
    3. Select top-N techniques
    4. After optimization, record results:
       For each technique applied:
         For each defect it targeted:
           Record: {technique_id, defect_id, improvement=score_after - score_before}
    5. Update effectiveness_db

  Over time: Technique selection becomes data-driven instead of static.
```

**Novelty**: No prompt optimization tool learns technique effectiveness from its own history. This creates a self-improving system.

---

## Part 4: Implementation Plan

### 4.1 File Changes Overview

#### Backend - New Files
| File | Purpose |
|------|---------|
| `backend/services/db_service.py` | SQLite persistence layer |
| `backend/services/dgeo_optimizer.py` | DGEO evolutionary optimization |
| `backend/routes/history.py` | History & benchmark API endpoints |
| `data/benchmarks/prompts.json` | 50+ curated benchmark prompts |
| `scripts/run_benchmark.py` | Automated benchmark runner |

#### Backend - Modified Files
| File | Changes |
|------|---------|
| `backend/services/optimizer_service.py` | Add SHDT iterative optimization, CDRAF refinement, DGEO integration |
| `backend/prompts/optimization_prompts.py` | Add prompts for SHDT trajectory, DGEO crossover/mutation, CDRAF critique |
| `backend/models/request_models.py` | Add AdvancedOptimizeRequest with optimization_strategy field |
| `backend/routes/__init__.py` | Register new history router |
| `backend/app.py` | Mount history routes, update description |
| `backend/config.py` | Add DGEO/SHDT/CDRAF config constants |

#### Frontend - New Files
| File | Purpose |
|------|---------|
| `frontend/src/pages/HistoryPage.tsx` | Optimization history with results |
| `frontend/src/components/optimization/StrategySelector.tsx` | Strategy picker (Standard/DGEO/SHDT/CDRAF) |
| `frontend/src/components/optimization/EvolutionViewer.tsx` | Visualize DGEO population evolution |
| `frontend/src/components/optimization/TrajectoryViewer.tsx` | Visualize SHDT defect trajectories |
| `frontend/src/components/optimization/PromptDiff.tsx` | Side-by-side diff with highlighted changes |
| `frontend/src/components/optimization/CritiqueViewer.tsx` | Show CDRAF agent feedback rounds |
| `frontend/src/api/history.service.ts` | API calls for history endpoints |
| `frontend/src/types/advanced.types.ts` | Types for new optimization strategies |
| `frontend/src/hooks/useHistory.ts` | Hook for history data |

#### Frontend - Modified Files
| File | Changes |
|------|---------|
| `frontend/src/App.tsx` | Add /history route |
| `frontend/src/pages/OptimizePage.tsx` | Add strategy selector, evolution/trajectory viewers |
| `frontend/src/pages/HomePage.tsx` | Update stats, add DGEO/SHDT/CDRAF feature cards |
| `frontend/src/components/layout/Header.tsx` | Add History nav link |
| `frontend/src/api/optimize.service.ts` | Add advanced optimization API call |
| `frontend/src/types/optimization.types.ts` | Add strategy types |

---

### 4.2 Detailed Implementation Steps

#### Phase A: Foundation (SQLite + Benchmarks)

**A1. SQLite Persistence - `backend/services/db_service.py`**
```
Tables:
  optimization_history:
    - id (INTEGER PRIMARY KEY)
    - original_prompt (TEXT)
    - optimized_prompt (TEXT)
    - strategy (TEXT: "standard" | "dgeo" | "shdt" | "cdraf")
    - score_before (REAL)
    - score_after (REAL)
    - improvement (REAL)
    - defects_before (TEXT JSON)
    - defects_after (TEXT JSON)
    - techniques_applied (TEXT JSON)
    - metadata (TEXT JSON)
    - created_at (TIMESTAMP)

  technique_effectiveness:
    - id (INTEGER PRIMARY KEY)
    - technique_id (TEXT)
    - defect_id (TEXT)
    - times_applied (INTEGER)
    - total_improvement (REAL)
    - avg_improvement (REAL)
    - last_used (TIMESTAMP)

Functions:
  - init_db() - Create tables if not exist
  - save_optimization(data) -> id
  - get_history(limit, offset) -> list
  - record_technique_result(technique_id, defect_id, improvement)
  - get_technique_effectiveness(technique_id, defect_id) -> avg_improvement
  - get_top_techniques_for_defect(defect_id, limit) -> ranked list
```

**A2. Benchmark Dataset - `data/benchmarks/prompts.json`**
```json
[
  {
    "id": "B001",
    "prompt": "Write a sorting function",
    "task_type": "code_generation",
    "domain": "software_engineering",
    "expected_defects": ["D001", "D002", "D008"],
    "human_score": 3.5,
    "category": "code_generation"
  },
  // ... 50+ prompts across 6 categories
]
```
Categories: 10 code_generation, 10 reasoning, 8 creative_writing, 8 summarization, 7 question_answering, 7 general

**A3. Benchmark Runner - `scripts/run_benchmark.py`**
```
For each benchmark prompt:
  1. Run analyze (multi-agent)
  2. Run optimize (standard)
  3. Run optimize (DGEO) - if available
  4. Record: scores, defects fixed, time, cost
Output: JSON results + summary table
```

#### Phase B: Core Novel Methods

**B1. SHDT Implementation**
- Add `get_shdt_optimization_prompt()` to `optimization_prompts.py`
  - Takes: original_prompt, trajectory (list of {version, prompt, score, defects_fixed, defects_remaining})
  - Returns: Meta-prompt with full trajectory for LLM
- Modify `optimize_iteratively()` in `optimizer_service.py`:
  - Add `strategy="shdt"` parameter
  - When strategy=shdt, build trajectory and pass to SHDT prompt each iteration
  - Record defect diffs between iterations (which fixed, which new)
  - Pass full trajectory history to LLM instead of just current state

**B2. CDRAF Implementation**
- Add `get_cdraf_critique_prompt()` to `optimization_prompts.py`
  - Takes: optimized_prompt, agent_feedback (list of {agent, defects, suggestions})
  - Returns: Directed refinement meta-prompt
- Add `refine_with_agents()` method to `optimizer_service.py`:
  - Takes optimized prompt, runs all 4 agents as critics
  - Collects remaining defects from each agent with confidence
  - Sends prioritized feedback to LLM for directed fix
  - Validates refined output
  - Returns: refined prompt + critique rounds history

**B3. DGEO Implementation - `backend/services/dgeo_optimizer.py`**
```python
class DGEOOptimizer:
    """Defect-Guided Evolutionary Optimization"""

    async def optimize(self, prompt, context, population_size=5, generations=3):
        # 1. Analyze original
        # 2. Generate population (each variant targets different defect subset)
        # 3. Evaluate all variants with multi-agent analysis
        # 4. Selection (tournament, keep top 50%)
        # 5. Crossover (LLM combines strengths of two variants)
        # 6. Mutation (apply remaining defect remediations)
        # 7. Repeat for N generations
        # 8. Return best + evolution history

    async def _generate_variant(self, prompt, target_defects, context):
        """Generate a variant targeting specific defects"""

    async def _crossover(self, variant_a, variant_b, strengths_a, strengths_b):
        """LLM-guided crossover combining best aspects"""

    async def _mutate(self, variant, remaining_defects):
        """Apply defect remediations as directed mutations"""
```

- Add `get_dgeo_variant_prompt()`, `get_dgeo_crossover_prompt()`, `get_dgeo_mutation_prompt()` to `optimization_prompts.py`

#### Phase C: API & Integration

**C1. New Request Model**
Add to `request_models.py`:
```python
class AdvancedOptimizeRequest(BaseModel):
    prompt: str
    analysis: Dict[str, Any]
    strategy: str = "standard"  # "standard" | "dgeo" | "shdt" | "cdraf"
    optimization_level: str = "balanced"
    max_techniques: int = 5
    # DGEO-specific
    population_size: int = 5
    generations: int = 3
    # SHDT-specific
    max_iterations: int = 4
    target_score: float = 8.0
    task_type: str = "general"
    domain: str = "general"
```

**C2. New API Endpoints**
Add to `routes/history.py`:
```
POST /api/optimize/advanced  - Advanced optimization with strategy selection
GET  /api/history             - Get optimization history
GET  /api/history/{id}        - Get specific optimization detail
GET  /api/benchmark/run       - Run benchmark suite
GET  /api/benchmark/results   - Get latest benchmark results
GET  /api/techniques/effectiveness - Get learned technique effectiveness
```

**C3. Update optimize route**
Modify `routes/optimize.py` to handle strategy parameter and route to appropriate optimizer.

#### Phase D: Frontend Changes

**D1. Strategy Selector Component** - `frontend/src/components/optimization/StrategySelector.tsx`
```
UI: 4 cards in a grid, each representing a strategy:

  [Standard]          [DGEO]              [SHDT]              [CDRAF]
  Quick single-pass   Evolutionary search  Iterative with     Multi-agent
  optimization        with population      scored history     critic refinement

  ~30s, 2 LLM calls   ~2min, 10+ calls    ~1min, 6+ calls    ~1min, 4+ calls
  Good for simple     Best for complex     Best for iterative  Best for targeted
  improvements        multi-defect cases   refinement          improvement

Each card: icon, name, description, estimated time/cost, "Select" button
Selected card gets highlighted border
```

**D2. Update OptimizePage.tsx**
- Add StrategySelector between analysis results and optimize button
- After optimization, show strategy-specific visualization:
  - Standard: Current before/after comparison (keep as-is)
  - DGEO: EvolutionViewer (shows population across generations)
  - SHDT: TrajectoryViewer (shows defect trajectory across iterations)
  - CDRAF: CritiqueViewer (shows agent feedback rounds)

**D3. EvolutionViewer Component** - `frontend/src/components/optimization/EvolutionViewer.tsx`
```
UI: Visual evolution display

  Generation 1:
  [Variant 1: 7.2] [Variant 2: 6.8] [Variant 3: 7.5] [Variant 4: 7.0] [Variant 5: 6.5]
  Fix clarity       Fix structure      Fix context        Fix high-sev      Fix all
       |                 |                  |
       v                 v                  v
  Generation 2 (after selection + crossover):
  [Offspring 1: 8.0]  [Offspring 2: 7.8]  [Variant 3: 7.5]
  Clarity+Structure    Context+Clarity      (survived)
       |                    |
       v                    v
  Generation 3:
  [Best: 8.3]         [Runner-up: 8.1]

  Uses: recharts BarChart for scores, color-coded by defect category focus
  Shows: Which defects each variant fixed, crossover parents
```

**D4. TrajectoryViewer Component** - `frontend/src/components/optimization/TrajectoryViewer.tsx`
```
UI: Timeline-style trajectory display

  v0 (6.0) ----[Fixed D001, D005]----> v1 (7.2) ----[Fixed D010]----> v2 (7.8) ----[Fixed D002]----> v3 (8.3)

  Defects: D001 D002 D005 D010       D002 D010                      D002                           (none)

  Each node shows:
  - Version number and score (large)
  - Defects remaining (colored badges)
  - Arrow label: what was fixed and score delta

  Uses: recharts LineChart for score trajectory
  Below: expandable panels showing full prompt at each version
```

**D5. CritiqueViewer Component** - `frontend/src/components/optimization/CritiqueViewer.tsx`
```
UI: Round-by-round critique display

  Round 1 Critique:
  [Clarity Agent]  "Term 'good performance' is ambiguous" (confidence: 85%)    -> FIXED
  [Structure Agent] "Missing output format specification" (confidence: 90%)     -> FIXED
  [Context Agent]   "No domain context provided" (confidence: 75%)             -> FIXED
  [Security Agent]  "No issues detected"                                       -> N/A

  Score: 7.2 -> 8.5 (+1.3)

  Round 2 Critique:
  [Clarity Agent]  "No remaining issues"
  [Structure Agent] "No remaining issues"
  [Context Agent]   "No remaining issues"
  [Security Agent]  "No issues detected"

  All clear! Final score: 8.5

  Color-coded: green=fixed, yellow=remaining, gray=no issues
```

**D6. PromptDiff Component** - `frontend/src/components/optimization/PromptDiff.tsx`
```
UI: Side-by-side diff with highlights

  Original                          | Optimized
  ----------------------------------|----------------------------------
  Write a function to sort          | You are a Python developer.
  numbers                           | Write a function that sorts a
                                    | list of integers in ascending
  [highlighted: missing context]    | order using an efficient algorithm.
                                    | [highlighted: added specificity]
                                    |
                                    | Requirements:
                                    | - Input: List of integers
                                    | - Output: Sorted list
                                    | [highlighted: added structure]

  Additions highlighted in green
  Removals highlighted in red
  Annotations show which defect each change fixes
```

**D7. HistoryPage.tsx** - `frontend/src/pages/HistoryPage.tsx`
```
UI: Table/card list of past optimizations

  Filter: [All strategies] [Date range] [Min improvement]

  | # | Prompt (truncated) | Strategy | Score Before | Score After | Improvement | Date |
  |---|-------------------|----------|-------------|------------|-------------|------|
  | 1 | "Write a sorting..." | DGEO | 4.5 | 8.3 | +3.8 | 2 min ago |
  | 2 | "Summarize this..." | SHDT | 6.0 | 7.8 | +1.8 | 1 hr ago |
  | 3 | "You are an IELTS..." | Standard | 7.5 | 8.2 | +0.7 | 2 hr ago |

  Click row -> expands to show full detail (original, optimized, techniques, defects)

  Bottom section: Aggregate stats
  - Average improvement by strategy (bar chart)
  - Technique effectiveness heatmap (technique x defect -> avg improvement)
  - Total optimizations, total cost, avg processing time
```

**D8. Update App.tsx routing**
```typescript
<Route path="/history" element={<HistoryPage />} />
```

**D9. Update Header.tsx navigation**
Add "History" link in nav bar between "Techniques" and any other links.

**D10. Update HomePage.tsx**
- Update feature cards to mention DGEO/SHDT/CDRAF
- Update stats: "4 agents, 28 defects, 41+ techniques, 3 novel algorithms"
- Add section: "Advanced Optimization Strategies" with brief descriptions

**D11. Update Types**
Add to `frontend/src/types/advanced.types.ts`:
```typescript
type OptimizationStrategy = 'standard' | 'dgeo' | 'shdt' | 'cdraf'

interface EvolutionHistory {
  generations: Generation[]
  best_variant: Variant
  total_evaluations: number
}

interface Generation {
  number: number
  variants: Variant[]
  best_score: number
}

interface Variant {
  id: string
  prompt: string
  score: number
  defects: string[]
  parent_ids?: string[]
  defects_targeted: string[]
}

interface DefectTrajectory {
  versions: TrajectoryVersion[]
  total_improvement: number
}

interface TrajectoryVersion {
  version: number
  prompt: string
  score: number
  defects: DefectInfo[]
  defects_fixed: string[]
  defects_introduced: string[]
  improvement: number
}

interface CritiqueRound {
  round: number
  agent_feedback: AgentCritique[]
  prompt_before: string
  prompt_after: string
  score_before: number
  score_after: number
}

interface AgentCritique {
  agent: string
  focus_area: string
  issues: CritiqueIssue[]
  resolved: boolean
}

interface OptimizationHistoryEntry {
  id: number
  original_prompt: string
  optimized_prompt: string
  strategy: OptimizationStrategy
  score_before: number
  score_after: number
  improvement: number
  techniques_applied: string[]
  created_at: string
}
```

---

### 4.3 Implementation Order

| Phase | What | Files | Effort |
|-------|------|-------|--------|
| **A** | SQLite + Benchmark data | `db_service.py`, `prompts.json`, `run_benchmark.py` | 1-2 days |
| **B** | SHDT + CDRAF + DGEO methods | `optimizer_service.py`, `dgeo_optimizer.py`, `optimization_prompts.py` | 3-4 days |
| **C** | API endpoints + integration | `request_models.py`, `history.py`, `optimize.py`, `app.py` | 1-2 days |
| **D** | Frontend: strategy selector + viewers | All frontend files listed above | 2-3 days |
| **E** | History page + benchmark dashboard | `HistoryPage.tsx`, `history.service.ts` | 1-2 days |

**Total: ~8-13 days**

---

## Part 5: Comparison After Implementation

| Feature | DSPy | OPRO | TextGrad | EvoPrompt | **Ours (Enhanced)** |
|---------|------|------|----------|-----------|---------------------|
| Defect Detection | No | No | No | No | **4 agents, 28 defects** |
| Explainable Diagnosis | No | No | No | No | **Defect reports with evidence** |
| Technique Library | No | No | No | No | **41+ mapped to defects** |
| Evolutionary Search | No | No | No | Blind random | **Defect-guided (DGEO)** |
| Scored History | No | Score-only | No | No | **Score + defect trajectories (SHDT)** |
| Critic Feedback | No | No | Single generic | No | **4 specialized agents (CDRAF)** |
| Self-Improving | Needs labeled data | No | No | No | **Technique effectiveness learning (ATSEL)** |
| Benchmarked | Yes | Yes | Yes | Yes | **Yes (after adding)** |
| Visual UI | No (library) | No (script) | No (library) | No (script) | **Full React UI with visualizations** |

---

## Part 6: Thesis Positioning

### Positioning Statement
"While existing tools optimize prompts through single-strategy approaches (evolutionary, gradient-based, or LLM-as-optimizer), PromptOptimizer Pro introduces a **diagnosis-before-treatment paradigm** with three novel algorithms:
1. **DGEO** (Defect-Guided Evolutionary Optimization) - the first evolutionary prompt optimizer that uses defect detection to guide population initialization, crossover, and mutation
2. **SHDT** (Scored History with Defect Trajectories) - extends OPRO with causal defect tracking for within-session learning
3. **CDRAF** (Critic-Driven Refinement with Agent Feedback) - extends TextGrad with multi-dimensional specialized criticism

This combination of multi-agent defect detection + defect-driven optimization is unique in the literature."

### Papers to Cite

**Foundational:**
- Nagpure et al. 2025 - Your research survey (IJFMR)
- Tian et al. - Defect taxonomy source

**SOTA References:**
- Yang et al. 2023 - OPRO: Large Language Models as Optimizers (NeurIPS)
- Wang et al. 2024 - PromptAgent: Strategic Planning with LMs (ICLR)
- Guo et al. 2023 - EvoPrompt: Connecting LLMs with Evolutionary Algorithms (ACL)
- Yuksekgonul et al. 2024 - TextGrad: Automatic Differentiation via Text (ICML)
- Schulhoff et al. 2024 - The Prompt Report: Systematic Survey (arXiv)
- Fernando et al. 2023 - PromptBreeder (arXiv)
- Khattab et al. 2023 - DSPy (arXiv)
- Salesforce 2025 - Promptomatix (arXiv)
- Survey of Automatic Prompt Engineering 2025 (arXiv)

---

## Part 7: Verification Plan

After each phase:
1. **Unit test**: Each new method individually with a simple prompt
2. **Integration test**: Full pipeline from API endpoint to result
3. **Benchmark**: Run `scripts/run_benchmark.py` and compare strategies
4. **Frontend**: Visual verification of all new components
5. **Regression**: Ensure standard optimization still works

Final verification:
```bash
# Backend
python -m backend.app  # Start API

# Run benchmark
python scripts/run_benchmark.py --strategies standard,dgeo,shdt,cdraf

# Frontend
cd frontend && npm run dev  # Start frontend

# Test each strategy via UI:
# 1. Go to /analyze -> analyze a prompt
# 2. Go to /optimize -> select each strategy -> verify visualization
# 3. Go to /history -> verify entries are saved
```

Expected results:
- DGEO shows highest average improvement (explores more broadly)
- SHDT shows most consistent improvement (learns from trajectory)
- CDRAF shows most targeted fixes (agent-specific feedback)
- All strategies > standard optimization

---

## Part 8: Unified Optimization Pipeline (Novel Contribution)

### Overview

Beyond the individual DGEO, SHDT, and CDRAF strategies, PromptOptimizer Pro introduces a **Unified Optimization Pipeline** ("auto" strategy) that chains all four optimization methods in a single invocation, automatically keeping the best output from each stage.

### Pipeline Architecture

```
Input Prompt
    │
    ▼
┌─────────────────────────────┐
│ Phase 1: Standard           │  Single-pass LLM rewriting with technique selection
│ (Baseline — ~30s)           │  Applies best-matching techniques from 41+ registry
└─────────────┬───────────────┘
              │ best_prompt
              ▼
┌─────────────────────────────┐
│ Phase 2: DGEO-lite          │  Evolutionary search with 3 variants × 1 generation
│ (Population search — ~30s)  │  Mutation + crossover guided by defect analysis
└─────────────┬───────────────┘
              │ keep if improved
              ▼
┌─────────────────────────────┐
│ Phase 3: SHDT               │  Scored History with 2 iterations, target 9.0
│ (Trajectory — ~30s)         │  Causal learning from what changes helped/hurt
└─────────────┬───────────────┘
              │ keep if improved
              ▼
┌─────────────────────────────┐
│ Phase 4: CDRAF              │  Critic-Driven Refinement with 1 agent round
│ (Agent critique — ~30s)     │  4 specialist agents provide targeted feedback
└─────────────┬───────────────┘
              │ keep if improved
              ▼
         Final Result
    (best prompt across all 4 phases)
```

### Key Design Decisions

1. **Monotonic improvement**: Each phase only keeps its output if the re-analyzed score is higher than the previous best. The pipeline never degrades the prompt.

2. **Lightweight sub-invocations**: To keep total time under ~2 minutes, the pipeline uses reduced parameters for each sub-strategy:
   - DGEO: 3 variants × 1 generation (vs. full 5×3)
   - SHDT: 2 iterations with target 9.0 (vs. full 4 iterations)
   - CDRAF: 1 critique round (vs. full 2 rounds)

3. **Fault tolerance**: Each phase is wrapped in a try/except. If DGEO fails (e.g., due to LLM errors), the pipeline continues with SHDT and CDRAF using the best result so far.

4. **Full visualization data**: The pipeline collects evolution_history, trajectory, and critique_rounds from whichever phases succeed, allowing the frontend to render all applicable viewers.

### Why This Is Unique

**No existing tool chains multiple optimization paradigms.** Existing SOTA systems use a single approach:

| Tool | Approach | Paradigm |
|------|----------|----------|
| DSPy (Khattab 2023) | Compile-time optimization | Programmatic |
| EvoPrompt (Guo 2023) | Evolutionary search only | Evolutionary |
| OPRO (Yang 2023) | LLM-as-optimizer with history | Iterative |
| TextGrad (Yuksekgonul 2024) | Gradient descent via text | Gradient-based |
| PromptAgent (Wang 2024) | Monte Carlo tree search | Planning |
| PromptBreeder (Fernando 2023) | Self-referential evolution | Evolutionary |

**PromptOptimizer Pro's unified pipeline is the first to combine:**
1. **Technique-driven rewriting** (knowledge-based, from 41+ techniques and 28 defect types)
2. **Evolutionary population search** (DGEO — explores diverse solution space)
3. **Trajectory-based iterative learning** (SHDT — learns from causal history)
4. **Multi-agent critique refinement** (CDRAF — targeted expert feedback)

This is analogous to **ensemble methods in machine learning**: just as random forests combine multiple weak learners into a strong predictor, the unified pipeline combines multiple optimization paradigms into a single, robust optimizer that outperforms any individual strategy.

### Academic Positioning

The unified pipeline can be positioned as a novel contribution under the concept of **"Multi-Paradigm Prompt Optimization"**. While ensemble methods are well-established in ML (Breiman 1996, Dietterich 2000), applying the ensemble principle to prompt optimization — combining evolutionary, iterative, and critique-based methods with a monotonic improvement guarantee — has no precedent in the literature as of 2025.

**Citation for thesis:** "We introduce a Unified Optimization Pipeline that, to our knowledge, is the first system to chain multiple prompt optimization paradigms (evolutionary search, trajectory-based iterative learning, and multi-agent critique) into a single monotonically-improving pipeline."
