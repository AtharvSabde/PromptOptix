"""
PromptOptimizer Pro - Structure Agent
Specialized agent for detecting Structure & Formatting defects

Detects:
- D005: Poor Role/Responsibility Separation
- D006: Disorganization
- D007: Syntax Errors
- D008: Format Specification Issues
- D009: Information Overload
"""

from typing import Dict, Any
from .base_agent import BaseAgent
from ..prompts.agents_prompts import get_structure_agent_prompt


class StructureAgent(BaseAgent):
    """
    Agent focused on Structure & Formatting defects (D005-D009)

    This agent examines prompts for structural issues such as:
    - Poor organization and lack of logical flow
    - Mixed roles or responsibilities
    - Syntax errors in code/format specifications
    - Vague or missing output format requirements
    - Information overload
    """

    def __init__(self):
        """Initialize Structure Agent with its focus area and defect IDs"""
        super().__init__(
            name="StructureAgent",
            focus_area="structure_and_formatting",
            defect_ids=["D005", "D006", "D007", "D008", "D009"]
        )

    def get_detection_prompt(self, prompt: str) -> str:
        """
        Generate detection prompt for structure issues

        Args:
            prompt: The user's prompt to analyze

        Returns:
            Meta-prompt tailored for detecting structural defects
        """
        return get_structure_agent_prompt(prompt)


# Export Structure Agent
__all__ = ["StructureAgent"]
