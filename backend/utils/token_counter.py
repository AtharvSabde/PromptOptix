"""
PromptOptimizer Pro - Token Counting Utilities
Accurate token counting using tiktoken and cost estimation
"""

import tiktoken
from typing import Optional, Dict, Tuple
from ..config import Config
from .logger import get_logger

logger = get_logger(__name__)


# Cache tokenizer instances
_tokenizers = {}


def get_tokenizer(model: str = "claude-sonnet-4-5-20250929") -> tiktoken.Encoding:
    """
    Get or create a tokenizer instance for the specified model
    
    Args:
        model: Model name
    
    Returns:
        Tokenizer instance
    """
    # Use cl100k_base encoding for Claude models (approximation)
    encoding_name = Config.TIKTOKEN_ENCODING if hasattr(Config, 'TIKTOKEN_ENCODING') else "cl100k_base"
    
    if encoding_name not in _tokenizers:
        try:
            _tokenizers[encoding_name] = tiktoken.get_encoding(encoding_name)
            logger.debug(f"Loaded tokenizer: {encoding_name}")
        except Exception as e:
            logger.error(f"Failed to load tokenizer {encoding_name}: {e}")
            # Fallback to basic encoding
            _tokenizers[encoding_name] = tiktoken.get_encoding("cl100k_base")
    
    return _tokenizers[encoding_name]


def count_tokens(text: str, model: str = "claude-sonnet-4-5-20250929") -> int:
    """
    Count the number of tokens in a text string
    
    Args:
        text: Text to count tokens for
        model: Model name (for model-specific tokenization)
    
    Returns:
        Number of tokens
    """
    if not text:
        return 0
    
    try:
        tokenizer = get_tokenizer(model)
        tokens = tokenizer.encode(text)
        return len(tokens)
    except Exception as e:
        logger.warning(f"Token counting failed, using approximation: {e}")
        # Fallback to rough approximation: ~4 chars per token
        return len(text) // 4


def estimate_cost(
    input_tokens: int,
    output_tokens: int,
    provider: str = "anthropic",
    model: str = "claude-sonnet-4-5-20250929"
) -> Dict[str, float]:
    """
    Estimate the cost of an LLM API call
    
    Args:
        input_tokens: Number of input tokens
        output_tokens: Number of output tokens
        provider: LLM provider name
        model: Model name
    
    Returns:
        Dictionary with cost breakdown
    """
    # Get model configuration
    model_config = Config.get_model_config(provider, model)
    
    if not model_config:
        logger.warning(f"No cost data for {provider}/{model}, returning zeros")
        return {
            "input_cost": 0.0,
            "output_cost": 0.0,
            "total_cost": 0.0,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens
        }
    
    # Calculate costs (prices are per 1K tokens)
    input_cost = (input_tokens / 1000) * model_config.get("cost_per_1k_input", 0)
    output_cost = (output_tokens / 1000) * model_config.get("cost_per_1k_output", 0)
    total_cost = input_cost + output_cost
    
    return {
        "input_cost": round(input_cost, 6),
        "output_cost": round(output_cost, 6),
        "total_cost": round(total_cost, 6),
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "model": model,
        "provider": provider
    }


def validate_token_limit(
    text: str,
    max_tokens: Optional[int] = None,
    model: str = "claude-sonnet-4-5-20250929"
) -> Tuple[bool, int, int]:
    """
    Check if text is within token limits
    
    Args:
        text: Text to validate
        max_tokens: Maximum allowed tokens (uses model's limit if not specified)
        model: Model name
    
    Returns:
        Tuple of (is_valid, token_count, max_allowed)
    """
    token_count = count_tokens(text, model)
    
    if max_tokens is None:
        # Get model's context window
        provider = Config.DEFAULT_PROVIDER
        model_config = Config.get_model_config(provider, model)
        max_tokens = model_config.get("context_window", 200000)
    
    is_valid = token_count <= max_tokens
    
    if not is_valid:
        logger.warning(
            f"Token limit exceeded: {token_count} tokens > {max_tokens} limit"
        )
    
    return is_valid, token_count, max_tokens


def estimate_tokens_from_chars(char_count: int) -> int:
    """
    Rough estimation of token count from character count
    Used when tiktoken is not available
    
    Args:
        char_count: Number of characters
    
    Returns:
        Estimated token count
    """
    # Average: ~4 characters per token for English text
    return char_count // 4


def calculate_token_reduction(
    original_text: str,
    optimized_text: str,
    model: str = "claude-sonnet-4-5-20250929"
) -> Dict[str, any]:
    """
    Calculate token reduction between original and optimized prompts
    
    Args:
        original_text: Original prompt
        optimized_text: Optimized prompt
        model: Model name
    
    Returns:
        Dictionary with reduction metrics
    """
    original_tokens = count_tokens(original_text, model)
    optimized_tokens = count_tokens(optimized_text, model)
    
    reduction = original_tokens - optimized_tokens
    reduction_percent = (reduction / original_tokens * 100) if original_tokens > 0 else 0
    
    return {
        "original_tokens": original_tokens,
        "optimized_tokens": optimized_tokens,
        "tokens_reduced": reduction,
        "reduction_percent": round(reduction_percent, 2),
        "is_reduction": reduction > 0
    }


def get_token_budget_remaining(
    used_tokens: int,
    total_budget: int
) -> Dict[str, any]:
    """
    Calculate remaining token budget
    
    Args:
        used_tokens: Tokens already used
        total_budget: Total token budget
    
    Returns:
        Dictionary with budget info
    """
    remaining = total_budget - used_tokens
    percent_used = (used_tokens / total_budget * 100) if total_budget > 0 else 0
    
    return {
        "used_tokens": used_tokens,
        "total_budget": total_budget,
        "remaining_tokens": remaining,
        "percent_used": round(percent_used, 2),
        "is_over_budget": used_tokens > total_budget
    }


def compare_token_efficiency(
    prompts: Dict[str, str],
    model: str = "claude-sonnet-4-5-20250929"
) -> Dict[str, Dict[str, int]]:
    """
    Compare token counts across multiple prompts
    
    Args:
        prompts: Dictionary of {name: prompt_text}
        model: Model name
    
    Returns:
        Dictionary with token counts and rankings
    """
    results = {}
    
    for name, text in prompts.items():
        token_count = count_tokens(text, model)
        results[name] = {
            "tokens": token_count,
            "characters": len(text),
            "tokens_per_char": round(token_count / len(text), 3) if len(text) > 0 else 0
        }
    
    # Add rankings
    sorted_by_tokens = sorted(results.items(), key=lambda x: x[1]["tokens"])
    for rank, (name, _) in enumerate(sorted_by_tokens, 1):
        results[name]["rank"] = rank
    
    return results


# Export all functions
__all__ = [
    "get_tokenizer",
    "count_tokens",
    "estimate_cost",
    "validate_token_limit",
    "estimate_tokens_from_chars",
    "calculate_token_reduction",
    "get_token_budget_remaining",
    "compare_token_efficiency"
]