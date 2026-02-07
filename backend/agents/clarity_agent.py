"""
PromptOptimizer Pro - Clarity Agent
Specialized agent for detecting Specification & Intent defects

Detects:
- D001: Ambiguity
- D002: Underspecification
- D003: Conflicting Requirements
- D004: Intent Misalignment
"""

from typing import Dict, Any
from .base_agent import BaseAgent
from ..prompts.agents_prompts import get_clarity_agent_prompt


class ClarityAgent(BaseAgent):
    """
    Agent focused on Specification & Intent defects (D001-D004)

    This agent examines prompts for clarity issues such as:
    - Vague or ambiguous terms
    - Missing specifications or constraints
    - Contradictory requirements
    - Misalignment between intent and request
    """

    def __init__(self):
        """Initialize Clarity Agent with its focus area and defect IDs"""
        super().__init__(
            name="ClarityAgent",
            focus_area="specification_and_intent",
            defect_ids=["D001", "D002", "D003", "D004"]
        )

    def get_detection_prompt(self, prompt: str) -> str:
        """
        Generate detection prompt for clarity issues

        Args:
            prompt: The user's prompt to analyze

        Returns:
            Meta-prompt tailored for detecting clarity defects
        """
        return get_clarity_agent_prompt(prompt)


# Export Clarity Agent
__all__ = ["ClarityAgent"]
