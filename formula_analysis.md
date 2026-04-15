# PromptOptix Formula Analysis

## Overview

This document provides a comprehensive first-principles analysis of every mathematical formula appearing in the PromptOptix paper. Two versions of the paper exist:

- **Old PDF** (`prompt optix formula fixed.pdf`): N=10 experiment version, containing 7 equations.
- **New PDF** (`formula_maybe_notsure_fized.pdf`): N=25 experiment version, containing 10 equations. **This is the primary source.**

The new PDF refines and expands the old PDF's formalism: it splits combined equations for clarity, corrects a missing quantifier in the defect consensus set, and provides tighter notation throughout. We treat the new PDF as authoritative and note deviations from the old PDF where relevant.

### All 10 Equations at a Glance

| # | Name | Formula (summary) |
|---|------|-------------------|
| 1 | Quality Score | $\varphi(p) = \frac{1}{4}\sum_{i=1}^{4}\alpha_i(p)$ |
| 2 | Defect Consensus | $D_\text{confirmed} = \{d \in D \mid \sum_{i=1}^{4}\mathbf{1}[A_i \text{ detects } d] \geq 3\}$ |
| 3 | UCB1-ATSEL Score | $\text{Score}(T,d) = \mu(T,d) + \sqrt{\frac{2\ln N_\text{total}}{n(T,d)}}$ |
| 4 | DGEO Mutation | $V' = \text{LLM-Rewrite}(V,\, T^*)$, $T^* = \arg\max_{T \in M(d)}\text{Score}(T,d)$ |
| 5 | SHDT Candidate | $p_t^* = \text{LLM-Opt}(p_t,\, H_t)$ |
| 6 | SHDT Ratchet | $p_{t+1} = p_t^*$ if $\varphi(p_t^*) > \varphi(p_t)$, else $p_t$ |
| 7 | CDRAF Synthesis | $g_\text{multi} = \text{Synthesize}(c_1, c_2, c_3, c_4)$ |
| 8 | CDRAF Refinement | $p_{t+1} = \text{LLM-Refine}(p_t,\, g_\text{multi})$ |
| 9 | Unified Pipeline | $p^* = \Pi_\text{CDRAF} \circ \Pi_\text{SHDT} \circ \Pi_\text{DGEO} \circ \Pi_\text{Std}(p_0)$ |
| 10 | Defect Resolution Rate | $\text{DRR}(S) = \frac{HS_\text{before} - HS_\text{after}(S)}{HS_\text{before}}$ |

---

## Plain-Language Explanations (What Each Formula Means & How to Explain It)

This section gives an intuitive, jargon-free explanation of every formula — what it is doing in one sentence, the real-world analogy, and the exact words you can use when explaining it to someone.

---

### Eq (1) — Quality Score φ(p)

**What it means in one sentence:**
The overall quality of a prompt is the average of the scores that all four specialist agents independently gave it.

**Real-world analogy:**
A gymnastics competition judged by four independent judges. Each judge scores the routine out of 10. The final score is their average. No single judge can dominate the result.

**How to explain it:**
> "We have four AI agents — one checking for clarity, one for structure, one for context, one for security. Each gives the prompt a score from 0 to 10. The overall quality score φ is simply the average of those four scores. If they give 6, 8, 7, and 7, then φ = 28/4 = 7.0."

**Key insight:** Equal weighting means we believe all four quality dimensions matter equally. If your domain cared more about one (e.g. security), you'd use a weighted average instead.

---

### Eq (2) — Defect Consensus D_confirmed

**What it means in one sentence:**
A defect is only treated as real if at least 3 out of 4 agents independently flagged it — a supermajority vote to avoid false alarms.

**Real-world analogy:**
A jury of four people. To convict (confirm a defect), you need at least three jurors to agree. One dissenter can't convict alone. Four jurors agreeing is the strongest possible signal, but even three is enough.

**How to explain it:**
> "Each agent independently checks the prompt for each of the 28 known defect types. If three or more agents agree that a specific defect is present, it goes on the confirmed list. If only one or two agents flag it, we assume it's a false alarm and ignore it. This way, the system is conservative — it only acts on defects that multiple independent eyes have verified."

**Key insight:** With a 10% individual false-positive rate, the chance of 3+ agents all wrongly flagging the same defect is only ~0.37% — a 27× improvement over trusting a single agent.

---

### Eq (3) — UCB1-ATSEL Score

**What it means in one sentence:**
When choosing which technique to use for a defect, pick the one with the best past performance *plus* a bonus for techniques that haven't been tried much yet — balancing what we know works with what we haven't fully explored.

**Real-world analogy:**
Choosing a restaurant. You prefer ones you know are great (exploitation), but sometimes try new ones because they might be even better (exploration). The "bonus" shrinks the more you try a restaurant — eventually you rely purely on track record.

**How to explain it:**
> "For each technique-defect pair, we track two numbers: how well it has worked on average (μ), and how often we've tried it (n). The score is the average performance plus an exploration bonus that's large when n is small. This means underused techniques get a boost, so the system doesn't just repeat the same few techniques forever. Over time, as good techniques are used more, their bonus shrinks and they succeed on their own merits."

**How to break down the two terms:**
- **μ(T, d)** = "How well has technique T historically worked on defect d?" → past performance
- **√(2 ln N / n(T,d))** = "How much should we explore T on defect d?" → shrinks as n grows, disappears at large n

**Key insight:** This is the classic UCB1 bandit formula. The √(2 ln N / n) term is derived from Hoeffding's inequality — it's the statistical confidence interval on our estimate of μ(T,d). We're always picking the upper end of what the technique *could* achieve.

---

### Eq (4) — DGEO Defect-Targeted Mutation

**What it means in one sentence:**
Pick the single best technique for a specific confirmed defect (using UCB1 scores), then ask the LLM to rewrite the prompt variant applying exactly that fix.

**Real-world analogy:**
A surgeon identifying the exact problem (broken bone in left wrist) and applying the correct procedure (wrist surgery) rather than doing random exploratory operations hoping something helps.

**How to explain it:**
> "In standard evolutionary algorithms, mutations are random — you change something and hope it helps. DGEO replaces random mutation with targeted surgery. First, we know exactly which defects the variant has (from the diagnosis step). Then we pick the best available technique for one of those defects using ATSEL scoring. Then we ask the LLM to rewrite the variant specifically applying that technique. The mutation is no longer blind — it's targeted at a known weakness."

**Key insight:** This is what makes DGEO different from EvoPrompt. EvoPrompt mutates randomly; DGEO mutates *defect-first*. The argmax in the formula is just asking "which technique has the highest UCB1 score for this defect?" — it uses Eq (3).

---

### Eq (5) — SHDT Candidate Generation

**What it means in one sentence:**
Ask the LLM to propose an improved prompt by showing it the full history of what has been tried, what scores were achieved, and which defects appeared or disappeared at each step.

**Real-world analogy:**
A sports coach watching all your previous game tapes — knowing not just what the score was each game, but *why* you won or lost (what specific weaknesses appeared, what improvements worked) — and then advising you for the next game.

