# PromptOptimizer Pro — Evaluation Methodology Guide

This document explains the step-by-step process for evaluating the PromptOptimizer Pro framework. Each step describes **what** we do, **why** we do it, and **how** the results map to our research questions.

---

## Why This Evaluation?

Our framework makes 5 core claims (RQ1–RQ5). Without empirical evidence, these claims are just assertions. This evaluation provides:

- **Quantitative proof** that optimization improves prompt quality
- **Comparative data** showing which strategy works best and when
- **Statistical rigor** (p-values, effect sizes) required for publication
- **Reproducibility** — anyone can re-run these experiments with the same script

### Research Questions

| RQ | Question | What It Proves |
|----|----------|---------------|
| RQ1 | Does PromptOptimizer Pro improve prompt quality vs baseline? | The framework works at all |
| RQ2 | Do DGEO, SHDT, CDRAF outperform standard single-pass? | Advanced strategies add value |
| RQ3 | Does the Unified Pipeline outperform individual strategies? | Chaining strategies helps |
| RQ4 | Does defect-guided optimization reduce high-severity defects? | We target the right problems |
| RQ5 | Does ATSEL improve technique selection over time? | The system learns |

---

## Prerequisites

Before running evaluation:

1. **API keys** configured in `.env`:
   - `GEMINI_API_KEY` — for Gemini 3.1 Pro Preview evaluation
   - `ANTHROPIC_API_KEY` — for Claude Sonnet 4.6 evaluation
   - `GROQ_API_KEY` — free/fast testing alternative
2. **Benchmark prompts** in `data/benchmarks/prompts.json` (55 prompts included)
3. **Dependencies** installed: `pip install -r backend/requirements.txt` (includes scipy)
4. **Backend** should NOT be running (the script imports services directly)

### Supported Models (2026)
| Provider | Model ID | Notes |
|----------|----------|-------|
| `gemini` | `gemini-3.1-pro-preview` | Default Gemini model (replaces deprecated Gemini 3 Pro) |
| `anthropic` | `claude-sonnet-4-6` | Default Claude model |
| `groq` | `llama-3.3-70b-versatile` | Free, fast testing |
| `openai` | `gpt-4o` | Alternative baseline |

> **Note:** Gemini 3 Pro Preview was deprecated on March 9, 2026. Use `gemini-3.1-pro-preview` instead.

---

## Step 1: Prepare Benchmark Dataset

**WHAT:** A collection of 55 real-world user prompts across multiple categories, sourced from published datasets.

**WHY:** Using prompts from published, peer-reviewed datasets ensures ecological validity — these are prompts real users actually submitted to LLMs, not synthetic constructs. The n≥30 convention for CLT is a historical rule of thumb, not a strict mathematical requirement; the real constraint is statistical power. We use all 55 prompts for maximum power.

**SOURCES:** Prompts are drawn from three published datasets of real user-LLM interactions:

| Dataset | Source | License | Prompts Used |
|---------|--------|---------|--------------|
| **LMSYS Chatbot Arena** | lmsys/chatbot_arena_conversations (HuggingFace) | CC-BY-4.0 (user prompts) | 30 |
| **LMSYS-Chat-1M** | lmsys/lmsys-chat-1m (HuggingFace) | CC-BY-NC-4.0 | 16 |
| **WildBench** | allenai/WildBench v2 (HuggingFace) | CC-BY-4.0 | 9 |

> **Why these datasets?** LMSYS Chatbot Arena contains 33K real pairwise conversations with human preference labels (Zheng et al., 2023). LMSYS-Chat-1M contains 1M real user-LLM conversations across 25 models. WildBench contains 1,024 curated tasks from real users designed to test frontier model capabilities (Lin et al., 2024). Together, they cover the full spectrum from terse/underspecified prompts to detailed, well-structured requests. Prompts are extracted via `scripts/pull_benchmark_prompts.py` which is reproducible — anyone can re-run it to regenerate the benchmark from source datasets.

