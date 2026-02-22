"""
History & Advanced Optimization Routes

Endpoints:
- POST /api/optimize/advanced - Advanced optimization with strategy selection
- GET /api/history - Optimization history
- GET /api/history/stats - Aggregate statistics
- GET /api/history/{id} - Specific optimization detail
- GET /api/techniques/effectiveness - Learned technique effectiveness
"""

import json
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse
from typing import Dict, Any, Optional

from ..models import AdvancedOptimizeRequest
from ..services.optimizer_service import get_optimizer
from ..services.dgeo_optimizer import get_dgeo_optimizer
from ..services.db_service import (
    save_optimization,
    get_history,
    get_history_by_id,
    get_history_stats,
    get_all_effectiveness,
    record_technique_result
)
from ..utils import get_logger, OptimizationError

logger = get_logger(__name__)
router = APIRouter()


@router.post("/optimize/advanced", status_code=status.HTTP_200_OK)
async def advanced_optimize(request: AdvancedOptimizeRequest) -> Dict[str, Any]:
    """
    Advanced optimization with strategy selection.

    Strategies:
    - **standard**: Single-pass LLM optimization (fastest, ~30s)
    - **dgeo**: Defect-Guided Evolutionary Optimization (best quality, ~2min)
    - **shdt**: Scored History with Defect Trajectories (iterative learning, ~1min)
    - **cdraf**: Critic-Driven Refinement with Agent Feedback (targeted fixes, ~1min)
    """
    try:
        context = {
            "task_type": request.task_type,
            "domain": request.domain,
            "provider": request.provider
        }

        strategy = request.strategy
        provider_label = request.provider or "default"
        logger.info(f"Advanced optimization: strategy={strategy}, provider={provider_label}, prompt={request.prompt[:50]}...")

        if strategy == "standard":
            optimizer = get_optimizer()
            result = await optimizer.optimize(
                prompt=request.prompt,
                context=context,
                optimization_level=request.optimization_level,
                max_techniques=request.max_techniques,
                analysis=request.analysis
            )
            # Normalize response
            response = {
                "original_prompt": result["original_prompt"],
                "optimized_prompt": result["optimized_prompt"],
                "strategy": "standard",
                "score_before": result["before_analysis"]["overall_score"],
                "score_after": result["after_analysis"]["overall_score"],
                "improvement": result["improvement_score"],
                "techniques_applied": result["techniques_applied"],
                "before_analysis": result["before_analysis"],
                "after_analysis": result["after_analysis"],
                "metadata": result["metadata"]
            }

        elif strategy == "dgeo":
            dgeo = get_dgeo_optimizer()
            result = await dgeo.optimize(
                prompt=request.prompt,
                context=context,
                analysis=request.analysis,
                population_size=request.population_size,
                generations=request.generations,
                optimization_level=request.optimization_level
            )
            response = {
                "original_prompt": result["original_prompt"],
                "optimized_prompt": result["best_prompt"],
                "strategy": "dgeo",
                "score_before": result["original_score"],
                "score_after": result["best_score"],
                "improvement": result["total_improvement"],
                "evolution_history": result["evolution_history"],
                "population_final": result.get("population_final", []),
                "before_analysis": result["before_analysis"],
                "after_analysis": result["after_analysis"],
                "metadata": result["metadata"]
            }

        elif strategy == "shdt":
            optimizer = get_optimizer()
            result = await optimizer.optimize_with_trajectory(
                prompt=request.prompt,
                context=context,
                analysis=request.analysis,
                max_iterations=request.max_iterations,
                target_score=request.target_score
            )
            response = {
                "original_prompt": result["original_prompt"],
                "optimized_prompt": result["final_prompt"],
                "strategy": "shdt",
                "score_before": result["original_score"],
                "score_after": result["final_score"],
                "improvement": result["total_improvement"],
                "trajectory": result["trajectory"],
                "before_analysis": result["before_analysis"],
                "after_analysis": result["after_analysis"],
                "metadata": result["metadata"]
            }

        elif strategy == "cdraf":
            optimizer = get_optimizer()
            # First do standard optimization, then refine with agents
            standard_result = await optimizer.optimize(
                prompt=request.prompt,
                context=context,
                optimization_level=request.optimization_level,
                max_techniques=request.max_techniques,
                analysis=request.analysis
            )

            cdraf_result = await optimizer.refine_with_agents(
                optimized_prompt=standard_result["optimized_prompt"],
                context=context,
                max_rounds=request.max_rounds
            )

            response = {
                "original_prompt": request.prompt,
                "optimized_prompt": cdraf_result["refined_prompt"],
                "strategy": "cdraf",
                "score_before": standard_result["before_analysis"]["overall_score"],
                "score_after": cdraf_result["final_score"],
                "improvement": round(
                    cdraf_result["final_score"] - standard_result["before_analysis"]["overall_score"], 2
                ),
                "critique_rounds": cdraf_result["critique_rounds"],
                "standard_result": {
                    "optimized_prompt": standard_result["optimized_prompt"],
                    "score": standard_result["after_analysis"]["overall_score"],
                    "techniques_applied": standard_result["techniques_applied"]
                },
                "before_analysis": standard_result["before_analysis"],
                "after_analysis": cdraf_result["after_analysis"],
                "metadata": cdraf_result["metadata"]
            }
        elif strategy == "auto":
            optimizer = get_optimizer()
            result = await optimizer.optimize_unified(
                prompt=request.prompt,
                context=context,
                analysis=request.analysis,
                optimization_level=request.optimization_level,
                max_techniques=request.max_techniques,
                task_type=request.task_type,
                domain=request.domain
            )
            response = result  # optimize_unified already returns the right shape

        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unknown strategy: {strategy}"
            )

        # Save to history
        try:
            save_optimization(
                original_prompt=response["original_prompt"],
                optimized_prompt=response["optimized_prompt"],
                strategy=strategy,
                score_before=response["score_before"],
                score_after=response["score_after"],
                defects_before=response.get("before_analysis", {}).get("defects"),
                defects_after=response.get("after_analysis", {}).get("defects"),
                techniques_applied=response.get("techniques_applied"),
                evolution_history=response.get("evolution_history"),
                trajectory_history=response.get("trajectory"),
                critique_history=response.get("critique_rounds"),
                metadata=response.get("metadata"),
                task_type=request.task_type,
                domain=request.domain
            )
        except Exception as db_err:
            logger.warning(f"Failed to save to history: {db_err}")

        return response

    except OptimizationError as e:
        logger.error(f"Advanced optimization error: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"error": "Optimization failed", "message": str(e)}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Advanced optimization failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Optimization failed", "message": str(e)}
        )