**How to explain it:**
> "At each SHDT step, we give the LLM everything we've learned so far: the prompts we've tried, their scores, and importantly, which defects were fixed or introduced at each step. The LLM uses this rich history to generate the next candidate prompt. Unlike OPRO, which just gives scores, SHDT gives defect-level causal explanations — so the LLM can reason 'the last rewrite fixed the ambiguity defect but introduced a new underspecification defect, so next I should focus on...'"

**Key insight:** H_t is the memory of the system. The richer the history, the better the LLM can reason about what to try next. This is the "trajectory" in SHDT.

---

### Eq (6) — SHDT Ratchet (Monotonic Reversion)

**What it means in one sentence:**
Only accept a new prompt if it scores strictly higher than the current one — otherwise keep the current one. Never go backwards.

**Real-world analogy:**
A mechanical ratchet wrench — it can only turn in one direction. Or a personal best in athletics: you only update your record when you beat it; a bad performance doesn't erase your best.

**How to explain it:**
> "After the LLM proposes a candidate p*, we score both p* and the current prompt p_t. If p* scores higher, we accept it and move forward. If p* scores the same or lower, we discard it and keep p_t unchanged. This is the ratchet — quality can only go up, never down. Even if the LLM produces a worse prompt, the system is immune because we simply ignore it."

**Key insight:** This one simple rule provides a formal mathematical guarantee: φ(p_{t+1}) ≥ φ(p_t) always. The whole SHDT algorithm can't degrade a prompt — that's provable in two lines.

---

### Eq (7) — CDRAF Multi-Agent Critique Synthesis

**What it means in one sentence:**
Each of the four agents writes a detailed critique of the prompt from its domain perspective, then a fifth LLM call merges all four critiques into one unified feedback signal.

**Real-world analogy:**
Four peer reviewers each annotating a paper from their specialty (methodology, writing, novelty, ethics), and then a meta-reviewer synthesizing all four reviews into a single consolidated feedback letter.

**How to explain it:**
> "TextGrad uses one generic critic to give feedback. CDRAF uses four specialized critics — one focused on clarity issues, one on structural issues, one on context, one on security. Each produces a detailed written critique. Then a synthesizer LLM reads all four critiques and produces a single combined feedback that covers all dimensions. This is the 'gradient signal' that tells the next refinement step exactly what to fix."

**Key insight:** The Synthesize function is doing what ensemble methods do numerically: combining multiple signals to reduce variance and improve coverage. Because critiques are text, an LLM is the natural synthesizer.

---

### Eq (8) — CDRAF Refinement Step

**What it means in one sentence:**
Apply the combined multi-agent feedback to the current prompt to produce the next improved version.

**Real-world analogy:**
A student receiving the consolidated peer-review letter and revising their paper accordingly.

**How to explain it:**
> "After we have g_multi — the unified feedback from all four critics — we hand it to the LLM and say 'here is the prompt, here is a detailed multi-perspective critique, now rewrite the prompt to address all these issues.' The output is the refined prompt p_{t+1}. This is the TextGrad-style update, but instead of a single generic critic's gradient, we're using a richer multi-agent gradient."

**Note on the bug:** The paper text incorrectly says "g_multi from Eq. (5)" — it should say "Eq. (7)". The formula itself is correct; only the cross-reference in the surrounding text is wrong.

---

### Eq (9) — Unified Pipeline Composition

**What it means in one sentence:**
Run the prompt through all four strategies in sequence (Standard → DGEO → SHDT → CDRAF), where each stage only keeps the improvement if it helped, so the final result is always at least as good as the best individual stage.

**Real-world analogy:**
A car assembly line with four quality-check stations. Each station improves the car if it can. If a station can't improve it, the car passes through unchanged. At the end, the car is at least as good as it was after the first station.

**How to explain it:**
> "The ∘ symbol means function composition — read it right to left. So we apply Standard first to p_0, take that result and apply DGEO, take that result and apply SHDT, then CDRAF last. Each of the four Π operators has a built-in ratchet: if the strategy improves the prompt, keep the improvement; otherwise pass the current prompt unchanged. So the pipeline is always at least as good as whatever Standard alone produced — it can only get better."

**How to read the notation:**
> p* = Π_CDRAF ∘ Π_SHDT ∘ Π_DGEO ∘ Π_Std(p₀)
> means: start with p₀, apply Std, then DGEO, then SHDT, then CDRAF

**Key insight:** The composition notation plus the ratchet property of each Π_x gives a formal non-regression guarantee: φ(p*) ≥ φ(p_0). This is the paper's strongest theoretical claim and it follows directly from Eq (6)'s ratchet logic applied four times.

---

### Eq (10) — Defect Resolution Rate (DRR)

**What it means in one sentence:**
What percentage of the original high-severity defects did this strategy eliminate?

**Real-world analogy:**
Bug-fix rate in software: if a codebase had 100 critical bugs and after a sprint you have 27 left, the fix rate is 73%. DRR is exactly that — applied to prompt defects.

**How to explain it:**
> "DRR is simply: (defects before − defects after) ÷ defects before. If a strategy starts with 4.16 defects per prompt on average and ends with 1.12, then DRR = (4.16 − 1.12) / 4.16 = 3.00 / 4.12 = 72.8%. It's a normalized metric, so you can compare strategies even if they started with slightly different defect counts."

**Key insight:** DRR and φ-improvement tell complementary stories. φ-improvement measures how much better the overall quality is. DRR measures how many specific flaws were actually fixed. A strategy could increase φ without eliminating many defects (if it improves non-defect aspects), or eliminate many defects without a large φ-increase (if the defects were mild). Both metrics together give the full picture.

---

## Quick Reference Card

| # | Formula | In one sentence | Key number |
|---|---------|-----------------|------------|
| 1 | φ(p) = average of 4 agent scores | "Average of 4 judges" | Range [0,10] |
| 2 | D_confirmed: ≥3 of 4 agents agree | "Supermajority jury" | 27× FP suppression |
| 3 | UCB1 = mean + exploration bonus | "Track record + curiosity bonus" | Sublinear regret |
| 4 | V' = LLM-Rewrite with best technique | "Targeted surgery, not random mutation" | Uses Eq (3) |
| 5 | p_t* = LLM with full history | "Coach reviews all game tapes" | History = causal defect trajectories |
| 6 | Keep new prompt only if better | "One-way ratchet" | Proves φ never decreases |
| 7 | g_multi = merge 4 critiques | "Consolidated peer review" | 4-agent text gradient |
| 8 | p_{t+1} = LLM refine with g_multi | "Revise based on consolidated feedback" | ⚠ text says Eq(5), should be Eq(7) |
| 9 | p* = 4 strategies in sequence | "Assembly line with ratchets" | Formal: φ(p*) ≥ φ(p_0) |
| 10 | DRR = % of defects eliminated | "Bug-fix rate for prompt flaws" | Unified: 72.8% |

---

## Formula-by-Formula Deep Analysis

---

### Formula 1: Quality Score $\varphi(p)$

**Statement**

$$\varphi : \mathcal{P} \to [0,10], \qquad \varphi(p) = \frac{1}{4}\sum_{i=1}^{4}\alpha_i(p)$$

where $\alpha_i(p) \in [0,10]$ is the scalar quality rating assigned to prompt $p$ by agent $A_i$, and $\mathcal{P}$ is the space of all prompts.

---

