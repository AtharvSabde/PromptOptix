"""
Health Route - GET /api/health

Health check endpoint for monitoring and status.
"""

from fastapi import APIRouter, status
from typing import Dict, Any
import sys

from ..config import Config
from ..models import DEFECT_TAXONOMY, TECHNIQUE_REGISTRY
from ..utils import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check() -> Dict[str, Any]:
    """
    Health check endpoint

    Returns system status, configuration, and component health.

    **Response:**
    - `status` (str): "healthy" or "degraded"
    - `version` (str): API version
    - `python_version` (str): Python runtime version
    - `api_keys` (dict): Which API keys are configured
    - `components` (dict): Status of each system component
    - `statistics` (dict): System statistics

    **Example Response:**
    ```json
    {
        "status": "healthy",
        "version": "1.0.0",
        "api_keys": {
            "anthropic": true,
            "groq": false
        },
        "components": {
            "defect_taxonomy": "operational",
            "technique_registry": "operational",
            "agents": "operational"
        }
    }
    ```
    """
    try:
        # Check API keys
        api_keys_status = {
            "anthropic": bool(Config.ANTHROPIC_API_KEY),
            "groq": bool(Config.GROQ_API_KEY),
            "any_configured": bool(Config.ANTHROPIC_API_KEY or Config.GROQ_API_KEY)
        }

        # Check components
        components_status = {}

        # Check defect taxonomy
        try:
            defects_loaded = len(DEFECT_TAXONOMY) > 0
            components_status["defect_taxonomy"] = "operational" if defects_loaded else "error"
        except Exception as e:
            logger.error(f"Defect taxonomy check failed: {e}")
            components_status["defect_taxonomy"] = "error"

        # Check technique registry
        try:
            techniques_loaded = len(TECHNIQUE_REGISTRY) > 0
            components_status["technique_registry"] = "operational" if techniques_loaded else "error"
        except Exception as e:
            logger.error(f"Technique registry check failed: {e}")
            components_status["technique_registry"] = "error"

        # Check agent system
        try:
            from ..services.agent_orchestrator import get_orchestrator
            orchestrator = get_orchestrator()
            agents_count = len(orchestrator.agents)
            components_status["agents"] = "operational" if agents_count == 4 else "degraded"
        except Exception as e:
            logger.error(f"Agent system check failed: {e}")
            components_status["agents"] = "error"

        # Check optimizer
        try:
            from ..services.optimizer_service import get_optimizer
            optimizer = get_optimizer()
            components_status["optimizer"] = "operational"
        except Exception as e:
            logger.error(f"Optimizer check failed: {e}")
            components_status["optimizer"] = "error"

        # Determine overall status
        all_operational = all(s == "operational" for s in components_status.values())
        has_error = any(s == "error" for s in components_status.values())
        has_api_keys = api_keys_status["any_configured"]

        if has_error or not has_api_keys:
            overall_status = "degraded"
        elif all_operational:
            overall_status = "healthy"
        else:
            overall_status = "operational"

        # System statistics
        statistics = {
            "total_defects": len(DEFECT_TAXONOMY),
            "total_techniques": len(TECHNIQUE_REGISTRY),
            "total_agents": 4,
            "consensus_threshold": Config.CONSENSUS_THRESHOLD,
            "max_analysis_tokens": Config.MAX_ANALYSIS_TOKENS
        }

        return {
            "status": overall_status,
            "version": "1.0.0",
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "environment": Config.FLASK_ENV,
            "debug_mode": Config.FLASK_DEBUG,
            "api_keys": api_keys_status,
            "components": components_status,
            "statistics": statistics,
            "warnings": _get_warnings(api_keys_status, components_status)
        }

    except Exception as e:
        logger.error(f"Health check failed: {e}", exc_info=True)
        return {
            "status": "error",
            "version": "1.0.0",
            "error": str(e),
            "type": type(e).__name__
        }


def _get_warnings(api_keys_status: Dict[str, bool], components_status: Dict[str, str]) -> list:
    """Generate warnings based on system status"""
    warnings = []

    if not api_keys_status["any_configured"]:
        warnings.append({
            "code": "NO_API_KEYS",
            "message": "No API keys configured. Analysis will fail.",
            "severity": "high"
        })

    if not api_keys_status["anthropic"] and api_keys_status["groq"]:
        warnings.append({
            "code": "USING_FALLBACK",
            "message": "Using Groq as fallback. Consider configuring Anthropic API key for primary provider.",
            "severity": "low"
        })

    for component, status_val in components_status.items():
        if status_val == "error":
            warnings.append({
                "code": f"{component.upper()}_ERROR",
                "message": f"Component '{component}' is not operational",
                "severity": "high"
            })
        elif status_val == "degraded":
            warnings.append({
                "code": f"{component.upper()}_DEGRADED",
                "message": f"Component '{component}' is degraded",
                "severity": "medium"
            })

    return warnings
