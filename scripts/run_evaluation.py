"""
Research Evaluation Script — PromptOptimizer Pro
=================================================
Generates all result tables for the research paper.
NOT exposed on the web interface — CLI only.

Runs benchmark prompts through all optimization strategies,
collects metrics, computes statistics, and outputs formatted tables.

Usage:
    python scripts/run_evaluation.py
    python scripts/run_evaluation.py --strategies standard,dgeo,shdt,cdraf,unified
    python scripts/run_evaluation.py --limit 10 --provider groq
    python scripts/run_evaluation.py --output-dir data/evaluation
"""

import asyncio
import argparse
import csv
import json
import math
import os
import sys
import time
from datetime import datetime
from statistics import mean, stdev
from typing import Any, Dict, List, Optional, Tuple

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

import logging

from backend.services.agent_orchestrator import get_orchestrator
from backend.services.optimizer_service import get_optimizer
from backend.services.db_service import save_benchmark_result, get_benchmark_summary

logger = logging.getLogger(__name__)

BENCHMARK_FILE = os.path.join(PROJECT_ROOT, "data", "benchmarks", "prompts.json")
DEFAULT_OUTPUT_DIR = os.path.join(PROJECT_ROOT, "data", "evaluation")

ALL_STRATEGIES = ["standard", "dgeo", "shdt", "cdraf", "unified"]

# ============================================================
# Statistical Functions
# ============================================================

def paired_ttest(before: List[float], after: List[float]) -> Tuple[float, float]:
    """Paired t-test. Returns (t_statistic, p_value)."""
    try:
        from scipy.stats import ttest_rel
        t_stat, p_val = ttest_rel(before, after)
        return float(t_stat), float(p_val)
    except ImportError:
        # Fallback: manual paired t-test
        n = len(before)
        if n < 2:
            return 0.0, 1.0
        diffs = [a - b for a, b in zip(after, before)]
        d_bar = mean(diffs)
        sd = stdev(diffs) if n > 1 else 1.0
        t_stat = d_bar / (sd / math.sqrt(n)) if sd > 0 else 0.0
        # Approximate p-value using normal distribution for large n
        p_val = 2 * (1 - _norm_cdf(abs(t_stat))) if n >= 30 else float("nan")
        return t_stat, p_val


def cohens_d(before: List[float], after: List[float]) -> float:
    """Cohen's d effect size for paired samples."""
    n = len(before)
    if n < 2:
        return 0.0
    diffs = [a - b for a, b in zip(after, before)]
    d_bar = mean(diffs)
    sd = stdev(diffs) if n > 1 else 1.0
    return d_bar / sd if sd > 0 else 0.0


def confidence_interval_95(values: List[float]) -> Tuple[float, float]:
    """95% confidence interval for the mean."""
    n = len(values)
    if n < 2:
        return (mean(values) if values else 0.0, mean(values) if values else 0.0)
    m = mean(values)
    se = stdev(values) / math.sqrt(n)
    margin = 1.96 * se  # z=1.96 for 95% CI
    return (m - margin, m + margin)


def one_way_anova(*groups: List[float]) -> Tuple[float, float]:
    """One-way ANOVA. Returns (F_statistic, p_value)."""
    try:
        from scipy.stats import f_oneway
        # Filter out groups with < 2 samples
        valid = [g for g in groups if len(g) >= 2]
        if len(valid) < 2:
            return 0.0, 1.0
        f_stat, p_val = f_oneway(*valid)
        return float(f_stat), float(p_val)
    except ImportError:
        return 0.0, float("nan")


def _norm_cdf(x: float) -> float:
    """Approximate standard normal CDF."""
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))


# ============================================================
# Metric Helpers
# ============================================================

def count_high_severity_defects(defects: List[Dict]) -> int:
    """Count critical + high severity defects."""
    return sum(1 for d in defects if d.get("severity") in ("critical", "high"))


