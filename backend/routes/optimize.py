"""
Optimize Route - POST /api/optimize

Optimizes a prompt by applying techniques to fix detected defects.
"""

from fastapi import APIRouter, HTTPException, status
from typing import Dict, Any

from ..models import OptimizeRequest, TECHNIQUE_REGISTRY, get_technique_by_id
from ..services.optimizer_service import get_optimizer
from ..utils import get_logger, OptimizationError

logger = get_logger(__name__)
router = APIRouter()


@router.post("/optimize", status_code=status.HTTP_200_OK)
async def optimize_prompt(request: OptimizeRequest) -> Dict[str, Any]:
    """
    Optimize a prompt by applying techniques to fix defects

    **Process:**
    1. Analyze prompt (or use provided analysis)
    2. Select techniques based on defects
    3. Apply techniques sequentially
    4. Re-analyze to verify improvement
    5. Return before/after comparison

    **Request Body:**
    - `prompt` (str, required): The prompt to optimize
    - `analysis` (dict, optional): Pre-computed analysis (from /api/analyze)
    - `optimization_level` (str, optional): "minimal", "balanced", or "aggressive"
    - `max_techniques` (int, optional): Maximum techniques to apply (1-10)
    - `task_type` (str, optional): Type of task
    - `domain` (str, optional): Domain context

    **Response:**
    - `original_prompt` (str): The original prompt
    - `optimized_prompt` (str): The improved prompt
    - `techniques_applied` (list): Which techniques were used
    - `improvement_score` (float): Score delta (positive = improvement)
    - `before_analysis` (dict): Original analysis results
    - `after_analysis` (dict): Post-optimization analysis
    - `metadata` (dict): Tokens, techniques considered, defects fixed

    **Example:**
    ```json
    {
        "prompt": "Write a sorting function",
        "optimization_level": "balanced",
        "max_techniques": 3,
        "task_type": "code_generation"
    }
    ```
    """
    try:
        logger.info(f"Optimizing prompt: {request.prompt[:50]}...")

        optimizer = get_optimizer()

        # Build context
        context = {
            "task_type": request.task_type,
            "domain": request.domain,
            "user_issues": request.user_issues
        }

        # Run optimization
        result = await optimizer.optimize(
            prompt=request.prompt,
            context=context,
            optimization_level=request.optimization_level,
            max_techniques=request.max_techniques,
            analysis=request.analysis,
            user_issues=request.user_issues
        )

        logger.info(
            f"Optimization complete: improvement={result['improvement_score']}, "
            f"techniques={len(result['techniques_applied'])}"
        )

        return result

    except OptimizationError as e:
        logger.error(f"Optimization error: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "error": "Optimization failed",
                "message": str(e),
                "type": "OptimizationError"
            }
        )

    except Exception as e:
        logger.error(f"Optimization failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Optimization failed",
                "message": str(e),
                "type": type(e).__name__
            }
        )


@router.get("/techniques", status_code=status.HTTP_200_OK)
async def list_techniques() -> Dict[str, Any]:
    """
    List all available prompt engineering techniques

    **Response:**
    - `total` (int): Total number of techniques
    - `categories` (dict): Techniques grouped by category
    - `techniques` (list): Full list of all techniques

    **Example Response:**
    ```json
    {
        "total": 15,
        "categories": {
            "role_based": 2,
            "few_shot": 3,
            ...
        },
        "techniques": [...]
    }
    ```
    """
    try:
        # Group techniques by category
        categories = {}
        techniques_list = []

        for tech_id, technique in TECHNIQUE_REGISTRY.items():
            # Group by category
            category = technique.category.value
            if category not in categories:
                categories[category] = []
            categories[category].append(tech_id)

            # Add to full list
            techniques_list.append({
                "id": technique.id,
                "name": technique.name,
                "category": technique.category.value,
                "description": technique.description,
                "effectiveness_score": technique.effectiveness_score,
                "fixes_defects": technique.fixes_defects,
                "when_to_use": technique.when_to_use,
                "example": technique.example[:100] + "..." if len(technique.example) > 100 else technique.example
            })

        # Sort techniques by effectiveness
        techniques_list.sort(key=lambda x: x["effectiveness_score"], reverse=True)

        return {
            "total": len(TECHNIQUE_REGISTRY),
            "categories": {cat: len(techs) for cat, techs in categories.items()},
            "techniques": techniques_list
        }

    except Exception as e:
        logger.error(f"Failed to list techniques: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Failed to retrieve techniques",
                "message": str(e)
            }
        )


@router.get("/techniques/{technique_id}", status_code=status.HTTP_200_OK)
async def get_technique_details(technique_id: str) -> Dict[str, Any]:
    """
    Get details for a specific technique

    **Path Parameters:**
    - `technique_id` (str): Technique ID (e.g., "T001", "T015")

    **Response:**
    Complete technique details including examples and templates
    """
    try:
        technique = get_technique_by_id(technique_id)

        if not technique:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": "Technique not found",
                    "message": f"No technique with ID '{technique_id}'"
                }
            )

        return {
            "id": technique.id,
            "name": technique.name,
            "category": technique.category.value,
            "description": technique.description,
            "when_to_use": technique.when_to_use,
            "example": technique.example,
            "fixes_defects": technique.fixes_defects,
            "effectiveness_score": technique.effectiveness_score,
            "template": technique.template
        }

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Failed to get technique {technique_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Failed to retrieve technique",
                "message": str(e)
            }
        )