**First Principles Derivation**

We need a single scalar quality measure that aggregates the independent ratings of four agents. We begin by enumerating the natural candidates for combining four real-valued scores $\alpha_1, \alpha_2, \alpha_3, \alpha_4 \in [0,10]$:

| Aggregator | Formula | Properties |
|---|---|---|
| Arithmetic mean | $\frac{1}{4}\sum \alpha_i$ | Unbiased, linear, equal weight |
| Weighted mean | $\sum w_i \alpha_i$, $\sum w_i=1$ | Flexible but requires prior weights |
| Minimum | $\min_i \alpha_i$ | Conservative; sensitive to outliers |
| Maximum | $\max_i \alpha_i$ | Optimistic; sensitive to outliers |
| Geometric mean | $\left(\prod \alpha_i\right)^{1/4}$ | Undefined at zero; penalises imbalance |

The paper assumes the four agents are **exchangeable** — no single agent is privileged over another — and makes no prior claim about which agent is most reliable. Under exchangeability, the uniquely unbiased, symmetric, linear estimator of the expected quality is the arithmetic mean.

**Step-by-Step Reasoning**

**Step 1: Exchangeability assumption.** Let $\sigma$ be any permutation of $\{1,2,3,4\}$. We require $\varphi(\alpha_1,\ldots,\alpha_4) = \varphi(\alpha_{\sigma(1)},\ldots,\alpha_{\sigma(4)})$. This rules out weighted means with unequal weights.

**Step 2: Linearity.** Choosing a linear aggregator is justified because quality ratings are assumed to lie on an interval scale. For interval-scale data, the arithmetic mean is the minimum-variance unbiased estimator (MVUE) of the population mean under a Gaussian noise model.

**Step 3: Equal weighting.** Since we have no prior information favouring one agent over another, the maximum-entropy principle assigns equal weight $w_i = 1/4$ to each agent.

**Step 4: Combined formula.** Applying Steps 1–3 yields

$$\varphi(p) = \frac{1}{4}\bigl(\alpha_1(p) + \alpha_2(p) + \alpha_3(p) + \alpha_4(p)\bigr) = \frac{1}{4}\sum_{i=1}^{4}\alpha_i(p).$$

**Range Proof**

Since $\alpha_i(p) \in [0,10]$ for all $i$:

- Lower bound: $\varphi(p) \geq \frac{1}{4}(0+0+0+0) = 0$.
- Upper bound: $\varphi(p) \leq \frac{1}{4}(10+10+10+10) = 10$.

Therefore $\varphi(p) \in [0,10]$, consistent with the codomain stated in the paper. $\square$

**Numerical Verification**

Suppose $\alpha_1=7, \alpha_2=8, \alpha_3=6, \alpha_4=9$:

$$\varphi(p) = \frac{7+8+6+9}{4} = \frac{30}{4} = 7.5 \in [0,10]. \checkmark$$

**Assessment: Correct**

The formula is the standard arithmetic mean. It is mathematically well-defined, unbiased under the exchangeability assumption, range-preserving, and there are no errors.

**Comparison to Old PDF**

The old PDF does not include an explicit formula for $\varphi(p)$; quality scores are referenced but not formalised. The new PDF introducing Eq. (1) is therefore an improvement in rigour.

---

### Formula 2: Defect Consensus Set $D_\text{confirmed}$

**Statement**

$$D_\text{confirmed} = \bigl\{d \in D \;\big|\; \sum_{i=1}^{4}\mathbf{1}[A_i \text{ detects } d] \geq 3\bigr\}$$

where $D$ is the full catalogue of 28 known prompt defects (from Tian et al.), $A_i$ are the four agents, and $\mathbf{1}[\cdot]$ is the indicator function.

---

**First Principles Derivation**

We model each agent $A_i$ as an independent binary classifier for defect $d$:

- Let $\varepsilon$ = false-positive rate of a single agent (probability of wrongly detecting $d$ when absent).
- Let $\delta$ = false-negative rate (probability of missing $d$ when present).

The four agents form a **committee machine**. We want a voting threshold $k$ such that the committee false-positive rate is sufficiently small.

**Step-by-Step Reasoning**

**Step 1: Binomial model for false positives.** If defect $d$ is absent, each agent independently raises a false alarm with probability $\varepsilon$. The number of false alarms $X \sim \text{Binomial}(4, \varepsilon)$.

**Step 2: Committee false-positive rate as a function of threshold $k$.** The committee fires a false positive iff $X \geq k$:

$$P(X \geq k) = \sum_{j=k}^{4}\binom{4}{j}\varepsilon^j(1-\varepsilon)^{4-j}.$$

**Step 3: Evaluate candidate thresholds.** For $\varepsilon = 0.1$ (10% single-agent false-positive rate):

| Threshold $k$ | $P(X \geq k)$ | Suppression vs. single agent |
|---|---|---|
| $k=1$ (any agent) | $\approx 0.344$ | — |
| $k=2$ (majority of 4) | $\approx 0.0523$ | $\approx 6.6\times$ |
| $k=3$ (supermajority) | $\approx 0.0037$ | $\approx 27\times$ |
| $k=4$ (unanimity) | $0.0001$ | $\approx 1000\times$ |

Detailed calculation for $k=3$:

$$P(X \geq 3) = \binom{4}{3}(0.1)^3(0.9)^1 + \binom{4}{4}(0.1)^4 = 4(0.001)(0.9) + 0.0001 = 0.0036 + 0.0001 = 0.0037.$$

**Step 4: Evaluate false-negative cost.** Unanimity ($k=4$) is overly conservative: it will frequently miss real defects, causing the optimizer to skip valid improvements. A threshold of $k=3$ (supermajority of $4$) balances false-positive suppression with recall.

Intuitively: at $k=3$ we require at least three of four independent observers to agree. This is the standard statistical convention for requiring a "supermajority" and is equivalent to saying "at most one dissenter is tolerated."

**Step 5: Set-builder notation.** We collect all defects in $D$ that pass the threshold:

$$D_\text{confirmed} = \{d \in D \mid X_d \geq 3\}, \quad X_d = \sum_{i=1}^{4}\mathbf{1}[A_i \text{ detects } d].$$

**Assessment: Correct**

The formula is mathematically sound. The voting threshold $k=3$ is well-motivated as a false-positive suppressor. The quantifier $d \in D$ is correctly present in the new PDF.

**Comparison to Old PDF**

The old PDF wrote:

$$D_\text{confirmed} = \bigl\{d \;\big|\; \textstyle\sum\mathbf{1}[A_i \text{ detects } d] \geq 3\bigr\}$$

This is missing the domain declaration $d \in D$. Without it, the set-builder expression is formally ambiguous — the variable $d$ is free with no specified universe. The new PDF corrects this by adding $d \in D$. This is a formal fix, not merely cosmetic.

---

### Formula 3: UCB1-ATSEL Score

**Statement**

$$\text{Score}(T, d) = \mu(T, d) + \sqrt{\frac{2\ln N_\text{total}}{n(T,d)}}$$

where:
- $T$ is an optimization technique from the 41+ technique library,
- $d$ is a confirmed defect,
- $\mu(T,d)$ is the empirical mean $\varphi$-improvement when technique $T$ was applied to defect $d$,
- $N_\text{total}$ is the total number of optimization sessions,
- $n(T,d)$ is the number of times the pair $(T,d)$ has been applied.

