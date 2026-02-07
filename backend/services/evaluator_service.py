"""
Evaluator Service - Evaluate optimization effectiveness

This service compares before/after analysis results to measure the
effectiveness of prompt optimization. It calculates improvement metrics,
tracks which defects were fixed, and provides detailed breakdowns.

Enhanced with:
- NLP metrics (BLEU, ROUGE, METEOR) for output similarity
- G-EVAL style LLM-based evaluation for qualitative assessment
- Comprehensive evaluation combining all metrics
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from ..utils import (
    get_logger,
    count_tokens,
    calculate_token_reduction
)
from ..config import Config
from ..evaluation import get_automated_metrics, get_llm_evaluator

logger = get_logger(__name__)


@dataclass
class EvaluationMetrics:
    """Container for evaluation metrics"""
    score_improvement: float
    defects_fixed: int
    defects_remaining: int
    new_defects: int
    token_change: int
    token_change_percent: float
    consensus_change: float


class EvaluatorService:
    """
    Evaluates the effectiveness of prompt optimization

    Compares before and after analysis results to determine:
    - How much the quality score improved
    - Which defects were fixed
    - Whether any new defects were introduced
    - Token efficiency changes
    - Overall optimization success

    Features:
    - Score improvement calculation
    - Defect tracking (fixed, remaining, new)
    - Token efficiency analysis
    - Severity-weighted metrics
    - Detailed breakdowns by category
    - NLP metrics (BLEU, ROUGE, METEOR) for output comparison
    - G-EVAL style LLM-based qualitative evaluation
    """

    def __init__(self):
        """Initialize evaluator with metrics calculators"""
        self.logger = get_logger(__name__)
        self.automated_metrics = get_automated_metrics()
        self.llm_evaluator = get_llm_evaluator()

    def evaluate_optimization(
        self,
        original_prompt: str,
        optimized_prompt: str,
        before_analysis: Dict[str, Any],
        after_analysis: Dict[str, Any],
        techniques_applied: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Evaluate the effectiveness of a prompt optimization

        Args:
            original_prompt: The original prompt text
            optimized_prompt: The optimized prompt text
            before_analysis: Analysis results before optimization
            after_analysis: Analysis results after optimization
            techniques_applied: List of techniques that were applied

        Returns:
            Evaluation result:
            {
                "success": True/False,
                "improvement_score": 2.5,
                "metrics": {
                    "score_before": 4.5,
                    "score_after": 7.0,
                    "score_improvement": 2.5,
                    "defects_fixed": 3,
                    "defects_remaining": 1,
                    "new_defects": 0,
                    "token_change": 50,
                    "token_change_percent": 33.3
                },
                "defect_analysis": {
                    "fixed": [...],
                    "remaining": [...],
                    "new": [...]
                },
                "technique_effectiveness": [...],
                "summary": "Optimization successful...",
                "recommendations": [...]
            }
        """
        self.logger.info("Evaluating optimization effectiveness")

        # Calculate basic metrics
        score_before = before_analysis.get("overall_score", 0)
        score_after = after_analysis.get("overall_score", 0)
        score_improvement = score_after - score_before

        # Analyze defects
        defects_before = before_analysis.get("defects", [])
        defects_after = after_analysis.get("defects", [])
        defect_analysis = self._analyze_defects(defects_before, defects_after)

        # Token analysis
        tokens_before = count_tokens(original_prompt)
        tokens_after = count_tokens(optimized_prompt)
        token_change = tokens_after - tokens_before
        token_change_percent = (token_change / tokens_before * 100) if tokens_before > 0 else 0

        # Consensus analysis
        consensus_before = before_analysis.get("consensus", 0)
        consensus_after = after_analysis.get("consensus", 0)
        consensus_change = consensus_after - consensus_before

        # Build metrics
        metrics = {
            "score_before": score_before,
            "score_after": score_after,
            "score_improvement": round(score_improvement, 2),
            "score_improvement_percent": round((score_improvement / max(score_before, 0.1)) * 100, 1),
            "defects_before": len(defects_before),
            "defects_after": len(defects_after),
            "defects_fixed": len(defect_analysis["fixed"]),
            "defects_remaining": len(defect_analysis["remaining"]),
            "new_defects": len(defect_analysis["new"]),
            "tokens_before": tokens_before,
            "tokens_after": tokens_after,
            "token_change": token_change,
            "token_change_percent": round(token_change_percent, 1),
            "consensus_before": consensus_before,
            "consensus_after": consensus_after,
            "consensus_change": round(consensus_change, 2)
        }

        # Evaluate technique effectiveness
        technique_effectiveness = []
        if techniques_applied:
            technique_effectiveness = self._evaluate_techniques(
                techniques_applied,
                defect_analysis["fixed"]
            )

        # Determine success
        success = self._determine_success(metrics, defect_analysis)

        # Generate summary and recommendations
        summary = self._generate_summary(metrics, defect_analysis, success)
        recommendations = self._generate_recommendations(
            metrics, defect_analysis, after_analysis
        )

        # Calculate overall effectiveness score (0-100)
        effectiveness_score = self._calculate_effectiveness_score(metrics, defect_analysis)

        result = {
            "success": success,
            "effectiveness_score": effectiveness_score,
            "improvement_score": round(score_improvement, 2),
            "metrics": metrics,
            "defect_analysis": defect_analysis,
            "technique_effectiveness": technique_effectiveness,
            "summary": summary,
            "recommendations": recommendations
        }

        self.logger.info(
            "Evaluation complete",
            extra={
                "success": success,
                "score_improvement": score_improvement,
                "defects_fixed": len(defect_analysis["fixed"])
            }
        )

        return result

    def _analyze_defects(
        self,
        defects_before: List[Dict[str, Any]],
        defects_after: List[Dict[str, Any]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Analyze which defects were fixed, remain, or are new

        Args:
            defects_before: Defects detected before optimization
            defects_after: Defects detected after optimization

        Returns:
            {
                "fixed": [...],     # Defects that were resolved
                "remaining": [...], # Defects still present
                "new": [...]        # New defects introduced
            }
        """
        before_ids = {d["id"] for d in defects_before}
        after_ids = {d["id"] for d in defects_after}

        # Fixed = in before but not in after
        fixed_ids = before_ids - after_ids
        fixed = [d for d in defects_before if d["id"] in fixed_ids]

        # Remaining = in both before and after
        remaining_ids = before_ids & after_ids
        remaining = [d for d in defects_after if d["id"] in remaining_ids]

        # New = in after but not in before
        new_ids = after_ids - before_ids
        new = [d for d in defects_after if d["id"] in new_ids]

        return {
            "fixed": fixed,
            "remaining": remaining,
            "new": new
        }

    def _evaluate_techniques(
        self,
        techniques_applied: List[Dict[str, Any]],
        fixed_defects: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Evaluate how effective each applied technique was

        Args:
            techniques_applied: List of techniques that were applied
            fixed_defects: List of defects that were fixed

        Returns:
            List of technique evaluations with effectiveness metrics
        """
        fixed_ids = {d["id"] for d in fixed_defects}
        results = []

        for technique in techniques_applied:
            target_defects = set(technique.get("target_defects", []))

            # How many targeted defects were actually fixed
            defects_fixed = target_defects & fixed_ids
            effectiveness = len(defects_fixed) / len(target_defects) if target_defects else 0

            results.append({
                "technique_id": technique.get("technique_id"),
                "technique_name": technique.get("technique_name"),
                "target_defects": list(target_defects),
                "defects_fixed": list(defects_fixed),
                "effectiveness": round(effectiveness, 2),
                "fully_effective": effectiveness == 1.0
            })

        return results

    def _determine_success(
        self,
        metrics: Dict[str, Any],
        defect_analysis: Dict[str, List[Dict[str, Any]]]
    ) -> bool:
        """
        Determine if the optimization was successful overall

        Success criteria:
        - Score improved OR stayed same with defects fixed
        - No critical new defects introduced
        - Token increase is reasonable (< 200%)
        """
        score_improved = metrics["score_improvement"] > 0
        defects_fixed = len(defect_analysis["fixed"]) > 0
        no_new_critical = not any(
            d.get("severity") == "critical" for d in defect_analysis["new"]
        )
        reasonable_token_increase = metrics["token_change_percent"] < 200

        # Success if score improved or defects fixed, without bad side effects
        return (score_improved or defects_fixed) and no_new_critical and reasonable_token_increase

    def _calculate_effectiveness_score(
        self,
        metrics: Dict[str, Any],
        defect_analysis: Dict[str, List[Dict[str, Any]]]
    ) -> int:
        """
        Calculate overall effectiveness score (0-100)

        Factors:
        - Score improvement (40%)
        - Defects fixed vs remaining (30%)
        - No new defects (20%)
        - Token efficiency (10%)
        """
        score = 0

        # Score improvement component (40 points max)
        # +10 points per 1.0 score improvement, max 40
        score_improvement = min(metrics["score_improvement"] * 10, 40)
        score += max(score_improvement, 0)

        # Defect resolution component (30 points max)
        total_original = metrics["defects_before"]
        if total_original > 0:
            fix_rate = len(defect_analysis["fixed"]) / total_original
            score += fix_rate * 30

        # No new defects component (20 points max)
        new_count = len(defect_analysis["new"])
        if new_count == 0:
            score += 20
        elif new_count == 1:
            score += 10
        # More than 1 new defect = 0 points

        # Token efficiency component (10 points max)
        token_change_pct = metrics["token_change_percent"]
        if token_change_pct <= 0:
            # Token reduction or no change
            score += 10
        elif token_change_pct <= 50:
            score += 7
        elif token_change_pct <= 100:
            score += 4
        # More than 100% increase = 0 points

        return min(int(score), 100)

    def _generate_summary(
        self,
        metrics: Dict[str, Any],
        defect_analysis: Dict[str, List[Dict[str, Any]]],
        success: bool
    ) -> str:
        """Generate human-readable summary of evaluation"""
        parts = []

        if success:
            parts.append("Optimization was successful.")
        else:
            parts.append("Optimization had mixed results.")

        # Score change
        if metrics["score_improvement"] > 0:
            parts.append(
                f"Quality score improved by {metrics['score_improvement']:.1f} points "
                f"({metrics['score_before']:.1f} -> {metrics['score_after']:.1f})."
            )
        elif metrics["score_improvement"] < 0:
            parts.append(
                f"Quality score decreased by {abs(metrics['score_improvement']):.1f} points."
            )
        else:
            parts.append("Quality score remained unchanged.")

        # Defect changes
        fixed_count = len(defect_analysis["fixed"])
        new_count = len(defect_analysis["new"])
        remaining_count = len(defect_analysis["remaining"])

        if fixed_count > 0:
            parts.append(f"Fixed {fixed_count} defect(s).")
        if remaining_count > 0:
            parts.append(f"{remaining_count} defect(s) still need attention.")
        if new_count > 0:
            parts.append(f"Warning: {new_count} new defect(s) were introduced.")

        # Token change
        if metrics["token_change"] != 0:
            direction = "increased" if metrics["token_change"] > 0 else "decreased"
            parts.append(
                f"Prompt length {direction} by {abs(metrics['token_change'])} tokens "
                f"({metrics['token_change_percent']:.1f}%)."
            )

        return " ".join(parts)

    def _generate_recommendations(
        self,
        metrics: Dict[str, Any],
        defect_analysis: Dict[str, List[Dict[str, Any]]],
        after_analysis: Dict[str, Any]
    ) -> List[str]:
        """Generate recommendations for further improvement"""
        recommendations = []

        # Remaining defects
        remaining = defect_analysis["remaining"]
        if remaining:
            # Group by severity
            critical = [d for d in remaining if d.get("severity") == "critical"]
            high = [d for d in remaining if d.get("severity") == "high"]

            if critical:
                recommendations.append(
                    f"Address {len(critical)} critical defect(s): "
                    f"{', '.join(d['name'] for d in critical)}"
                )
            if high:
                recommendations.append(
                    f"Consider fixing {len(high)} high-severity defect(s): "
                    f"{', '.join(d['name'] for d in high)}"
                )

        # New defects
        new_defects = defect_analysis["new"]
        if new_defects:
            recommendations.append(
                f"Review and fix newly introduced defects: "
                f"{', '.join(d['name'] for d in new_defects)}"
            )

        # Score still low
        if metrics["score_after"] < 7.0:
            recommendations.append(
                "Consider additional optimization techniques to raise score above 7.0"
            )

        # High token increase
        if metrics["token_change_percent"] > 50:
            recommendations.append(
                "Consider condensing the prompt to reduce token usage while maintaining quality"
            )

        # Low consensus
        if after_analysis.get("consensus", 1.0) < 0.7:
            recommendations.append(
                "Agent consensus is low; review disagreements for potential issues"
            )

        if not recommendations:
            recommendations.append("Optimization looks good! No further changes recommended.")

        return recommendations

    def compare_prompts(
        self,
        prompts: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Compare multiple prompt versions

        Args:
            prompts: List of {"prompt": str, "analysis": dict, "label": str}

        Returns:
            Comparison results with rankings
        """
        if len(prompts) < 2:
            return {"error": "Need at least 2 prompts to compare"}

        # Rank by score
        ranked = sorted(
            prompts,
            key=lambda p: p["analysis"].get("overall_score", 0),
            reverse=True
        )

        comparisons = []
        best = ranked[0]

        for i, prompt_data in enumerate(ranked):
            analysis = prompt_data["analysis"]
            comparisons.append({
                "rank": i + 1,
                "label": prompt_data.get("label", f"Prompt {i+1}"),
                "score": analysis.get("overall_score", 0),
                "defect_count": len(analysis.get("defects", [])),
                "tokens": count_tokens(prompt_data["prompt"]),
                "score_diff_from_best": round(
                    best["analysis"].get("overall_score", 0) - analysis.get("overall_score", 0),
                    2
                )
            })

        return {
            "winner": best.get("label", "Prompt 1"),
            "rankings": comparisons,
            "score_range": {
                "highest": ranked[0]["analysis"].get("overall_score", 0),
                "lowest": ranked[-1]["analysis"].get("overall_score", 0)
            }
        }

    async def comprehensive_evaluation(
        self,
        original_prompt: str,
        optimized_prompt: str,
        original_output: Optional[str] = None,
        optimized_output: Optional[str] = None,
        reference_output: Optional[str] = None,
        before_analysis: Optional[Dict[str, Any]] = None,
        after_analysis: Optional[Dict[str, Any]] = None,
        techniques_applied: Optional[List[Dict[str, Any]]] = None,
        include_llm_eval: bool = True
    ) -> Dict[str, Any]:
        """
        Perform comprehensive evaluation combining all available metrics

        This method integrates:
        - Defect-based evaluation (if analyses provided)
        - NLP metrics (BLEU, ROUGE, METEOR) for output comparison
        - G-EVAL style LLM-based evaluation for qualitative assessment

        Args:
            original_prompt: The original prompt text
            optimized_prompt: The optimized prompt text
            original_output: Output generated from original prompt
            optimized_output: Output generated from optimized prompt
            reference_output: Optional gold-standard reference output
            before_analysis: Analysis results before optimization
            after_analysis: Analysis results after optimization
            techniques_applied: List of techniques that were applied
            include_llm_eval: Whether to include LLM-based evaluation

        Returns:
            Comprehensive evaluation with all metrics combined
        """
        self.logger.info("Starting comprehensive evaluation")

        result = {
            "evaluation_type": "comprehensive",
            "prompt_comparison": {},
            "output_comparison": {},
            "defect_evaluation": None,
            "nlp_metrics": None,
            "llm_evaluation": None,
            "combined_score": 0.0,
            "summary": "",
            "recommendations": []
        }

        # 1. Basic prompt comparison
        result["prompt_comparison"] = {
            "original_length": len(original_prompt),
            "optimized_length": len(optimized_prompt),
            "original_tokens": count_tokens(original_prompt),
            "optimized_tokens": count_tokens(optimized_prompt),
            "length_change_percent": round(
                ((len(optimized_prompt) - len(original_prompt)) / max(len(original_prompt), 1)) * 100, 1
            )
        }

        # 2. Prompt similarity metrics
        prompt_similarity = self.automated_metrics.calculate_prompt_similarity(
            original_prompt, optimized_prompt
        )
        result["prompt_comparison"]["similarity"] = prompt_similarity

        # 3. Defect-based evaluation (if analyses provided)
        if before_analysis and after_analysis:
            defect_eval = self.evaluate_optimization(
                original_prompt=original_prompt,
                optimized_prompt=optimized_prompt,
                before_analysis=before_analysis,
                after_analysis=after_analysis,
                techniques_applied=techniques_applied
            )
            result["defect_evaluation"] = defect_eval
            result["recommendations"].extend(defect_eval.get("recommendations", []))

        # 4. NLP metrics for output comparison (if outputs provided)
        if original_output and optimized_output:
            if reference_output:
                # Compare both against reference
                nlp_comparison = self.automated_metrics.compare_outputs(
                    original_output=original_output,
                    optimized_output=optimized_output,
                    reference_output=reference_output
                )
            else:
                # Compare optimized against original
                nlp_comparison = self.automated_metrics.compare_outputs(
                    original_output=original_output,
                    optimized_output=optimized_output
                )

            result["nlp_metrics"] = nlp_comparison
            result["output_comparison"] = {
                "original_length": len(original_output),
                "optimized_length": len(optimized_output),
                "length_change_percent": round(
                    ((len(optimized_output) - len(original_output)) / max(len(original_output), 1)) * 100, 1
                )
            }

        # 5. LLM-based evaluation (if enabled and outputs provided)
        if include_llm_eval and optimized_output:
            try:
                if original_output:
                    # Compare outputs
                    llm_comparison = await self.llm_evaluator.compare_outputs(
                        original_output=original_output,
                        optimized_output=optimized_output,
                        prompt=optimized_prompt,
                        reference_output=reference_output
                    )
                    result["llm_evaluation"] = llm_comparison
                else:
                    # Evaluate optimized output alone
                    llm_eval = await self.llm_evaluator.evaluate_output(
                        prompt=optimized_prompt,
                        output=optimized_output,
                        reference=reference_output
                    )
                    result["llm_evaluation"] = {"optimized_evaluation": llm_eval}
            except Exception as e:
                self.logger.warning(f"LLM evaluation failed: {e}")
                result["llm_evaluation"] = {"error": str(e)}

        # 6. Calculate combined score
        result["combined_score"] = self._calculate_combined_score(result)

        # 7. Generate comprehensive summary
        result["summary"] = self._generate_comprehensive_summary(result)

        self.logger.info(
            "Comprehensive evaluation complete",
            extra={"combined_score": result["combined_score"]}
        )

        return result

    def _calculate_combined_score(self, evaluation_result: Dict[str, Any]) -> float:
        """
        Calculate a combined score from all evaluation components

        Weights:
        - Defect evaluation: 35%
        - NLP metrics: 25%
        - LLM evaluation: 40%
        """
        scores = []
        weights = []

        # Defect evaluation component (0-100 scale)
        if evaluation_result.get("defect_evaluation"):
            defect_score = evaluation_result["defect_evaluation"].get("effectiveness_score", 0)
            scores.append(defect_score / 100.0)  # Normalize to 0-1
            weights.append(0.35)

        # NLP metrics component
        if evaluation_result.get("nlp_metrics"):
            nlp_data = evaluation_result["nlp_metrics"]
            if "improvement" in nlp_data:
                # Reference-based comparison
                composite_improvement = nlp_data["improvement"].get("composite", 0)
                # Convert improvement to score (base 0.5 + improvement capped at 0.5)
                nlp_score = min(1.0, 0.5 + composite_improvement)
            elif "similarity_metrics" in nlp_data:
                # Original vs optimized comparison
                nlp_score = nlp_data["similarity_metrics"].get("composite_score", 0.5)
            else:
                nlp_score = 0.5
            scores.append(nlp_score)
            weights.append(0.25)

        # LLM evaluation component
        if evaluation_result.get("llm_evaluation") and "error" not in evaluation_result["llm_evaluation"]:
            llm_data = evaluation_result["llm_evaluation"]
            if "comparison" in llm_data:
                # Use improvement indicator from comparison
                comparison = llm_data["comparison"]
                if comparison.get("optimized_is_better"):
                    llm_score = 0.8
                elif comparison.get("scores_equal"):
                    llm_score = 0.5
                else:
                    llm_score = 0.3
            elif "optimized_evaluation" in llm_data:
                # Use overall score from single evaluation
                opt_eval = llm_data["optimized_evaluation"]
                llm_score = opt_eval.get("overall_score", 5) / 10.0
            else:
                llm_score = 0.5
            scores.append(llm_score)
            weights.append(0.40)

        # Calculate weighted average
        if not scores:
            return 0.0

        total_weight = sum(weights)
        combined = sum(s * w for s, w in zip(scores, weights)) / total_weight

        return round(combined * 100, 1)  # Return as 0-100 scale

    def _generate_comprehensive_summary(self, evaluation_result: Dict[str, Any]) -> str:
        """Generate a comprehensive summary from all evaluation components"""
        parts = []

        # Overall score
        combined = evaluation_result.get("combined_score", 0)
        if combined >= 80:
            parts.append(f"Excellent optimization (score: {combined}/100).")
        elif combined >= 60:
            parts.append(f"Good optimization (score: {combined}/100).")
        elif combined >= 40:
            parts.append(f"Moderate optimization (score: {combined}/100).")
        else:
            parts.append(f"Limited optimization effectiveness (score: {combined}/100).")

        # Defect summary
        if evaluation_result.get("defect_evaluation"):
            defect_eval = evaluation_result["defect_evaluation"]
            if defect_eval.get("success"):
                fixed = defect_eval["metrics"].get("defects_fixed", 0)
                parts.append(f"Fixed {fixed} defect(s).")
            else:
                parts.append("Defect-based evaluation indicates mixed results.")

        # NLP metrics summary
        if evaluation_result.get("nlp_metrics"):
            nlp = evaluation_result["nlp_metrics"]
            if "improvement" in nlp:
                composite_imp = nlp["improvement"].get("composite", 0)
                if composite_imp > 0:
                    parts.append(f"Output quality improved by {composite_imp:.1%} vs reference.")
                else:
                    parts.append("Output quality similar to or below baseline.")
            elif "interpretation" in nlp:
                parts.append(nlp["interpretation"])

        # LLM evaluation summary
        if evaluation_result.get("llm_evaluation") and "error" not in evaluation_result["llm_evaluation"]:
            llm = evaluation_result["llm_evaluation"]
            if "comparison" in llm:
                comparison = llm["comparison"]
                if comparison.get("optimized_is_better"):
                    parts.append("LLM evaluation confirms improved output quality.")
                elif comparison.get("scores_equal"):
                    parts.append("LLM evaluation shows similar quality between versions.")
                else:
                    parts.append("LLM evaluation prefers the original output.")

        # Prompt changes
        prompt_comp = evaluation_result.get("prompt_comparison", {})
        similarity = prompt_comp.get("similarity", {})
        if similarity:
            change_level = similarity.get("change_level", "moderate")
            parts.append(f"Prompt underwent {change_level} changes.")

        return " ".join(parts)

    async def evaluate_with_llm(
        self,
        prompt: str,
        output: str,
        reference: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Evaluate a single prompt-output pair using LLM-based evaluation

        Args:
            prompt: The prompt that generated the output
            output: The output to evaluate
            reference: Optional reference output for comparison

        Returns:
            G-EVAL style evaluation with dimension scores
        """
        return await self.llm_evaluator.evaluate_output(
            prompt=prompt,
            output=output,
            reference=reference
        )

    def evaluate_with_nlp_metrics(
        self,
        reference: str,
        candidate: str,
        include_bert: bool = False
    ) -> Dict[str, Any]:
        """
        Evaluate using NLP metrics only (BLEU, ROUGE, METEOR)

        Args:
            reference: Reference text
            candidate: Candidate text to evaluate
            include_bert: Whether to include BERT Score (slower)

        Returns:
            Dict with all NLP metric scores
        """
        return self.automated_metrics.calculate_all_metrics(
            reference=reference,
            candidate=candidate,
            include_bert=include_bert
        )


# Singleton instance
_evaluator = None


def get_evaluator() -> EvaluatorService:
    """Get or create singleton evaluator instance"""
    global _evaluator
    if _evaluator is None:
        _evaluator = EvaluatorService()
    return _evaluator


__all__ = [
    "EvaluatorService",
    "get_evaluator",
    "EvaluationMetrics"
]