**HOW:** The file `data/benchmarks/prompts.json` contains 55 prompts across 6 categories:
- Code Generation (11 prompts) — from terse "make an api" to detailed multi-component specifications
- Reasoning (11 prompts) — math, logic, ethics, policy analysis
- Creative Writing (9 prompts) — stories, business copy, speeches, social media
- Question Answering (7 prompts) — technical explanations, comparisons, debugging
- Summarization (8 prompts) — document condensation, meeting notes, executive briefs
- General (9 prompts) — planning, career advice, learning roadmaps, mixed tasks

Each prompt has: `id`, `prompt`, `category`, `task_type`, `domain`, `expected_defects` (ground truth from Tian et al. taxonomy), `human_score` (manual baseline), `difficulty`, `source` (originating dataset).

**DECISION:** We deliberately include underspecified prompts (human_score 1.0–3.0) alongside well-crafted ones (7.5+) to test the full quality range. Real-world prompt quality follows a bimodal distribution — many users write minimal prompts while power users write detailed ones. Our benchmark reflects this natural distribution.

---

## Step 2: Establish Baselines (answers RQ1)

**WHAT:** Run each prompt through the 4-agent analysis system WITHOUT any optimization.

**WHY:** We need a control group. Without knowing the starting score, we can't measure improvement. The baseline also tells us:
- How many defects exist in typical prompts
- What the agent consensus looks like
- How much room for improvement exists

**METRICS COLLECTED:**
| Metric | Why We Need It |
|--------|---------------|
| `overall_score` | Primary outcome variable for all comparisons |
| `total_defects` | Measures problem density |
| `high_severity_defects` | Critical+High count — what really matters |
| `consensus` | Agent agreement — higher = more confident |
| `total_tokens` | Cost baseline |
| `total_cost` | Dollar baseline |

**HOW IT WORKS:** The 4 agents (Clarity, Structure, Context, Security) analyze the prompt in parallel. Each agent checks its assigned defect range (D001-D004, D005-D009, D010-D014, D023-D028). Results are aggregated with consensus voting — defects detected by multiple agents get boosted confidence.

---

## Step 3: Run Each Strategy Independently (answers RQ2)

**WHAT:** For each prompt, run Standard, DGEO, SHDT, and CDRAF optimization independently.

**WHY:** Independent runs prevent contamination. If we ran strategies sequentially on the same prompt, later strategies would benefit from earlier improvements, making comparison unfair. Each strategy receives the same baseline prompt and analysis.

**STRATEGIES:**

### Standard Optimization
- **How:** Single LLM call with defect-aware prompt rewriting
- **What it does:** Analyzes defects → selects matching techniques → generates improved prompt
- **Expected:** Fast, consistent improvement, but limited depth

### DGEO (Defect-Guided Evolutionary Optimization)
- **How:** Generates a population of 5 variants, each focusing on different defect subsets. Evaluates all, picks best. Optionally evolves through crossover/mutation.
- **What it does:** Explores multiple optimization paths in parallel
- **Expected:** Higher variance in results, but finds non-obvious improvements

### SHDT (Scored History with Defect Trajectories)
- **How:** Iteratively refines: optimize → re-analyze → optimize again, tracking which defects were fixed/introduced at each step
- **What it does:** Learns from its own history to avoid regression
- **Expected:** Steady monotonic improvement, good for complex prompts

### CDRAF (Critic-Driven Refinement with Agent Feedback)
- **How:** Runs standard optimization first, then sends result through all 4 agents as critics. Each agent provides targeted feedback, which is used for refinement.
- **What it does:** Uses specialized domain knowledge (security, clarity, structure, context) for targeted fixes
- **Expected:** Best at fixing specific defect categories

**METRICS COLLECTED (per strategy, per prompt):**
- `score_after` — final quality score
- `defects_after` — remaining defect count
- `high_severity_after` — remaining critical+high defects
- `processing_time_ms` — wall clock time
- `cost_after` — API cost
- `techniques_applied` — which techniques were used (Standard/Unified only)

---

## Step 4: Run Unified Pipeline (answers RQ3)

**WHAT:** Run the chained Standard → DGEO → SHDT → CDRAF pipeline on each prompt.

