"""
PromptOptimizer Pro - Response Models
Pydantic models for API responses
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional


class DefectResponse(BaseModel):
    """
    Individual defect detected in a prompt

    Represents a single defect found by one or more agents during analysis.
    """
    id: str = Field(
        ...,
        description="Defect ID from taxonomy (D001-D028)"
    )
    name: str = Field(
        ...,
        description="Human-readable defect name"
    )
    category: str = Field(
        ...,
        description="Defect category (specification_and_intent, structure_and_formatting, etc.)"
    )
    severity: str = Field(
        ...,
        description="Severity level: critical, high, medium, or low"
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence score (0.0-1.0) - boosted when multiple agents agree"
    )
    consensus: Optional[float] = Field(
        None,
        ge=0.0,
        le=1.0,
        description="Percentage of agents that detected this defect"
    )
    description: str = Field(
        ...,
        description="Explanation of what this defect means"
    )
    evidence: str = Field(
        ...,
        description="Specific text from the prompt showing the defect"
    )
    explanation: Optional[str] = Field(
        None,
        description="Why this is a defect and how it impacts quality"
    )
    remediation: str = Field(
        ...,
        description="How to fix this defect"
    )
    detected_by: List[str] = Field(
        ...,
        description="List of agents that detected this defect"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "id": "D001",
                "name": "Ambiguity",
                "category": "specification_and_intent",
                "severity": "high",
                "confidence": 0.92,
                "consensus": 0.75,
                "description": "The prompt contains vague or ambiguous terms",
                "evidence": "Write code to make it better",
                "explanation": "Terms like 'better' are subjective and ambiguous",
                "remediation": "Replace vague terms with specific, measurable criteria",
                "detected_by": ["ClarityAgent", "StructureAgent", "ContextAgent"]
            }
        }


class AgentResult(BaseModel):
    """
    Individual agent's analysis result

    Used in the agent_results breakdown to show what each agent found.
    """
    agent: str = Field(..., description="Agent name")
    focus_area: str = Field(..., description="Agent's focus area")
    defects: List[DefectResponse] = Field(..., description="Defects found by this agent")
    score: float = Field(..., ge=0.0, le=10.0, description="Quality score from this agent")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Agent's overall confidence")
    summary: str = Field(..., description="Agent's summary of findings")

    class Config:
        json_schema_extra = {
            "example": {
                "agent": "ClarityAgent",
                "focus_area": "specification_and_intent",
                "defects": [],
                "score": 7.5,
                "confidence": 0.85,
                "summary": "Prompt has minor ambiguity but overall intent is clear"
            }
        }


class AnalysisResponse(BaseModel):
    """
    Response from prompt analysis

    This is the main output of the multi-agent defect detection system.
    """
    overall_score: float = Field(
        ...,
        ge=0.0,
        le=10.0,
        description="Overall quality score (0=many defects, 10=perfect)"
    )
    defects: List[DefectResponse] = Field(
        ...,
        description="List of detected defects (deduplicated and consensus-filtered)"
    )
    consensus: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Overall agent agreement level (1.0=perfect consensus)"
    )
    agent_results: Optional[Dict[str, Dict[str, Any]]] = Field(
        None,
        description="Per-agent breakdown of results (optional)"
    )
    disagreements: Optional[List[Dict[str, Any]]] = Field(
        None,
        description="Defects where agents disagreed (below consensus threshold)"
    )
    summary: str = Field(
        ...,
        description="Human-readable summary of the analysis"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata (token usage, cost, processing time, etc.)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "overall_score": 6.5,
                "defects": [
                    {
                        "id": "D002",
                        "name": "Underspecification",
                        "severity": "high",
                        "confidence": 0.88,
                        "detected_by": ["ClarityAgent", "StructureAgent"]
                    }
                ],
                "consensus": 0.82,
                "agent_results": {},
                "disagreements": [],
                "summary": "Prompt has 3 significant defects requiring attention",
                "metadata": {
                    "num_agents": 4,
                    "processing_time_ms": 2345,
                    "total_cost": 0.0023
                }
            }
        }


class TechniqueApplicationResponse(BaseModel):
    """
    A technique applied to fix defects

    Represents one optimization technique applied to the prompt.
    """
    technique_id: str = Field(
        ...,
        description="Technique ID (T001-T041)"
    )
    technique_name: str = Field(
        ...,
        description="Human-readable technique name"
    )
    target_defects: List[str] = Field(
        ...,
        description="List of defect IDs this technique addresses"
    )
    modification: str = Field(
        ...,
        description="Description of what changed in the prompt"
    )
    before_snippet: Optional[str] = Field(
        None,
        description="Snippet of prompt before applying technique"
    )
    after_snippet: Optional[str] = Field(
        None,
        description="Snippet of prompt after applying technique"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "technique_id": "T001",
                "technique_name": "Role Prompting",
                "target_defects": ["D002", "D005"],
                "modification": "Added expert role specification at the beginning",
                "before_snippet": "Write a function...",
                "after_snippet": "You are an expert Python developer. Write a function..."
            }
        }


class OptimizationResponse(BaseModel):
    """
    Response from prompt optimization

    Contains both the original and optimized prompts, plus analysis of improvements.
    """
    original_prompt: str = Field(
        ...,
        description="The original unoptimized prompt"
    )
    optimized_prompt: str = Field(
        ...,
        description="The improved prompt after applying techniques"
    )
    techniques_applied: List[TechniqueApplicationResponse] = Field(
        ...,
        description="List of techniques that were applied"
    )
    improvement_score: float = Field(
        ...,
        ge=0.0,
        le=10.0,
        description="Estimated improvement in quality (difference between before and after scores)"
    )
    before_analysis: AnalysisResponse = Field(
        ...,
        description="Analysis of the original prompt"
    )
    after_analysis: AnalysisResponse = Field(
        ...,
        description="Analysis of the optimized prompt"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata (token usage, cost, processing time)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "original_prompt": "Write code to sort numbers",
                "optimized_prompt": "You are an expert Python developer. Write a function that takes a list of integers and returns them sorted in ascending order. Include type hints and a docstring.",
                "techniques_applied": [
                    {"technique_id": "T001", "technique_name": "Role Prompting"}
                ],
                "improvement_score": 3.5,
                "before_analysis": {"overall_score": 4.5},
                "after_analysis": {"overall_score": 8.0},
                "metadata": {"total_cost": 0.0045}
            }
        }


class TestIteration(BaseModel):
    """
    Single test iteration result

    Represents one run of a prompt with test input.
    """
    iteration: int = Field(..., description="Iteration number")
    output: str = Field(..., description="Generated output")
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Metadata for this iteration (tokens, latency, etc.)"
    )


class TestResponse(BaseModel):
    """
    Response from A/B testing

    Compares original vs optimized prompt across multiple iterations.
    """
    original_results: List[TestIteration] = Field(
        ...,
        description="Results from testing the original prompt"
    )
    optimized_results: List[TestIteration] = Field(
        ...,
        description="Results from testing the optimized prompt"
    )
    winner: str = Field(
        ...,
        description="Which prompt performed better: 'original', 'optimized', or 'tie'"
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Statistical confidence in the winner determination"
    )
    metrics: Dict[str, float] = Field(
        ...,
        description="Comparison metrics (BLEU, ROUGE, quality scores, etc.)"
    )
    summary: str = Field(
        ...,
        description="Human-readable summary of test results"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "original_results": [],
                "optimized_results": [],
                "winner": "optimized",
                "confidence": 0.87,
                "metrics": {
                    "quality_improvement": 0.23,
                    "consistency_improvement": 0.15
                },
                "summary": "Optimized prompt produced more consistent and higher quality outputs",
                "metadata": {"total_iterations": 10}
            }
        }


class BatchAnalysisResponse(BaseModel):
    """
    Response from batch analysis

    Contains analysis results for multiple prompts.
    """
    results: List[AnalysisResponse] = Field(
        ...,
        description="List of analysis results, one per prompt"
    )
    summary_stats: Dict[str, Any] = Field(
        ...,
        description="Summary statistics across all prompts"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Batch processing metadata"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "results": [],
                "summary_stats": {
                    "total_prompts": 10,
                    "average_score": 6.8,
                    "total_defects": 45,
                    "most_common_defect": "D002"
                },
                "metadata": {"total_processing_time_ms": 12340}
            }
        }


# Export all response models
__all__ = [
    "DefectResponse",
    "AgentResult",
    "AnalysisResponse",
    "TechniqueApplicationResponse",
    "OptimizationResponse",
    "TestIteration",
    "TestResponse",
    "BatchAnalysisResponse"
]
