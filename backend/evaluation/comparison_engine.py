"""
PromptOptimizer Pro - Research Comparison Engine

Utilities for publication-grade benchmark comparisons:
- bootstrap confidence intervals
- paired significance testing
- multiple-comparison correction
- pairwise strategy win/loss analysis
- repeated-trial stability summaries
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
import math
import random
from statistics import mean, median, stdev
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

from ..utils import get_logger

logger = get_logger(__name__)

try:
    from scipy.stats import pearsonr, spearmanr, ttest_rel, wilcoxon
    SCIPY_AVAILABLE = True
except ImportError:  # pragma: no cover - dependency fallback
    SCIPY_AVAILABLE = False


@dataclass
class StrategyPairwiseResult:
    """Pairwise strategy comparison summary."""

    strategy_a: str
    strategy_b: str
    n: int
    mean_delta: float
    median_delta: float
    wins_a: int
    wins_b: int
    ties: int
    cohens_d: float
    t_statistic: float
    p_value_ttest: float
    wilcoxon_statistic: float
    p_value_wilcoxon: float
    p_value_corrected: Optional[float] = None
    significant: Optional[bool] = None


class ComparisonEngine:
    """Publication-oriented benchmark comparison helpers."""

    def __init__(self, seed: int = 42):
        self.seed = seed
        self._rng = random.Random(seed)

    @staticmethod
    def safe_mean(values: Sequence[float]) -> float:
        return mean(values) if values else 0.0

    @staticmethod
    def safe_median(values: Sequence[float]) -> float:
        return median(values) if values else 0.0

    @staticmethod
    def safe_stdev(values: Sequence[float]) -> float:
        return stdev(values) if len(values) > 1 else 0.0

    def bootstrap_confidence_interval(
        self,
        values: Sequence[float],
        confidence: float = 0.95,
        n_bootstrap: int = 2000
    ) -> Tuple[float, float]:
        """Non-parametric bootstrap confidence interval for the mean."""
        if not values:
            return 0.0, 0.0
        if len(values) == 1:
            return values[0], values[0]

        samples = []
        n = len(values)
        for _ in range(max(200, n_bootstrap)):
            resample = [values[self._rng.randrange(n)] for _ in range(n)]
            samples.append(mean(resample))

        samples.sort()
        alpha = 1.0 - confidence
        low_idx = int((alpha / 2) * (len(samples) - 1))
        high_idx = int((1 - alpha / 2) * (len(samples) - 1))
        return samples[low_idx], samples[high_idx]

    @staticmethod
    def cohens_d_paired(before: Sequence[float], after: Sequence[float]) -> float:
        """Effect size for paired observations."""
        if len(before) != len(after) or len(before) < 2:
            return 0.0
        diffs = [a - b for a, b in zip(after, before)]
        if len(diffs) < 2:
            return 0.0
        diff_sd = stdev(diffs)
        if diff_sd == 0:
            return 0.0
        return mean(diffs) / diff_sd

    @staticmethod
    def _normal_cdf(x: float) -> float:
        return 0.5 * (1 + math.erf(x / math.sqrt(2)))

    def paired_significance(
        self,
        before: Sequence[float],
        after: Sequence[float]
    ) -> Dict[str, float]:
        """Return paired t-test and Wilcoxon results when possible."""
        if len(before) != len(after) or len(before) < 2:
            return {
                "t_statistic": 0.0,
                "p_value_ttest": 1.0,
                "wilcoxon_statistic": 0.0,
                "p_value_wilcoxon": 1.0,
            }

        if SCIPY_AVAILABLE:
            try:
                t_stat, p_t = ttest_rel(before, after)
                try:
                    w_stat, p_w = wilcoxon(after, before, zero_method="wilcox")
                except ValueError:
                    w_stat, p_w = 0.0, 1.0
                return {
                    "t_statistic": float(t_stat),
                    "p_value_ttest": float(p_t),
                    "wilcoxon_statistic": float(w_stat),
                    "p_value_wilcoxon": float(p_w),
                }
            except Exception:  # pragma: no cover - scipy fallback
                logger.warning("SciPy paired test failed, falling back to manual t-test")

        diffs = [a - b for a, b in zip(after, before)]
        diff_mean = mean(diffs)
        diff_sd = stdev(diffs) if len(diffs) > 1 else 0.0
        t_stat = diff_mean / (diff_sd / math.sqrt(len(diffs))) if diff_sd > 0 else 0.0
        p_val = 2 * (1 - self._normal_cdf(abs(t_stat)))
        return {
            "t_statistic": float(t_stat),
            "p_value_ttest": float(p_val),
            "wilcoxon_statistic": 0.0,
            "p_value_wilcoxon": 1.0,
        }

    @staticmethod
    def holm_bonferroni(p_values: Sequence[float], alpha: float = 0.05) -> List[Tuple[float, bool]]:
        """Return Holm-Bonferroni corrected p-values and significance flags."""
        if not p_values:
            return []

        indexed = sorted(enumerate(p_values), key=lambda item: item[1])
        m = len(indexed)
        corrected = [1.0] * m
        significant = [False] * m

        running_max = 0.0
        for rank, (original_idx, p_val) in enumerate(indexed):
            factor = m - rank
            adjusted = min(1.0, p_val * factor)
            running_max = max(running_max, adjusted)
            corrected[original_idx] = running_max

        for idx, value in enumerate(corrected):
            significant[idx] = value <= alpha

        return list(zip(corrected, significant))

    def summarize_trials(
        self,
        trials: Sequence[Dict[str, Any]],
        baseline_score: float,
        n_bootstrap: int = 2000,
    ) -> Dict[str, Any]:
        """Aggregate repeated strategy trials into a stable summary."""
        successful = [t for t in trials if t.get("status") == "success"]
        if not successful:
            return {
                "status": "error",
                "num_trials": len(trials),
                "successful_trials": 0,
                "trial_success_rate": 0.0,
                "trial_results": list(trials),
            }

        score_after = [t.get("score_after", 0.0) for t in successful]
        improvements = [s - baseline_score for s in score_after]
        defects_after = [t.get("defects_after", 0) for t in successful]
        hs_after = [t.get("high_severity_after", 0) for t in successful]
        time_ms = [t.get("processing_time_ms", 0) for t in successful]
        cost_after = [t.get("cost_after", 0.0) for t in successful]

        avg_score = self.safe_mean(score_after)
        low_ci, high_ci = self.bootstrap_confidence_interval(improvements, n_bootstrap=n_bootstrap)
        stability_sd = self.safe_stdev(score_after)
        stability_cv = (stability_sd / avg_score) if avg_score else 0.0

        representative = max(successful, key=lambda item: item.get("score_after", 0.0))

        return {
            "status": "success",
            "num_trials": len(trials),
            "successful_trials": len(successful),
            "trial_success_rate": round(len(successful) / max(len(trials), 1), 3),
            "score_after": round(avg_score, 2),
            "score_after_mean": round(avg_score, 2),
            "score_after_median": round(self.safe_median(score_after), 2),
            "score_after_std": round(stability_sd, 3),
            "score_after_min": round(min(score_after), 2),
            "score_after_max": round(max(score_after), 2),
            "improvement_mean": round(self.safe_mean(improvements), 2),
            "improvement_median": round(self.safe_median(improvements), 2),
            "improvement_std": round(self.safe_stdev(improvements), 3),
            "improvement_ci95": [round(low_ci, 2), round(high_ci, 2)],
            "defects_after": round(self.safe_mean(defects_after), 2),
            "high_severity_after": round(self.safe_mean(hs_after), 2),
            "processing_time_ms": int(round(self.safe_mean(time_ms))),
            "processing_time_total_ms": int(sum(time_ms)),
            "cost_after": round(self.safe_mean(cost_after), 6),
            "cost_total": round(sum(cost_after), 6),
            "stability": {
                "score_std": round(stability_sd, 3),
                "score_cv": round(stability_cv, 4),
            },
            "trial_results": list(trials),
            "representative_result": representative,
            "techniques_applied": representative.get("techniques_applied", []),
            "evolution_history": representative.get("evolution_history", []),
            "trajectory": representative.get("trajectory", []),
            "critique_rounds": representative.get("critique_rounds", []),
            "pipeline_metadata": representative.get("pipeline_metadata", {}),
            "optimized_prompt": representative.get("optimized_prompt"),
            "defects_list_after": representative.get("defects_list_after", []),
        }

    def pairwise_strategy_comparisons(
        self,
        results: Sequence[Dict[str, Any]],
        strategies: Sequence[str],
    ) -> List[StrategyPairwiseResult]:
        """Compare strategy improvements pairwise on the same prompts."""
        pairwise_results: List[StrategyPairwiseResult] = []

        for strategy_a, strategy_b in combinations(strategies, 2):
            improvements_a = []
            improvements_b = []
            wins_a = 0
            wins_b = 0
            ties = 0

            for prompt_result in results:
                strat_a = prompt_result.get("strategies", {}).get(strategy_a, {})
                strat_b = prompt_result.get("strategies", {}).get(strategy_b, {})
                if strat_a.get("status") != "success" or strat_b.get("status") != "success":
                    continue

                baseline = prompt_result.get("baseline", {}).get("score", 0.0)
                imp_a = strat_a.get("improvement_mean", strat_a.get("score_after", 0.0) - baseline)
                imp_b = strat_b.get("improvement_mean", strat_b.get("score_after", 0.0) - baseline)
                improvements_a.append(imp_a)
                improvements_b.append(imp_b)

                if abs(imp_a - imp_b) < 1e-9:
                    ties += 1
                elif imp_a > imp_b:
                    wins_a += 1
                else:
                    wins_b += 1

            n = len(improvements_a)
            if n < 2:
                pairwise_results.append(
                    StrategyPairwiseResult(
                        strategy_a=strategy_a,
                        strategy_b=strategy_b,
                        n=n,
                        mean_delta=0.0,
                        median_delta=0.0,
                        wins_a=wins_a,
                        wins_b=wins_b,
                        ties=ties,
                        cohens_d=0.0,
                        t_statistic=0.0,
                        p_value_ttest=1.0,
                        wilcoxon_statistic=0.0,
                        p_value_wilcoxon=1.0,
                    )
                )
                continue

            deltas = [a - b for a, b in zip(improvements_a, improvements_b)]
            sig = self.paired_significance(improvements_b, improvements_a)
            pairwise_results.append(
                StrategyPairwiseResult(
                    strategy_a=strategy_a,
                    strategy_b=strategy_b,
                    n=n,
                    mean_delta=round(self.safe_mean(deltas), 3),
                    median_delta=round(self.safe_median(deltas), 3),
                    wins_a=wins_a,
                    wins_b=wins_b,
                    ties=ties,
                    cohens_d=round(self.cohens_d_paired(improvements_b, improvements_a), 3),
                    t_statistic=round(sig["t_statistic"], 4),
                    p_value_ttest=round(sig["p_value_ttest"], 6),
                    wilcoxon_statistic=round(sig["wilcoxon_statistic"], 4),
                    p_value_wilcoxon=round(sig["p_value_wilcoxon"], 6),
                )
            )

        corrected = self.holm_bonferroni([r.p_value_wilcoxon for r in pairwise_results])
        for result, (p_corr, significant) in zip(pairwise_results, corrected):
            result.p_value_corrected = round(p_corr, 6)
            result.significant = significant

        return pairwise_results

    def benchmark_correlation(
        self,
        x_values: Sequence[float],
        y_values: Sequence[float]
    ) -> Dict[str, float]:
        """Correlation helper for benchmark sanity checks."""
        if len(x_values) < 2 or len(y_values) < 2 or len(x_values) != len(y_values):
            return {
                "pearson_r": 0.0,
                "pearson_p": 1.0,
                "spearman_rho": 0.0,
                "spearman_p": 1.0,
            }

        if SCIPY_AVAILABLE:
            try:
                pearson_r, pearson_p = pearsonr(x_values, y_values)
                spearman_rho, spearman_p = spearmanr(x_values, y_values)
                return {
                    "pearson_r": round(float(pearson_r), 4),
                    "pearson_p": round(float(pearson_p), 6),
                    "spearman_rho": round(float(spearman_rho), 4),
                    "spearman_p": round(float(spearman_p), 6),
                }
            except Exception:  # pragma: no cover
                logger.warning("Correlation computation failed, returning zeros")

        return {
            "pearson_r": 0.0,
            "pearson_p": 1.0,
            "spearman_rho": 0.0,
            "spearman_p": 1.0,
        }


_comparison_engine: Optional[ComparisonEngine] = None


def get_comparison_engine(seed: int = 42) -> ComparisonEngine:
    """Get or create singleton comparison engine."""
    global _comparison_engine
    if _comparison_engine is None or _comparison_engine.seed != seed:
        _comparison_engine = ComparisonEngine(seed=seed)
    return _comparison_engine


__all__ = [
    "ComparisonEngine",
    "StrategyPairwiseResult",
    "get_comparison_engine",
]
