"""
PromptOptimizer Pro - Request Models
Pydantic models for API request validation
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List


class AnalyzeRequest(BaseModel):
    """
    Request to analyze a prompt for defects

    This is the main entry point for the multi-agent defect detection system.
    """
    prompt: str = Field(
        ...,
        min_length=10,
        max_length=50000,
        description="The prompt to analyze for defects"
    )
    task_type: str = Field(
        default="general",
        description="Type of task: code_generation, reasoning, creative_writing, etc."
    )
    domain: str = Field(
        default="general",
        description="Domain context: software_engineering, mathematics, science, etc."
    )
    provider: Optional[str] = Field(
        default=None,
        description="LLM provider: anthropic, groq, openai, gemini. Uses server default if not specified."
    )
    include_agent_breakdown: bool = Field(
        default=True,
        description="Include per-agent analysis results in response"
    )
    user_issues: Optional[List[str]] = Field(
        default=None,
        description="User-reported issues with their prompt (e.g., 'output too verbose', 'wrong format')"
    )

    @validator('prompt')
    def prompt_not_empty(cls, v):
        """Ensure prompt is not just whitespace"""
        if not v.strip():
            raise ValueError('Prompt cannot be empty or whitespace only')
        return v.strip()

    @validator('provider')
    def validate_provider(cls, v):
        """Validate LLM provider"""
        if v is None:
            return v
        valid = ["anthropic", "groq", "openai", "gemini"]
        v_lower = v.lower()
        if v_lower not in valid:
            raise ValueError(f"provider must be one of: {', '.join(valid)}")
        return v_lower

    @validator('task_type')
    def validate_task_type(cls, v):
        """Validate task_type is recognized"""
        valid_types = [
            "code_generation", "reasoning", "creative_writing",
            "information_extraction", "classification", "conversation",
            "summarization", "question_answering", "translation", "general"
        ]
        if v not in valid_types:
            # Allow custom types but log warning
            pass
        return v.lower()

    @validator('domain')
    def validate_domain(cls, v):
        """Validate domain is recognized"""
        valid_domains = [
            "software_engineering", "mathematics", "science", "business",
            "education", "healthcare", "legal", "creative", "general"
        ]
        if v not in valid_domains:
            # Allow custom domains but log warning
            pass
        return v.lower()

    @validator('user_issues')
    def validate_user_issues(cls, v):
        """Validate user issues are non-empty strings"""
        if v is None:
            return v
        validated = []
        for issue in v:
            if isinstance(issue, str) and issue.strip():
                validated.append(issue.strip())
        return validated if validated else None

    class Config:
        json_schema_extra = {
            "example": {
                "prompt": "Write a function to sort a list of numbers",
                "task_type": "code_generation",
                "domain": "software_engineering",
                "include_agent_breakdown": True,
                "user_issues": ["output is too verbose", "missing examples"]
            }
        }


class OptimizeRequest(BaseModel):
    """
    Request to optimize a prompt by applying techniques to fix detected defects

    This endpoint uses the technique registry to automatically improve prompts.
    """
    prompt: str = Field(
        ...,
        min_length=10,
        max_length=50000,
        description="The original prompt to optimize"
    )
    analysis: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Pre-computed analysis from /api/analyze (optional - will analyze if not provided)"
    )
    optimization_level: str = Field(
        default="balanced",
        description="Optimization aggressiveness: minimal, balanced, or aggressive"
    )
    max_techniques: int = Field(
        default=5,
        ge=1,
        le=10,
        description="Maximum number of techniques to apply"
    )
    preserve_intent: bool = Field(
        default=True,
        description="Preserve the original intent even if it means keeping some defects"
    )
    task_type: str = Field(
        default="general",
        description="Type of task: code_generation, reasoning, creative_writing, etc."
    )
    domain: str = Field(
        default="general",
        description="Domain context: software_engineering, mathematics, science, etc."
    )
    user_issues: Optional[List[str]] = Field(
        default=None,
        description="User-reported issues to prioritize during optimization"
    )

    @validator('optimization_level')
    def validate_optimization_level(cls, v):
        """Ensure optimization level is valid"""
        valid_levels = ["minimal", "balanced", "aggressive"]
        v_lower = v.lower()
        if v_lower not in valid_levels:
            raise ValueError(f"optimization_level must be one of: {', '.join(valid_levels)}")
        return v_lower

    @validator('analysis')
    def validate_analysis(cls, v):
        """Ensure analysis has required fields when provided"""
        if v is None:
            return v
        required_fields = ["defects", "overall_score"]
        for field in required_fields:
            if field not in v:
                raise ValueError(f"Analysis must contain '{field}' field")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "prompt": "Write code to sort numbers",
                "analysis": {
                    "defects": [{"id": "D001", "name": "Ambiguity"}],
                    "overall_score": 4.5
                },
                "optimization_level": "balanced",
                "max_techniques": 5,
                "preserve_intent": True
            }
        }


class TestRequest(BaseModel):
    """
    Request to A/B test original vs optimized prompt

    Runs both prompts multiple times and compares outputs statistically.
    """
    original_prompt: str = Field(
        ...,
        min_length=10,
        max_length=50000,
        description="The original unoptimized prompt"
    )
    optimized_prompt: str = Field(
        ...,
        min_length=10,
        max_length=50000,
        description="The optimized prompt to compare against"
    )
    test_input: str = Field(
        ...,
        min_length=1,
        max_length=10000,
        description="Input data to test both prompts with"
    )
    iterations: int = Field(
        default=5,
        ge=1,
        le=10,
        description="Number of test iterations per prompt"
    )
    evaluation_criteria: Optional[list] = Field(
        default=None,
        description="Custom evaluation criteria (if None, uses automated metrics)"
    )

    @validator('original_prompt', 'optimized_prompt')
    def prompts_not_empty(cls, v):
        """Ensure prompts are not whitespace"""
        if not v.strip():
            raise ValueError('Prompts cannot be empty or whitespace only')
        return v.strip()

    @validator('test_input')
    def test_input_not_empty(cls, v):
        """Ensure test input is not whitespace"""
        if not v.strip():
            raise ValueError('Test input cannot be empty or whitespace only')
        return v.strip()

    class Config:
        json_schema_extra = {
            "example": {
                "original_prompt": "Summarize this text",
                "optimized_prompt": "You are a summarization expert. Summarize the following text in 2-3 sentences, focusing on key points.",
                "test_input": "Long article text here...",
                "iterations": 5,
                "evaluation_criteria": None
            }
        }


class AdvancedOptimizeRequest(BaseModel):
    """
    Request for advanced optimization using DGEO, SHDT, or CDRAF strategies.

    Strategies:
    - standard: Default single-pass optimization
    - dgeo: Defect-Guided Evolutionary Optimization (population-based search)
    - shdt: Scored History with Defect Trajectories (iterative with causal learning)
    - cdraf: Critic-Driven Refinement with Agent Feedback (multi-agent critique loop)
    """
    prompt: str = Field(
        ...,
        min_length=10,
        max_length=50000,
        description="The original prompt to optimize"
    )
    analysis: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Pre-computed analysis results (optional, will analyze if not provided)"
    )
    strategy: str = Field(
        default="standard",
        description="Optimization strategy: standard, dgeo, shdt, or cdraf"
    )
    optimization_level: str = Field(
        default="balanced",
        description="Optimization aggressiveness: minimal, balanced, or aggressive"
    )
    max_techniques: int = Field(
        default=5,
        ge=1,
        le=10,
        description="Maximum number of techniques to apply (standard strategy)"
    )
    population_size: int = Field(
        default=5,
        ge=3,
        le=7,
        description="DGEO: Number of variants per generation"
    )
    generations: int = Field(
        default=3,
        ge=2,
        le=5,
        description="DGEO: Number of evolutionary generations"
    )
    max_iterations: int = Field(
        default=4,
        ge=2,
        le=6,
        description="SHDT: Maximum optimization iterations"
    )
    target_score: float = Field(
        default=8.0,
        ge=5.0,
        le=10.0,
        description="SHDT: Target score to stop optimization"
    )
    max_rounds: int = Field(
        default=2,
        ge=1,
        le=3,
        description="CDRAF: Maximum critique-refine rounds"
    )
    task_type: str = Field(
        default="general",
        description="Type of task"
    )
    domain: str = Field(
        default="general",
        description="Domain context"
    )
    provider: Optional[str] = Field(
        default=None,
        description="LLM provider: anthropic, groq, openai, gemini. Uses server default if not specified."
    )
    user_issues: Optional[List[str]] = Field(
        default=None,
        description="User-reported issues to prioritize during optimization"
    )

    @validator('provider')
    def validate_provider(cls, v):
        """Validate LLM provider"""
        if v is None:
            return v
        valid = ["anthropic", "groq", "openai", "gemini"]
        v_lower = v.lower()
        if v_lower not in valid:
            raise ValueError(f"provider must be one of: {', '.join(valid)}")
        return v_lower

    @validator('user_issues')
    def validate_user_issues_advanced(cls, v):
        """Validate user issues are non-empty strings"""
        if v is None:
            return v
        validated = []
        for issue in v:
            if isinstance(issue, str) and issue.strip():
                validated.append(issue.strip())
        return validated if validated else None

    @validator('strategy')
    def validate_strategy(cls, v):
        valid = ["standard", "dgeo", "shdt", "cdraf", "auto"]
        v_lower = v.lower()
        if v_lower not in valid:
            raise ValueError(f"strategy must be one of: {', '.join(valid)}")
        return v_lower

    @validator('optimization_level')
    def validate_opt_level(cls, v):
        valid = ["minimal", "balanced", "aggressive"]
        v_lower = v.lower()
        if v_lower not in valid:
            raise ValueError(f"optimization_level must be one of: {', '.join(valid)}")
        return v_lower

    class Config:
        json_schema_extra = {
            "example": {
                "prompt": "Write a function to sort numbers",
                "strategy": "dgeo",
                "optimization_level": "balanced",
                "task_type": "code_generation"
            }
        }


class BatchAnalyzeRequest(BaseModel):
    """
    Request to analyze multiple prompts in batch

    Useful for evaluating entire prompt libraries or datasets.
    """
    prompts: list = Field(
        ...,
        min_items=1,
        max_items=50,
        description="List of prompts to analyze"
    )
    task_type: str = Field(
        default="general",
        description="Task type (same for all prompts in batch)"
    )
    domain: str = Field(
        default="general",
        description="Domain context (same for all prompts in batch)"
    )
    parallel: bool = Field(
        default=True,
        description="Process prompts in parallel (faster but more resource intensive)"
    )

    @validator('prompts')
    def validate_prompts(cls, v):
        """Ensure all prompts are non-empty strings"""
        for i, prompt in enumerate(v):
            if not isinstance(prompt, str):
                raise ValueError(f"Prompt at index {i} must be a string")
            if not prompt.strip():
                raise ValueError(f"Prompt at index {i} cannot be empty")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "prompts": [
                    "Write a sorting function",
                    "Explain quantum computing",
                    "Create a user registration form"
                ],
                "task_type": "general",
                "domain": "general",
                "parallel": True
            }
        }


# Export all request models
__all__ = [
    "AnalyzeRequest",
    "OptimizeRequest",
    "AdvancedOptimizeRequest",
    "TestRequest",
    "BatchAnalyzeRequest"
]
