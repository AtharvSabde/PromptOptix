"""
PromptOptimizer Pro - Security Agent
Specialized agent for detecting Security & Safety defects

Detects:
- D023: Prompt Injection Vulnerabilities
- D024: Jailbreaking Attempts
- D025: Policy Violations
- D026: Malicious Content Requests
- D027: Privacy Leakage Risk
- D028: Data Leakage Risk
"""

from typing import Dict, Any
from .base_agent import BaseAgent
from ..prompts.agents_prompts import get_security_agent_prompt


class SecurityAgent(BaseAgent):
    """
    Agent focused on Security & Safety defects (D023-D028)

    This agent examines prompts for security issues such as:
    - Prompt injection vulnerabilities (undelimited user input)
    - Jailbreaking attempts or attempts to bypass safety guidelines
    - Requests for prohibited or policy-violating content
    - Malicious content generation requests
    - Privacy risks (exposed PII, personal data)
    - Data leakage risks (credentials, API keys, proprietary info)
    """

    def __init__(self):
        """Initialize Security Agent with its focus area and defect IDs"""
        super().__init__(
            name="SecurityAgent",
            focus_area="security_and_safety",
            defect_ids=["D023", "D024", "D025", "D026", "D027", "D028"]
        )

    def get_detection_prompt(self, prompt: str) -> str:
        """
        Generate detection prompt for security issues

        Args:
            prompt: The user's prompt to analyze

        Returns:
            Meta-prompt tailored for detecting security defects
        """
        return get_security_agent_prompt(prompt)


# Export Security Agent
__all__ = ["SecurityAgent"]