@router.post("/optimize/advanced/stream")
async def advanced_optimize_stream(request: AdvancedOptimizeRequest):
    """
    Stream optimization progress via SSE. Shows each pipeline phase in real-time.

    Events:
    - phase: {"type": "phase", "phase": 1, "name": "Standard Optimization", "status": "running|complete|failed"}
    - final: {"type": "final", "original_prompt": ..., "optimized_prompt": ..., ...}
    """
    optimizer = get_optimizer()
    context = {
        "task_type": request.task_type,
        "domain": request.domain,
        "provider": request.provider
    }

    async def event_generator():
        try:
            async for event in optimizer.optimize_unified_streaming(
                prompt=request.prompt,
                context=context,
                analysis=request.analysis,
                optimization_level=request.optimization_level,
                max_techniques=request.max_techniques,
                task_type=request.task_type,
                domain=request.domain,
                user_issues=request.user_issues
            ):
                yield f"data: {json.dumps(event)}\n\n"
        except Exception as e:
            logger.error(f"Streaming optimization failed: {e}", exc_info=True)
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@router.get("/history", status_code=status.HTTP_200_OK)
async def list_history(
    limit: int = 20,
    offset: int = 0,
    strategy: Optional[str] = None
) -> Dict[str, Any]:
    """Get optimization history, most recent first"""
    try:
        records = get_history(limit=limit, offset=offset, strategy=strategy)
        stats = get_history_stats()
        return {
            "records": records,
            "total": stats["total_optimizations"],
            "stats": stats
        }
    except Exception as e:
        logger.error(f"Failed to get history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Failed to retrieve history", "message": str(e)}
        )


@router.get("/history/stats", status_code=status.HTTP_200_OK)
async def history_stats() -> Dict[str, Any]:
    """Get aggregate optimization statistics"""
    try:
        return get_history_stats()
    except Exception as e:
        logger.error(f"Failed to get stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Failed to retrieve stats", "message": str(e)}
        )


@router.get("/history/{record_id}", status_code=status.HTTP_200_OK)
async def get_history_detail(record_id: int) -> Dict[str, Any]:
    """Get detailed optimization record by ID"""
    try:
        record = get_history_by_id(record_id)
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": "Record not found", "message": f"No record with ID {record_id}"}
            )
        return record
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get history detail: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Failed to retrieve record", "message": str(e)}
        )


@router.get("/techniques/effectiveness", status_code=status.HTTP_200_OK)
async def technique_effectiveness() -> Dict[str, Any]:
    """Get learned technique effectiveness matrix"""
    try:
        data = get_all_effectiveness()
        return {
            "effectiveness": data,
            "total_records": len(data)
        }
    except Exception as e:
        logger.error(f"Failed to get effectiveness: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Failed to retrieve effectiveness data", "message": str(e)}
        )