**WHY:** This tests our core hypothesis — that combining strategies produces better results than any single one. The pipeline is designed for monotonic improvement: each phase builds on the previous phase's output.

**HOW THE PIPELINE WORKS:**
1. **Phase 1 (Standard):** Quick technique-based rewrite → establishes improved baseline
2. **Phase 2 (DGEO):** Generates variants of the Phase 1 output → picks best
3. **Phase 3 (SHDT):** Iteratively refines Phase 2 output → fixes remaining defects
4. **Phase 4 (CDRAF):** Agent critique of Phase 3 output → targeted final polish

**WHAT WE EXPECT:** Unified score > max(individual strategy scores), because:
- Standard handles low-hanging fruit (formatting, structure)
- DGEO explores alternative approaches
- SHDT addresses regression from DGEO
- CDRAF provides expert-level final review

**IF UNIFIED IS NOT BETTER:** This is still a valid result — it means the strategies interfere with each other, which is publishable as a negative finding.

---

## Step 5: Analyze High-Severity Defects (answers RQ4)

**WHAT:** Count critical and high severity defects before and after each strategy.

**WHY:** Not all defects are equal. A prompt with 5 low-severity formatting issues is far less problematic than one with 2 critical ambiguity defects. Our defect-guided approach should prioritize fixing the most impactful defects.

**SEVERITY DEFINITIONS (from Tian et al.):**
| Severity | Impact | Examples |
|----------|--------|---------|
| CRITICAL | Prompt will likely produce wrong/harmful output | D003 (Contradictions), D023 (Injection vulnerability), D024 (Data leakage) |
| HIGH | Significant quality degradation | D001 (Ambiguity), D002 (Incomplete specification), D014 (Missing constraints) |
| MEDIUM | Noticeable but manageable issues | D005 (Poor structure), D006 (No formatting guidance) |
| LOW | Minor polish items | D007 (Inconsistent terminology), D012 (Redundant context) |

**METRIC:** `high_severity_reduction_% = (HS_before - HS_after) / HS_before * 100`

**DECISION:** We combine CRITICAL and HIGH into one "high-severity" bucket because:
- Both have significant impact on output quality
- Separating them would reduce sample sizes below statistical significance
- This is standard practice in software defect research

---

## Step 6: Evaluate Technique Learning (answers RQ5)

**WHAT:** Track which prompt engineering techniques were applied and their average improvement.

**WHY:** ATSEL (Adaptive Technique Selection via Exploration and Learning) uses a UCB1-based multi-armed bandit to select techniques. Over time, it should learn which techniques work best for which defects.

**HOW:**
- The `technique_effectiveness` table in SQLite tracks: technique_id, defect_id, times_applied, avg_improvement
- After each optimization, technique results are recorded
- The evaluation script collects this data and computes per-technique stats

**WHAT WE EXPECT:** After 50+ optimizations, frequently successful techniques should have higher selection rates and improvement scores than rarely-used ones.

---

## Step 7: Statistical Analysis

**WHAT:** Apply formal statistical tests to our results.

**WHY:** Without statistics, "Strategy A got 7.2 and Strategy B got 6.8" tells us nothing — the difference could be random noise. Statistical tests tell us the probability that observed differences are real.

### Tests Used

**Paired t-test (Baseline vs Strategy)**
- **Why paired:** Same prompts tested under two conditions → reduces variance
- **What it tells us:** Is the improvement statistically significant? (p < 0.05)
- **Formula:** t = mean(differences) / (SD(differences) / sqrt(n))

**Cohen's d (Effect Size)**
- **Why:** p-values tell us IF there's an effect, not HOW BIG it is. A study with 1000 prompts might find p < 0.001 for a 0.1-point improvement — statistically significant but practically useless.
- **Interpretation:** d < 0.2 (negligible), 0.2-0.5 (small), 0.5-0.8 (medium), > 0.8 (large)

**95% Confidence Interval**
- **Why:** Gives a range for the true improvement, not just a point estimate
- **Interpretation:** "We are 95% confident the true improvement is between +1.2 and +2.4 points"