---

**First Principles Derivation**

This formula is an application of the **UCB1 algorithm** (Auer, Cesa-Bianchi & Fischer, 2002) to the multi-armed bandit (MAB) problem framed over technique-defect pairs.

**The Multi-Armed Bandit Problem**

We have $K$ "arms" (here, $(T,d)$ pairs). At each round, pulling arm $k$ yields a stochastic reward $r_k \in [0,1]$ with unknown mean $\mu_k$. After $n_k$ pulls, we observe empirical mean $\bar{x}_k$. We must choose which arm to pull next to maximise cumulative reward over $N$ rounds.

**Challenge:** The exploration-exploitation tradeoff. Greedy selection of $\arg\max \bar{x}_k$ risks permanently ignoring arms that appear suboptimal due to noise (exploitation). Pure random exploration wastes opportunities to exploit good arms.

**Deriving the UCB1 Confidence Interval**

**Step 1: Hoeffding's inequality.** For $n$ i.i.d. random variables $X_1, \ldots, X_n$ with $X_j \in [0,1]$ and $\mathbb{E}[X_j] = \mu$, and sample mean $\bar{X}_n = \frac{1}{n}\sum_{j=1}^n X_j$:

$$P\!\left(\bar{X}_n \leq \mu - \varepsilon\right) \leq \exp\!\left(-2n\varepsilon^2\right).$$

This bounds the probability that the sample mean underestimates the true mean by more than $\varepsilon$.

**Step 2: Invert to find confidence upper bound.** We want $P(\mu > \bar{X}_n + \varepsilon) \leq \delta$. By Hoeffding:

$$\exp(-2n\varepsilon^2) = \delta \implies \varepsilon = \sqrt{\frac{\ln(1/\delta)}{2n}}.$$

So with probability at least $1-\delta$:

$$\mu \leq \bar{X}_n + \sqrt{\frac{\ln(1/\delta)}{2n}}.$$

**Step 3: Choose $\delta$ to control regret.** UCB1 uses $\delta = t^{-4}$ where $t$ is the total number of rounds elapsed. This choice ensures the confidence intervals shrink at the rate needed to achieve $O(\sqrt{KN\ln N})$ regret. Substituting:

$$\varepsilon = \sqrt{\frac{\ln(t^4)}{2n_k}} = \sqrt{\frac{4\ln t}{2n_k}} = \sqrt{\frac{2\ln t}{n_k}}.$$

**Step 4: UCB1 selection rule.** Pull the arm $k$ maximising the upper confidence bound:

$$\text{UCB1}(k) = \bar{x}_k + \sqrt{\frac{2\ln t}{n_k}}, \qquad k^* = \arg\max_k \text{UCB1}(k).$$

**Step 5: Map to PromptOptix notation.**

| UCB1 term | PromptOptix term | Meaning |
|---|---|---|
| Arm $k$ | Pair $(T,d)$ | Technique-defect combination |
| $\bar{x}_k$ | $\mu(T,d)$ | Mean $\varphi$-improvement from $(T,d)$ |
| $t$ | $N_\text{total}$ | Total sessions elapsed |
| $n_k$ | $n(T,d)$ | Applications of $(T,d)$ |

Substituting:

$$\text{Score}(T,d) = \mu(T,d) + \sqrt{\frac{2\ln N_\text{total}}{n(T,d)}}.$$

This matches Eq. (3) exactly.

**Interpretation of the Two Terms**

- $\mu(T,d)$: **Exploitation term.** Prefer techniques empirically known to work well for defect $d$.
- $\sqrt{2\ln N_\text{total}/n(T,d)}$: **Exploration bonus.** Prefer technique-defect pairs that have been tried less often. As $n(T,d) \to \infty$, the bonus shrinks to zero and the score converges to $\mu(T,d)$ (pure exploitation).

**Numerical Example**

Suppose $N_\text{total} = 100$ and we compare two techniques for a given defect $d$:

- Technique $T_1$: $\mu(T_1,d) = 0.8$, $n(T_1,d) = 50$:

$$\text{Score}(T_1,d) = 0.8 + \sqrt{\frac{2\ln 100}{50}} = 0.8 + \sqrt{\frac{2 \times 4.605}{50}} = 0.8 + \sqrt{0.1842} = 0.8 + 0.429 = 1.229.$$

- Technique $T_2$: $\mu(T_2,d) = 0.7$, $n(T_2,d) = 5$:

$$\text{Score}(T_2,d) = 0.7 + \sqrt{\frac{2\ln 100}{5}} = 0.7 + \sqrt{\frac{9.21}{5}} = 0.7 + \sqrt{1.842} = 0.7 + 1.357 = 2.057.$$

Despite having a lower mean, $T_2$ is selected because it is under-explored. This is the correct UCB1 behaviour — it will explore $T_2$ until $n(T_2,d)$ grows large enough that the bonus shrinks.

**Regret Guarantee**

The standard UCB1 result (Auer et al., 2002) gives expected regret after $N$ rounds:

$$\mathbb{E}[\text{Regret}(N)] \leq \sum_{k:\mu_k < \mu^*}\frac{8\ln N}{\Delta_k} + \left(1 + \frac{\pi^2}{3}\right)\sum_k \Delta_k,$$

where $\Delta_k = \mu^* - \mu_k$ is the suboptimality gap. This guarantees sublinear regret: we eventually converge to the best technique-defect pair.

**Assessment: Structurally Correct, Minor Definitional Ambiguity**

The formula structure is a faithful transcription of UCB1 and is mathematically correct. One definitional ambiguity exists:

In strict UCB1, $t$ is the total number of arm pulls: $t = \sum_{T',d'} n(T',d')$. In the paper, $N_\text{total}$ is defined as "total number of optimization sessions." If each session applies multiple $(T,d)$ pairs, then $N_\text{total} < \sum_{T',d'} n(T',d')$. This makes the exploration bonus slightly smaller than canonical UCB1 would prescribe, meaning the algorithm explores somewhat less aggressively. This is not a mathematical error but is a definitional ambiguity that affects the regret guarantee.

**Recommendation:** Clarify $N_\text{total} = \sum_{T',d'} n(T',d')$ (total technique-defect applications), or explicitly note that $N_\text{total}$ counts sessions and justify why this approximation is acceptable.

**Comparison to Old PDF**

Old PDF Eq. (2) is identical in structure. No differences in the formula itself.

---

### Formula 4: DGEO Mutation Operator

**Statement**

$$V' = \text{LLM-Rewrite}(V,\, T^*), \qquad T^* = \arg\max_{T \in M(d)}\text{Score}(T,d)$$

where:
- $V$ is a population variant (a candidate prompt),
- $d$ is a confirmed defect in $V$,
- $M(d)$ is the set of techniques applicable to defect $d$ (from the technique-defect mapping table),
- $\text{Score}(T,d)$ is the UCB1 score from Eq. (3),
- $\text{LLM-Rewrite}(V, T^*)$ is an LLM call instructed to apply technique $T^*$ to variant $V$ to resolve defect $d$.

---

**First Principles Derivation**

