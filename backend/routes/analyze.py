"""
Analyze Route - POST /api/analyze

Analyzes a prompt for defects using the multi-agent system.
Includes SSE streaming endpoint for real-time progress.
"""

import json
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse
from typing import Dict, Any

from ..models import AnalyzeRequest
from ..services.agent_orchestrator import get_orchestrator
from ..utils import get_logger, AgentOrchestrationError

logger = get_logger(__name__)
router = APIRouter()


@router.post("/analyze", status_code=status.HTTP_200_OK)
async def analyze_prompt(request: AnalyzeRequest) -> Dict[str, Any]:
    """
    Analyze a prompt for defects using multi-agent consensus

    **Process:**
    1. Run 4 specialized agents in parallel
    2. Detect defects with consensus voting
    3. Calculate overall quality score
    4. Return detailed analysis with evidence

    **Request Body:**
    - `prompt` (str, required): The prompt to analyze (10-50,000 chars)
    - `task_type` (str, optional): Type of task (code_generation, reasoning, etc.)
    - `domain` (str, optional): Domain context (software_engineering, science, etc.)
    - `include_agent_breakdown` (bool, optional): Include per-agent results

    **Response:**
    - `overall_score` (float): Quality score 0-10
    - `defects` (list): Detected defects with evidence
    - `consensus` (float): Agent agreement level 0-1
    - `agent_results` (dict, optional): Per-agent breakdown
    - `summary` (str): Analysis summary
    - `metadata` (dict): Token usage, cost, processing time

    **Example:**
    ```json
    {
        "prompt": "Write a function to sort numbers",
        "task_type": "code_generation",
        "domain": "software_engineering"
    }
    ```
    """
    try:
        logger.info(f"Analyzing prompt: {request.prompt[:50]}...")

        orchestrator = get_orchestrator()

        # Build context from request
        context = {
            "task_type": request.task_type,
            "domain": request.domain,
            "provider": request.provider
        }

        # Run multi-agent analysis
        result = await orchestrator.analyze_with_agents(
            prompt=request.prompt,
            context=context,
            user_issues=request.user_issues
        )

        # Filter agent results if not requested
        if not request.include_agent_breakdown:
            result.pop("agent_results", None)

        logger.info(
            f"Analysis complete: score={result['overall_score']}, "
            f"defects={len(result.get('defects', []))}"
        )

        return result

    except AgentOrchestrationError as e:
        logger.error(f"Agent orchestration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "error": "Agent orchestration failed",
                "message": str(e),
                "type": "AgentOrchestrationError"
            }
        )

    except Exception as e:
        logger.error(f"Analysis failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Analysis failed",
                "message": str(e),
                "type": type(e).__name__
            }
        )


@router.post("/analyze/stream")
async def analyze_prompt_stream(request: AnalyzeRequest):
    """
    Stream analysis results via SSE as each agent completes.

    Events:
    - agent_start: {"type": "agent_start", "agent": "ClarityAgent", "focus_area": "..."}
    - agent_complete: {"type": "agent_complete", "agent": "ClarityAgent", "score": 7.5, ...}
    - final: {"type": "final", "overall_score": ..., "defects": [...], ...}
    """
    orchestrator = get_orchestrator()
    context = {
        "task_type": request.task_type,
        "domain": request.domain,
        "provider": request.provider
    }

    async def event_generator():
        try:
            async for event in orchestrator.analyze_with_agents_streaming(
                prompt=request.prompt,
                context=context,
                user_issues=request.user_issues
            ):
                yield f"data: {json.dumps(event)}\n\n"
        except Exception as e:
            logger.error(f"Streaming analysis failed: {e}", exc_info=True)
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
