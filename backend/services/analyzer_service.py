"""
Analyzer Service - High-level prompt analysis orchestration

This service provides a clean interface for analyzing prompts using
the multi-agent defect detection system. It wraps the AgentOrchestrator
and adds human-readable summaries, response formatting, and metadata.
"""

import asyncio
import time
from typing import Dict, Any, Optional, List

from ..utils import (
    get_logger,
    count_tokens,
    estimate_cost,
    DefectDetectionError
)
from ..config import Config
from .agent_orchestrator import get_orchestrator

logger = get_logger(__name__)


class AnalyzerService:
    """
    High-level service for prompt analysis

    Provides a simple interface for analyzing prompts and getting
    formatted, human-readable results with all metadata included.

    Features:
    - Multi-agent analysis via AgentOrchestrator
    - Human-readable summary generation
    - Token and cost tracking
    - Processing time measurement
    - Response formatting for API responses
    """

    def __init__(self):
        """Initialize analyzer with orchestrator"""
        self.orchestrator = get_orchestrator()
        self.logger = get_logger(__name__)

    async def analyze(
        self,
        prompt: str,
        task_type: str = "general",
        domain: str = "general",
        include_agent_breakdown: bool = True
    ) -> Dict[str, Any]:
        """
        Analyze a prompt for defects using the multi-agent system

        This is the main entry point for prompt analysis. It runs all
        agents in parallel, aggregates results, and formats the response.

        Args:
            prompt: The prompt text to analyze
            task_type: Type of task (code_generation, reasoning, etc.)
            domain: Domain context (software_engineering, mathematics, etc.)
            include_agent_breakdown: Whether to include per-agent results

        Returns:
            Formatted analysis result:
            {
                "overall_score": 7.5,
                "defects": [...],
                "consensus": 0.85,
                "agent_results": {...} or None,
                "disagreements": [...],
                "summary": "Human-readable summary...",
                "metadata": {
                    "prompt_tokens": 150,
                    "estimated_cost": 0.002,
                    "processing_time_ms": 1234,
                    "task_type": "code_generation",
                    "domain": "software_engineering"
                }
            }

        Raises:
            DefectDetectionError: If analysis fails
        """
        start_time = time.time()

        try:
            self.logger.info(
                "Starting prompt analysis",
                extra={
                    "prompt_length": len(prompt),
                    "task_type": task_type,
                    "domain": domain
                }
            )

            # Build context for agents
            context = {
                "task_type": task_type,
                "domain": domain
            }

            # Count tokens before analysis
            prompt_tokens = count_tokens(prompt)

            # Run multi-agent analysis
            raw_result = await self.orchestrator.analyze_with_agents(prompt, context)

            # Calculate processing time
            processing_time_ms = int((time.time() - start_time) * 1000)

            # Generate human-readable summary
            summary = self._generate_summary(raw_result, task_type)

            # Estimate cost (rough estimate based on token usage)
            estimated_cost = estimate_cost(
                input_tokens=prompt_tokens * 4,  # Each agent processes the prompt
                output_tokens=500 * 4,  # Estimated output per agent
                provider="anthropic"
            )

            # Build response
            response = {
                "overall_score": raw_result["overall_score"],
                "defects": raw_result["defects"],
                "consensus": raw_result["consensus"],
                "agent_results": raw_result["agent_results"] if include_agent_breakdown else None,
                "disagreements": raw_result.get("disagreements", []),
                "summary": summary,
                "metadata": {
                    "prompt_tokens": prompt_tokens,
                    "estimated_cost": round(estimated_cost, 6),
                    "processing_time_ms": processing_time_ms,
                    "task_type": task_type,
                    "domain": domain,
                    "num_agents": raw_result["metadata"]["num_agents"],
                    "total_defects_raw": raw_result["metadata"]["total_defects_raw"],
                    "total_defects_filtered": raw_result["metadata"]["total_defects_after_dedup"],
                    "consensus_threshold": raw_result["metadata"]["consensus_threshold"]
                }
            }

            self.logger.info(
                "Analysis complete",
                extra={
                    "overall_score": response["overall_score"],
                    "num_defects": len(response["defects"]),
                    "processing_time_ms": processing_time_ms
                }
            )

            return response

        except Exception as e:
            self.logger.error(f"Analysis failed: {e}", exc_info=True)
            raise DefectDetectionError(
                message=f"Failed to analyze prompt: {str(e)}",
                details={
                    "prompt_length": len(prompt),
                    "task_type": task_type,
                    "domain": domain
                }
            )

    async def batch_analyze(
        self,
        prompts: List[str],
        task_type: str = "general",
        domain: str = "general",
        parallel: bool = True
    ) -> Dict[str, Any]:
        """
        Analyze multiple prompts in batch

        Args:
            prompts: List of prompts to analyze
            task_type: Task type (same for all prompts)
            domain: Domain context (same for all prompts)
            parallel: Whether to process prompts in parallel

        Returns:
            Batch analysis result with individual results and summary stats
        """
        start_time = time.time()

        self.logger.info(
            f"Starting batch analysis of {len(prompts)} prompts",
            extra={"parallel": parallel}
        )

        if parallel:
            # Process all prompts in parallel
            tasks = [
                self.analyze(prompt, task_type, domain, include_agent_breakdown=False)
                for prompt in prompts
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)
        else:
            # Process sequentially
            results = []
            for prompt in prompts:
                try:
                    result = await self.analyze(
                        prompt, task_type, domain, include_agent_breakdown=False
                    )
                    results.append(result)
                except Exception as e:
                    results.append(e)

        # Separate successful results from failures
        successful_results = []
        failed_indices = []

        for i, result in enumerate(results):
            if isinstance(result, Exception):
                failed_indices.append(i)
            else:
                successful_results.append(result)

        # Calculate summary statistics
        if successful_results:
            scores = [r["overall_score"] for r in successful_results]
            all_defect_ids = []
            for r in successful_results:
                all_defect_ids.extend([d["id"] for d in r["defects"]])

            # Find most common defect
            defect_counts = {}
            for defect_id in all_defect_ids:
                defect_counts[defect_id] = defect_counts.get(defect_id, 0) + 1

            most_common_defect = max(defect_counts, key=defect_counts.get) if defect_counts else None

            summary_stats = {
                "total_prompts": len(prompts),
                "successful_analyses": len(successful_results),
                "failed_analyses": len(failed_indices),
                "average_score": round(sum(scores) / len(scores), 2),
                "min_score": min(scores),
                "max_score": max(scores),
                "total_defects": len(all_defect_ids),
                "unique_defects": len(set(all_defect_ids)),
                "most_common_defect": most_common_defect,
                "defect_distribution": defect_counts
            }
        else:
            summary_stats = {
                "total_prompts": len(prompts),
                "successful_analyses": 0,
                "failed_analyses": len(prompts),
                "error": "All analyses failed"
            }

        processing_time_ms = int((time.time() - start_time) * 1000)

        return {
            "results": results,
            "summary_stats": summary_stats,
            "metadata": {
                "total_prompts": len(prompts),
                "parallel_processing": parallel,
                "processing_time_ms": processing_time_ms,
                "failed_indices": failed_indices
            }
        }

    def _generate_summary(self, result: Dict[str, Any], task_type: str) -> str:
        """
        Generate a human-readable summary of the analysis

        Args:
            result: Raw analysis result from orchestrator
            task_type: Type of task being analyzed

        Returns:
            Human-readable summary string
        """
        score = result["overall_score"]
        defects = result["defects"]
        consensus = result["consensus"]

        # Determine quality level
        if score >= 9.0:
            quality = "excellent"
        elif score >= 7.0:
            quality = "good"
        elif score >= 5.0:
            quality = "moderate"
        elif score >= 3.0:
            quality = "poor"
        else:
            quality = "very poor"

        # Count defects by severity
        severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        for defect in defects:
            severity = defect.get("severity", "low")
            severity_counts[severity] = severity_counts.get(severity, 0) + 1

        # Build summary
        parts = []

        # Overall quality
        parts.append(f"This {task_type} prompt has {quality} quality (score: {score}/10).")

        # Defect summary
        if not defects:
            parts.append("No significant defects were detected.")
        else:
            defect_summary = []
            if severity_counts["critical"] > 0:
                defect_summary.append(f"{severity_counts['critical']} critical")
            if severity_counts["high"] > 0:
                defect_summary.append(f"{severity_counts['high']} high-severity")
            if severity_counts["medium"] > 0:
                defect_summary.append(f"{severity_counts['medium']} medium-severity")
            if severity_counts["low"] > 0:
                defect_summary.append(f"{severity_counts['low']} low-severity")

            parts.append(f"Found {len(defects)} defect(s): {', '.join(defect_summary)}.")

        # Consensus info
        if consensus >= 0.9:
            parts.append("Agents showed strong consensus on findings.")
        elif consensus >= 0.7:
            parts.append("Agents showed moderate consensus on findings.")
        else:
            parts.append("Agents showed some disagreement; review findings carefully.")

        # Top recommendation
        if defects and defects[0].get("remediation"):
            parts.append(f"Top priority: {defects[0]['remediation']}")

        return " ".join(parts)

    def get_defect_details(self, defect_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific defect type

        Args:
            defect_id: Defect ID (e.g., "D001")

        Returns:
            Defect definition or None if not found
        """
        from ..models import get_defect_by_id
        return get_defect_by_id(defect_id)


# Singleton instance
_analyzer = None


def get_analyzer() -> AnalyzerService:
    """Get or create singleton analyzer instance"""
    global _analyzer
    if _analyzer is None:
        _analyzer = AnalyzerService()
    return _analyzer


__all__ = ["AnalyzerService", "get_analyzer"]