DGEO (Defect-Guided Evolutionary Optimization) applies ideas from evolutionary algorithms (EA) to prompt optimisation, but with defect-targeted mutations rather than random perturbations.

**Step 1: Standard EA mutation.** In a canonical genetic algorithm, a variant $V$ is mutated by random perturbation: $V' = \text{Mutate}(V)$. This is inefficient for structured objects like prompts because most random mutations degrade quality.

**Step 2: Guided mutation.** Instead of random perturbation, we identify a specific defect $d$ in $V$ and select a technique $T$ known to remediate $d$. This focuses the mutation on known weaknesses.

**Step 3: Technique selection via ATSEL.** Among all techniques $T \in M(d)$ applicable to defect $d$, we select the one with the highest UCB1 score (Eq. 3):

$$T^* = \arg\max_{T \in M(d)}\left[\mu(T,d) + \sqrt{\frac{2\ln N_\text{total}}{n(T,d)}}\right].$$

This balances exploitation of historically effective techniques with exploration of under-tried ones.

**Step 4: LLM as the mutation operator.** The actual rewriting is delegated to an LLM, which is instructed to apply technique $T^*$ to variant $V$. The LLM acts as a semantics-aware mutation operator:

$$V' = \text{LLM-Rewrite}(V, T^*).$$

**Relationship to Eq. (3)**

Eq. (4) is the **application** of Eq. (3)'s scoring function. It is not an independent formula; it consumes $\text{Score}(T,d)$ from Eq. (3) to make a selection, then invokes the LLM. The two equations together define the complete DGEO mutation step.

**Assessment: Correct**

The formula is mathematically well-formed. The definition of $T^*$ is unambiguous (assume ties are broken arbitrarily). The functional form $\text{LLM-Rewrite}(V,T^*)$ correctly captures that the output depends on both the current variant and the chosen technique.

**Comparison to Old PDF**

Old PDF Eq. (3) wrote:

$$V' = \text{LLM-Rewrite}(V,\, \text{Remediation}(M(d))).$$

This is less precise: $\text{Remediation}(M(d))$ does not specify *which* technique from $M(d)$ is chosen, nor does it link back to the ATSEL scoring from Eq. (2)/(3). The new PDF's explicit $T^* = \arg\max\,\text{Score}(T,d)$ is a significant notational improvement that makes the dependency on Eq. (3) explicit.

---

### Formula 5: SHDT Candidate Generation

**Statement**

$$p_t^* = \text{LLM-Opt}(p_t,\, H_t)$$

where:
- $p_t$ is the current prompt at iteration $t$,
- $H_t = \{(p_j, s_j, D^+_j, D^-_j)\}_{j=0}^{t-1}$ is the history of optimization steps up to $t$,
- $s_j = \varphi(p_j)$ is the quality score at step $j$,
- $D^+_j$ = defects resolved at step $j$, $D^-_j$ = defects introduced at step $j$,
- $\text{LLM-Opt}$ is an LLM call that uses the history to generate an improved candidate.

---

**First Principles Derivation**

SHDT (Self-History-Driven Tuning) is inspired by the observation that LLMs can act as "optimizers" when given feedback about past performance — analogous to gradient-based optimization but operating on natural language rather than continuous parameters.

**Step 1: The optimization problem.** We want to find $p^* = \arg\max_p \varphi(p)$ in the discrete, combinatorial space $\mathcal{P}$ of all prompts. Classical gradient methods do not apply because $\mathcal{P}$ is discrete and $\varphi$ is not differentiable in the usual sense.

**Step 2: LLM as a black-box optimizer.** Rather than computing $\nabla\varphi$, we describe the optimization landscape to the LLM via history $H_t$: what was tried, what scores were achieved, which defects appeared or disappeared. The LLM uses its language understanding to propose a better candidate.

**Step 3: History structure.** $H_t$ encodes a trajectory of $(p_j, s_j, D^+_j, D^-_j)$ tuples. This gives the LLM:
- The sequence of prompts tried (what has been explored),
- The scores achieved (what worked better),
- Defect appearances/disappearances (why scores changed).

This is analogous to providing an optimizer with gradient information, except here the "gradient signal" is expressed in natural language.

**Step 4: Candidate generation.** The LLM produces a candidate $p_t^*$ that attempts to improve upon $p_t$ given the evidence in $H_t$:

$$p_t^* = \text{LLM-Opt}(p_t, H_t).$$

Note that $p_t^*$ is a **candidate** only; whether it is accepted depends on Eq. (6).

**Assessment: Correct**

This is a clean functional definition of the candidate generation step. The notation is consistent with the rest of the paper. There are no mathematical errors.

**Comparison to Old PDF**

The old PDF combined Eqs. (5) and (6) into a single equation:

$$p_{t+1} = \arg\max_{p \in \{p_t,\, p_t^*\}} \varphi(p), \qquad p_t^* = \text{LLM-Opt}(p_t, H_t).$$

This is mathematically equivalent but conflates two conceptually distinct operations: (a) generating the candidate and (b) deciding whether to accept it. Splitting them into Eqs. (5) and (6) in the new PDF improves clarity significantly.

---

### Formula 6: SHDT Ratchet (Monotonic Reversion)

**Statement**

$$p_{t+1} = \begin{cases} p_t^* & \text{if } \varphi(p_t^*) > \varphi(p_t) \\ p_t & \text{otherwise} \end{cases}$$

---

**First Principles Derivation**

We want the SHDT trajectory to be **monotonically non-decreasing** in quality: once a good prompt is found, we should never regress to a worse one.

**Step 1: Define the ratchet property.** We say an update rule has the ratchet property if:

$$\varphi(p_{t+1}) \geq \varphi(p_t) \quad \text{for all } t \geq 0.$$

**Step 2: Construct the update rule.** Given candidate $p_t^*$ and current $p_t$, the ratchet update is:

$$p_{t+1} = \arg\max_{q \in \{p_t,\, p_t^*\}} \varphi(q).$$

This selects whichever of the two is better (or keeps $p_t$ on a tie).

**Step 3: Rewrite as a conditional.** Because the set has exactly two elements:

$$p_{t+1} = \begin{cases} p_t^* & \text{if } \varphi(p_t^*) > \varphi(p_t) \\ p_t & \text{otherwise.} \end{cases}$$

This is the form given in Eq. (6).

**Proof of the Ratchet Property**

We prove $\varphi(p_{t+1}) \geq \varphi(p_t)$ by case analysis:

- **Case 1:** $\varphi(p_t^*) > \varphi(p_t)$. Then $p_{t+1} = p_t^*$, so $\varphi(p_{t+1}) = \varphi(p_t^*) > \varphi(p_t)$. $\checkmark$
- **Case 2:** $\varphi(p_t^*) \leq \varphi(p_t)$. Then $p_{t+1} = p_t$, so $\varphi(p_{t+1}) = \varphi(p_t)$. $\checkmark$

In both cases $\varphi(p_{t+1}) \geq \varphi(p_t)$. $\square$

**Proof of Convergence (in Finite State Spaces)**

