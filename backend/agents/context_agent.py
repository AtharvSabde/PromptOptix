"""
PromptOptimizer Pro - Context Agent
Specialized agent for detecting Context & Memory defects

Detects:
- D010: Context Overflow
- D011: Missing Context
- D012: Irrelevant Information
- D013: Misreferencing
- D014: Forgotten Instructions
"""

from typing import Dict, Any
from .base_agent import BaseAgent
from ..prompts.agents_prompts import get_context_agent_prompt


class ContextAgent(BaseAgent):
    """
    Agent focused on Context & Memory defects (D010-D014)

    This agent examines prompts for context-related issues such as:
    - Too much or too little context
    - Missing definitions or background information
    - Irrelevant information that distracts from the task
    - Ambiguous references or pronouns
    - Instructions that contradict earlier parts of the prompt
    """

    def __init__(self):
        """Initialize Context Agent with its focus area and defect IDs"""
        super().__init__(
            name="ContextAgent",
            focus_area="context_and_memory",
            defect_ids=["D010", "D011", "D012", "D013", "D014"]
        )

    def get_detection_prompt(self, prompt: str) -> str:
        """
        Generate detection prompt for context issues

        Args:
            prompt: The user's prompt to analyze

        Returns:
            Meta-prompt tailored for detecting context defects
        """
        return get_context_agent_prompt(prompt)


# Export Context Agent
__all__ = ["ContextAgent"]
