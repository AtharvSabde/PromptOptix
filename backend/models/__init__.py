"""
Models package - exports all data structures

This package contains:
- Defect taxonomy (28 defects across 6 categories)
- Technique registry (41+ prompt engineering techniques)
- Request/response models for API validation
"""

# Defect Taxonomy exports
from .defect_taxonomy import (
    DefectCategory,
    DefectSeverity,
    DefectDefinition,
    DEFECT_TAXONOMY,
    get_defect_by_id,
    get_defects_by_category,
    get_critical_defects
)

# User Issue Registry exports
from .issue_registry import (
    IssueCategory,
    IssueDefinition,
    ISSUE_REGISTRY,
    get_issue_by_id,
    get_issues_by_category,
    match_user_issue,
    match_user_issues_with_scores,
    get_defects_for_issue,
    get_issues_for_defect,
    aggregate_defect_priorities,
    aggregate_suggested_techniques
)

# Technique Registry exports
from .technique_registry import (
    TechniqueCategory,
    TechniqueDefinition,
    TECHNIQUE_REGISTRY,
    get_technique_by_id,
    get_techniques_by_category,
    get_techniques_for_defect,
    get_top_techniques,
    get_all_techniques
)

# Request Models exports
from .request_models import (
    AnalyzeRequest,
    OptimizeRequest,
    AdvancedOptimizeRequest,
    TestRequest,
    BatchAnalyzeRequest
)

# Response Models exports
from .response_models import (
    DefectResponse,
    AgentResult,
    AnalysisResponse,
    TechniqueApplicationResponse,
    OptimizationResponse,
    TestIteration,
    TestResponse,
    BatchAnalysisResponse
)

__all__ = [
    # Defect Taxonomy
    "DefectCategory",
    "DefectSeverity",
    "DefectDefinition",
    "DEFECT_TAXONOMY",
    "get_defect_by_id",
    "get_defects_by_category",
    "get_critical_defects",
    # User Issue Registry
    "IssueCategory",
    "IssueDefinition",
    "ISSUE_REGISTRY",
    "get_issue_by_id",
    "get_issues_by_category",
    "match_user_issue",
    "match_user_issues_with_scores",
    "get_defects_for_issue",
    "get_issues_for_defect",
    "aggregate_defect_priorities",
    "aggregate_suggested_techniques",
    # Technique Registry
    "TechniqueCategory",
    "TechniqueDefinition",
    "TECHNIQUE_REGISTRY",
    "get_technique_by_id",
    "get_techniques_by_category",
    "get_techniques_for_defect",
    "get_top_techniques",
    "get_all_techniques",
    # Request Models
    "AnalyzeRequest",
    "OptimizeRequest",
    "AdvancedOptimizeRequest",
    "TestRequest",
    "BatchAnalyzeRequest",
    # Response Models
    "DefectResponse",
    "AgentResult",
    "AnalysisResponse",
    "TechniqueApplicationResponse",
    "OptimizationResponse",
    "TestIteration",
    "TestResponse",
    "BatchAnalysisResponse"
]