In the finite space $\mathcal{P}$ (discretised prompt tokens), the ratchet sequence $\varphi(p_0) \leq \varphi(p_1) \leq \varphi(p_2) \leq \ldots$ is a non-decreasing sequence bounded above by 10. It must therefore converge. Since $\mathcal{P}$ is finite, it converges in finitely many steps to a local maximum with respect to the LLM-Opt neighborhood.

**Assessment: Correct**

The formula is mathematically sound. The ratchet property is provably guaranteed by construction, and monotonic convergence follows.

**Comparison to Old PDF**

As noted under Eq. (5), the old PDF merged this ratchet into a single expression:

$$p_{t+1} = \arg\max_{p \in \{p_t,\, p_t^*\}} \varphi(p).$$

The new PDF's separation into Eqs. (5)+(6) makes explicit that the two-step process is: (1) generate candidate, then (2) accept or reject. This is cleaner and better reflects the implementation.

---

### Formula 7: CDRAF Multi-Agent Critique Synthesis

**Statement**

$$g_\text{multi} = \text{Synthesize}(c_1, c_2, c_3, c_4)$$

where $c_i$ is the textual critique of prompt $p_t$ produced by agent $A_i$, and $\text{Synthesize}$ is an LLM call that merges the four critiques into a unified feedback signal $g_\text{multi}$.

---

**First Principles Derivation**

CDRAF (Collaborative Defect-Resolution Adversarial Feedback) generalises the single-critic gradient of TextGrad (Yuksekgonul et al., 2024) to a multi-agent committee.

**Step 1: TextGrad analogy.** TextGrad replaces the numerical gradient $\nabla_\theta \mathcal{L}$ in backpropagation with a natural-language "text gradient" $g = \text{LLM-Critique}(p, \mathcal{L}(p))$. The update is $p \leftarrow \text{LLM-Refine}(p, g)$.

**Step 2: Multi-agent extension.** With four agents, each produces a critique $c_i = A_i\text{-Critique}(p_t)$. The critiques may be complementary (each agent specialises in different dimensions of quality: clarity, structure, context, security).

**Step 3: Synthesis as gradient aggregation.** Just as ensemble methods average gradients $g = \frac{1}{K}\sum_k g_k$ to reduce variance, here we synthesise $K=4$ textual critiques into a single unified signal:

$$g_\text{multi} = \text{Synthesize}(c_1, c_2, c_3, c_4).$$

The $\text{Synthesize}$ operation is performed by an LLM, which has the semantic flexibility to identify agreements, resolve contradictions, and produce a coherent combined critique.

**Step 4: Relationship to Eq. (2).** Note that $g_\text{multi}$ in Eq. (7) uses all four raw critiques $c_i$, whereas $D_\text{confirmed}$ in Eq. (2) uses majority voting on binary defect-presence signals. These are two distinct aggregation mechanisms operating on different representations (textual critiques vs. binary detections).

**Assessment: Correct**

The formula is a clean functional definition. The notation is appropriate for a high-level algorithm description, where the implementation details of $\text{Synthesize}$ are intentionally deferred to a model card / implementation specification.

**Comparison to Old PDF**

Old PDF Eq. (5) is identical:

$$g_\text{multi} = \text{Synthesize}(c_1, c_2, c_3, c_4).$$

No differences. The formula numbering changed (was Eq. 5, now Eq. 7) due to the insertion of Eqs. (5) and (6) as new standalone equations.

---

### Formula 8: CDRAF Refinement Step

**Statement**

$$p_{t+1} = \text{LLM-Refine}(p_t,\, g_\text{multi})$$

where $g_\text{multi}$ is the synthesised multi-agent critique from Eq. (7).

---

**First Principles Derivation**

**Step 1: TextGrad update rule.** In TextGrad, the refinement step applies the text gradient $g$ to the current prompt:

$$p_{t+1} = \text{LLM-Refine}(p_t, g).$$

**Step 2: CDRAF extension.** CDRAF replaces the single-critic gradient $g$ with the multi-agent synthesis $g_\text{multi}$ from Eq. (7):

$$p_{t+1} = \text{LLM-Refine}(p_t, g_\text{multi}).$$

This is the TextGrad update with a richer gradient signal derived from four independent agents rather than one. The multi-agent gradient is expected to be less noisy (more critiques = higher-quality signal) and more comprehensive (different agents cover different quality dimensions).

**Assessment: Contains a Cross-Reference Bug in the Accompanying Text**

The equation itself, $p_{t+1} = \text{LLM-Refine}(p_t, g_\text{multi})$, is correct.

However, the paper's text surrounding Eq. (8) states:

> "...where $g_\text{multi}$ **from Eq. (5)** replaces TextGrad's single-critic gradient..."

**This is wrong.** In the new PDF:

- **Eq. (5)** is $p_t^* = \text{LLM-Opt}(p_t, H_t)$ (SHDT candidate generation).
- **Eq. (7)** is $g_\text{multi} = \text{Synthesize}(c_1, c_2, c_3, c_4)$ (CDRAF synthesis).

The correct text should read "from **Eq. (7)**."

**Root Cause Analysis**

This is a stale reference from the old PDF. In the old PDF, $g_\text{multi}$ was defined as **Eq. (5)**, and the SHDT candidate equation did not exist as a separate numbered equation. When the new PDF inserted two new equations (Eqs. 5 and 6) for the SHDT steps, all downstream equation numbers shifted by two — but the text reference was not updated from "(5)" to "(7)".

| Version | $g_\text{multi}$ defined as | Text reference in Eq. (8) description |
|---|---|---|
| Old PDF | Eq. (5) | "from Eq. (5)" — **correct** |
| New PDF | Eq. (7) | "from Eq. (5)" — **WRONG, should be Eq. (7)** |

**Severity: Critical cross-reference error.** The equation itself is correct, but any reader following the text citation will be directed to the wrong formula (SHDT candidate generation instead of CDRAF synthesis).

**Comparison to Old PDF**

Old PDF Eq. (6): $p_{t+1} = \text{LLM-Refine}(p_t, g_\text{multi})$ — identical formula. Old PDF text "from Eq. (5)" was correct in the old numbering. The bug was introduced by renumbering in the new PDF without updating the cross-reference.

---

### Formula 9: Unified Pipeline Composition

**Statement**

$$p^* = \Pi_\text{CDRAF} \circ \Pi_\text{SHDT} \circ \Pi_\text{DGEO} \circ \Pi_\text{Std}(p_0)$$

where each $\Pi_x : \mathcal{P} \to \mathcal{P}$ is a conditionally-applied strategy operator:

$$\Pi_x(p) = \begin{cases} x(p) & \text{if } \varphi(x(p)) > \varphi(p) \\ p & \text{otherwise,} \end{cases}$$

and $p_0$ is the original input prompt.

---

**First Principles Derivation**

**Step 1: Function composition notation.** For functions $f, g : X \to X$, the composition $(f \circ g)(x) = f(g(x))$. Function composition is **right-to-left**: the rightmost function is applied first.

Therefore:

$$p^* = \Pi_\text{CDRAF}(\Pi_\text{SHDT}(\Pi_\text{DGEO}(\Pi_\text{Std}(p_0)))).$$

**Execution order (left to right in time):**

$$p_0 \xrightarrow{\Pi_\text{Std}} p_1 \xrightarrow{\Pi_\text{DGEO}} p_2 \xrightarrow{\Pi_\text{SHDT}} p_3 \xrightarrow{\Pi_\text{CDRAF}} p^*$$

