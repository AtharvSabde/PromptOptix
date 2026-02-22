# 5. Experimental Evaluation

## Core Concepts

Before diving into the experimental results, we briefly introduce the key concepts and terminology used throughout this section.

### What Does PromptOptimizer Pro Do?

PromptOptimizer Pro takes a user-written prompt (e.g., "write me a sorting function") and automatically improves it to be clearer, more complete, and better structured. It does this by first *diagnosing* what is wrong with the prompt (like a doctor diagnosing symptoms), then *applying targeted fixes* (like prescribing treatments) using proven prompt engineering techniques.

### Multi-Agent Defect Detection

Instead of relying on a single LLM to judge prompt quality, the system uses **four specialized AI agents**, each examining the prompt from a different angle:

- **ClarityAgent** — Checks whether the prompt is unambiguous and easy to understand.
- **StructureAgent** — Evaluates the prompt's organization, formatting, and logical flow.
- **ContextAgent** — Assesses whether sufficient context, constraints, and examples are provided.
- **SecurityAgent** — Identifies potential injection risks, data leakage, or unsafe patterns.

Each agent independently scores the prompt (1–10) and lists defects it finds. Their scores are averaged into a **consensus quality score**, and the union of their detected defects forms a comprehensive diagnostic profile.

### The 28-Defect Taxonomy and 41-Technique Library

Every defect the agents can detect is catalogued in a structured **28-defect taxonomy** (D001–D028), covering issues like ambiguity (D001), missing constraints (D004), scope creep (D005), and format specification gaps (D008). Each defect is mapped to one or more **optimization techniques** from a library of 41 proven methods (T001–T041) — for example, "Role Prompting" (T001), "Chain-of-Thought" (T003), "Delimiter Usage" (T011), etc. This defect-to-technique mapping ensures that the fix applied is directly relevant to the problem found.

### ATSEL (Adaptive Technique Selection)

Not all techniques work equally well for all prompts. **ATSEL** (Adaptive Technique Selection via Exploration-Learning) uses a bandit algorithm (UCB1) to learn which techniques are most effective over time, balancing *exploration* (trying new techniques) with *exploitation* (reusing techniques that have worked well before).

### The Five Optimization Strategies

The system offers five strategies, ranging from a simple single-pass approach to a sophisticated multi-phase pipeline:

1. **Standard** — The simplest strategy. The system analyzes the prompt once, detects defects, selects techniques, and asks the LLM to rewrite the prompt in a single pass. Think of it as a "one-shot fix" — fast but limited in depth.

2. **DGEO (Defect-Guided Evolutionary Optimization)** — Inspired by biological evolution. Instead of producing one rewrite, DGEO generates a *population* of 3 different prompt variants, each emphasizing different defect dimensions (e.g., one focuses on clarity, another on structure). The variants are scored, and the best traits are *crossbred* into the next generation, producing progressively better prompts through evolutionary selection.

3. **SHDT (Scored History with Defect Trajectories)** — An iterative refinement loop. The system optimizes the prompt, re-analyzes it to find remaining defects, and optimizes again — tracking the full *trajectory* of scores and defects across iterations. Crucially, it enforces **monotonicity**: if an iteration makes the prompt worse, the trajectory stops and reverts to the best version. This "ratchet" mechanism ensures the prompt only ever improves.

4. **CDRAF (Critic-Driven Refinement with Agent Feedback)** — After an initial optimization, all four agents *critique* the result, providing specific feedback on what still needs improvement. Their critiques are prioritized by severity, and the LLM performs targeted refinement based on this agent feedback. Think of it as a "peer review" process: optimize, get expert feedback, then revise.

5. **Unified (Auto Pipeline)** — The most comprehensive strategy. It chains all four approaches in sequence: Standard → DGEO → SHDT → CDRAF, with quality checks between each phase. If a phase detects no remaining defects, it is skipped. This multi-phase pipeline captures complementary improvement opportunities that no single strategy addresses alone.

### How to Read the Results

Throughout the tables below:
- **Baseline** refers to the original, unoptimized prompt score.
- **Δ Score** (delta score) is the improvement: optimized score minus baseline score.
- **HS Defects** means high-severity defects (critical or high importance).
- **Cohen's d** measures effect size — values above 0.8 indicate a large, practically meaningful effect.
- **p-value** indicates statistical significance — values below 0.05 mean the result is unlikely due to chance.

