"""
PromptOptimizer Pro - Error Handling Utilities
Custom exceptions and error handling logic
"""

from typing import Optional, Dict, Any
from .logger import get_logger

logger = get_logger(__name__)


# =============================================================================
# Custom Exception Classes
# =============================================================================

class PromptOptimizerError(Exception):
    """Base exception for all PromptOptimizer errors"""
    
    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or "UNKNOWN_ERROR"
        self.details = details or {}
        
        # Log the error
        logger.error(
            f"[{self.error_code}] {message}",
            extra={"details": self.details}
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for API responses"""
        return {
            "error": True,
            "error_code": self.error_code,
            "message": self.message,
            "details": self.details
        }


class ValidationError(PromptOptimizerError):
    """Raised when input validation fails"""
    
    def __init__(self, message: str, field: Optional[str] = None, **kwargs):
        details = kwargs.get("details", {})
        if field:
            details["field"] = field
        
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            details=details
        )


class ConfigurationError(PromptOptimizerError):
    """Raised when configuration is invalid or missing"""
    
    def __init__(self, message: str, config_key: Optional[str] = None, **kwargs):
        details = kwargs.get("details", {})
        if config_key:
            details["config_key"] = config_key
        
        super().__init__(
            message=message,
            error_code="CONFIG_ERROR",
            details=details
        )


class LLMServiceError(PromptOptimizerError):
    """Raised when LLM API calls fail"""
    
    def __init__(
        self,
        message: str,
        provider: Optional[str] = None,
        status_code: Optional[int] = None,
        **kwargs
    ):
        details = kwargs.get("details", {})
        if provider:
            details["provider"] = provider
        if status_code:
            details["status_code"] = status_code
        
        super().__init__(
            message=message,
            error_code="LLM_SERVICE_ERROR",
            details=details
        )


class APIKeyError(LLMServiceError):
    """Raised when API key is missing or invalid"""
    
    def __init__(self, provider: str, **kwargs):
        super().__init__(
            message=f"Invalid or missing API key for {provider}",
            provider=provider,
            error_code="API_KEY_ERROR",
            **kwargs
        )


class RateLimitError(LLMServiceError):
    """Raised when API rate limit is exceeded"""
    
    def __init__(
        self,
        provider: str,
        retry_after: Optional[int] = None,
        **kwargs
    ):
        details = kwargs.get("details", {})
        if retry_after:
            details["retry_after"] = retry_after
        
        super().__init__(
            message=f"Rate limit exceeded for {provider}",
            provider=provider,
            error_code="RATE_LIMIT_ERROR",
            details=details
        )


class TokenLimitError(PromptOptimizerError):
    """Raised when token limit is exceeded"""
    
    def __init__(
        self,
        message: str,
        token_count: Optional[int] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ):
        details = kwargs.get("details", {})
        if token_count:
            details["token_count"] = token_count
        if max_tokens:
            details["max_tokens"] = max_tokens
        
        super().__init__(
            message=message,
            error_code="TOKEN_LIMIT_ERROR",
            details=details
        )


class DefectDetectionError(PromptOptimizerError):
    """Raised when defect detection fails"""
    
    def __init__(self, message: str, agent: Optional[str] = None, **kwargs):
        details = kwargs.get("details", {})
        if agent:
            details["agent"] = agent
        
        super().__init__(
            message=message,
            error_code="DEFECT_DETECTION_ERROR",
            details=details
        )


class OptimizationError(PromptOptimizerError):
    """Raised when optimization fails"""
    
    def __init__(self, message: str, technique: Optional[str] = None, **kwargs):
        details = kwargs.get("details", {})
        if technique:
            details["technique"] = technique
        
        super().__init__(
            message=message,
            error_code="OPTIMIZATION_ERROR",
            details=details
        )


class AgentOrchestrationError(PromptOptimizerError):
    """Raised when multi-agent orchestration fails"""
    
    def __init__(
        self,
        message: str,
        failed_agents: Optional[list] = None,
        **kwargs
    ):
        details = kwargs.get("details", {})
        if failed_agents:
            details["failed_agents"] = failed_agents
        
        super().__init__(
            message=message,
            error_code="AGENT_ORCHESTRATION_ERROR",
            details=details
        )


class ResponseParseError(PromptOptimizerError):
    """Raised when LLM response parsing fails"""
    
    def __init__(
        self,
        message: str,
        response_text: Optional[str] = None,
        **kwargs
    ):
        details = kwargs.get("details", {})
        if response_text:
            # Only include first 200 chars to avoid huge error logs
            details["response_preview"] = response_text[:200] + "..."
        
        super().__init__(
            message=message,
            error_code="RESPONSE_PARSE_ERROR",
            details=details
        )


# =============================================================================
# Error Handler Functions
# =============================================================================

def handle_api_error(error: Exception, provider: str) -> LLMServiceError:
    """
    Convert various API errors to LLMServiceError
    
    Args:
        error: Original exception
        provider: LLM provider name
    
    Returns:
        LLMServiceError with appropriate details
    """
    error_message = str(error)
    
    # Check for common error patterns
    if "api_key" in error_message.lower() or "authentication" in error_message.lower():
        return APIKeyError(provider=provider)
    
    elif "rate" in error_message.lower() or "quota" in error_message.lower():
        return RateLimitError(provider=provider)
    
    elif "token" in error_message.lower() and "limit" in error_message.lower():
        return TokenLimitError(message=error_message)
    
    # Generic LLM service error
    return LLMServiceError(
        message=f"API call failed: {error_message}",
        provider=provider,
        details={"original_error": type(error).__name__}
    )


def handle_validation_error(error: Exception, field: Optional[str] = None) -> ValidationError:
    """
    Convert various validation errors to ValidationError
    
    Args:
        error: Original exception
        field: Field that failed validation
    
    Returns:
        ValidationError with appropriate details
    """
    return ValidationError(
        message=str(error),
        field=field,
        details={"original_error": type(error).__name__}
    )


def safe_error_response(error: Exception) -> Dict[str, Any]:
    """
    Create a safe error response dictionary
    
    Args:
        error: Exception to convert
    
    Returns:
        Dictionary suitable for API response
    """
    # If it's one of our custom errors, use its to_dict method
    if isinstance(error, PromptOptimizerError):
        return error.to_dict()
    
    # For other exceptions, create a generic response
    return {
        "error": True,
        "error_code": "INTERNAL_ERROR",
        "message": str(error),
        "details": {
            "type": type(error).__name__
        }
    }


def log_error_with_context(
    error: Exception,
    context: Dict[str, Any],
    level: str = "error"
) -> None:
    """
    Log error with additional context
    
    Args:
        error: Exception to log
        context: Additional context information
        level: Log level (error, warning, critical)
    """
    log_func = getattr(logger, level.lower(), logger.error)
    
    log_func(
        f"Error: {str(error)}",
        extra={
            "error_type": type(error).__name__,
            "context": context,
            "error_details": getattr(error, "details", {})
        }
    )


def retry_with_backoff(
    func,
    max_retries: int = 3,
    base_delay: float = 1.0,
    backoff_factor: float = 2.0,
    exceptions: tuple = (Exception,)
):
    """
    Decorator to retry a function with exponential backoff
    
    Args:
        func: Function to retry
        max_retries: Maximum number of retry attempts
        base_delay: Initial delay in seconds
        backoff_factor: Multiplier for delay on each retry
        exceptions: Tuple of exceptions to catch and retry
    
    Returns:
        Decorated function
    """
    import time
    from functools import wraps
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        delay = base_delay
        last_error = None
        
        for attempt in range(max_retries + 1):
            try:
                return func(*args, **kwargs)
            except exceptions as e:
                last_error = e
                
                if attempt == max_retries:
                    logger.error(
                        f"Function {func.__name__} failed after {max_retries} retries"
                    )
                    raise
                
                logger.warning(
                    f"Attempt {attempt + 1}/{max_retries} failed for {func.__name__}. "
                    f"Retrying in {delay}s..."
                )
                
                time.sleep(delay)
                delay *= backoff_factor
        
        # Should never reach here, but just in case
        if last_error:
            raise last_error
    
    return wrapper


# Export all error classes and handlers
__all__ = [
    # Base errors
    "PromptOptimizerError",
    "ValidationError",
    "ConfigurationError",
    
    # LLM errors
    "LLMServiceError",
    "APIKeyError",
    "RateLimitError",
    "TokenLimitError",
    
    # Processing errors
    "DefectDetectionError",
    "OptimizationError",
    "AgentOrchestrationError",
    "ResponseParseError",
    
    # Handler functions
    "handle_api_error",
    "handle_validation_error",
    "safe_error_response",
    "log_error_with_context",
    "retry_with_backoff"
]