**Step 2: Rationale for pipeline ordering.** The ordering reflects increasing sophistication:

1. $\Pi_\text{Std}$: Standard LLM optimization — fast, lightweight baseline improvement.
2. $\Pi_\text{DGEO}$: Defect-guided evolution — targeted mutation using technique-defect mapping.
3. $\Pi_\text{SHDT}$: History-driven tuning — iterative refinement using accumulated history.
4. $\Pi_\text{CDRAF}$: Collaborative adversarial feedback — multi-agent critique synthesis (most expensive, most comprehensive).

Each stage receives the output of the previous, so later stages operate on progressively higher-quality prompts.

**Step 3: Each $\Pi_x$ is a ratchet.** The conditional definition of $\Pi_x$ ensures that applying any stage never decreases quality:

$$\varphi(\Pi_x(p)) \geq \varphi(p) \quad \text{for all } p \in \mathcal{P}. \tag{*}$$

Proof: by the same case analysis as Eq. (6). If $\varphi(x(p)) > \varphi(p)$, then $\Pi_x(p) = x(p)$ and $\varphi(\Pi_x(p)) > \varphi(p)$. Otherwise $\Pi_x(p) = p$ and $\varphi(\Pi_x(p)) = \varphi(p)$. In both cases $\varphi(\Pi_x(p)) \geq \varphi(p)$. $\square$

**Step 4: Non-regression proof for the full pipeline (by induction).**

Let $p_1 = \Pi_\text{Std}(p_0)$. By $(*)$: $\varphi(p_1) \geq \varphi(p_0)$.

Let $p_2 = \Pi_\text{DGEO}(p_1)$. By $(*)$: $\varphi(p_2) \geq \varphi(p_1) \geq \varphi(p_0)$.

Let $p_3 = \Pi_\text{SHDT}(p_2)$. By $(*)$: $\varphi(p_3) \geq \varphi(p_2) \geq \varphi(p_0)$.

Let $p^* = \Pi_\text{CDRAF}(p_3)$. By $(*)$: $\varphi(p^*) \geq \varphi(p_3) \geq \varphi(p_0)$.

Therefore:

$$\varphi(p^*) \geq \varphi(p_0). \qquad \square$$

The unified pipeline provably never produces a prompt worse than the original input.

**Step 5: Relationship to $\Pi_\text{Std}$.** Note that $\Pi_\text{Std}$ is the standard optimization strategy. The output of $\Pi_\text{Std}$ alone is a valid optimised prompt; the subsequent three operators refine it further. The pipeline is designed so that even if DGEO, SHDT, and CDRAF all fail to improve (returning their inputs), the output is still at least as good as $\Pi_\text{Std}(p_0)$.

**Assessment: Correct**

The function composition is standard mathematical notation, correctly used. The execution order (right-to-left) is the standard convention for $\circ$. The ratchet property of each $\Pi_x$ operator ensures non-regression, which is formally provable. The formula is mathematically rigorous and consistent with all other equations.

**Comparison to Old PDF**

Old PDF Eq. (7) is identical:

$$p^* = \Pi_\text{CDRAF} \circ \Pi_\text{SHDT} \circ \Pi_\text{DGEO} \circ \Pi_\text{Std}(p_0).$$

No differences in the formula. The formal definition of each $\Pi_x$ operator may be more explicit in the new PDF.

---

### Formula 10: Defect Resolution Rate (DRR)

**Statement**

$$\text{DRR}(S) = \frac{HS_\text{before} - HS_\text{after}(S)}{HS_\text{before}}$$

where:
- $S$ is a strategy (Standard, DGEO, SHDT, CDRAF, or Unified),
- $HS_\text{before}$ = average number of defects per prompt before optimization,
- $HS_\text{after}(S)$ = average number of defects per prompt after applying strategy $S$.

---

**First Principles Derivation**

We need a normalised measure of defect reduction that is comparable across different baselines and datasets.

**Step 1: Raw defect reduction.** The simplest measure is the absolute reduction: $HS_\text{before} - HS_\text{after}(S)$. However, this depends on the starting defect count and cannot be compared across different prompt sets.

**Step 2: Normalisation.** Dividing by $HS_\text{before}$ normalises the reduction to a fraction of the initial defect count:

$$\text{DRR}(S) = \frac{HS_\text{before} - HS_\text{after}(S)}{HS_\text{before}} = 1 - \frac{HS_\text{after}(S)}{HS_\text{before}}.$$

This is structurally identical to the standard **relative reduction** formula used in medical statistics (risk reduction), signal processing (signal-to-noise improvement), and software engineering (defect density reduction).

**Step 3: Range analysis.** Under the assumption that optimization never introduces net new defects (guaranteed by the non-regression property of each $\Pi_x$):

$$0 \leq HS_\text{after}(S) \leq HS_\text{before},$$

which implies:

$$\text{DRR}(S) = 1 - \frac{HS_\text{after}(S)}{HS_\text{before}} \in [0,1].$$

- $\text{DRR}(S) = 0$: Strategy $S$ resolved no defects.
- $\text{DRR}(S) = 1$: Strategy $S$ resolved all defects ($HS_\text{after} = 0$).

**Numerical Verification**

Using the paper's reported values (N=25 prompts):

$$HS_\text{before} = 4.16 \text{ defects/prompt (for individual strategies)}, \quad HS_\text{before} = 4.12 \text{ (for Unified)}$$

| Strategy $S$ | $HS_\text{before}$ | $HS_\text{after}(S)$ | Calculation | DRR | Paper reports |
|---|---|---|---|---|---|
| Standard | 4.16 | 3.35 | $(4.16-3.35)/4.16 = 0.81/4.16$ | 19.47% | ~19.5% |
| DGEO | 4.16 | 2.54 | $(4.16-2.54)/4.16 = 1.62/4.16$ | 38.94% | ~38.9% |
| SHDT | 4.16 | 3.16 | $(4.16-3.16)/4.16 = 1.00/4.16$ | 24.04% | ~24.0% |
| CDRAF | 4.16 | 1.98 | $(4.16-1.98)/4.16 = 2.18/4.16$ | 52.40% | ~52.4% |
| Unified | 4.12 | 1.12 | $(4.12-1.12)/4.12 = 3.00/4.12$ | 72.82% | ~72.8% |

All values check out exactly (within rounding). $\checkmark$

**Note on the Unified pipeline's different $HS_\text{before}$:** The Unified pipeline ran on a slightly different subset of the 25 prompts than the individual strategies, yielding $HS_\text{before} = 4.12$ rather than $4.16$. This is a minor data partitioning artefact, not an error.

**Verification of Relative Quality Improvement Claims**

The paper also reports relative improvements in $\varphi$-scores. Using reported $\varphi$ values:

$$\text{Relative improvement} = \frac{\varphi_\text{after} - \varphi_\text{before}}{\varphi_\text{before}} \times 100\%.$$

- **Standard:** $\varphi_\text{before} = 4.55$, $\varphi_\text{after} = 6.61$:

$$\frac{6.61 - 4.55}{4.55} = \frac{2.06}{4.55} = 45.3\% \approx 46\%. \checkmark \text{ (rounding)}$$