**One-Way ANOVA**
- **Why:** Compares ALL strategies simultaneously. Running multiple t-tests inflates false positive rate (multiple comparisons problem). ANOVA tests the null hypothesis that all strategies produce equal improvement.
- **What it tells us:** Are there ANY significant differences between strategies? (If yes, follow up with pairwise comparisons)

---

## Step 8: Generate Result Tables

The evaluation script generates up to 7 tables:

| Table | Contents | Maps To |
|-------|----------|---------|
| Table 1 | Score improvement by strategy (mean ± SD, p-value, Cohen's d, 95% CI) | RQ1, RQ2, RQ3 |
| Table 2 | High-severity defect reduction % by strategy | RQ4 |
| Table 3 | Time & cost efficiency (seconds, dollars, cost per score point) | Practical deployment |
| Table 4 | Per-category breakdown (QA, Code, Summarization, etc.) | Task-specific insights |
| Table 5 | ANOVA across all strategies | RQ2 (omnibus test) |
| Table 6 | Technique effectiveness rankings | RQ5 |
| Table 7 | **Cross-provider comparison** (Gemini 3.1 Pro vs Claude Sonnet 4.6) | Provider generalizability |

> Table 7 is only generated when `--providers` flag specifies multiple providers.

---

## Step 9: Ablation Study (optional)

**WHAT:** Run the unified pipeline with one component removed at a time.

**WHY:** Shows the individual contribution of each module. If removing DGEO drops the score by 0.5 but removing CDRAF only drops it by 0.1, we know DGEO contributes more.

**HOW:**
```bash
# Full pipeline (baseline for ablation)
python scripts/run_evaluation.py --strategies unified --limit 30 --provider gemini

# Without DGEO: manually set DGEO to skip in optimizer_service.py
# Without SHDT: manually set SHDT to skip
# Without CDRAF: manually set CDRAF to skip
```

This requires manual code changes (commenting out phases in `optimize_unified()`), so it's done as a follow-up experiment.

---

## How to Run

### Quick Test (2 prompts, 1 strategy)
```bash
python scripts/run_evaluation.py --strategies standard --limit 2 --provider groq
```

### Single-Provider Evaluation — Gemini 3.1 Pro (30 prompts, CLT minimum)
```bash
python scripts/run_evaluation.py --strategies standard,dgeo,shdt,cdraf,unified --limit 30 --provider gemini
```

### Single-Provider Evaluation — Claude Sonnet 4.6 (30 prompts, CLT minimum)
```bash
python scripts/run_evaluation.py --strategies standard,dgeo,shdt,cdraf,unified --limit 30 --provider anthropic
```

### Cross-Provider Comparison — Gemini vs Claude (all 55 prompts, generates Table 7)
```bash
python scripts/run_evaluation.py --strategies standard,dgeo,shdt,cdraf,unified --providers gemini,anthropic
```

### Full Evaluation (all 55 prompts, all strategies)
```bash
python scripts/run_evaluation.py --strategies standard,dgeo,shdt,cdraf,unified --provider gemini
```

### Output
- Console: Pretty-printed tables (copy into paper)
- `data/evaluation/results_{timestamp}.json`: Full raw data
- `data/evaluation/summary_{timestamp}.csv`: Spreadsheet-ready summary

---

## Interpreting Results

### What Counts as "Good"?

| Metric | Poor | Acceptable | Good | Excellent |
|--------|------|-----------|------|-----------|
| Score improvement | < 0.5 | 0.5-1.0 | 1.0-2.0 | > 2.0 |
| High-severity reduction | < 20% | 20-40% | 40-60% | > 60% |
| Cohen's d | < 0.2 | 0.2-0.5 | 0.5-0.8 | > 0.8 |
| p-value | > 0.1 | 0.05-0.1 | 0.01-0.05 | < 0.01 |

### Common Pitfalls
- **Low n warning:** If fewer than 10 prompts per strategy, confidence intervals will be wide and p-values may not reach significance even with large effects
- **Ceiling effect:** Prompts that start with score 8+ have little room for improvement — this isn't a failure of the system
- **Cost variation:** API costs depend on prompt length and LLM response length — compare cost-per-improvement-point, not raw cost
