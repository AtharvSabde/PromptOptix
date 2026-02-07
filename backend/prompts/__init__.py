"""
PromptOptimizer Pro - Prompts Package
Contains meta-prompts for analysis and optimization
"""

from .agents_prompts import *

from .analysis_prompts import (
    get_comprehensive_analysis_prompt,
    get_defect_severity_prompt,
    get_task_specific_analysis_prompt,
    get_quick_analysis_prompt,
    get_comparison_analysis_prompt,
    get_domain_specific_analysis_prompt
)

from .optimization_prompts import (
    get_optimization_prompt,
    get_technique_application_prompt,
    get_incremental_optimization_prompt,
    get_style_optimization_prompt,
    get_task_optimization_prompt,
    get_safety_optimization_prompt,
    get_refinement_suggestions_prompt
)

__all__ = [
    # Analysis prompts
    "get_comprehensive_analysis_prompt",
    "get_defect_severity_prompt",
    "get_task_specific_analysis_prompt",
    "get_quick_analysis_prompt",
    "get_comparison_analysis_prompt",
    "get_domain_specific_analysis_prompt",
    # Optimization prompts
    "get_optimization_prompt",
    "get_technique_application_prompt",
    "get_incremental_optimization_prompt",
    "get_style_optimization_prompt",
    "get_task_optimization_prompt",
    "get_safety_optimization_prompt",
    "get_refinement_suggestions_prompt"
]
