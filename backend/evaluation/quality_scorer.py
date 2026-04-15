"""
PromptOptimizer Pro - Benchmark Quality Scorer

Helpers for evaluating benchmark coverage and detector alignment:
- dataset composition summaries
- expected-vs-detected defect overlap
- human-score alignment diagnostics
"""

from __future__ import annotations

from collections import Counter
from typing import Any, Dict, Iterable, List, Sequence


def _safe_divide(num: float, den: float) -> float:
    return num / den if den else 0.0


class BenchmarkQualityScorer:
    """Summarize benchmark quality and detector alignment."""

    def summarize_dataset(self, prompts: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
        categories = Counter(p.get("category", "unknown") for p in prompts)
        task_types = Counter(p.get("task_type", "unknown") for p in prompts)
        domains = Counter(p.get("domain", "unknown") for p in prompts)
        difficulties = Counter(p.get("difficulty", "unknown") for p in prompts)
        sources = Counter(p.get("source", "unknown") for p in prompts)

        human_scores = [float(p.get("human_score", 0.0)) for p in prompts if p.get("human_score") is not None]
        expected_defect_counts = [len(p.get("expected_defects", [])) for p in prompts]

        return {
            "num_prompts": len(prompts),
            "category_distribution": dict(categories),
            "task_type_distribution": dict(task_types),
            "domain_distribution": dict(domains),
            "difficulty_distribution": dict(difficulties),
            "source_distribution": dict(sources),
            "avg_human_score": round(sum(human_scores) / len(human_scores), 3) if human_scores else 0.0,
            "avg_expected_defects": round(sum(expected_defect_counts) / len(expected_defect_counts), 3)
            if expected_defect_counts else 0.0,
        }

    def score_defect_overlap(
        self,
        expected_defects: Sequence[str],
        detected_defects: Sequence[str]
    ) -> Dict[str, float]:
        expected = set(expected_defects)
        detected = set(detected_defects)

        tp = len(expected & detected)
        fp = len(detected - expected)
        fn = len(expected - detected)

        precision = _safe_divide(tp, tp + fp)
        recall = _safe_divide(tp, tp + fn)
        f1 = _safe_divide(2 * precision * recall, precision + recall)
        jaccard = _safe_divide(tp, len(expected | detected))

        return {
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1": round(f1, 4),
            "jaccard": round(jaccard, 4),
            "tp": tp,
            "fp": fp,
            "fn": fn,
        }

    def summarize_alignment(self, results: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregate overlap between expected benchmark labels and baseline detections."""
        precision_scores = []
        recall_scores = []
        f1_scores = []
        jaccard_scores = []
        total_tp = 0
        total_fp = 0
        total_fn = 0

        for result in results:
            expected = result.get("expected_defects", [])
            detected = result.get("baseline", {}).get("detected_defect_ids", [])
            overlap = self.score_defect_overlap(expected, detected)
            precision_scores.append(overlap["precision"])
            recall_scores.append(overlap["recall"])
            f1_scores.append(overlap["f1"])
            jaccard_scores.append(overlap["jaccard"])
            total_tp += overlap["tp"]
            total_fp += overlap["fp"]
            total_fn += overlap["fn"]

        macro_precision = sum(precision_scores) / len(precision_scores) if precision_scores else 0.0
        macro_recall = sum(recall_scores) / len(recall_scores) if recall_scores else 0.0
        macro_f1 = sum(f1_scores) / len(f1_scores) if f1_scores else 0.0
        macro_jaccard = sum(jaccard_scores) / len(jaccard_scores) if jaccard_scores else 0.0

        micro_precision = _safe_divide(total_tp, total_tp + total_fp)
        micro_recall = _safe_divide(total_tp, total_tp + total_fn)
        micro_f1 = _safe_divide(2 * micro_precision * micro_recall, micro_precision + micro_recall)

        return {
            "macro_precision": round(macro_precision, 4),
            "macro_recall": round(macro_recall, 4),
            "macro_f1": round(macro_f1, 4),
            "macro_jaccard": round(macro_jaccard, 4),
            "micro_precision": round(micro_precision, 4),
            "micro_recall": round(micro_recall, 4),
            "micro_f1": round(micro_f1, 4),
            "total_tp": total_tp,
            "total_fp": total_fp,
            "total_fn": total_fn,
        }


_quality_scorer: BenchmarkQualityScorer | None = None


def get_quality_scorer() -> BenchmarkQualityScorer:
    global _quality_scorer
    if _quality_scorer is None:
        _quality_scorer = BenchmarkQualityScorer()
    return _quality_scorer


__all__ = [
    "BenchmarkQualityScorer",
    "get_quality_scorer",
]
