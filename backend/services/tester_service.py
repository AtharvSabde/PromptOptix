"""
Tester Service - A/B testing for original vs optimized prompts

This service runs both versions of a prompt multiple times with test input,
compares the outputs, and determines which performs better with statistical
confidence.
"""

import asyncio
import time
from typing import Dict, Any, List, Optional
from collections import Counter
import statistics

from ..utils import (
    get_logger,
    count_tokens,
    estimate_cost
)
from ..config import Config
from .llm_service import get_llm_service

logger = get_logger(__name__)


class TesterService:
    """
    A/B testing service for comparing prompt versions

    Runs both original and optimized prompts multiple times with the same
    test input, then analyzes the outputs to determine which performs better.

    Features:
    - Multiple iteration testing
    - Output consistency analysis
    - Quality scoring
    - Response length analysis
    - Statistical confidence calculation
    - Cost tracking
    """

    def __init__(self):
        """Initialize tester with LLM service"""
        self.llm_service = get_llm_service()
        self.logger = get_logger(__name__)

    async def run_test(
        self,
        original_prompt: str,
        optimized_prompt: str,
        test_input: str,
        iterations: int = 5,
        evaluation_criteria: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Run A/B test comparing original and optimized prompts

        Args:
            original_prompt: The original unoptimized prompt
            optimized_prompt: The optimized prompt to compare
            test_input: Input data to test both prompts with
            iterations: Number of test runs per prompt (1-10)
            evaluation_criteria: Custom criteria for evaluation (optional)

        Returns:
            Test results:
            {
                "original_results": [
                    {"iteration": 1, "output": "...", "metadata": {...}},
                    ...
                ],
                "optimized_results": [...],
                "winner": "optimized" | "original" | "tie",
                "confidence": 0.87,
                "metrics": {
                    "quality_improvement": 0.23,
                    "consistency_original": 0.85,
                    "consistency_optimized": 0.92,
                    "avg_length_original": 150,
                    "avg_length_optimized": 180
                },
                "summary": "The optimized prompt produced...",
                "metadata": {
                    "total_iterations": 10,
                    "total_cost": 0.05,
                    "processing_time_ms": 5000
                }
            }
        """
        start_time = time.time()
        iterations = max(1, min(iterations, 10))  # Clamp to 1-10

        self.logger.info(
            f"Starting A/B test with {iterations} iterations per prompt",
            extra={
                "original_length": len(original_prompt),
                "optimized_length": len(optimized_prompt),
                "test_input_length": len(test_input)
            }
        )

        # Run tests for both prompts
        original_results = await self._run_prompt_iterations(
            prompt=original_prompt,
            test_input=test_input,
            iterations=iterations,
            label="original"
        )

        optimized_results = await self._run_prompt_iterations(
            prompt=optimized_prompt,
            test_input=test_input,
            iterations=iterations,
            label="optimized"
        )

        # Analyze results
        metrics = self._calculate_metrics(original_results, optimized_results)

        # Determine winner
        winner, confidence = self._determine_winner(
            original_results,
            optimized_results,
            metrics,
            evaluation_criteria
        )

        # Generate summary
        summary = self._generate_summary(winner, confidence, metrics)

        # Calculate total cost
        total_cost = sum(
            r["metadata"].get("cost", 0)
            for r in original_results + optimized_results
        )

        processing_time_ms = int((time.time() - start_time) * 1000)

        result = {
            "original_results": original_results,
            "optimized_results": optimized_results,
            "winner": winner,
            "confidence": round(confidence, 2),
            "metrics": metrics,
            "summary": summary,
            "metadata": {
                "total_iterations": iterations * 2,
                "iterations_per_prompt": iterations,
                "total_cost": round(total_cost, 6),
                "processing_time_ms": processing_time_ms,
                "test_input_tokens": count_tokens(test_input)
            }
        }

        self.logger.info(
            f"A/B test complete: winner={winner}, confidence={confidence}",
            extra={"processing_time_ms": processing_time_ms}
        )

        return result

    async def _run_prompt_iterations(
        self,
        prompt: str,
        test_input: str,
        iterations: int,
        label: str
    ) -> List[Dict[str, Any]]:
        """
        Run a prompt multiple times and collect results

        Args:
            prompt: The prompt to test
            test_input: Test input to include
            iterations: Number of iterations
            label: Label for logging

        Returns:
            List of iteration results
        """
        results = []

        # Combine prompt with test input
        full_prompt = f"{prompt}\n\nInput:\n{test_input}"

        for i in range(iterations):
            iteration_start = time.time()

            try:
                # Call LLM
                response = await self.llm_service.call_async(
                    prompt=full_prompt,
                    max_tokens=1000,
                    temperature=0.7  # Some variation for consistency testing
                )

                output = response.get("content", "")
                tokens_used = response.get("usage", {})

                iteration_time_ms = int((time.time() - iteration_start) * 1000)

                results.append({
                    "iteration": i + 1,
                    "output": output,
                    "success": True,
                    "metadata": {
                        "response_length": len(output),
                        "response_tokens": count_tokens(output),
                        "latency_ms": iteration_time_ms,
                        "input_tokens": tokens_used.get("input_tokens", 0),
                        "output_tokens": tokens_used.get("output_tokens", 0),
                        "cost": estimate_cost(
                            tokens_used.get("input_tokens", 0),
                            tokens_used.get("output_tokens", 0),
                            "anthropic"
                        )
                    }
                })

            except Exception as e:
                self.logger.warning(
                    f"Iteration {i+1} failed for {label}: {e}"
                )
                results.append({
                    "iteration": i + 1,
                    "output": "",
                    "success": False,
                    "error": str(e),
                    "metadata": {}
                })

        return results

    def _calculate_metrics(
        self,
        original_results: List[Dict[str, Any]],
        optimized_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Calculate comparison metrics between original and optimized outputs

        Metrics calculated:
        - Consistency (how similar outputs are across iterations)
        - Average response length
        - Average latency
        - Success rate
        """
        def get_successful_outputs(results):
            return [r["output"] for r in results if r.get("success", False)]

        def calculate_consistency(outputs: List[str]) -> float:
            """Calculate consistency as average pairwise similarity"""
            if len(outputs) < 2:
                return 1.0

            # Simple consistency: coefficient of variation of lengths
            lengths = [len(o) for o in outputs]
            if not lengths:
                return 0.0

            mean_len = statistics.mean(lengths)
            if mean_len == 0:
                return 1.0

            try:
                stdev = statistics.stdev(lengths)
                cv = stdev / mean_len
                # Convert CV to consistency score (lower CV = higher consistency)
                return max(0, 1 - cv)
            except statistics.StatisticsError:
                return 1.0

        def calculate_avg_length(outputs: List[str]) -> float:
            if not outputs:
                return 0
            return statistics.mean([len(o) for o in outputs])

        def calculate_avg_latency(results: List[Dict]) -> float:
            latencies = [
                r["metadata"].get("latency_ms", 0)
                for r in results if r.get("success", False)
            ]
            return statistics.mean(latencies) if latencies else 0

        original_outputs = get_successful_outputs(original_results)
        optimized_outputs = get_successful_outputs(optimized_results)

        original_consistency = calculate_consistency(original_outputs)
        optimized_consistency = calculate_consistency(optimized_outputs)

        original_avg_length = calculate_avg_length(original_outputs)
        optimized_avg_length = calculate_avg_length(optimized_outputs)

        # Calculate quality proxy (based on response completeness and consistency)
        original_quality = self._estimate_quality(original_results)
        optimized_quality = self._estimate_quality(optimized_results)
        quality_improvement = optimized_quality - original_quality

        return {
            "consistency_original": round(original_consistency, 2),
            "consistency_optimized": round(optimized_consistency, 2),
            "consistency_improvement": round(optimized_consistency - original_consistency, 2),
            "avg_length_original": int(original_avg_length),
            "avg_length_optimized": int(optimized_avg_length),
            "length_change_percent": round(
                ((optimized_avg_length - original_avg_length) / max(original_avg_length, 1)) * 100,
                1
            ),
            "avg_latency_original_ms": int(calculate_avg_latency(original_results)),
            "avg_latency_optimized_ms": int(calculate_avg_latency(optimized_results)),
            "success_rate_original": round(
                len(original_outputs) / max(len(original_results), 1), 2
            ),
            "success_rate_optimized": round(
                len(optimized_outputs) / max(len(optimized_results), 1), 2
            ),
            "quality_original": round(original_quality, 2),
            "quality_optimized": round(optimized_quality, 2),
            "quality_improvement": round(quality_improvement, 2)
        }

    def _estimate_quality(self, results: List[Dict[str, Any]]) -> float:
        """
        Estimate quality score based on response characteristics

        Quality factors:
        - Success rate (40%)
        - Response completeness/length (30%)
        - Consistency (30%)
        """
        successful = [r for r in results if r.get("success", False)]

        if not successful:
            return 0.0

        # Success rate component (0-40 points)
        success_rate = len(successful) / len(results)
        success_score = success_rate * 40

        # Completeness component (0-30 points)
        # Assume responses between 100-500 chars are complete
        lengths = [len(r["output"]) for r in successful]
        avg_length = statistics.mean(lengths)
        if avg_length < 50:
            completeness_score = 10
        elif avg_length < 100:
            completeness_score = 20
        else:
            completeness_score = 30

        # Consistency component (0-30 points)
        if len(lengths) >= 2:
            try:
                cv = statistics.stdev(lengths) / max(statistics.mean(lengths), 1)
                consistency_score = max(0, (1 - cv) * 30)
            except statistics.StatisticsError:
                consistency_score = 30
        else:
            consistency_score = 30

        return (success_score + completeness_score + consistency_score) / 100

    def _determine_winner(
        self,
        original_results: List[Dict[str, Any]],
        optimized_results: List[Dict[str, Any]],
        metrics: Dict[str, Any],
        evaluation_criteria: Optional[List[str]]
    ) -> tuple:
        """
        Determine which prompt performed better

        Returns:
            (winner: str, confidence: float)
        """
        # Score each prompt based on metrics
        original_score = 0
        optimized_score = 0

        # Quality (40% weight)
        if metrics["quality_optimized"] > metrics["quality_original"]:
            optimized_score += 40
        elif metrics["quality_original"] > metrics["quality_optimized"]:
            original_score += 40
        else:
            original_score += 20
            optimized_score += 20

        # Consistency (30% weight)
        if metrics["consistency_optimized"] > metrics["consistency_original"]:
            optimized_score += 30
        elif metrics["consistency_original"] > metrics["consistency_optimized"]:
            original_score += 30
        else:
            original_score += 15
            optimized_score += 15

        # Success rate (20% weight)
        if metrics["success_rate_optimized"] > metrics["success_rate_original"]:
            optimized_score += 20
        elif metrics["success_rate_original"] > metrics["success_rate_optimized"]:
            original_score += 20
        else:
            original_score += 10
            optimized_score += 10

        # Response quality (10% weight) - prefer substantial responses
        if metrics["avg_length_optimized"] > metrics["avg_length_original"] * 0.8:
            optimized_score += 10
        elif metrics["avg_length_original"] > metrics["avg_length_optimized"] * 0.8:
            original_score += 10
        else:
            original_score += 5
            optimized_score += 5

        # Determine winner and confidence
        total_score = original_score + optimized_score
        if total_score == 0:
            return "tie", 0.5

        score_diff = abs(optimized_score - original_score)
        confidence = 0.5 + (score_diff / total_score) * 0.5

        if optimized_score > original_score:
            winner = "optimized"
        elif original_score > optimized_score:
            winner = "original"
        else:
            winner = "tie"
            confidence = 0.5

        return winner, confidence

    def _generate_summary(
        self,
        winner: str,
        confidence: float,
        metrics: Dict[str, Any]
    ) -> str:
        """Generate human-readable summary of test results"""
        parts = []

        # Winner announcement
        if winner == "optimized":
            parts.append(
                f"The optimized prompt performed better with {confidence*100:.0f}% confidence."
            )
        elif winner == "original":
            parts.append(
                f"The original prompt performed better with {confidence*100:.0f}% confidence."
            )
        else:
            parts.append("Both prompts performed similarly (tie).")

        # Key metrics
        if metrics["consistency_improvement"] > 0.1:
            parts.append(
                f"Consistency improved by {metrics['consistency_improvement']:.0%}."
            )
        elif metrics["consistency_improvement"] < -0.1:
            parts.append(
                f"Consistency decreased by {abs(metrics['consistency_improvement']):.0%}."
            )

        if metrics["quality_improvement"] > 0:
            parts.append(
                f"Quality score improved by {metrics['quality_improvement']:.2f} points."
            )
        elif metrics["quality_improvement"] < 0:
            parts.append(
                f"Quality score decreased by {abs(metrics['quality_improvement']):.2f} points."
            )

        # Length change
        if abs(metrics["length_change_percent"]) > 10:
            direction = "longer" if metrics["length_change_percent"] > 0 else "shorter"
            parts.append(
                f"Optimized responses were {abs(metrics['length_change_percent']):.0f}% {direction}."
            )

        return " ".join(parts)

    async def quick_test(
        self,
        original_prompt: str,
        optimized_prompt: str,
        test_input: str
    ) -> Dict[str, Any]:
        """
        Run a quick single-iteration test

        Useful for fast comparisons without full statistical analysis.
        """
        return await self.run_test(
            original_prompt=original_prompt,
            optimized_prompt=optimized_prompt,
            test_input=test_input,
            iterations=1
        )


# Singleton instance
_tester = None


def get_tester() -> TesterService:
    """Get or create singleton tester instance"""
    global _tester
    if _tester is None:
        _tester = TesterService()
    return _tester


__all__ = ["TesterService", "get_tester"]
