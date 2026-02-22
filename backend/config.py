"""
PromptOptimizer Pro - Configuration Management
Centralizes all configuration, constants, and environment variables
"""

import os
from typing import Dict, List, Any
from enum import Enum
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class TaskType(str, Enum):
    """Supported task types for prompt optimization"""
    CODE_GENERATION = "code_generation"
    REASONING = "reasoning"
    CREATIVE_WRITING = "creative_writing"
    INFORMATION_EXTRACTION = "information_extraction"
    CLASSIFICATION = "classification"
    CONVERSATION = "conversation"
    SUMMARIZATION = "summarization"
    QUESTION_ANSWERING = "question_answering"
    TRANSLATION = "translation"
    GENERAL = "general"


class Domain(str, Enum):
    """Domain-specific contexts"""
    SOFTWARE_ENGINEERING = "software_engineering"
    MATHEMATICS = "mathematics"
    SCIENCE = "science"
    BUSINESS = "business"
    EDUCATION = "education"
    HEALTHCARE = "healthcare"
    LEGAL = "legal"
    CREATIVE = "creative"
    GENERAL = "general"


class OptimizationLevel(str, Enum):
    """How aggressive to be with optimization"""
    MINIMAL = "minimal"  # Only fix critical defects
    BALANCED = "balanced"  # Fix most defects, maintain readability
    AGGRESSIVE = "aggressive"  # Maximum optimization, may restructure heavily


class LLMProvider(str, Enum):
    """Supported LLM providers"""
    ANTHROPIC = "anthropic"
    GROQ = "groq"
    OPENAI = "openai"
    GEMINI = "gemini"