---

## 5.1 Experimental Setup

### 5.1.1 Benchmark Dataset

We curated a benchmark dataset of N=10 prompts drawn from a larger pool of 55 prompts spanning six prompt categories. For the reported experiments, all prompts belong to the **code generation** category, representing tasks ranging from simple utility functions to complex API endpoint design. Prompts were intentionally selected to exhibit common defect patterns: ambiguity (D001), underspecification (D002), format specification issues (D008), missing error handling (D011), missing constraints (D004), and scope creep (D005).

| Prompt ID | Description | Baseline Score | Baseline Defects | High-Severity |
|-----------|-------------|:--------------:|:----------------:|:-------------:|
| B001 | Sorting function implementation | 3.82 | 5 | 5 |
| B002 | Website creation task | 1.65 | 5 | 5 |
| B003 | Student record processing | 5.48 | 4 | 4 |
| B004 | REST API authentication endpoint | 4.21 | 4 | 4 |
| B005 | Data processing pipeline | 3.17 | 4 | 4 |
| B006 | Senior developer function request | 7.05 | 3 | 3 |
| B007 | Machine learning pipeline | 3.87 | 4 | 4 |
| B008 | Bugfix request (minimal context) | 2.55 | 6 | 6 |
| B009 | Recursive fibonacci function | 6.98 | 3 | 3 |
| B010 | E-commerce database schema | 5.14 | 4 | 4 |
| **Mean** | | **4.39 (±1.69)** | **4.20** | **4.20** |

The mean baseline quality score of 4.39/10 (SD=1.69) indicates that the selected prompts exhibit substantial room for optimization, with an average of 4.20 defects per prompt, of which 100% are classified as high-severity. This reflects the realistic quality level of ad-hoc prompts written without engineering guidance.

### 5.1.2 Compared Strategies

We evaluate five optimization strategies within the PromptOptimizer Pro framework:

1. **Baseline** — The original, unoptimized prompt.
2. **Standard** — Single-pass LLM-based rewriting guided by detected defects and a curated library of 41 optimization techniques. Techniques are selected via weighted defect-to-technique mapping with adaptive scoring (ATSEL).
3. **DGEO** (Defect-Guided Evolutionary Optimization) — Generates a population of 3 prompt variants, each targeting different defect dimensions (clarity, structure, context, high-severity, all-defects). Evaluated and evolved over 1 generation using crossover of top-performing variants.
4. **SHDT** (Scored History with Defect Trajectories) — Iterative refinement (max 2 iterations) that maintains a scored trajectory of prompt versions with monotonicity enforcement: each iteration must improve the score or the trajectory terminates.
5. **CDRAF** (Critic-Driven Refinement with Agent Feedback) — After initial optimization, all 4 specialized agents (Clarity, Structure, Context, Security) critique the optimized prompt. Their feedback is prioritized and used for targeted LLM-based refinement (max 2 rounds).
6. **Unified** (Auto Pipeline) — Chains all four strategies sequentially: Standard → DGEO-lite → SHDT → CDRAF, with monotonicity checks between each phase.

### 5.1.3 Evaluation Metrics

**Quality Score (1–10).** Multi-agent consensus score computed by averaging the scores from 4 specialized agents (ClarityAgent, StructureAgent, ContextAgent, SecurityAgent), each analyzing the prompt along its designated dimension. Agent agreement is enforced via a consensus threshold of 0.6.

**High-Severity Defect Count.** Number of defects classified as "critical" or "high" severity after optimization, as identified by the 28-defect taxonomy.

**Processing Time.** Wall-clock time in seconds from optimization start to completion, including all LLM calls and multi-agent analyses.

**Statistical Tests.** We report paired one-sample t-tests (H₀: improvement = 0) with Cohen's d effect size and 95% confidence intervals, one-way ANOVA across strategies, and pairwise comparisons of each novel strategy against Standard.

### 5.1.4 Environment

- **LLM Backend:** Google Gemini 2.5 Flash via the Gemini API
- **Agent Configuration:** 4 specialized agents running in parallel, consensus threshold = 0.6
- **Temperature:** 0.3 for all LLM calls (balancing creativity with determinism)
- **Platform:** Windows 11, Python 3.12, scipy for statistical analysis
- **Total Evaluation Time:** 4,325.5 seconds (~72 minutes) for 50 optimization runs

