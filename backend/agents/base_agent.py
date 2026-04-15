"""
PromptOptimizer Pro - Base Agent
Abstract base class for all defect detection agents

Each specialized agent inherits from this class and implements
defect detection for a specific category of prompt issues.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
import asyncio

from ..utils import get_logger
from ..utils.error_handlers import DefectDetectionError
from ..services.llm_service import get_llm_service
from ..models.defect_taxonomy import DefectDefinition, get_defect_by_id


def _stringify_field(value: Any) -> str:
    """Normalize LLM fields that may come back as strings, lists, or objects."""
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return " | ".join(_stringify_field(item) for item in value if item is not None)
    if isinstance(value, dict):
        return " | ".join(f"{k}: {_stringify_field(v)}" for k, v in value.items())
    return str(value)


def _coerce_float(value: Any, default: float) -> float:
    """Convert possibly-missing numeric fields from model output safely."""
    if value is None:
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


class BaseAgent(ABC):
    """
    Abstract base class for all defect detection agents

    Each agent specializes in detecting a specific category of defects
    by using LLMs with specialized meta-prompts.

    Architecture:
    1. Agent receives a prompt to analyze
    2. Agent generates a meta-prompt tailored to its focus area
    3. Meta-prompt is sent to LLM
    4. LLM returns JSON with detected defects
    5. Agent enriches defects with taxonomy information
    6. Agent returns standardized analysis result
    """

    def __init__(self, name: str, focus_area: str, defect_ids: List[str]):
        """
        Initialize agent

        Args:
            name: Agent name (e.g., "ClarityAgent")
            focus_area: Focus area description (e.g., "specification_and_intent")
            defect_ids: List of defect IDs this agent detects (e.g., ["D001", "D002"])
        """
        self.name = name
        self.focus_area = focus_area
        self.defect_ids = defect_ids
        self.logger = get_logger(name)
        self.llm_service = get_llm_service()

        self.logger.info(
            f"Initialized {name}",
            extra={
                "focus_area": focus_area,
                "num_defects": len(defect_ids),
                "defect_ids": defect_ids
            }
        )

    @abstractmethod
    def get_detection_prompt(self, prompt: str) -> str:
        """
        Generate meta-prompt for LLM to detect defects

        This method must be implemented by each specialized agent to provide
        a meta-prompt tailored to its defect detection focus area.

        Args:
            prompt: The user's prompt to analyze

        Returns:
            Meta-prompt string to send to the LLM
        """
        pass

    async def analyze(self, prompt: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze prompt for defects in this agent's focus area

        This is the main entry point for agent analysis. It:
        1. Validates input
        2. Generates detection meta-prompt
        3. Calls LLM asynchronously
        4. Parses and enriches response
        5. Returns standardized result

        Args:
            prompt: The prompt to analyze
            context: Additional context (task_type, domain, etc.)

        Returns:
            Analysis result dictionary:
            {
                "agent": self.name,
                "focus_area": self.focus_area,
                "defects": [
                    {
                        "id": "D001",
                        "name": "Ambiguity",
                        "category": "specification_and_intent",
                        "severity": "high",
                        "confidence": 0.85,
                        "description": "...",
                        "evidence": "...",
                        "explanation": "...",
                        "remediation": "..."
                    }
                ],
                "score": 7.5,  # 0-10
                "confidence": 0.80,
                "summary": "brief summary",
                "metadata": {
                    "provider": "anthropic",
                    "model": "claude-sonnet-4",
                    "usage": {...},
                    "cost": {...}
                }
            }

        Raises:
            DefectDetectionError: If analysis fails
        """
        try:
            # Validate input
            if not prompt or not prompt.strip():
                raise DefectDetectionError(
                    agent=self.name,
                    details={"error": "Prompt cannot be empty"}
                )

            self.logger.info(
                f"{self.name} starting analysis",
                extra={
                    "prompt_length": len(prompt),
                    "context": context
                }
            )

            # Generate detection prompt
            detection_prompt = self.get_detection_prompt(prompt)

            # Call LLM asynchronously (use asyncio.to_thread for sync LLM service)
            # This allows parallel execution of multiple agents
            # Pass provider from context if specified by user
            provider = context.get("provider") if context else None
            result = await asyncio.to_thread(
                self.llm_service.call_with_json_response,
                prompt=detection_prompt,
                system_prompt="You are an expert prompt defect detection system. Return only valid JSON.",
                temperature=0.3,
                max_tokens=4096,
                required_fields=["defects", "overall_score"],
                default={"defects": [], "overall_score": 5.0, "analysis_summary": ""},
                field_defaults={"defects": [], "overall_score": 5.0, "analysis_summary": ""},
                provider=provider
            )

            # Parse response
            parsed = result["parsed_response"]

            # Handle case where LLM returns a list instead of a dict
            if isinstance(parsed, list):
                self.logger.warning(f"{self.name}: LLM returned list instead of dict, wrapping")
                parsed = {"defects": parsed, "overall_score": 5.0}
            elif not isinstance(parsed, dict):
                self.logger.warning(f"{self.name}: LLM returned {type(parsed).__name__}, using empty result")
                parsed = {"defects": [], "overall_score": 5.0}

            # Validate response structure
            if "defects" not in parsed:
                self.logger.warning(f"{self.name}: LLM response missing 'defects' field")
                parsed["defects"] = []

            if "overall_score" not in parsed:
                self.logger.warning(f"{self.name}: LLM response missing 'overall_score' field")
                parsed["overall_score"] = 5.0
            elif parsed.get("overall_score") is None:
                self.logger.warning(f"{self.name}: LLM response returned null overall_score")
                parsed["overall_score"] = 5.0

            # Enrich defects with taxonomy information
            enriched_defects = []
            for defect in parsed.get("defects", []):
                try:
                    if not isinstance(defect, dict):
                        self.logger.warning(f"{self.name}: Defect payload was {type(defect).__name__}, skipping")
                        continue

                    defect_id = defect.get("id")
                    if not defect_id:
                        self.logger.warning(f"{self.name}: Defect missing ID, skipping")
                        continue

                    # Get full defect definition from taxonomy
                    defect_def = get_defect_by_id(defect_id)

                    if defect_def:
                        # Merge LLM-detected info with taxonomy definition
                        enriched_defects.append({
                            "id": defect_id,
                            "name": defect_def.name,
                            "category": defect_def.category.value,
                            "severity": defect_def.severity.value,
                            "confidence": _coerce_float(defect.get("confidence", 0.7), 0.7),
                            "description": defect_def.description,
                            "evidence": _stringify_field(defect.get("evidence", "")),
                            "explanation": _stringify_field(defect.get("explanation", "")),
                            "remediation": defect_def.remediation
                        })
                    else:
                        self.logger.warning(
                            f"{self.name}: Unknown defect ID {defect_id}, skipping"
                        )

                except Exception as e:
                    self.logger.error(f"{self.name}: Error enriching defect: {e}")
                    continue

            # Calculate overall confidence
            overall_confidence = self._calculate_confidence(enriched_defects)

            self.logger.info(
                f"{self.name} completed analysis",
                extra={
                    "defects_found": len(enriched_defects),
                    "score": parsed.get("overall_score", 0),
                    "confidence": overall_confidence
                }
            )

            # Return standardized result
            return {
                "agent": self.name,
                "focus_area": self.focus_area,
                "defects": enriched_defects,
                "score": _coerce_float(parsed.get("overall_score", 5.0), 5.0),
                "confidence": overall_confidence,
                "summary": _stringify_field(parsed.get("analysis_summary", f"{self.name} analysis complete")),
                "metadata": result["metadata"]
            }

        except DefectDetectionError:
            # Re-raise DefectDetectionError as-is
            raise

        except Exception as e:
            # Wrap other exceptions in DefectDetectionError
            self.logger.error(f"{self.name} analysis failed: {e}", exc_info=True)
            raise DefectDetectionError(
                agent=self.name,
                details={
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "prompt_length": len(prompt) if prompt else 0
                }
            )

    def _calculate_confidence(self, defects: List[Dict]) -> float:
        """
        Calculate overall confidence from defect confidences

        Args:
            defects: List of enriched defect dictionaries

        Returns:
            Overall confidence score (0.0-1.0)
        """
        if not defects:
            # High confidence when no defects found
            return 0.9

        # Average confidence across all detected defects
        total_confidence = sum(d["confidence"] for d in defects)
        return round(total_confidence / len(defects), 2)

    def __repr__(self) -> str:
        """String representation of agent"""
        return f"{self.name}(focus={self.focus_area}, defects={len(self.defect_ids)})"


# Export base agent
__all__ = ["BaseAgent"]