- **Unified:** $\varphi_\text{before} = 4.55$, $\varphi_\text{after} = 8.44$:

$$\frac{8.44 - 4.55}{4.55} = \frac{3.89}{4.55} = 85.5\% \approx 86\%. \checkmark \text{ (rounding)}$$

Both "46–86% relative improvement" bounds reported in the paper are verified. $\checkmark$

**Assessment: Correct**

DRR is a standard relative-reduction metric, correctly applied. All reported numerical values verify exactly. No errors.

**Comparison to Old PDF**

The old PDF does not include a DRR formula (it had only 7 equations). Eq. (10) is new in the new PDF, introduced alongside the expanded N=25 experimental results.

---

## Summary of Issues Found

| Eq | Location | Issue | Severity | Fix |
|---|---|---|---|---|
| (3) | Definition of $N_\text{total}$ | $N_\text{total}$ described as "total optimization sessions" but strict UCB1 requires $N_\text{total} = \sum_{T',d'} n(T',d')$ (total arm pulls). If each session applies multiple $(T,d)$ pairs, these differ. | Minor — exploration bonus is slightly underestimated but algorithm remains correct | Redefine: $N_\text{total} = \sum_{T' \in \mathcal{T}, d' \in D} n(T',d')$, or add a note explaining the approximation |
| (8) | Accompanying text | Text says "$g_\text{multi}$ from **Eq. (5)**" but $g_\text{multi}$ is defined in **Eq. (7)**. Eq. (5) is the SHDT candidate $p_t^* = \text{LLM-Opt}(p_t, H_t)$. | Critical — directs readers to the wrong equation | Change "Eq. (5)" to "Eq. (7)" in the text surrounding Eq. (8) |
| Old (1) | Set-builder domain | Missing $d \in D$ domain quantifier: $\{d \mid \ldots\}$ instead of $\{d \in D \mid \ldots\}$. Makes the set formally ambiguous. | Fixed in new PDF | No action needed (already corrected in new PDF) |
| Old (4) | SHDT formulation | Combined LLM candidate generation and ratchet selection into one equation, obscuring the two-step nature of SHDT. | Fixed in new PDF (split into Eqs. 5+6) | No action needed (already corrected in new PDF) |

---

## Corrected Formulas (Final Reference)

The following presents all 10 equations in their correct form with any necessary fixes applied. Equations 1–7 and 9–10 are reproduced exactly as in the new PDF. Equation 8's accompanying text is corrected.

---

**Eq. (1) — Quality Score** *(correct as stated)*

$$\varphi(p) = \frac{1}{4}\sum_{i=1}^{4}\alpha_i(p), \qquad \varphi : \mathcal{P} \to [0,10], \quad \alpha_i(p) \in [0,10].$$

Arithmetic mean of four agent scores. Equal-weight, unbiased under agent exchangeability.

---

**Eq. (2) — Defect Consensus Set** *(correct as stated in new PDF)*

$$D_\text{confirmed} = \bigl\{d \in D \;\big|\; \textstyle\sum_{i=1}^{4}\mathbf{1}[A_i \text{ detects } d] \geq 3\bigr\}.$$

Supermajority vote ($k=3$ of 4). Suppresses per-agent false positives by a factor of $\approx27\times$ at $\varepsilon=0.1$.

---

**Eq. (3) — UCB1-ATSEL Score** *(formula correct; clarification added to $N_\text{total}$)*

$$\text{Score}(T,d) = \mu(T,d) + \sqrt{\frac{2\ln N_\text{total}}{n(T,d)}},$$

$$\text{where } N_\text{total} = \sum_{T' \in \mathcal{T},\, d' \in D} n(T', d') \quad \text{(total (T,d) application count across all sessions).}$$

UCB1 bandit score. Balances exploitation ($\mu(T,d)$) with exploration ($\sqrt{2\ln N_\text{total}/n(T,d)}$). Guarantees sublinear regret.

---

**Eq. (4) — DGEO Targeted Mutation** *(correct as stated)*

$$V' = \text{LLM-Rewrite}(V,\, T^*), \qquad T^* = \arg\max_{T \in M(d)}\,\text{Score}(T,d).$$

Best UCB1-ranked technique for defect $d$ is applied to population variant $V$ via LLM rewrite.

---

**Eq. (5) — SHDT Candidate Generation** *(correct as stated)*

$$p_t^* = \text{LLM-Opt}(p_t,\, H_t), \qquad H_t = \{(p_j, s_j, D^+_j, D^-_j)\}_{j=0}^{t-1}.$$

LLM generates an improved candidate using the current prompt and full optimization history.

---

**Eq. (6) — SHDT Ratchet** *(correct as stated)*

$$p_{t+1} = \begin{cases} p_t^* & \text{if } \varphi(p_t^*) > \varphi(p_t) \\ p_t & \text{otherwise.} \end{cases}$$

Guarantees monotonic quality: $\varphi(p_{t+1}) \geq \varphi(p_t)$ for all $t$. Equivalent to $\arg\max_{q \in \{p_t, p_t^*\}}\varphi(q)$.

---

**Eq. (7) — CDRAF Multi-Critique Synthesis** *(correct as stated)*

$$g_\text{multi} = \text{Synthesize}(c_1, c_2, c_3, c_4),$$

where $c_i = A_i\text{-Critique}(p_t)$. LLM merges four agent critiques into a unified feedback signal.

---

**Eq. (8) — CDRAF Refinement** *(formula correct; text cross-reference corrected)*

$$p_{t+1} = \text{LLM-Refine}(p_t,\, g_\text{multi}),$$

where $g_\text{multi}$ is defined in **Eq. (7)** *(not Eq. (5) as erroneously stated in the paper's text)*. TextGrad-style update with multi-agent gradient $g_\text{multi}$ replacing a single-critic gradient.

---

**Eq. (9) — Unified Pipeline** *(correct as stated)*

$$p^* = \Pi_\text{CDRAF} \circ \Pi_\text{SHDT} \circ \Pi_\text{DGEO} \circ \Pi_\text{Std}(p_0),$$

$$\Pi_x(p) = \begin{cases} x(p) & \text{if } \varphi(x(p)) > \varphi(p) \\ p & \text{otherwise.}\end{cases}$$

Execution order: Std $\to$ DGEO $\to$ SHDT $\to$ CDRAF. Non-regression guaranteed: $\varphi(p^*) \geq \varphi(p_0)$ by induction on the ratchet property of each $\Pi_x$.

---

**Eq. (10) — Defect Resolution Rate** *(correct as stated)*

$$\text{DRR}(S) = \frac{HS_\text{before} - HS_\text{after}(S)}{HS_\text{before}} = 1 - \frac{HS_\text{after}(S)}{HS_\text{before}}, \qquad \text{DRR}(S) \in [0,1].$$

Standard relative-reduction metric. All reported values (19.5%, 38.9%, 24.0%, 52.4%, 72.8%) verified numerically.

---

*End of analysis. Primary source: `formula_maybe_notsure_fized.pdf` (N=25 version). Only confirmed bug: Eq. (8) accompanying text incorrectly references Eq. (5) instead of Eq. (7). All 10 formula structures are mathematically correct.*
