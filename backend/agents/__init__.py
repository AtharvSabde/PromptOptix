"""
Agents package - multi-agent defect detection system

This package contains the core innovation of PromptOptimizer Pro:
a multi-agent system where specialized agents detect different categories
of prompt defects in parallel, then aggregate results with consensus voting.

Available agents:
- BaseAgent: Abstract base class for all agents
- ClarityAgent: Detects specification & intent defects (D001-D004)
- StructureAgent: Detects structure & formatting defects (D005-D009)
- ContextAgent: Detects context & memory defects (D010-D014)
- SecurityAgent: Detects security & safety defects (D023-D028)

Usage:
    from backend.agents import ClarityAgent, StructureAgent

    clarity = ClarityAgent()
    result = await clarity.analyze("Write code", {})
"""

from .base_agent import BaseAgent
from .clarity_agent import ClarityAgent
from .structure_agent import StructureAgent
from .context_agent import ContextAgent
from .security_agent import SecurityAgent

__all__ = [
    "BaseAgent",
    "ClarityAgent",
    "StructureAgent",
    "ContextAgent",
    "SecurityAgent"
]
