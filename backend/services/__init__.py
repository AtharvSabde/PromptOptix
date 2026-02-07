"""
Services package - business logic and orchestration

This package contains the core services of PromptOptimizer Pro:
- LLMService: Abstracts LLM API calls (Anthropic Claude, Groq)
- AgentOrchestrator: Coordinates multi-agent defect detection with consensus voting
- AnalyzerService: High-level prompt analysis orchestration
- OptimizerService: Applies techniques to fix detected defects
- EvaluatorService: Evaluates optimization effectiveness with NLP & LLM metrics
- TesterService: A/B testing for original vs optimized prompts
- IssueMatcherService: Matches user-reported issues to defects

Usage:
    from backend.services import get_llm_service, get_analyzer, get_evaluator

    llm = get_llm_service()
    analyzer = get_analyzer()

    result = await analyzer.analyze(
        prompt="Write code to sort numbers",
        task_type="code_generation"
    )
"""

from .llm_service import LLMService, get_llm_service
from .analyzer_service import AnalyzerService, get_analyzer
from .evaluator_service import EvaluatorService, get_evaluator
from .tester_service import TesterService, get_tester
from .issue_matcher_service import IssueMatcherService, get_issue_matcher

# Note: agent_orchestrator and optimizer_service are not imported here to avoid circular imports
# Import them directly when needed:
#   from backend.services.agent_orchestrator import get_orchestrator
#   from backend.services.optimizer_service import get_optimizer

__all__ = [
    "LLMService",
    "get_llm_service",
    "AnalyzerService",
    "get_analyzer",
    "EvaluatorService",
    "get_evaluator",
    "TesterService",
    "get_tester",
    "IssueMatcherService",
    "get_issue_matcher"
]
