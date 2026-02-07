"""
Utils package - utility functions and helpers
"""

# Logger exports
from .logger import setup_logging, get_logger, LoggerMixin

# Error handler exports
from .error_handlers import (
    PromptOptimizerError,
    ValidationError,
    ConfigurationError,
    LLMServiceError,
    APIKeyError,
    RateLimitError,
    TokenLimitError,
    DefectDetectionError,
    OptimizationError,
    AgentOrchestrationError,
    ResponseParseError,
    handle_api_error,
    handle_validation_error,
    safe_error_response,
    log_error_with_context,
    retry_with_backoff
)

# Response parser exports
from .response_parser import (
    extract_json_from_markdown,
    safe_json_parse,
    parse_json_response,
    extract_code_blocks,
    clean_llm_response,
    parse_list_response,
    extract_key_value_pairs,
    validate_json_schema
)

# Token counter exports
from .token_counter import (
    get_tokenizer,
    count_tokens,
    estimate_cost,
    validate_token_limit,
    estimate_tokens_from_chars,
    calculate_token_reduction,
    get_token_budget_remaining,
    compare_token_efficiency
)

# Validator exports
from .validators import (
    sanitize_input,
    validate_prompt,
    validate_task_type,
    validate_domain,
    validate_optimization_level,
    validate_provider,
    validate_json_structure,
    sanitize_json_output,
    validate_confidence_score,
    validate_severity
)

__all__ = [
    "setup_logging", "get_logger", "LoggerMixin",
    "PromptOptimizerError", "ValidationError", "ConfigurationError",
    "LLMServiceError", "APIKeyError", "RateLimitError",
    "TokenLimitError", "DefectDetectionError", "OptimizationError",
    "AgentOrchestrationError", "ResponseParseError",
    "handle_api_error", "handle_validation_error", "safe_error_response",
    "log_error_with_context", "retry_with_backoff",
    "extract_json_from_markdown", "safe_json_parse", "parse_json_response",
    "extract_code_blocks", "clean_llm_response", "parse_list_response",
    "extract_key_value_pairs", "validate_json_schema",
    "get_tokenizer", "count_tokens", "estimate_cost",
    "validate_token_limit", "estimate_tokens_from_chars",
    "calculate_token_reduction", "get_token_budget_remaining",
    "compare_token_efficiency",
    "sanitize_input", "validate_prompt", "validate_task_type",
    "validate_domain", "validate_optimization_level", "validate_provider",
    "validate_json_structure", "sanitize_json_output",
    "validate_confidence_score", "validate_severity"
]