def extract_analysis_metrics(analysis: Dict) -> Dict:
    """Extract key metrics from an analysis result."""
    defects = analysis.get("defects", [])
    metadata = analysis.get("metadata", {})
    return {
        "score": analysis.get("overall_score", 0.0),
        "total_defects": len(defects),
        "high_severity_defects": count_high_severity_defects(defects),
        "consensus": analysis.get("consensus", 0.0),
        "total_tokens": metadata.get("total_tokens", 0),
        "total_cost": metadata.get("total_cost", 0.0),
        "processing_time_ms": metadata.get("processing_time_ms", 0),
        "defects": defects,
    }


# ============================================================
# Strategy Runners
# ============================================================

async def run_strategy(
    prompt: str,
    strategy: str,
    analysis: Dict,
    context: Dict,
    provider: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Run a single optimization strategy on a prompt.
    Returns a dict with all collected metrics.
    """
    optimizer = get_optimizer()
    orchestrator = get_orchestrator()

    result: Dict[str, Any] = {
        "strategy": strategy,
        "status": "success",
    }

    start_time = time.time()

    try:
        if strategy == "standard":
            opt = await optimizer.optimize(
                prompt=prompt, context=context,
                optimization_level="balanced", analysis=analysis
            )
            optimized_prompt = opt.get("optimized_prompt", prompt)
            after_analysis = opt.get("after_analysis", {})
            result["techniques_applied"] = opt.get("techniques_applied", [])

        elif strategy == "dgeo":
            from backend.services.dgeo_optimizer import DGEOOptimizer
            dgeo = DGEOOptimizer()
            opt = await dgeo.optimize(
                prompt=prompt, context=context, analysis=analysis,
                population_size=3, generations=1
            )
            optimized_prompt = opt.get("best_prompt", prompt)
            after_analysis = opt.get("after_analysis", {})
            result["evolution_history"] = opt.get("evolution_history", [])

        elif strategy == "shdt":
            opt = await optimizer.optimize_with_trajectory(
                prompt=prompt, context=context, analysis=analysis,
                max_iterations=2, target_score=8.0
            )
            optimized_prompt = opt.get("final_prompt", prompt)
            after_analysis = opt.get("after_analysis", {})
            result["trajectory"] = opt.get("trajectory", [])

        elif strategy == "cdraf":
            # Standard optimize first, then refine with agents
            std_opt = await optimizer.optimize(
                prompt=prompt, context=context,
                optimization_level="balanced", analysis=analysis
            )
            std_prompt = std_opt.get("optimized_prompt", prompt) if isinstance(std_opt, dict) else prompt
            refined = await optimizer.refine_with_agents(
                optimized_prompt=std_prompt,
                context=context, max_rounds=2
            )
            if not isinstance(refined, dict):
                raise ValueError(f"CDRAF returned {type(refined).__name__} instead of dict")
            optimized_prompt = refined.get("refined_prompt", std_prompt)
            after_analysis = refined.get("after_analysis", {})
            result["critique_rounds"] = refined.get("critique_rounds", [])

        elif strategy == "unified":
            opt = await optimizer.optimize_unified(
                prompt=prompt, context=context, analysis=analysis,
                optimization_level="balanced", max_techniques=5,
                task_type=context.get("task_type", "general"),
                domain=context.get("domain", "general")
            )
            optimized_prompt = opt.get("optimized_prompt", prompt)
            after_analysis = opt.get("after_analysis", {})
            result["techniques_applied"] = opt.get("techniques_applied", [])
            result["pipeline_metadata"] = opt.get("metadata", {})

        else:
            raise ValueError(f"Unknown strategy: {strategy}")

        elapsed_ms = int((time.time() - start_time) * 1000)

        # If after_analysis is missing or empty, re-analyze
        if not after_analysis or not after_analysis.get("overall_score"):
            after_analysis = await orchestrator.analyze_with_agents(optimized_prompt, context)

        after_metrics = extract_analysis_metrics(after_analysis)

        result.update({
            "optimized_prompt": optimized_prompt,
            "score_after": after_metrics["score"],
            "defects_after": after_metrics["total_defects"],
            "high_severity_after": after_metrics["high_severity_defects"],
            "tokens_after": after_metrics["total_tokens"],
            "cost_after": after_metrics["total_cost"],
            "processing_time_ms": elapsed_ms,
            "defects_list_after": after_metrics["defects"],
        })

    except Exception as e:
        elapsed_ms = int((time.time() - start_time) * 1000)
        result.update({
            "status": "error",
            "error": str(e),
            "processing_time_ms": elapsed_ms,
            "score_after": 0.0,
            "defects_after": 0,
            "high_severity_after": 0,
        })

    return result


async def run_single_prompt(
    prompt_data: Dict,
    strategies: List[str],
    provider: Optional[str] = None,
) -> Dict[str, Any]:
    """Run all strategies on a single benchmark prompt."""
    orchestrator = get_orchestrator()

    context = {
        "task_type": prompt_data.get("task_type", "general"),
        "domain": prompt_data.get("domain", "general"),
    }
    if provider:
        context["provider"] = provider

    # Step 1: Baseline analysis (shared across all strategies)
    # Retry up to 3 times on transient failures (network, API errors)
    analysis = None
    for attempt in range(3):
        try:
            analysis = await orchestrator.analyze_with_agents(prompt_data["prompt"], context)
            break
        except Exception as e:
            if attempt < 2:
                logger.warning(f"Baseline analysis attempt {attempt+1} failed: {e}, retrying in 5s...")
                await asyncio.sleep(5)
            else:
                logger.error(f"Baseline analysis failed after 3 attempts: {e}")
                # Return a skip result so the evaluation continues
                return {
                    "id": prompt_data["id"],
                    "category": prompt_data.get("category", "general"),
                    "task_type": prompt_data.get("task_type", "general"),
                    "prompt_preview": prompt_data["prompt"][:80],
                    "baseline": {
                        "score": 0, "total_defects": 0, "high_severity_defects": 0,
                        "consensus": 0, "tokens": 0, "cost": 0,
                    },
                    "strategies": {},
                    "skipped": True,
                    "skip_reason": str(e),
                }

    baseline = extract_analysis_metrics(analysis)

    prompt_result = {
        "id": prompt_data["id"],
        "category": prompt_data.get("category", "general"),
        "task_type": prompt_data.get("task_type", "general"),
        "prompt_preview": prompt_data["prompt"][:80],
        "baseline": {
            "score": baseline["score"],
            "total_defects": baseline["total_defects"],
            "high_severity_defects": baseline["high_severity_defects"],
            "consensus": baseline["consensus"],
            "tokens": baseline["total_tokens"],
            "cost": baseline["total_cost"],
        },
        "strategies": {},
    }

    # Step 2: Run all strategies IN PARALLEL for speed
    async def _run_and_save(strategy):
        strat_result = await run_strategy(
            prompt=prompt_data["prompt"],
            strategy=strategy,
            analysis=analysis,
            context=context,
            provider=provider,
        )
        # Save to database
        if strat_result["status"] == "success":
            try:
                save_benchmark_result(
                    benchmark_id=prompt_data["id"],
                    strategy=strategy,
                    score_before=baseline["score"],
                    score_after=strat_result.get("score_after", 0.0),
                    defects_fixed=max(0, baseline["total_defects"] - strat_result.get("defects_after", 0)),
                    processing_time_ms=strat_result.get("processing_time_ms", 0),
                    cost=strat_result.get("cost_after", 0.0),
                )
            except Exception:
                pass  # DB save is best-effort
        return strategy, strat_result

    tasks = [_run_and_save(s) for s in strategies]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    for idx, item in enumerate(results):
        if isinstance(item, Exception):
            strat_name = strategies[idx] if idx < len(strategies) else "unknown"
            logger.error(f"Strategy {strat_name} raised exception: {item}")
            prompt_result["strategies"][strat_name] = {
                "status": "error",
                "error": str(item),
                "strategy": strat_name,
            }
            continue
        strategy, strat_result = item
        prompt_result["strategies"][strategy] = strat_result

    return prompt_result


# ============================================================
# Table Generators
# ============================================================

def generate_table1_score_improvement(results: List[Dict], strategies: List[str]) -> str:
    """Table 1: Average Defect Score Improvement Across Strategies"""
    lines = []
    lines.append("\n" + "=" * 90)
    lines.append("  TABLE 1: Average Defect Score Improvement Across Strategies")
    lines.append("=" * 90)
    lines.append(f"  {'Strategy':<12} {'N':>4} {'Before':>8} {'After':>8} {'Improve':>8} {'SD':>6} {'p-value':>9} {'Cohen d':>8} {'95% CI':>16}")
    lines.append("  " + "-" * 84)

    baseline_scores = []
    strategy_data: Dict[str, Dict[str, List[float]]] = {}

    for r in results:
        bs = r["baseline"]["score"]
        baseline_scores.append(bs)
        for strat in strategies:
            s = r["strategies"].get(strat, {})
            if s.get("status") != "success":
                continue
            if strat not in strategy_data:
                strategy_data[strat] = {"before": [], "after": [], "improvement": []}
            strategy_data[strat]["before"].append(bs)
            sa = s.get("score_after", 0.0)
            strategy_data[strat]["after"].append(sa)
            strategy_data[strat]["improvement"].append(sa - bs)

    for strat in strategies:
        d = strategy_data.get(strat)
        if not d or len(d["improvement"]) < 2:
            lines.append(f"  {strat:<12} {'N/A':>4}")
            continue

        n = len(d["improvement"])
        avg_before = mean(d["before"])
        avg_after = mean(d["after"])
        avg_imp = mean(d["improvement"])
        sd_imp = stdev(d["improvement"]) if n > 1 else 0.0
        t_stat, p_val = paired_ttest(d["before"], d["after"])
        d_effect = cohens_d(d["before"], d["after"])
        ci_low, ci_high = confidence_interval_95(d["improvement"])

        p_str = f"{p_val:.4f}" if not math.isnan(p_val) else "N/A"
        lines.append(
            f"  {strat:<12} {n:>4} {avg_before:>8.2f} {avg_after:>8.2f} "
            f"{avg_imp:>+8.2f} {sd_imp:>6.2f} {p_str:>9} {d_effect:>8.2f} "
            f"[{ci_low:>+.2f},{ci_high:>+.2f}]"
        )

    return "\n".join(lines)


def generate_table2_severity_reduction(results: List[Dict], strategies: List[str]) -> str:
    """Table 2: High-Severity Defect Reduction (%) by Strategy"""
    lines = []
    lines.append("\n" + "=" * 80)
    lines.append("  TABLE 2: High-Severity Defect Reduction (%) by Strategy")
    lines.append("=" * 80)
    lines.append(f"  {'Strategy':<12} {'N':>4} {'HS Before':>10} {'HS After':>10} {'Reduction%':>11} {'Avg Fixed':>10}")
    lines.append("  " + "-" * 62)

    for strat in strategies:
        hs_before_list = []
        hs_after_list = []
        for r in results:
            s = r["strategies"].get(strat, {})
            if s.get("status") != "success":
                continue
            hs_b = r["baseline"]["high_severity_defects"]
            hs_a = s.get("high_severity_after", 0)
            hs_before_list.append(hs_b)
            hs_after_list.append(hs_a)

        if not hs_before_list:
            lines.append(f"  {strat:<12} {'N/A':>4}")
            continue

        n = len(hs_before_list)
        total_before = sum(hs_before_list)
        total_after = sum(hs_after_list)
        reduction = ((total_before - total_after) / total_before * 100) if total_before > 0 else 0.0
        avg_fixed = mean([b - a for b, a in zip(hs_before_list, hs_after_list)])

        lines.append(
            f"  {strat:<12} {n:>4} {mean(hs_before_list):>10.1f} {mean(hs_after_list):>10.1f} "
            f"{reduction:>10.1f}% {avg_fixed:>10.1f}"
        )

    return "\n".join(lines)


def generate_table3_efficiency(results: List[Dict], strategies: List[str]) -> str:
    """Table 3: Optimization Time & Cost Comparison"""
    lines = []
    lines.append("\n" + "=" * 80)
    lines.append("  TABLE 3: Optimization Time & Cost Comparison")
    lines.append("=" * 80)
    lines.append(f"  {'Strategy':<12} {'N':>4} {'Avg Time(s)':>12} {'Avg Cost($)':>12} {'Cost/Point':>11}")
    lines.append("  " + "-" * 56)

    for strat in strategies:
        times = []
        costs = []
        improvements = []
        for r in results:
            s = r["strategies"].get(strat, {})
            if s.get("status") != "success":
                continue
            times.append(s.get("processing_time_ms", 0) / 1000.0)
            costs.append(s.get("cost_after", 0.0))
            improvements.append(s.get("score_after", 0.0) - r["baseline"]["score"])

        if not times:
            lines.append(f"  {strat:<12} {'N/A':>4}")
            continue

        n = len(times)
        avg_time = mean(times)
        avg_cost = mean(costs)
        avg_imp = mean(improvements)
        cost_per_point = avg_cost / avg_imp if avg_imp > 0 else float("inf")

        lines.append(
            f"  {strat:<12} {n:>4} {avg_time:>12.1f} {avg_cost:>12.4f} "
            f"{'N/A' if cost_per_point == float('inf') else f'${cost_per_point:.4f}':>11}"
        )

    return "\n".join(lines)


def generate_table4_by_category(results: List[Dict], strategies: List[str]) -> str:
    """Table 4: Per-Category Breakdown"""
    lines = []
    lines.append("\n" + "=" * 90)
    lines.append("  TABLE 4: Score Improvement by Category and Strategy")
    lines.append("=" * 90)

    # Collect categories
    categories = sorted(set(r["category"] for r in results))

    header = f"  {'Category':<20}"
    for strat in strategies:
        header += f" {strat:>12}"
    lines.append(header)
    lines.append("  " + "-" * (20 + 13 * len(strategies)))

    for cat in categories:
        row = f"  {cat:<20}"
        for strat in strategies:
            improvements = []
            for r in results:
                if r["category"] != cat:
                    continue
                s = r["strategies"].get(strat, {})
                if s.get("status") != "success":
                    continue
                improvements.append(s.get("score_after", 0.0) - r["baseline"]["score"])

            if improvements:
                avg = mean(improvements)
                row += f" {avg:>+11.2f}±" if len(improvements) > 1 else f" {avg:>+12.2f}"
                if len(improvements) > 1:
                    row = row[:-1]  # remove trailing ±
                    sd = stdev(improvements)
                    # Reformat with ± notation
                    row_parts = row.rsplit(" ", 1)
                    row = row_parts[0] + f" {avg:>+.2f}±{sd:.2f}"
            else:
                row += f" {'N/A':>12}"
        lines.append(row)

    return "\n".join(lines)


def generate_table5_anova(results: List[Dict], strategies: List[str]) -> str:
    """Table 5: ANOVA — Are strategy differences significant?"""
    lines = []
    lines.append("\n" + "=" * 60)
    lines.append("  TABLE 5: One-Way ANOVA Across Strategies")
    lines.append("=" * 60)

    groups = []
    for strat in strategies:
        improvements = []
        for r in results:
            s = r["strategies"].get(strat, {})
            if s.get("status") != "success":
                continue
            improvements.append(s.get("score_after", 0.0) - r["baseline"]["score"])
        groups.append(improvements)

    f_stat, p_val = one_way_anova(*groups)
    p_str = f"{p_val:.6f}" if not math.isnan(p_val) else "N/A"
    sig = "YES (p < 0.05)" if (not math.isnan(p_val) and p_val < 0.05) else "NO"

    lines.append(f"  F-statistic: {f_stat:.4f}")
    lines.append(f"  p-value:     {p_str}")
    lines.append(f"  Significant: {sig}")
    lines.append(f"  Groups:      {len(strategies)} strategies, {sum(len(g) for g in groups)} total observations")

    return "\n".join(lines)


def generate_technique_effectiveness(results: List[Dict]) -> str:
    """Table 6: Technique Effectiveness Summary"""
    lines = []
    lines.append("\n" + "=" * 80)
    lines.append("  TABLE 6: Technique Effectiveness (from Standard & Unified strategies)")
    lines.append("=" * 80)

    tech_stats: Dict[str, Dict[str, Any]] = {}

    for r in results:
        for strat in ["standard", "unified"]:
            s = r["strategies"].get(strat, {})
            if s.get("status") != "success":
                continue
            for tech in s.get("techniques_applied", []):
                tid = tech.get("technique_id") or "unknown"
                tname = tech.get("technique_name") or tid
                improvement = s.get("score_after", 0.0) - r["baseline"]["score"]
                if tid not in tech_stats:
                    tech_stats[tid] = {"name": tname, "count": 0, "improvements": []}
                tech_stats[tid]["count"] += 1
                tech_stats[tid]["improvements"].append(improvement)

    if not tech_stats:
        lines.append("  No technique data collected.")
        return "\n".join(lines)

    lines.append(f"  {'ID':<8} {'Technique Name':<35} {'Used':>5} {'Avg Improve':>12}")
    lines.append("  " + "-" * 64)

    # Sort by average improvement descending
    sorted_techs = sorted(
        tech_stats.items(),
        key=lambda x: mean(x[1]["improvements"]) if x[1]["improvements"] else 0,
        reverse=True
    )

    for tid, data in sorted_techs[:15]:  # Top 15
        avg_imp = mean(data["improvements"]) if data["improvements"] else 0
        display_id = str(tid or "unknown")[:8]
        display_name = str(data.get('name') or display_id)[:35]
        lines.append(f"  {display_id:<8} {display_name:<35} {data['count']:>5} {avg_imp:>+12.2f}")

    return "\n".join(lines)


# ============================================================
# Main Orchestrator
# ============================================================

async def run_evaluation(
    strategies: List[str],
    limit: Optional[int] = None,
    provider: Optional[str] = None,
    output_dir: str = DEFAULT_OUTPUT_DIR,
):
    """Run the full research evaluation."""
    # Load benchmarks
    with open(BENCHMARK_FILE, "r") as f:
        all_prompts = json.load(f)
    if limit:
        all_prompts = all_prompts[:limit]

    n_prompts = len(all_prompts)
    n_strategies = len(strategies)
    total_runs = n_prompts * n_strategies

    print(f"\n{'=' * 70}")
    print(f"  PromptOptimizer Pro — Research Evaluation")
    print(f"  {n_prompts} prompts x {n_strategies} strategies = {total_runs} optimization runs")
    print(f"  Strategies: {', '.join(strategies)}")
    print(f"  Provider: {provider or 'default'}")
    print(f"  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'=' * 70}\n")

    all_results = []
    total_start = time.time()

    for i, prompt_data in enumerate(all_prompts):
        print(f"  [{i+1}/{n_prompts}] {prompt_data['id']} ({prompt_data.get('category', '?')}): "
              f"{prompt_data['prompt'][:50]}...")
        sys.stdout.flush()

        try:
            prompt_result = await run_single_prompt(prompt_data, strategies, provider)
        except Exception as e:
            logger.error(f"Prompt {prompt_data['id']} failed entirely: {e}")
            print(f"    SKIPPED - {str(e)[:60]}")
            prompt_result = {
                "id": prompt_data["id"],
                "category": prompt_data.get("category", "general"),
                "task_type": prompt_data.get("task_type", "general"),
                "prompt_preview": prompt_data["prompt"][:80],
                "baseline": {
                    "score": 0, "total_defects": 0, "high_severity_defects": 0,
                    "consensus": 0, "tokens": 0, "cost": 0,
                },
                "strategies": {},
                "skipped": True,
                "skip_reason": str(e),
            }

        all_results.append(prompt_result)

        # Print per-prompt summary
        if prompt_result.get("skipped"):
            print(f"    SKIPPED: {prompt_result.get('skip_reason', 'Unknown')[:60]}")
            continue

        bs = prompt_result["baseline"]["score"]
        for strat in strategies:
            s = prompt_result["strategies"].get(strat, {})
            if s.get("status") == "success":
                sa = s.get("score_after", 0.0)
                ms = s.get("processing_time_ms", 0)
                print(f"    {strat:>10}: {bs:.1f} -> {sa:.1f} ({sa-bs:+.1f}) [{ms}ms]")
            else:
                print(f"    {strat:>10}: ERROR - {s.get('error', 'Unknown')[:40]}")

    total_elapsed = time.time() - total_start

    # ---- Generate Tables ----
    print(generate_table1_score_improvement(all_results, strategies))
    print(generate_table2_severity_reduction(all_results, strategies))
    print(generate_table3_efficiency(all_results, strategies))
    print(generate_table4_by_category(all_results, strategies))
    print(generate_table5_anova(all_results, strategies))
    print(generate_technique_effectiveness(all_results))

    print(f"\n{'=' * 70}")
    print(f"  Total evaluation time: {total_elapsed:.1f}s")
    print(f"  Successful runs: {sum(1 for r in all_results for s in r['strategies'].values() if s.get('status') == 'success')}/{total_runs}")
    print(f"{'=' * 70}")

    # ---- Save outputs ----
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Full JSON results
    json_path = os.path.join(output_dir, f"results_{timestamp}.json")
    # Clean non-serializable fields
    clean_results = json.loads(json.dumps(all_results, default=str))
    with open(json_path, "w") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "config": {
                "strategies": strategies,
                "num_prompts": n_prompts,
                "provider": provider,
                "total_time_seconds": total_elapsed,
            },
            "results": clean_results,
        }, f, indent=2)
    print(f"\n  JSON results: {json_path}")

    # CSV summary
    csv_path = os.path.join(output_dir, f"summary_{timestamp}.csv")
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        header = ["prompt_id", "category", "baseline_score"]
        for strat in strategies:
            header.extend([
                f"{strat}_score_after",
                f"{strat}_improvement",
                f"{strat}_hs_defects_after",
                f"{strat}_time_ms",
            ])
        writer.writerow(header)

        for r in all_results:
            row = [r["id"], r["category"], r["baseline"]["score"]]
            for strat in strategies:
                s = r["strategies"].get(strat, {})
                if s.get("status") == "success":
                    row.extend([
                        s.get("score_after", ""),
                        round(s.get("score_after", 0) - r["baseline"]["score"], 2),
                        s.get("high_severity_after", ""),
                        s.get("processing_time_ms", ""),
                    ])
                else:
                    row.extend(["ERR", "ERR", "ERR", "ERR"])
            writer.writerow(row)
    print(f"  CSV summary:  {csv_path}")
    print()


# ============================================================
# CLI Entry Point
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="PromptOptimizer Pro — Research Evaluation Script"
    )
    parser.add_argument(
        "--strategies",
        default="standard,dgeo,shdt,cdraf,unified",
        help="Comma-separated strategies: standard,dgeo,shdt,cdraf,unified (default: all)"
    )
    parser.add_argument(
        "--limit", type=int, default=None,
        help="Limit number of benchmark prompts (default: all)"
    )
    parser.add_argument(
        "--provider", default=None,
        help="LLM provider: groq, anthropic, openai, gemini (default: server default)"
    )
    parser.add_argument(
        "--output-dir", default=DEFAULT_OUTPUT_DIR,
        help=f"Output directory (default: {DEFAULT_OUTPUT_DIR})"
    )
    args = parser.parse_args()

    strategies = [s.strip() for s in args.strategies.split(",")]
    for s in strategies:
        if s not in ALL_STRATEGIES:
            print(f"Error: Unknown strategy '{s}'. Choose from: {', '.join(ALL_STRATEGIES)}")
            sys.exit(1)

    asyncio.run(run_evaluation(
        strategies=strategies,
        limit=args.limit,
        provider=args.provider,
        output_dir=args.output_dir,
    ))


if __name__ == "__main__":
    main()
