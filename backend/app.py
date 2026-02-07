"""
PromptOptimizer Pro - FastAPI Application

Main API application with routes for:
- POST /api/analyze - Analyze prompts for defects
- POST /api/optimize - Optimize prompts with techniques
- GET /api/health - Health check
- GET /api/techniques - List available techniques
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Dict, Any

from .config import Config
from .utils import get_logger
from .routes import analyze, optimize, health

# Initialize logger
logger = get_logger(__name__)


# Lifespan event handler (replaces deprecated on_event)
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events"""
    # Startup
    logger.info("Starting PromptOptimizer Pro API")
    logger.info(f"Debug mode: {Config.FLASK_DEBUG}")
    logger.info(f"Environment: {Config.FLASK_ENV}")

    # Check API keys
    if Config.ANTHROPIC_API_KEY:
        logger.info("Anthropic API key configured")
    elif Config.GROQ_API_KEY:
        logger.info("Groq API key configured (fallback)")
    else:
        logger.warning("No API keys configured! Analysis will fail.")

    yield

    # Shutdown
    logger.info("Shutting down PromptOptimizer Pro API")


# Create FastAPI app
app = FastAPI(
    title="PromptOptimizer Pro",
    description="""
    Multi-Agent Prompt Engineering System

    Automatically detects and fixes prompt defects using:
    - 4 specialized AI agents (Clarity, Structure, Context, Security)
    - 15+ proven prompt engineering techniques
    - Consensus-based defect detection
    - Evidence-based optimization

    Based on research: Nagpure et al. (2025) - Prompt Engineering Survey
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=Config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(analyze.router, prefix="/api", tags=["Analysis"])
app.include_router(optimize.router, prefix="/api", tags=["Optimization"])
app.include_router(health.router, prefix="/api", tags=["Health"])


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)

    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc) if Config.FLASK_DEBUG else "An unexpected error occurred",
            "type": type(exc).__name__
        }
    )


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "PromptOptimizer Pro",
        "version": "1.0.0",
        "description": "Multi-Agent Prompt Engineering System",
        "endpoints": {
            "docs": "/docs",
            "health": "/api/health",
            "analyze": "/api/analyze",
            "optimize": "/api/optimize",
            "techniques": "/api/techniques"
        },
        "agents": 4,
        "techniques": 15,
        "defects_tracked": 28
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "backend.app:app",
        host=Config.HOST,
        port=Config.PORT,
        reload=Config.FLASK_DEBUG,
        log_level="info"
    )
