"""
PromptOptimizer Pro - Evaluation Package

Uses lazy imports to avoid circular dependencies between evaluation helpers
and services that depend on them.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from .automated_metrics import AutomatedMetrics
    from .comparison_engine import ComparisonEngine, StrategyPairwiseResult
    from .llm_evaluator import LLMEvaluator
    from .quality_scorer import BenchmarkQualityScorer


def get_automated_metrics():
    from .automated_metrics import get_automated_metrics as _impl
    return _impl()


def get_llm_evaluator():
    from .llm_evaluator import get_llm_evaluator as _impl
    return _impl()


def get_comparison_engine(seed: int = 42):
    from .comparison_engine import get_comparison_engine as _impl
    return _impl(seed=seed)


def get_quality_scorer():
    from .quality_scorer import get_quality_scorer as _impl
    return _impl()


def annotate_prompt_records(prompt_records):
    from .benchmark_registry import annotate_prompt_records as _impl
    return _impl(prompt_records)


def filter_prompt_records(prompt_records, buckets=None, split=None):
    from .benchmark_registry import filter_prompt_records as _impl
    return _impl(prompt_records, buckets=buckets, split=split)


def summarize_buckets(prompt_records):
    from .benchmark_registry import summarize_buckets as _impl
    return _impl(prompt_records)


def assign_protocol_splits(prompt_records, dev_ratio=0.2, test_ratio=0.6, seed=42):
    from .benchmark_registry import assign_protocol_splits as _impl
    return _impl(prompt_records, dev_ratio=dev_ratio, test_ratio=test_ratio, seed=seed)


def __getattr__(name):  # pragma: no cover - import convenience
    if name == "AutomatedMetrics":
        from .automated_metrics import AutomatedMetrics
        return AutomatedMetrics
    if name in {"ComparisonEngine", "StrategyPairwiseResult"}:
        from .comparison_engine import ComparisonEngine, StrategyPairwiseResult
        return {"ComparisonEngine": ComparisonEngine, "StrategyPairwiseResult": StrategyPairwiseResult}[name]
    if name == "LLMEvaluator":
        from .llm_evaluator import LLMEvaluator
        return LLMEvaluator
    if name == "BenchmarkQualityScorer":
        from .quality_scorer import BenchmarkQualityScorer
        return BenchmarkQualityScorer
    raise AttributeError(name)


__all__ = [
    "get_automated_metrics",
    "get_llm_evaluator",
    "get_comparison_engine",
    "get_quality_scorer",
    "annotate_prompt_records",
    "filter_prompt_records",
    "summarize_buckets",
    "assign_protocol_splits",
    "AutomatedMetrics",
    "ComparisonEngine",
    "StrategyPairwiseResult",
    "LLMEvaluator",
    "BenchmarkQualityScorer",
]
