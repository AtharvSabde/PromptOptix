"""
PromptOptimizer Pro - Agent Orchestrator
Coordinates multiple agents and aggregates results with consensus mechanism

This is the CORE INNOVATION of PromptOptimizer Pro:
- Runs 4 specialized agents in parallel (asyncio)
- Implements consensus voting (multiple agents = higher confidence)
- Deduplicates defects across agents
- Boosts confidence when agents agree
- Tracks disagreements for analysis
- Calculates weighted overall scores
"""

import asyncio
from typing import Dict, List, Any, Optional
from collections import defaultdict

from ..agents import ClarityAgent, StructureAgent, ContextAgent, SecurityAgent
from ..utils import get_logger
from ..utils.error_handlers import AgentOrchestrationError
from ..config import Config
from ..models.issue_registry import (
    match_user_issue,
    aggregate_defect_priorities,
    aggregate_suggested_techniques
)

logger = get_logger(__name__)


class AgentOrchestrator:
    """
    Coordinates multiple agents and aggregates results with consensus mechanism

    Key Features:
    1. Parallel Execution: All agents run simultaneously using asyncio
    2. Consensus Voting: Defects detected by multiple agents get higher confidence
    3. Deduplication: Same defect from multiple agents is merged
    4. Threshold Filtering: Only defects above consensus threshold are included
    5. Disagreement Tracking: Records where agents disagreed
    6. Weighted Scoring: Overall score is weighted average of all agent scores

    Architecture:
    User Prompt
        ↓
    AgentOrchestrator
        ↓
    [asyncio.gather - Parallel Execution]
        ↓
    ├── ClarityAgent → LLM → D001-D004
    ├── StructureAgent → LLM → D005-D009
    ├── ContextAgent → LLM → D010-D014
    └── SecurityAgent → LLM → D023-D028
        ↓
    Consensus Mechanism (voting + aggregation)
        ↓
    Unified Analysis Result
    """

    def __init__(self):
        """
        Initialize all agents

        Creates instances of all 4 specialized agents. Each agent
        will analyze prompts independently and in parallel.
        """
        self.agents = [
            ClarityAgent(),
            StructureAgent(),
            ContextAgent(),
            SecurityAgent()
        ]

        logger.info(
            f"AgentOrchestrator initialized with {len(self.agents)} agents",
            extra={
                "agents": [agent.name for agent in self.agents],
                "consensus_threshold": Config.CONSENSUS_THRESHOLD
            }
        )

    async def analyze_with_agents(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]] = None,
        user_issues: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Run all agents in parallel and aggregate results with consensus mechanism

        This is the main entry point for the multi-agent analysis system.

        Args:
            prompt: The prompt to analyze
            context: Additional context (task_type, domain, etc.)
            user_issues: Optional list of user-reported issues for priority boosting

        Returns:
            Aggregated analysis result:
            {
                "overall_score": 7.5,  # Weighted average of agent scores
                "defects": [  # Deduplicated, consensus-filtered defects
                    {
                        "id": "D001",
                        "name": "Ambiguity",
                        "confidence": 0.92,  # Boosted by multi-agent agreement
                        "consensus": 0.75,  # 3/4 agents detected it
                        "detected_by": ["ClarityAgent", "StructureAgent", "ContextAgent"],
                        ...
                    }
                ],
                "agent_results": {  # Per-agent breakdown
                    "ClarityAgent": {...},
                    "StructureAgent": {...},
                    ...
                },
                "consensus": 0.85,  # Overall agent agreement level
                "disagreements": [  # Defects below consensus threshold
                    {
                        "defect_id": "D005",
                        "consensus": 0.5,  # Only 2/4 agents detected it
                        "detected_by": ["StructureAgent", "SecurityAgent"],
                        "not_detected_by": ["ClarityAgent", "ContextAgent"]
                    }
                ],
                "metadata": {
                    "num_agents": 4,
                    "total_defects_raw": 12,  # Before deduplication
                    "total_defects_after_dedup": 8,  # After deduplication
                    "consensus_threshold": 0.7
                }
            }

        Raises:
            AgentOrchestrationError: If orchestration fails or all agents fail
        """
        if context is None:
            context = {}

        try:
            logger.info(
                "Starting multi-agent analysis",
                extra={
                    "prompt_length": len(prompt),
                    "num_agents": len(self.agents),
                    "context": context
                }
            )

            # Run all agents in parallel using asyncio.gather
            # This is the key to performance - all 4 LLM calls happen simultaneously
            agent_tasks = [
                agent.analyze(prompt, context)
                for agent in self.agents
            ]

            # Wait for all agents to complete (or fail)
            # return_exceptions=True means we get results even if some fail
            results = await asyncio.gather(*agent_tasks, return_exceptions=True)

            # Separate successful results from failures
            successful_results = []
            failed_agents = []

            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    agent_name = self.agents[i].name
                    logger.warning(
                        f"Agent {agent_name} failed",
                        extra={"error": str(result)}
                    )
                    failed_agents.append(agent_name)
                else:
                    successful_results.append(result)

            # Check if we have at least some successful results
            if not successful_results:
                raise AgentOrchestrationError(
                    message="All agents failed - cannot perform analysis",
                    details={
                        "failed_agents": failed_agents,
                        "num_agents": len(self.agents)
                    }
                )

            if failed_agents:
                logger.warning(
                    f"{len(failed_agents)} agent(s) failed, continuing with {len(successful_results)} successful agents",
                    extra={"failed_agents": failed_agents}
                )

            # Aggregate results with consensus mechanism
            # This is where the magic happens: consensus voting, deduplication, etc.
            task_type = context.get("task_type", "general")
            domain = context.get("domain", "general")
            aggregated = self._aggregate_results(
                successful_results,
                task_type=task_type,
                domain=domain,
                user_issues=user_issues
            )

            logger.info(
                "Multi-agent analysis complete",
                extra={
                    "overall_score": aggregated["overall_score"],
                    "total_defects": len(aggregated["defects"]),
                    "consensus": aggregated["consensus"],
                    "successful_agents": len(successful_results),
                    "failed_agents": len(failed_agents),
                    "user_issues_provided": bool(user_issues)
                }
            )

            return aggregated

        except AgentOrchestrationError:
            # Re-raise orchestration errors as-is
            raise

        except Exception as e:
            logger.error(f"Agent orchestration failed: {e}", exc_info=True)
            raise AgentOrchestrationError(
                message=f"Orchestration failed: {str(e)}",
                details={
                    "prompt_length": len(prompt),
                    "error_type": type(e).__name__
                }
            )

    def _aggregate_results(
        self,
        results: List[Dict[str, Any]],
        task_type: str = "general",
        domain: str = "general",
        user_issues: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Aggregate agent results with enhanced consensus voting mechanism

        This method implements the core consensus algorithm with enhancements:
        1. Group defects by ID (same defect from multiple agents)
        2. Calculate consensus score (% of agents that detected it)
        3. Confidence-weighted voting (higher confidence = more weight)
        4. Task-type based defect prioritization
        5. User issue integration for priority boosting
        6. Filter defects below consensus threshold
        7. Track disagreements
        8. Calculate weighted overall score

        Key Innovation:
        - If multiple agents detect same defect → higher confidence
        - Confidence-weighted scoring instead of simple average
        - Task-specific defect priorities (e.g., syntax errors for code)
        - User-reported issues boost related defect priorities

        Args:
            results: List of agent results (successful only)
            task_type: Type of task (code_generation, reasoning, etc.)
            domain: Domain context (software_engineering, healthcare, etc.)
            user_issues: Optional list of user-reported issues

        Returns:
            Aggregated result with consensus information
        """
        # Build agent capability map: which agents CAN detect each defect
        # This is critical because agents specialize in non-overlapping defect ranges
        # (ClarityAgent→D001-D004, StructureAgent→D005-D009, etc.)
        # Consensus must be relative to capable agents, not total agents
        agent_capability_map = {}
        for agent in self.agents:
            for defect_id in agent.defect_ids:
                if defect_id not in agent_capability_map:
                    agent_capability_map[defect_id] = set()
                agent_capability_map[defect_id].add(agent.name)

        # Group defects by ID
        defects_by_id = defaultdict(list)

        for result in results:
            for defect in result.get("defects", []):
                defects_by_id[defect["id"]].append({
                    "agent": result["agent"],
                    "confidence": defect["confidence"],
                    "evidence": defect.get("evidence", ""),
                    "explanation": defect.get("explanation", ""),
                    **defect
                })

        # Get task-type and domain priority boosts
        task_priorities = Config.TASK_DEFECT_PRIORITIES.get(task_type, {})
        domain_priorities = Config.DOMAIN_DEFECT_PRIORITIES.get(domain, {})

        # Get user issue priority boosts
        user_issue_boosts = {}
        user_issue_analysis = None
        if user_issues:
            user_issue_boosts = aggregate_defect_priorities(user_issues)
            suggested_techniques = aggregate_suggested_techniques(user_issues)
            user_issue_analysis = {
                "user_issues": user_issues,
                "matched_defect_boosts": user_issue_boosts,
                "suggested_techniques": suggested_techniques
            }

        # Calculate consensus for each defect
        aggregated_defects = []
        disagreements = []
        num_agents = len(results)

        for defect_id, detections in defects_by_id.items():
            num_detections = len(detections)

            # Consensus score = percentage of CAPABLE agents that detected this defect
            # Since agents specialize (ClarityAgent only checks D001-D004, etc.),
            # we calculate consensus relative to agents that CAN detect this defect
            num_capable = len(agent_capability_map.get(defect_id, set()))
            if num_capable == 0:
                # Unknown defect ID - fall back to total agents
                num_capable = num_agents
            consensus_score = num_detections / num_capable

            # ENHANCED: Confidence-weighted average instead of simple average
            # Higher confidence detections have more weight
            total_weight = sum(d["confidence"] for d in detections)
            if total_weight > 0:
                weighted_confidence = sum(
                    d["confidence"] ** 2 for d in detections  # Square for emphasis
                ) / total_weight
            else:
                weighted_confidence = sum(d["confidence"] for d in detections) / num_detections

            # Boost confidence if multiple agents agree
            confidence_boost = 1 + 0.1 * (num_detections - 1)
            final_confidence = min(1.0, weighted_confidence * confidence_boost)

            # ENHANCED: Apply task-type priority boost
            task_boost = task_priorities.get(defect_id, 1.0)
            if task_boost > 1.0:
                final_confidence = min(1.0, final_confidence * task_boost)

            # ENHANCED: Apply domain priority boost
            domain_boost = domain_priorities.get(defect_id, 1.0)
            if domain_boost > 1.0:
                final_confidence = min(1.0, final_confidence * domain_boost)

            # ENHANCED: Apply user issue priority boost
            user_boost = user_issue_boosts.get(defect_id, 1.0)
            if user_boost > 1.0:
                final_confidence = min(1.0, final_confidence * user_boost)

            # Take the first detection and enrich it with consensus info
            primary_detection = detections[0].copy()
            primary_detection["confidence"] = round(final_confidence, 2)
            primary_detection["consensus"] = round(consensus_score, 2)
            primary_detection["detected_by"] = [d["agent"] for d in detections]

            # Track boost information
            boosts_applied = []
            if task_boost > 1.0:
                boosts_applied.append(f"task:{task_type}(x{task_boost:.1f})")
            if domain_boost > 1.0:
                boosts_applied.append(f"domain:{domain}(x{domain_boost:.1f})")
            if user_boost > 1.0:
                boosts_applied.append(f"user_issue(x{user_boost:.1f})")
            if boosts_applied:
                primary_detection["priority_boosts"] = boosts_applied

            # Combine evidence from all agents
            all_evidence = [d["evidence"] for d in detections if d.get("evidence")]
            if all_evidence:
                primary_detection["evidence"] = " | ".join(all_evidence[:3])

            # Check if defect meets consensus threshold
            if consensus_score >= Config.CONSENSUS_THRESHOLD:
                aggregated_defects.append(primary_detection)
            else:
                disagreements.append({
                    "defect_id": defect_id,
                    "defect_name": primary_detection.get("name", "Unknown"),
                    "consensus": round(consensus_score, 2),
                    "detected_by": [d["agent"] for d in detections],
                    "not_detected_by": [
                        r["agent"] for r in results
                        if r["agent"] not in [d["agent"] for d in detections]
                    ],
                    "reason": f"Below consensus threshold ({Config.CONSENSUS_THRESHOLD})"
                })

        # Sort defects by severity and confidence (most critical first)
        severity_order = {"critical": 4, "high": 3, "medium": 2, "low": 1}
        aggregated_defects.sort(
            key=lambda d: (
                severity_order.get(d.get("severity", "low"), 0),
                d.get("confidence", 0)
            ),
            reverse=True
        )

        # ENHANCED: Confidence-weighted overall score
        agent_scores = [r["score"] for r in results]
        agent_confidences = [
            sum(d.get("confidence", 0.5) for d in r.get("defects", [])) / max(len(r.get("defects", [])), 1)
            for r in results
        ]

        # If all agents have defects with confidence, use weighted average
        total_confidence = sum(agent_confidences)
        if total_confidence > 0:
            overall_score = sum(
                score * conf for score, conf in zip(agent_scores, agent_confidences)
            ) / total_confidence
        else:
            overall_score = sum(agent_scores) / len(agent_scores)

        # Calculate overall consensus
        if defects_by_id:
            consensus_values = [
                len(detections) / num_agents
                for detections in defects_by_id.values()
            ]
            overall_consensus = sum(consensus_values) / len(consensus_values)
        else:
            overall_consensus = 1.0

        # Build agent results dictionary
        agent_results_dict = {r["agent"]: r for r in results}

        result = {
            "overall_score": round(overall_score, 2),
            "defects": aggregated_defects,
            "agent_results": agent_results_dict,
            "consensus": round(overall_consensus, 2),
            "disagreements": disagreements,
            "metadata": {
                "num_agents": num_agents,
                "total_defects_raw": sum(len(r.get("defects", [])) for r in results),
                "total_defects_after_dedup": len(aggregated_defects),
                "total_disagreements": len(disagreements),
                "consensus_threshold": Config.CONSENSUS_THRESHOLD,
                "task_type": task_type,
                "domain": domain,
                "priority_boosts_applied": bool(task_priorities or domain_priorities or user_issue_boosts)
            }
        }

        # Include user issue analysis if provided
        if user_issue_analysis:
            result["user_issue_analysis"] = user_issue_analysis

        return result


    async def analyze_with_self_consistency(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]] = None,
        user_issues: Optional[List[str]] = None,
        num_passes: int = 3
    ) -> Dict[str, Any]:
        """
        Run analysis multiple times and aggregate for consistency

        This implements self-consistency from the research paper:
        - Run multiple analysis passes
        - Compare results across passes
        - Boost confidence for consistently detected defects
        - Flag inconsistent detections

        Args:
            prompt: The prompt to analyze
            context: Additional context (task_type, domain, etc.)
            user_issues: Optional list of user-reported issues
            num_passes: Number of analysis passes (default: 3)

        Returns:
            Self-consistency aggregated result with confidence scores
        """
        if context is None:
            context = {}

        logger.info(
            f"Starting self-consistency analysis with {num_passes} passes",
            extra={"prompt_length": len(prompt), "num_passes": num_passes}
        )

        # Run multiple analysis passes
        all_results = []
        for pass_num in range(num_passes):
            try:
                result = await self.analyze_with_agents(prompt, context, user_issues)
                all_results.append(result)
                logger.debug(f"Self-consistency pass {pass_num + 1} complete")
            except Exception as e:
                logger.warning(f"Self-consistency pass {pass_num + 1} failed: {e}")
                continue

        if not all_results:
            raise AgentOrchestrationError(
                message="All self-consistency passes failed",
                details={"num_passes": num_passes}
            )

        # Aggregate results across passes
        return self._aggregate_self_consistency_results(all_results)

    def _aggregate_self_consistency_results(
        self,
        all_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Aggregate results from multiple analysis passes for self-consistency

        Args:
            all_results: List of results from multiple passes

        Returns:
            Aggregated result with consistency scores
        """
        num_passes = len(all_results)
        defect_counts = defaultdict(int)
        defect_confidences = defaultdict(list)
        defect_data = {}

        # Count defect occurrences across passes
        for result in all_results:
            for defect in result.get("defects", []):
                defect_id = defect["id"]
                defect_counts[defect_id] += 1
                defect_confidences[defect_id].append(defect["confidence"])
                if defect_id not in defect_data:
                    defect_data[defect_id] = defect.copy()

        # Calculate consistency score for each defect
        consistent_defects = []
        inconsistent_defects = []

        for defect_id, count in defect_counts.items():
            consistency = count / num_passes
            avg_confidence = sum(defect_confidences[defect_id]) / len(defect_confidences[defect_id])

            defect = defect_data[defect_id].copy()
            defect["consistency_score"] = round(consistency, 2)
            defect["detection_count"] = count
            defect["num_passes"] = num_passes

            # Boost confidence for consistently detected defects
            # Defects detected in all passes get confidence boost
            if consistency >= 0.5:  # Detected in majority of passes
                boosted_confidence = min(1.0, avg_confidence * (1 + 0.2 * (consistency - 0.5)))
                defect["confidence"] = round(boosted_confidence, 2)
                defect["consistency_status"] = "consistent"
                consistent_defects.append(defect)
            else:
                defect["confidence"] = round(avg_confidence, 2)
                defect["consistency_status"] = "inconsistent"
                inconsistent_defects.append(defect)

        # Sort by consistency then confidence
        consistent_defects.sort(
            key=lambda d: (d["consistency_score"], d["confidence"]),
            reverse=True
        )

        # Calculate overall metrics
        all_scores = [r["overall_score"] for r in all_results]
        avg_score = sum(all_scores) / len(all_scores)
        score_variance = sum((s - avg_score) ** 2 for s in all_scores) / len(all_scores)

        # Self-consistency score (how consistent were the results)
        if consistent_defects:
            self_consistency_score = sum(
                d["consistency_score"] for d in consistent_defects
            ) / len(consistent_defects)
        else:
            self_consistency_score = 1.0  # Perfect consistency if no defects

        return {
            "overall_score": round(avg_score, 2),
            "score_variance": round(score_variance, 4),
            "defects": consistent_defects,
            "inconsistent_defects": inconsistent_defects,
            "self_consistency_score": round(self_consistency_score, 2),
            "num_passes": num_passes,
            "consensus": all_results[0].get("consensus", 1.0) if all_results else 1.0,
            "metadata": {
                "analysis_type": "self_consistency",
                "num_passes": num_passes,
                "consistent_defects_count": len(consistent_defects),
                "inconsistent_defects_count": len(inconsistent_defects),
                "score_stability": "high" if score_variance < 0.5 else "medium" if score_variance < 1.0 else "low"
            }
        }


# Singleton instance
_orchestrator = None


def get_orchestrator() -> AgentOrchestrator:
    """
    Get or create the singleton orchestrator instance

    Using singleton pattern ensures we don't create multiple instances
    of agents unnecessarily.

    Returns:
        AgentOrchestrator instance
    """
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = AgentOrchestrator()
    return _orchestrator


# Export orchestrator
__all__ = ["AgentOrchestrator", "get_orchestrator"]
