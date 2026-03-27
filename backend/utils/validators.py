"""
PromptOptimizer Pro - Input Validation Utilities
Sanitizes and validates user inputs to prevent injection attacks
"""

import re
from typing import Optional, Any
from ..config import Config, TaskType, Domain, OptimizationLevel
from .logger import get_logger

logger = get_logger(__name__)


class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass


def sanitize_input(text: str, max_length: Optional[int] = None) -> str:
    """
    Sanitize text input by removing dangerous characters
    
    Args:
        text: Input text to sanitize
        max_length: Maximum allowed length
    
    Returns:
        Sanitized text
    
    Raises:
        ValidationError: If input is invalid
    """
    if not isinstance(text, str):
        raise ValidationError(f"Expected string, got {type(text).__name__}")
    
    # Remove null bytes (common injection technique)
    text = text.replace('\x00', '')
    
    # Limit length
    if max_length is None:
        max_length = Config.MAX_PROMPT_LENGTH
    
    if len(text) > max_length:
        logger.warning(f"Input truncated from {len(text)} to {max_length} characters")
        text = text[:max_length]
    
    # Strip leading/trailing whitespace
    text = text.strip()
    
    return text


def validate_prompt(prompt: str, min_length: Optional[int] = None) -> str:
    """
    Validate that a prompt meets minimum requirements
    
    Args:
        prompt: User prompt to validate
        min_length: Minimum required length
    
    Returns:
        Validated prompt
    
    Raises:
        ValidationError: If prompt is invalid
    """
    if not prompt:
        raise ValidationError("Prompt cannot be empty")
    
    # Sanitize first
    prompt = sanitize_input(prompt)
    
    # Check minimum length
    if min_length is None:
        min_length = Config.MIN_PROMPT_LENGTH
    
    if len(prompt) < min_length:
        raise ValidationError(
            f"Prompt too short: {len(prompt)} characters (minimum: {min_length})"
        )
    
    # Check if prompt is just whitespace or repeated characters
    if len(set(prompt.replace(' ', '').replace('\n', ''))) < 5:
        raise ValidationError("Prompt appears to be invalid or repetitive")
    
    return prompt


def validate_task_type(task_type: str) -> TaskType:
    """
    Validate and convert task_type to enum
    
    Args:
        task_type: Task type string
    
    Returns:
        TaskType enum value
    
    Raises:
        ValidationError: If task_type is invalid
    """
    try:
        return TaskType(task_type.lower())
    except ValueError:
        valid_types = [t.value for t in TaskType]
        raise ValidationError(
            f"Invalid task_type: '{task_type}'. Must be one of: {', '.join(valid_types)}"
        )


def validate_domain(domain: str) -> Domain:
    """
    Validate and convert domain to enum
    
    Args:
        domain: Domain string
    
    Returns:
        Domain enum value
    
    Raises:
        ValidationError: If domain is invalid
    """
    try:
        return Domain(domain.lower())
    except ValueError:
        valid_domains = [d.value for d in Domain]
        raise ValidationError(
            f"Invalid domain: '{domain}'. Must be one of: {', '.join(valid_domains)}"
        )


def validate_optimization_level(level: str) -> OptimizationLevel:
    """
    Validate and convert optimization level to enum
    
    Args:
        level: Optimization level string
    
    Returns:
        OptimizationLevel enum value
    
    Raises:
        ValidationError: If level is invalid
    """
    try:
        return OptimizationLevel(level.lower())
    except ValueError:
        valid_levels = [l.value for l in OptimizationLevel]
        raise ValidationError(
            f"Invalid optimization_level: '{level}'. Must be one of: {', '.join(valid_levels)}"
        )


def validate_provider(provider: str) -> str:
    """
    Validate LLM provider
    
    Args:
        provider: Provider name
    
    Returns:
        Validated provider name
    
    Raises:
        ValidationError: If provider is invalid
    """
    provider = provider.lower()
    valid_providers = ["anthropic", "groq", "openai", "gemini"]
    if provider not in valid_providers:
        raise ValidationError(
            f"Invalid provider: '{provider}'. Must be one of: {', '.join(valid_providers)}"
        )
    return provider


def validate_json_structure(data: dict, required_fields: list) -> None:
    """
    Validate that a dictionary has required fields
    
    Args:
        data: Dictionary to validate
        required_fields: List of required field names
    
    Raises:
        ValidationError: If required fields are missing
    """
    missing = [field for field in required_fields if field not in data]
    
    if missing:
        raise ValidationError(f"Missing required fields: {', '.join(missing)}")


def sanitize_json_output(obj: Any) -> Any:
    """
    Recursively sanitize JSON output to prevent XSS and injection
    
    Args:
        obj: Object to sanitize (dict, list, str, etc.)
    
    Returns:
        Sanitized object
    """
    if isinstance(obj, dict):
        return {k: sanitize_json_output(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [sanitize_json_output(item) for item in obj]
    elif isinstance(obj, str):
        # Remove potential XSS vectors
        obj = obj.replace('<script>', '').replace('</script>', '')
        obj = obj.replace('javascript:', '').replace('vbscript:', '').replace('data:', '')
        # Strip dangerous event handlers
        for handler in ['onclick', 'onload', 'onerror', 'onmouseover', 'onfocus', 'onblur']:
            obj = re.sub(rf'{handler}\s*=', '', obj, flags=re.IGNORECASE)
        return obj
    else:
        return obj


def validate_confidence_score(score: float) -> float:
    """
    Validate confidence score is in valid range
    
    Args:
        score: Confidence score
    
    Returns:
        Validated score
    
    Raises:
        ValidationError: If score is out of range
    """
    if not isinstance(score, (int, float)):
        raise ValidationError(f"Confidence score must be numeric, got {type(score).__name__}")
    
    if score < 0.0 or score > 1.0:
        raise ValidationError(f"Confidence score must be between 0 and 1, got {score}")
    
    return float(score)


def validate_severity(severity: str) -> str:
    """
    Validate defect severity level
    
    Args:
        severity: Severity level
    
    Returns:
        Validated severity
    
    Raises:
        ValidationError: If severity is invalid
    """
    severity = severity.lower()
    valid_severities = list(Config.SEVERITY_LEVELS.keys())
    
    if severity not in valid_severities:
        raise ValidationError(
            f"Invalid severity: '{severity}'. Must be one of: {', '.join(valid_severities)}"
        )
    
    return severity


# Export all validation functions
__all__ = [
    "ValidationError",
    "sanitize_input",
    "validate_prompt",
    "validate_task_type",
    "validate_domain",
    "validate_optimization_level",
    "validate_provider",
    "validate_json_structure",
    "sanitize_json_output",
    "validate_confidence_score",
    "validate_severity"
]