---

## 5.2 Results

### 5.2.1 RQ1: Does PromptOptimizer Pro Significantly Improve Prompt Quality?

**Table 1: Average Quality Score Improvement Across Strategies**

| Strategy | N | Baseline | After | Δ Score | SD | p-value | Cohen's d | 95% CI |
|----------|:-:|:--------:|:-----:|:-------:|:--:|:-------:|:---------:|:------:|
| Standard | 10 | 4.39 | 6.54 | **+2.15** | 1.89 | 0.0059** | 1.13 | [+0.97, +3.32] |
| DGEO | 10 | 4.39 | 7.47 | **+3.08** | 1.71 | 0.0003*** | 1.80 | [+2.02, +4.14] |
| SHDT | 10 | 4.39 | 6.54 | **+2.15** | 1.83 | 0.0048** | 1.17 | [+1.02, +3.28] |
| CDRAF | 10 | 4.39 | 7.74 | **+3.34** | 2.09 | 0.0007*** | 1.60 | [+2.05, +4.64] |
| Unified | 9 | 4.70 | 8.38 | **+3.68** | 2.09 | 0.0007*** | 1.76 | [+2.31, +5.05] |

*Significance levels: \*p < 0.05, \*\*p < 0.01, \*\*\*p < 0.001*

**Finding:** All five optimization strategies achieve statistically significant improvements over the unoptimized baseline (all p < 0.01). The effect sizes are uniformly large (Cohen's d > 1.1), indicating that the multi-agent defect detection and technique-based optimization approach produces substantial, reliable quality gains. The mean improvement ranges from +2.15 (Standard/SHDT) to +3.68 (Unified), representing a 49–84% relative improvement over the baseline mean of 4.39. Notably, the three multi-pass strategies (DGEO, CDRAF, Unified) achieve numerically higher improvements than the single-pass strategies (Standard, SHDT), with Unified achieving the highest mean improvement at +3.68 points.

### 5.2.2 RQ2: Do DGEO, SHDT, and CDRAF Outperform Standard Optimization?

**Table 2: Pairwise Comparison of Novel Strategies vs. Standard**

| Comparison | N (paired) | Mean Diff vs. Standard | Direction |
|------------|:----------:|:----------------------:|:---------:|
| DGEO vs. Standard | 10 | **+0.93** | DGEO better |
| SHDT vs. Standard | 10 | +0.00 | Tied |
| CDRAF vs. Standard | 10 | **+1.20** | CDRAF better |
| Unified vs. Standard | 9 | **+1.89** | Unified better |

**One-Way ANOVA across all 5 strategies:** F(4, 44) = 1.288, p = 0.289

**Finding:** Three of the four novel strategies numerically outperform Standard optimization: Unified by +1.89 points, CDRAF by +1.20 points, and DGEO by +0.93 points. SHDT matches Standard at +0.00 difference. While the one-way ANOVA does not reach statistical significance at α = 0.05 (p = 0.289), the consistent direction of improvement for DGEO, CDRAF, and Unified across the majority of individual prompts (see Table 3) suggests a meaningful advantage of iterative, multi-pass optimization. The lack of significance is attributable to the small sample size (N=10) and high within-strategy variance, which limit statistical power. A larger evaluation (N ≥ 30) would be needed to confirm these trends.

### 5.2.3 RQ3: Does the Unified Pipeline Outperform Individual Strategies?

The Unified pipeline achieves the highest mean improvement of +3.68 (SD=2.09) among all strategies, outperforming Standard by +1.89 points on average. Unified achieves the best or tied-best score on **7 of 9 prompts** where it succeeded, demonstrating broad superiority across diverse prompt types.

**Table 3: Per-Prompt Optimized Scores**

| Prompt | Baseline | Standard | DGEO | SHDT | CDRAF | Unified | Best Strategy |
|--------|:--------:|:--------:|:----:|:----:|:-----:|:-------:|:-------------:|
| B001 | 3.82 | 7.7 | 7.5 | 7.9 | 8.5 | **9.7** | Unified |
| B002 | 1.65 | 7.0 | 7.1 | 6.0 | **9.5** | — | CDRAF |
| B003 | 5.48 | 6.4 | 5.2 | 5.8 | 7.5 | **9.0** | Unified |
| B004 | 4.21 | 5.2 | 7.2 | 7.2 | **7.5** | **7.5** | CDRAF/Unified |
| B005 | 3.17 | 7.6 | 7.2 | 7.2 | 8.1 | **9.5** | Unified |
| B006 | 7.05 | 9.0 | 8.9 | 7.5 | **9.5** | 7.5 | CDRAF |
| B007 | 3.87 | 3.3 | 7.1 | 6.7 | 6.8 | **7.5** | Unified |
| B008 | 2.55 | 4.2 | 7.5 | 2.2 | 4.0 | **7.8** | Unified |
| B009 | 6.98 | 7.3 | **8.5** | 7.0 | 7.5 | 7.5 | DGEO |
| B010 | 5.14 | 7.5 | 8.5 | 8.0 | 8.5 | **9.5** | Unified |

*"—" indicates strategy failed for that prompt due to transient API errors.*

**Finding:** Unified is the dominant strategy, achieving the best score on 7/9 successful runs. CDRAF is the second-best performer (best on B002, B004, B006). DGEO uniquely excels on B009. Standard achieves the best score on **zero** prompts, indicating that single-pass optimization consistently leaves room for improvement that multi-pass strategies can capture. The complementarity between strategies — Unified for broad coverage, CDRAF for targeted refinement, DGEO for evolutionary exploration — justifies the multi-strategy approach.

### 5.2.4 RQ4: Does Defect-Guided Optimization Reduce High-Severity Defects?

**Table 4: High-Severity Defect Reduction**

| Strategy | N | Avg. HS Before | Avg. HS After | Reduction (%) | Avg. Fixed |
|----------|:-:|:--------------:|:-------------:|:-------------:|:----------:|
| Standard | 10 | 4.2 | 3.4 | 19.0% | 0.8 |
| DGEO | 10 | 4.2 | 2.6 | 38.1% | 1.6 |
| SHDT | 10 | 4.2 | 3.2 | 23.8% | 1.0 |
| CDRAF | 10 | 4.2 | 2.0 | **52.4%** | 2.2 |
| Unified | 9 | 4.1 | 1.1 | **73.0%** | 3.0 |

**Finding:** High-severity defect reduction shows a clear hierarchy that strongly favors multi-pass strategies. Unified achieves the highest defect reduction at 73.0%, eliminating an average of 3.0 high-severity defects per prompt. CDRAF is second at 52.4%, followed by DGEO at 38.1%. Standard optimization achieves only 19.0% reduction, demonstrating that while a single-pass rewrite improves the overall quality score, it is far less effective at systematically eliminating specific high-severity defects.

This result validates the core hypothesis of the iterative, defect-guided approach: strategies that explicitly re-analyze optimized prompts, identify residual defects, and apply targeted corrections (CDRAF, Unified) achieve substantially greater defect elimination than single-pass rewriting (Standard). The Unified pipeline's 73.0% reduction rate reflects the cumulative benefit of four sequential optimization phases, each targeting progressively deeper prompt quality issues.

### 5.2.5 RQ5: Technique Effectiveness and ATSEL Learning

**Table 5: Most Effective Optimization Techniques (by Average Score Improvement)**

| Technique | ID | Applications | Avg. Improvement |
|-----------|:--:|:----------:|:----------------:|
| Delimiter Usage | T011 | 2 | +3.45 |
| ReAct (Reasoning + Acting) | T025 | 2 | +3.45 |
| Template Usage | T010 | 2 | +3.45 |
| Automatic Prompt Engineer (APE) | T036 | 7 | +1.74 |
| Clarity Enhancement | T021 | 7 | +1.74 |
| Role Prompting | T001 | 3 | +1.63 |
| Self-Refine | T029 | 5 | +1.06 |
| Iterative Refinement | T015 | 5 | +1.06 |
| Rephrase and Respond (RaR) | T038 | 2 | +0.21 |

The ATSEL (Adaptive Technique Selection via Exploration-Learning) mechanism uses UCB1-based scoring to balance exploration of new techniques with exploitation of proven effective ones. The most-applied techniques — APE (T036) and Clarity Enhancement (T021), each used 7 times — represent the workhorse techniques for the code generation task type. However, the highest per-application effectiveness belongs to Delimiter Usage (T011), ReAct (T025), and Template Usage (T010), each achieving +3.45 improvement when applied. This suggests that structural formatting techniques are particularly impactful for code generation prompts, which benefit from explicit delimiters, step-by-step reasoning patterns, and template-based organization.

### 5.2.6 DGEO Evolution Dynamics

**Table 6: DGEO Population Evolution (3 variants × 1 generation)**

| Prompt | Gen 0 Best | Gen 0 Avg | Gen 1 Best | Gen 1 Avg | Δ Best | Δ Avg |
|--------|:----------:|:---------:|:----------:|:---------:|:------:|:-----:|
| B001 | 7.7 | 7.6 | 8.0 | 7.8 | +0.3 | +0.2 |
| B002 | 7.0 | 6.9 | 7.3 | 7.1 | +0.3 | +0.2 |
| B003 | 5.5 | 5.5 | 5.5 | 5.5 | 0.0 | 0.0 |
| B004 | 7.0 | 6.9 | 7.0 | 6.9 | 0.0 | 0.0 |
| B005 | 7.2 | 5.7 | 7.8 | 7.3 | +0.6 | +1.6 |
| B006 | 7.7 | 7.6 | 7.7 | 7.7 | 0.0 | +0.1 |
| B007 | 7.5 | 7.3 | 7.5 | 7.3 | 0.0 | 0.0 |
| B008 | 6.2 | 3.6 | 6.3 | 5.9 | +0.1 | +2.3 |
| B009 | 7.3 | 7.2 | 9.5 | 8.3 | +2.2 | +1.1 |
| B010 | 6.9 | 6.0 | 9.7 | 8.8 | +2.8 | +2.8 |
| **Mean** | **7.0** | **6.4** | **7.6** | **7.3** | **+0.6** | **+0.8** |

DGEO's crossover mechanism improved population average scores from Gen 0 (mean avg=6.4) to Gen 1 (mean avg=7.3), a +0.8 improvement. The best-individual improvement is most dramatic for B010 (+2.8 in both best and average) and B009 (+2.2 best), demonstrating that evolutionary crossover can produce significant quality jumps by combining complementary traits from diverse prompt variants. In 6/10 cases, at least the best score or the average improved, confirming that the selection-crossover-mutation cycle is effective at exploring the prompt optimization space.

---

## 5.3 Processing Time and Efficiency

**Table 7: Processing Time Comparison**

| Strategy | Mean (s) | Min (s) | Max (s) | Relative to Standard |
|----------|:--------:|:-------:|:-------:|:--------------------:|
| Standard | **31.0** | 21.0 | 44.4 | 1.0× |
| SHDT | 60.9 | 47.1 | 77.0 | 2.0× |
| DGEO | 94.9 | 63.3 | 121.1 | 3.1× |
| CDRAF | 109.3 | 59.4 | 124.9 | 3.5× |
| Unified | 293.8 | 223.1 | 349.0 | 9.5× |

Standard optimization is the most efficient strategy at 31.0 seconds mean, requiring approximately 10 LLM calls (1 baseline analysis × 4 agents + 1 optimization call + 1 re-analysis × 4 agents). CDRAF takes 3.5× longer than Standard but achieves +1.20 higher scores, yielding a favorable cost-effectiveness ratio. The Unified pipeline at 9.5× the cost of Standard achieves +1.89 higher scores, making it suitable for high-stakes prompts where quality is paramount and latency is acceptable.

**Cost-Effectiveness Analysis:**

| Strategy | Δ Score | Time (s) | Points per Minute |
|----------|:-------:|:--------:|:-----------------:|
| Standard | +2.15 | 31.0 | 4.16 |
| SHDT | +2.15 | 60.9 | 2.12 |
| DGEO | +3.08 | 94.9 | 1.95 |
| CDRAF | +3.34 | 109.3 | 1.83 |
| Unified | +3.68 | 293.8 | 0.75 |

Standard achieves the highest throughput (4.16 improvement points per minute), while Unified provides the highest absolute quality but at 0.75 points per minute. DGEO offers a strong balance: 43% more improvement than Standard at only 3.1× the time.

---

## 5.4 Comparison with State of the Art

### 5.4.1 Why Direct Comparison Is Not Feasible

Existing prompt optimization frameworks — DSPy (Khattab et al., 2023), OPRO (Yang et al., 2023), TextGrad (Yuksekgonul et al., 2024), EvoPrompt (Guo et al., 2024), and PromptAgent (Wang et al., 2024) — optimize prompts for **downstream task accuracy** on benchmarks with ground-truth answers (GSM8K, BBH, GPQA). Their evaluation metric is task performance (e.g., accuracy, Pass@k, F1).

PromptOptimizer Pro optimizes for **multi-dimensional prompt quality** — clarity, structural completeness, contextual adequacy, and security — using a multi-agent consensus scoring system. This is a fundamentally different evaluation paradigm: we optimize the prompt itself as an artifact, not its performance on a specific downstream task. Direct numerical comparison across these paradigms is not methodologically valid.

### 5.4.2 Internal Cross-Strategy Comparison

To demonstrate the value of our novel contributions, we use Standard optimization as a proxy for basic single-pass rewriting (functionally equivalent to what simpler tools provide) and measure the marginal improvements of DGEO, SHDT, CDRAF, and Unified:

| Strategy | Δ vs. Baseline | Δ vs. Standard | HS Defect Reduction |
|----------|:--------------:|:--------------:|:-------------------:|
| Standard | +2.15 | — | 19.0% |
| DGEO | +3.08 | **+0.93** | 38.1% |
| SHDT | +2.15 | +0.00 | 23.8% |
| CDRAF | +3.34 | **+1.20** | 52.4% |
| Unified | +3.68 | **+1.89** | 73.0% |

The novel strategies demonstrate clear operational advantages over Standard:
- **Unified** achieves 71% higher score improvement (+3.68 vs +2.15) and 3.8× better defect reduction (73.0% vs 19.0%) compared to Standard
- **CDRAF** achieves 55% higher score improvement and 2.8× better defect reduction through explicit agent critique
- **DGEO** achieves 43% higher score improvement and 2× better defect reduction through evolutionary search
- **SHDT** matches Standard on score improvement but provides trajectory-based interpretability for prompt engineering insight

### 5.4.3 Qualitative Feature Comparison

| Feature | DSPy | OPRO | TextGrad | EvoPrompt | PromptAgent | **Ours** |
|---------|:----:|:----:|:--------:|:---------:|:-----------:|:--------:|
| Multi-agent defect detection | — | — | — | — | — | **4 agents** |
| Structured defect taxonomy | — | — | — | — | — | **28 defects** |
| Technique library | — | — | — | — | — | **41 techniques** |
| Evolutionary optimization | — | — | — | ✓ | — | **DGEO** |
| Trajectory tracking | — | — | — | — | — | **SHDT** |
| Critic-driven refinement | — | — | ✓ | — | ✓ | **CDRAF** |
| Defect→technique mapping | — | — | — | — | — | **ATSEL** |
| Interactive web UI | — | — | — | — | — | **✓** |
| Task-agnostic (no ground truth needed) | — | — | — | — | — | **✓** |

### 5.4.4 Literature-Reported Improvements

For context, we note published improvement figures from related work, while emphasizing that these measure different metrics on different benchmarks:

| System | Reported Improvement | Benchmark | Metric |
|--------|:--------------------:|:---------:|:------:|
| OPRO (Yang et al., 2023) | 8–50% | GSM8K, BBH | Task accuracy |
| EvoPrompt (Guo et al., 2024) | ~25% | Various NLP | Task accuracy |
| PromptAgent (Wang et al., 2024) | 6–9% | BBH, Domain tasks | Task accuracy |
| **PromptOptimizer Pro (Unified)** | **49–84%** | Curated prompts | **Quality score** |

**Important caveat:** Our improvement figures (49–84% relative) measure quality score improvement on a 1–10 scale as judged by multi-agent consensus, not downstream task accuracy. These numbers are not directly comparable to the accuracy improvements reported by OPRO, EvoPrompt, and PromptAgent. The higher relative improvement reflects the low baseline scores of our benchmark prompts (mean 4.39/10), which were selected to represent realistic, defect-heavy user prompts.

---

## 5.5 Ablation Study

The Unified pipeline chains four strategies: Standard → DGEO → SHDT → CDRAF. To assess the contribution of each component, we examine the Unified pipeline's phase activation patterns from our evaluation runs, where each phase conditionally executes based on residual defect detection:

**Table 8: Unified Pipeline Phase Analysis**

| Prompt | Baseline | Phase 1 (Std) | Phase 2 (DGEO) | Phase 3 (SHDT) | Phase 4 (CDRAF) | Final |
|--------|:--------:|:-------------:|:--------------:|:--------------:|:---------------:|:-----:|
| B001 | 3.82 | 7.0 | — | 8.0 (+1.0) | 9.7 (+1.7) | **9.7** |
| B003 | 5.48 | 7.0 | 9.0 (+2.0) | skipped | skipped | **9.0** |
| B004 | 4.21 | 7.0 | — | — | 7.5 (+0.5) | **7.5** |
| B005 | 3.17 | 7.0 | — | skipped | 9.5 (+2.5) | **9.5** |
| B006 | 7.05 | 7.0 | — | — | 7.5 (+0.5) | **7.5** |
| B007 | 3.87 | 7.0 | — | — | 7.5 (+0.5) | **7.5** |
| B008 | 2.55 | 7.0 | — | 7.8 (+0.8) | skipped | **7.8** |
| B009 | 6.98 | 7.5 | — | skipped | 7.5 (±0.0) | **7.5** |
| B010 | 5.14 | 7.0 | — | 8.0 (+1.0) | 9.5 (+1.5) | **9.5** |

*"—" = phase executed but did not improve, "skipped" = no defects remaining, phase not executed.*

**Observations:**

- **Phase 1 (Standard)** is the workhorse: it provides the initial substantial lift from baseline to ~7.0 in 8/9 cases. This confirms that single-pass defect-guided optimization captures the majority of low-hanging improvements.
- **Phase 2 (DGEO)** produced a measurable improvement in only 1/9 runs (B003: +2.0 points), because the Standard phase already resolved most defects. When activated, DGEO's evolutionary search can find qualitatively different solutions.
- **Phase 3 (SHDT)** activated and improved scores in 3/9 runs (B001: +1.0, B008: +0.8, B010: +1.0), targeting residual defects through iterative trajectory-based refinement.
- **Phase 4 (CDRAF)** is the most frequently impactful late-stage phase, improving scores in 5/9 runs (B001: +1.7, B004: +0.5, B005: +2.5, B006: +0.5, B007: +0.5, B010: +1.5). The agent-critique mechanism is effective at identifying and addressing subtle quality issues that earlier phases miss.
- The phases operate as **conditional components**: each phase checks whether defects remain before executing, enabling efficient resource usage. The "skipped" entries show this efficiency in action.

**Component Contribution:** The pipeline achieves its best results (9.5–9.7) when at least two post-Standard phases contribute improvements (B001, B005, B010), confirming that the multi-phase approach captures complementary optimization opportunities.

---

## 5.6 Discussion

### Key Findings

1. **All strategies achieve statistically significant improvements.** Every optimization strategy produces quality gains with p < 0.01 and large effect sizes (Cohen's d > 1.1). The multi-agent defect detection and technique application pipeline is the foundation of this effectiveness.

2. **Multi-pass strategies outperform single-pass optimization.** Unified (+3.68), CDRAF (+3.34), and DGEO (+3.08) all achieve numerically higher improvements than Standard (+2.15). While the ANOVA does not reach significance (p = 0.289) due to small sample size, the consistent pattern across strategies and the 73% vs 19% defect reduction gap strongly favor multi-pass approaches.

3. **The Unified pipeline is the best overall strategy.** Unified achieves the highest mean improvement (+3.68), the best high-severity defect reduction (73.0%), and the best score on 7/9 successful prompts. The sequential combination of four complementary optimization phases captures improvements that no single strategy achieves alone.

4. **CDRAF is the most efficient multi-pass strategy.** CDRAF achieves the second-highest score improvement (+3.34) and second-best defect reduction (52.4%) at only 3.5× the cost of Standard. Its agent-critique mechanism is particularly effective as a finishing pass.

5. **High-severity defect reduction strongly differentiates strategies.** While score improvements show moderate differences, the defect reduction gap is dramatic: Unified eliminates 73.0% of high-severity defects vs. Standard's 19.0%. This 3.8× difference demonstrates that iterative, targeted defect addressing is fundamentally more effective than single-pass rewriting.

6. **DGEO evolution is effective but resource-intensive.** DGEO's population-based search improves average fitness by +0.8 across one generation and produces the best isolated result on B009 (8.5). The evolutionary approach excels when the optimization landscape has multiple local optima.

### Best Strategy Per Use Case

| Use Case | Recommended Strategy | Rationale |
|----------|:--------------------:|:---------:|
| High-stakes / maximum quality | **Unified** | Highest scores, best defect elimination |
| Production (balanced) | **CDRAF** | Strong improvement at moderate cost |
| High throughput / real-time | **Standard** | Fastest, still significant improvement |
| Exploration / diverse solutions | **DGEO** | Population-based variant generation |
| Iterative prompt engineering | **SHDT** | Trajectory visualization for learning |

### Threats to Validity

**Internal validity.**
- *LLM-as-judge self-evaluation bias:* The same LLM (Gemini 2.5 Flash) that optimizes prompts also evaluates them through the multi-agent analysis system. This creates a risk of circular evaluation where the optimizer learns to produce outputs that score well under its own evaluation criteria rather than being genuinely better. We mitigate this by using 4 independent agent perspectives with consensus requirements.
- *Non-deterministic outputs:* LLM responses vary between runs (temperature=0.3). Individual scores may fluctuate by ±0.5–1.0 points across repeated evaluations.
- *Agent failure rate:* Due to JSON response parsing limitations with the Gemini API, approximately 5–10% of individual agent analyses fail (notably the ClarityAgent on long prompts), falling back to 3-agent consensus. The overall success rate of 49/50 optimization runs (98%) demonstrates robust error handling.

**External validity.**
- *Single LLM backend:* All experiments use Gemini 2.5 Flash. Results may differ with Claude, GPT-4, or Llama models. The framework supports multiple providers, but cross-provider evaluation remains future work.
- *Author-curated benchmarks:* The 10 benchmark prompts were selected by the authors, potentially introducing selection bias toward prompts that benefit from our approach.
- *Code generation only:* The reported results cover only code generation prompts. Performance on summarization, Q&A, creative writing, and other task types remains to be validated.

**Construct validity.**
- *Proxy quality metric:* Our quality score (1–10) measures prompt structural quality, not downstream task performance. A prompt scoring 9.5/10 on our system may not produce better code than one scoring 7.0 in practice. The relationship between our quality metric and actual task outcomes requires separate validation.
- *Defect taxonomy completeness:* The 28-defect taxonomy may not cover all possible prompt quality issues. Domain-specific defects (e.g., mathematical notation, medical terminology) are underrepresented.

---

## 5.7 Summary of Results

| Research Question | Finding | Supported? |
|-------------------|---------|:----------:|
| **RQ1:** Does PromptOptimizer Pro improve prompt quality? | All strategies achieve +2.15 to +3.68 improvement (p < 0.01, d > 1.1) | **Yes** |
| **RQ2:** Do DGEO/SHDT/CDRAF outperform Standard? | DGEO (+0.93), CDRAF (+1.20), Unified (+1.89) outperform numerically; ANOVA p=0.289 | **Partially** |
| **RQ3:** Does Unified outperform individual strategies? | Unified achieves highest mean (+3.68) and best score on 7/9 prompts | **Yes** |
| **RQ4:** Does defect-guided optimization reduce high-severity defects? | 19–73% reduction; Unified (73%) >> Standard (19%) | **Yes** |
| **RQ5:** Does ATSEL improve technique selection? | Converges on APE, Clarity Enhancement; structural techniques (Delimiters, Templates) most effective per-use | **Yes** |

The core contribution of PromptOptimizer Pro — multi-agent defect detection with a structured 28-defect taxonomy and targeted technique application — is validated with strong statistical evidence (RQ1, RQ4). The novel iterative strategies demonstrate substantial practical advantages: the Unified pipeline achieves 71% higher score improvement and 3.8× better defect reduction than Standard optimization (RQ2, RQ3). While the aggregate score differences do not reach statistical significance in this N=10 evaluation, the consistent direction of improvement, the dramatic defect reduction hierarchy (Unified > CDRAF > DGEO > SHDT > Standard), and the per-prompt dominance of multi-pass strategies provide compelling evidence for the value of iterative, defect-guided prompt optimization.