class Config:
    """Main configuration class"""
    
    # ===== API Keys =====
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    
    # ===== Flask Settings =====
    FLASK_ENV = os.getenv("FLASK_ENV", "development")
    FLASK_DEBUG = os.getenv("FLASK_DEBUG", "True").lower() == "true"
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    PORT = int(os.getenv("PORT", "5000"))
    HOST = os.getenv("HOST", "0.0.0.0")

    # ===== LLM Configuration =====
    DEFAULT_PROVIDER = os.getenv("DEFAULT_PROVIDER", "anthropic")
    
    # Model registry with capabilities and pricing
    MODELS = {
        "anthropic": {
            "claude-sonnet-4-20250514": {
                "name": "Claude Sonnet 4",
                "context_window": 200000,
                "max_output": 8192,
                "cost_per_1k_input": 0.003,
                "cost_per_1k_output": 0.015,
                "supports_streaming": True,
                "best_for": ["analysis", "optimization", "reasoning"]
            },
            "claude-opus-4-5-20251101": {
                "name": "Claude Opus 4.5",
                "context_window": 200000,
                "max_output": 16384,
                "cost_per_1k_input": 0.015,
                "cost_per_1k_output": 0.075,
                "supports_streaming": True,
                "best_for": ["complex_analysis", "creative_optimization"]
            }
        },
        "groq": {
            "llama-3.3-70b-versatile": {
                "name": "Llama 3.3 70B",
                "context_window": 128000,
                "max_output": 32768,
                "cost_per_1k_input": 0.00059,
                "cost_per_1k_output": 0.00079,
                "supports_streaming": True,
                "best_for": ["fast_analysis", "testing"]
            }
        },
        "openai": {
            "gpt-4o": {
                "name": "GPT-4o",
                "context_window": 128000,
                "max_output": 16384,
                "cost_per_1k_input": 0.0025,
                "cost_per_1k_output": 0.01,
                "supports_streaming": True,
                "best_for": ["analysis", "optimization", "reasoning"]
            },
            "gpt-4o-mini": {
                "name": "GPT-4o Mini",
                "context_window": 128000,
                "max_output": 16384,
                "cost_per_1k_input": 0.00015,
                "cost_per_1k_output": 0.0006,
                "supports_streaming": True,
                "best_for": ["fast_analysis", "testing"]
            }
        },
        "gemini": {
            "gemini-2.0-flash": {
                "name": "Gemini 2.0 Flash",
                "context_window": 1048576,
                "max_output": 8192,
                "cost_per_1k_input": 0.0001,
                "cost_per_1k_output": 0.0004,
                "supports_streaming": True,
                "best_for": ["fast_analysis", "testing"]
            },
            "gemini-1.5-pro": {
                "name": "Gemini 1.5 Pro",
                "context_window": 2097152,
                "max_output": 8192,
                "cost_per_1k_input": 0.00125,
                "cost_per_1k_output": 0.005,
                "supports_streaming": True,
                "best_for": ["analysis", "optimization", "reasoning"]
            }
        }
    }
    
    # Default models for each provider
    ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514")
    GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
    
    # ===== Token Limits =====
    MAX_ANALYSIS_TOKENS = int(os.getenv("MAX_ANALYSIS_TOKENS", "4000"))
    MAX_OPTIMIZATION_TOKENS = int(os.getenv("MAX_OPTIMIZATION_TOKENS", "8000"))
    MAX_PROMPT_LENGTH = int(os.getenv("MAX_PROMPT_LENGTH", "50000"))
    
    # ===== Multi-Agent Configuration =====
    NUM_AGENTS = int(os.getenv("NUM_AGENTS", "4"))
    CONSENSUS_THRESHOLD = float(os.getenv("CONSENSUS_THRESHOLD", "0.7"))
    
    # Agent types and their focus areas
    AGENT_TYPES = {
        "clarity": {
            "name": "Clarity Agent",
            "focus": "specification_and_intent",
            "defect_categories": [
                "ambiguity",
                "underspecification", 
                "conflicting_requirements",
                "intent_misalignment"
            ]
        },
        "structure": {
            "name": "Structure Agent",
            "focus": "formatting_and_organization",
            "defect_categories": [
                "poor_role_separation",
                "disorganization",
                "syntax_errors",
                "format_issues",
                "information_overload"
            ]
        },
        "context": {
            "name": "Context Agent",
            "focus": "memory_and_relevance",
            "defect_categories": [
                "context_overflow",
                "missing_context",
                "irrelevant_information",
                "misreferencing",
                "forgotten_instructions"
            ]
        },
        "security": {
            "name": "Security Agent",
            "focus": "safety_and_injection",
            "defect_categories": [
                "prompt_injection",
                "jailbreaking_attempts",
                "policy_violations",
                "malicious_content",
                "data_leakage_risk"
            ]
        }
    }
    
    # ===== A/B Testing Settings =====
    TEST_ITERATIONS = int(os.getenv("TEST_ITERATIONS", "5"))
    TEST_TIMEOUT = int(os.getenv("TEST_TIMEOUT", "30"))
    
    # ===== Evaluation Settings =====
    ENABLE_BERTSCORE = os.getenv("ENABLE_BERTSCORE", "false").lower() == "true"
    ENABLE_SIGNIFICANCE_TESTING = os.getenv("ENABLE_SIGNIFICANCE_TESTING", "true").lower() == "true"
    
    # Quality scoring dimensions (1-10 scale)
    QUALITY_DIMENSIONS = [
        "clarity",
        "completeness",
        "structure",
        "coherence",
        "specificity",
        "consistency"
    ]
    
    # ===== Rate Limiting =====
    RATE_LIMIT = int(os.getenv("RATE_LIMIT", "60"))
    
    # ===== Logging =====
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = os.getenv("LOG_FORMAT", "json")
    
    # ===== CORS Settings =====
    # Strip whitespace from each origin to prevent CORS matching issues
    _cors_origins_raw = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:3000,http://localhost:5173,http://localhost:5174"
    )
    CORS_ORIGINS = [origin.strip() for origin in _cors_origins_raw.split(",")]
    
    # ===== Defect Severity Levels =====
    SEVERITY_LEVELS = {
        "critical": {
            "score": 4,
            "description": "Makes prompt completely unusable or unsafe",
            "color": "red",
            "requires_fix": True
        },
        "high": {
            "score": 3,
            "description": "Significantly degrades output quality",
            "color": "orange",
            "requires_fix": True
        },
        "medium": {
            "score": 2,
            "description": "Noticeable quality impact",
            "color": "yellow",
            "requires_fix": False
        },
        "low": {
            "score": 1,
            "description": "Minor improvement opportunity",
            "color": "blue",
            "requires_fix": False
        }
    }

    # ===== Task-Type Specific Defect Priorities =====
    # Maps task types to defects that should be prioritized (boost factor > 1.0)
    # These boosts are applied during multi-agent consensus to emphasize
    # defects that are most impactful for specific task types
    TASK_DEFECT_PRIORITIES = {
        "code_generation": {
            "D007": 1.5,  # Syntax errors - critical for code
            "D002": 1.4,  # Underspecification - need clear requirements
            "D008": 1.4,  # Format specification - code structure matters
            "D019": 1.3,  # Missing examples - examples help code generation
            "D017": 1.2,  # Success criteria - need testable requirements
        },
        "reasoning": {
            "D001": 1.5,  # Ambiguity - clarity crucial for reasoning
            "D003": 1.5,  # Conflicting requirements - logic must be consistent
            "D004": 1.4,  # Intent misalignment - correct problem understanding
            "D017": 1.3,  # Success criteria - need clear reasoning goals
            "D014": 1.2,  # Instruction forgetting - maintain reasoning thread
        },
        "creative_writing": {
            "D018": 1.5,  # Tone/style mismatch - style is critical
            "D015": 1.3,  # Output constraints - length/format guidance
            "D002": 1.2,  # Underspecification - creative freedom needs bounds
            "D001": 1.1,  # Ambiguity - some ambiguity acceptable
        },
        "summarization": {
            "D015": 1.5,  # Output constraints - length is critical
            "D009": 1.4,  # Information overload - need to prioritize
            "D002": 1.3,  # Underspecification - need clear scope
            "D006": 1.2,  # Disorganization - structure matters
        },
        "question_answering": {
            "D001": 1.5,  # Ambiguity - questions must be clear
            "D011": 1.4,  # Missing context - need relevant background
            "D004": 1.3,  # Intent misalignment - understand the question
            "D008": 1.2,  # Format specification - answer format matters
        },
        "classification": {
            "D019": 1.5,  # Missing examples - examples are essential
            "D021": 1.4,  # Insufficient diversity - need varied examples
            "D002": 1.3,  # Underspecification - clear categories needed
            "D020": 1.3,  # Poor example quality - examples must be correct
        },
        "information_extraction": {
            "D008": 1.5,  # Format specification - output schema critical
            "D002": 1.4,  # Underspecification - clear extraction targets
            "D005": 1.3,  # Poor role separation - separate instructions from data
            "D011": 1.2,  # Missing context - domain context helps
        },
        "conversation": {
            "D018": 1.4,  # Tone/style - conversational style matters
            "D001": 1.3,  # Ambiguity - clarity in dialogue
            "D005": 1.3,  # Role separation - clear persona definition
            "D023": 1.5,  # Prompt injection - security in conversations
        },
        "translation": {
            "D002": 1.4,  # Underspecification - source/target languages
            "D018": 1.4,  # Tone/style - preserve original tone
            "D007": 1.3,  # Syntax errors - language accuracy
            "D011": 1.2,  # Missing context - cultural context
        },
        "general": {
            # No specific boosts for general tasks
        }
    }

    # ===== Domain-Specific Defect Priorities =====
    # Additional priority boosts based on domain
    DOMAIN_DEFECT_PRIORITIES = {
        "software_engineering": {
            "D007": 1.3,  # Syntax errors
            "D023": 1.4,  # Security - prompt injection
            "D024": 1.3,  # Jailbreaking
        },
        "healthcare": {
            "D025": 1.5,  # Privacy violations - HIPAA
            "D026": 1.4,  # Harmful content - medical safety
            "D016": 1.3,  # Unrealistic expectations - medical accuracy
        },
        "legal": {
            "D001": 1.4,  # Ambiguity - legal precision
            "D025": 1.4,  # Privacy - client confidentiality
            "D028": 1.3,  # IP concerns - legal citations
        },
        "education": {
            "D019": 1.4,  # Examples - teaching requires examples
            "D021": 1.3,  # Example diversity - varied learning
            "D027": 1.3,  # Bias - educational fairness
        },
        "business": {
            "D025": 1.3,  # Privacy - business confidentiality
            "D006": 1.2,  # Organization - professional structure
            "D018": 1.2,  # Tone - business appropriate
        },
        "mathematics": {
            "D007": 1.4,  # Syntax - mathematical notation
            "D003": 1.4,  # Conflicts - logical consistency
            "D017": 1.3,  # Success criteria - verifiable proofs
        },
        "science": {
            "D016": 1.3,  # Unrealistic expectations - scientific accuracy
            "D011": 1.3,  # Missing context - methodology context
            "D003": 1.2,  # Conflicts - hypothesis consistency
        },
        "creative": {
            "D018": 1.4,  # Tone/style
            "D015": 1.2,  # Output constraints
        },
        "general": {
            # No specific boosts for general domain
        }
    }
    
    # ===== Advanced Optimization Strategies =====
    # DGEO: Defect-Guided Evolutionary Optimization
    DGEO_POPULATION_SIZE = int(os.getenv("DGEO_POPULATION_SIZE", "5"))
    DGEO_GENERATIONS = int(os.getenv("DGEO_GENERATIONS", "3"))

    # SHDT: Scored History with Defect Trajectories
    SHDT_MAX_ITERATIONS = int(os.getenv("SHDT_MAX_ITERATIONS", "4"))
    SHDT_TARGET_SCORE = float(os.getenv("SHDT_TARGET_SCORE", "8.0"))
    SHDT_MIN_IMPROVEMENT = float(os.getenv("SHDT_MIN_IMPROVEMENT", "0.3"))

    # CDRAF: Critic-Driven Refinement with Agent Feedback
    CDRAF_MAX_ROUNDS = int(os.getenv("CDRAF_MAX_ROUNDS", "2"))

    # Available strategies
    OPTIMIZATION_STRATEGIES = ["standard", "dgeo", "shdt", "cdraf"]

    # ===== API Retry Configuration =====
    MAX_RETRIES = 3
    RETRY_DELAY = 1  # seconds
    RETRY_BACKOFF = 2  # exponential backoff multiplier
    
    # ===== Validation Rules =====
    MIN_PROMPT_LENGTH = 10  # characters
    MAX_DEFECTS_PER_PROMPT = 50  # sanity check
    MAX_TECHNIQUES_PER_OPTIMIZATION = 10
    
    @classmethod
    def validate(cls) -> List[str]:
        """Validate configuration and return list of errors"""
        errors = []

        if not cls.ANTHROPIC_API_KEY and cls.DEFAULT_PROVIDER == "anthropic":
            errors.append("ANTHROPIC_API_KEY is required when using Anthropic as default provider")

        if not cls.GROQ_API_KEY and cls.DEFAULT_PROVIDER == "groq":
            errors.append("GROQ_API_KEY is required when using Groq as default provider")

        if not cls.OPENAI_API_KEY and cls.DEFAULT_PROVIDER == "openai":
            errors.append("OPENAI_API_KEY is required when using OpenAI as default provider")

        if not cls.GEMINI_API_KEY and cls.DEFAULT_PROVIDER == "gemini":
            errors.append("GEMINI_API_KEY is required when using Gemini as default provider")
        
        if cls.CONSENSUS_THRESHOLD < 0 or cls.CONSENSUS_THRESHOLD > 1:
            errors.append("CONSENSUS_THRESHOLD must be between 0 and 1")
        
        if cls.NUM_AGENTS < 1 or cls.NUM_AGENTS > 10:
            errors.append("NUM_AGENTS must be between 1 and 10")
        
        return errors
    
    @classmethod
    def get_model_config(cls, provider: str, model: str) -> Dict[str, Any]:
        """Get configuration for a specific model"""
        return cls.MODELS.get(provider, {}).get(model, {})
    
    @classmethod
    def is_development(cls) -> bool:
        """Check if running in development mode"""
        return cls.FLASK_ENV == "development"
    
    @classmethod
    def is_production(cls) -> bool:
        """Check if running in production mode"""
        return cls.FLASK_ENV == "production"


# Export commonly used enums and config
__all__ = [
    "Config",
    "TaskType",
    "Domain",
    "OptimizationLevel",
    "LLMProvider"
]