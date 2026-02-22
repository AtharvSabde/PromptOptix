"""
PromptOptimizer Pro - LLM Service Layer
Abstracts LLM API calls with support for multiple providers (Anthropic, Groq, OpenAI, Gemini)
"""

import time
from typing import Dict, Any, Optional, List
from anthropic import Anthropic, APIError, APIConnectionError, RateLimitError as AnthropicRateLimitError
from groq import Groq
from openai import OpenAI
from google import genai
import os

from ..config import Config, LLMProvider
from ..utils import (
    get_logger,
    LLMServiceError,
    APIKeyError,
    RateLimitError,
    TokenLimitError,
    parse_json_response,
    count_tokens,
    estimate_cost,
    retry_with_backoff
)

logger = get_logger(__name__)


class LLMService:
    """
    Singleton service for making LLM API calls
    Supports Anthropic Claude, Groq, OpenAI, and Gemini — no automatic fallback
    """

    _instance = None
    _initialized = False

    VALID_PROVIDERS = ["anthropic", "groq", "openai", "gemini"]

    def __new__(cls):
        """Ensure only one instance exists (Singleton pattern)"""
        if cls._instance is None:
            cls._instance = super(LLMService, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize LLM clients"""
        if self._initialized:
            return

        logger.info("Initializing LLM Service")

        # Initialize clients
        self.anthropic_client = None
        self.groq_client = None
        self.openai_client = None
        self.gemini_configured = False

        # Setup Anthropic client
        if Config.ANTHROPIC_API_KEY:
            try:
                self.anthropic_client = Anthropic(api_key=Config.ANTHROPIC_API_KEY)
                logger.info("Anthropic client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Anthropic client: {e}")
        else:
            logger.warning("Anthropic API key not found")

        # Setup Groq client
        if Config.GROQ_API_KEY:
            try:
                self.groq_client = Groq(api_key=Config.GROQ_API_KEY)
                logger.info("Groq client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Groq client: {e}")
        else:
            logger.warning("Groq API key not found")

        # Setup OpenAI client
        if Config.OPENAI_API_KEY:
            try:
                self.openai_client = OpenAI(api_key=Config.OPENAI_API_KEY)
                logger.info("OpenAI client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}")
        else:
            logger.warning("OpenAI API key not found")

        # Setup Gemini client (google-genai SDK)
        if Config.GEMINI_API_KEY:
            try:
                self.gemini_client = genai.Client(api_key=Config.GEMINI_API_KEY)
                self.gemini_configured = True
                logger.info("Gemini client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini client: {e}")
        else:
            logger.warning("Gemini API key not found")

        # Validate at least one provider is available
        if not any([self.anthropic_client, self.groq_client, self.openai_client, self.gemini_configured]):
            raise APIKeyError(
                provider="all",
                details={"message": "No valid API keys found for any provider"}
            )

        self._initialized = True
        available = [p for p, ok in [
            ("anthropic", self.anthropic_client),
            ("groq", self.groq_client),
            ("openai", self.openai_client),
            ("gemini", self.gemini_configured)
        ] if ok]
        logger.info(f"LLM Service initialization complete. Available providers: {available}")
    
    def _call_anthropic(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        max_tokens: int = 4096,
        temperature: float = 0.3,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Make API call to Anthropic Claude
        
        Args:
            prompt: User prompt
            system_prompt: System instructions
            model: Model name (defaults to Config.ANTHROPIC_MODEL)
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            **kwargs: Additional API parameters
        
        Returns:
            API response dictionary
        
        Raises:
            LLMServiceError: If API call fails
        """
        if not self.anthropic_client:
            raise APIKeyError(provider="anthropic")
        
        if model is None:
            model = Config.ANTHROPIC_MODEL
        
        try:
            # Count input tokens
            input_text = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
            input_tokens = count_tokens(input_text, model)
            
            logger.info(
                f"Calling Anthropic API",
                extra={
                    "model": model,
                    "input_tokens": input_tokens,
                    "max_tokens": max_tokens
                }
            )
            
            # Build messages
            messages = [{"role": "user", "content": prompt}]
            
            # Make API call
            response = self.anthropic_client.messages.create(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_prompt if system_prompt else "",
                messages=messages,
                **kwargs
            )
            
            # Extract response text
            response_text = response.content[0].text
            
            # Count output tokens
            output_tokens = count_tokens(response_text, model)
            
            # Estimate cost
            cost_info = estimate_cost(
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                provider="anthropic",
                model=model
            )
            
            logger.info(
                f"Anthropic API call successful",
                extra={
                    "output_tokens": output_tokens,
                    "total_cost": cost_info["total_cost"]
                }
            )
            
            return {
                "provider": "anthropic",
                "model": model,
                "response": response_text,
                "usage": {
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "total_tokens": input_tokens + output_tokens
                },
                "cost": cost_info,
                "raw_response": response
            }
            
        except AnthropicRateLimitError as e:
            logger.error(f"Anthropic rate limit error: {e}")
            raise RateLimitError(provider="anthropic")
        
        except APIConnectionError as e:
            logger.error(f"Anthropic connection error: {e}")
            raise LLMServiceError(
                message=f"Connection error: {str(e)}",
                provider="anthropic"
            )
        
        except APIError as e:
            logger.error(f"Anthropic API error: {e}")
            raise LLMServiceError(
                message=f"API error: {str(e)}",
                provider="anthropic",
                status_code=getattr(e, 'status_code', None)
            )
        
        except Exception as e:
            logger.error(f"Unexpected Anthropic error: {e}")
            raise LLMServiceError(
                message=f"Unexpected error: {str(e)}",
                provider="anthropic"
            )
    
    def _call_groq(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        max_tokens: int = 4096,
        temperature: float = 0.3,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Make API call to Groq
        
        Args:
            prompt: User prompt
            system_prompt: System instructions
            model: Model name (defaults to Config.GROQ_MODEL)
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            **kwargs: Additional API parameters
        
        Returns:
            API response dictionary
        
        Raises:
            LLMServiceError: If API call fails
        """
        if not self.groq_client:
            raise APIKeyError(provider="groq")
        
        if model is None:
            model = Config.GROQ_MODEL
        
        try:
            # Build messages
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            # Count input tokens (approximation for Groq)
            input_text = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
            input_tokens = count_tokens(input_text, model)
            
            logger.info(
                f"Calling Groq API",
                extra={
                    "model": model,
                    "input_tokens": input_tokens,
                    "max_tokens": max_tokens
                }
            )
            
            # Make API call
            response = self.groq_client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                **kwargs
            )
            
            # Extract response text
            response_text = response.choices[0].message.content
            
            # Get token usage from response
            usage = response.usage
            output_tokens = usage.completion_tokens if hasattr(usage, 'completion_tokens') else count_tokens(response_text, model)
            
            # Estimate cost
            cost_info = estimate_cost(
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                provider="groq",
                model=model
            )
            
            logger.info(
                f"Groq API call successful",
                extra={
                    "output_tokens": output_tokens,
                    "total_cost": cost_info["total_cost"]
                }
            )
            
            return {
                "provider": "groq",
                "model": model,
                "response": response_text,
                "usage": {
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "total_tokens": input_tokens + output_tokens
                },
                "cost": cost_info,
                "raw_response": response
            }
            
        except Exception as e:
            error_message = str(e).lower()
            
            # Check for rate limit
            if "rate" in error_message or "quota" in error_message:
                logger.error(f"Groq rate limit error: {e}")
                raise RateLimitError(provider="groq")
            
            # Check for auth errors
            if "auth" in error_message or "api_key" in error_message:
                logger.error(f"Groq authentication error: {e}")
                raise APIKeyError(provider="groq")
            
            # Generic error
            logger.error(f"Groq API error: {e}")
            raise LLMServiceError(
                message=f"API error: {str(e)}",
                provider="groq"
            )
    
    def _call_openai(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        max_tokens: int = 4096,
        temperature: float = 0.3,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Make API call to OpenAI

        Args:
            prompt: User prompt
            system_prompt: System instructions
            model: Model name (defaults to Config.OPENAI_MODEL)
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature

        Returns:
            API response dictionary

        Raises:
            LLMServiceError: If API call fails
        """
        if not self.openai_client:
            raise APIKeyError(
                provider="openai",
                details={"message": "OpenAI API key is not configured. Add OPENAI_API_KEY to your .env file."}
            )

        if model is None:
            model = Config.OPENAI_MODEL

        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            input_text = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
            input_tokens = count_tokens(input_text, model)

            logger.info(
                f"Calling OpenAI API",
                extra={"model": model, "input_tokens": input_tokens, "max_tokens": max_tokens}
            )

            response = self.openai_client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
            )

            response_text = response.choices[0].message.content
            usage = response.usage
            output_tokens = usage.completion_tokens if usage else count_tokens(response_text, model)

            cost_info = estimate_cost(
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                provider="openai",
                model=model
            )

            logger.info(
                f"OpenAI API call successful",
                extra={"output_tokens": output_tokens, "total_cost": cost_info["total_cost"]}
            )

            return {
                "provider": "openai",
                "model": model,
                "response": response_text,
                "usage": {
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "total_tokens": input_tokens + output_tokens
                },
                "cost": cost_info,
                "raw_response": response
            }

        except Exception as e:
            error_message = str(e).lower()

            if "rate" in error_message or "quota" in error_message:
                logger.error(f"OpenAI rate limit error: {e}")
                raise RateLimitError(provider="openai")

            if "auth" in error_message or "api_key" in error_message or "invalid" in error_message:
                logger.error(f"OpenAI authentication error: {e}")
                raise APIKeyError(
                    provider="openai",
                    details={"message": f"OpenAI authentication failed: {str(e)}"}
                )

            logger.error(f"OpenAI API error: {e}")
            raise LLMServiceError(
                message=f"OpenAI API error: {str(e)}",
                provider="openai"
            )

    def _call_gemini(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        max_tokens: int = 4096,
        temperature: float = 0.3,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Make API call to Google Gemini

        Args:
            prompt: User prompt
            system_prompt: System instructions
            model: Model name (defaults to Config.GEMINI_MODEL)
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature

        Returns:
            API response dictionary

        Raises:
            LLMServiceError: If API call fails
        """
        if not self.gemini_configured:
            raise APIKeyError(
                provider="gemini",
                details={"message": "Gemini API key is not configured. Add GEMINI_API_KEY to your .env file."}
            )

        if model is None:
            model = Config.GEMINI_MODEL

        try:
            input_text = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
            input_tokens = count_tokens(input_text, model)

            logger.info(
                f"Calling Gemini API",
                extra={"model": model, "input_tokens": input_tokens, "max_tokens": max_tokens}
            )

            config = genai.types.GenerateContentConfig(
                max_output_tokens=max_tokens,
                temperature=temperature,
                system_instruction=system_prompt if system_prompt else None
            )

            response = self.gemini_client.models.generate_content(
                model=model,
                contents=prompt,
                config=config
            )
            response_text = response.text

            output_tokens = count_tokens(response_text, model)

            cost_info = estimate_cost(
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                provider="gemini",
                model=model
            )

            logger.info(
                f"Gemini API call successful",
                extra={"output_tokens": output_tokens, "total_cost": cost_info["total_cost"]}
            )

            return {
                "provider": "gemini",
                "model": model,
                "response": response_text,
                "usage": {
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "total_tokens": input_tokens + output_tokens
                },
                "cost": cost_info,
                "raw_response": response
            }

        except Exception as e:
            error_message = str(e).lower()

            if "rate" in error_message or "quota" in error_message or "resource" in error_message:
                logger.error(f"Gemini rate limit error: {e}")
                raise RateLimitError(provider="gemini")

            if "api_key" in error_message or "permission" in error_message or "403" in error_message:
                logger.error(f"Gemini authentication error: {e}")
                raise APIKeyError(
                    provider="gemini",
                    details={"message": f"Gemini authentication failed: {str(e)}"}
                )

            logger.error(f"Gemini API error: {e}")
            raise LLMServiceError(
                message=f"Gemini API error: {str(e)}",
                provider="gemini"
            )

    def call(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        max_tokens: int = 4096,
        temperature: float = 0.3,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Make LLM API call to the specified provider (NO automatic fallback).
        If the provider fails, the error is raised directly with a clear message.

        Args:
            prompt: User prompt
            system_prompt: System instructions
            provider: Provider to use (anthropic, groq, openai, gemini). Uses default if None
            model: Model name (provider-specific)
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            **kwargs: Additional API parameters

        Returns:
            API response dictionary with:
                - provider: Provider used
                - model: Model used
                - response: Generated text
                - usage: Token usage statistics
                - cost: Cost information

        Raises:
            LLMServiceError: If the provider call fails
        """
        # Determine provider
        if provider is None:
            provider = Config.DEFAULT_PROVIDER

        provider = provider.lower()

        # Validate provider
        if provider not in self.VALID_PROVIDERS:
            raise LLMServiceError(
                message=f"Invalid provider: '{provider}'. Must be one of: {', '.join(self.VALID_PROVIDERS)}",
                provider=provider
            )

        # Route to the correct provider — NO fallback, errors propagate directly
        call_args = dict(
            prompt=prompt,
            system_prompt=system_prompt,
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            **kwargs
        )

        if provider == "anthropic":
            return self._call_anthropic(**call_args)
        elif provider == "groq":
            return self._call_groq(**call_args)
        elif provider == "openai":
            return self._call_openai(**call_args)
        elif provider == "gemini":
            return self._call_gemini(**call_args)
    
    def call_with_json_response(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        required_fields: Optional[List[str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Make LLM call and parse JSON response
        
        Args:
            prompt: User prompt (should request JSON output)
            system_prompt: System instructions
            required_fields: List of required fields in JSON response
            **kwargs: Additional call parameters
        
        Returns:
            Dictionary with:
                - parsed_response: Parsed JSON object
                - raw_response: Original response text
                - metadata: API call metadata (usage, cost, etc.)
        
        Raises:
            ResponseParseError: If JSON parsing fails
        """
        # Make API call
        result = self.call(prompt=prompt, system_prompt=system_prompt, **kwargs)
        
        # Parse JSON response
        parsed = parse_json_response(
            result["response"],
            required_fields=required_fields
        )
        
        return {
            "parsed_response": parsed,
            "raw_response": result["response"],
            "metadata": {
                "provider": result["provider"],
                "model": result["model"],
                "usage": result["usage"],
                "cost": result["cost"]
            }
        }
    
    def batch_call(
        self,
        prompts: List[str],
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Make multiple LLM calls (sequential for now)
        
        Args:
            prompts: List of prompts to process
            system_prompt: System instructions (same for all)
            **kwargs: Additional call parameters
        
        Returns:
            List of response dictionaries
        """
        results = []
        
        for i, prompt in enumerate(prompts):
            logger.info(f"Processing batch request {i+1}/{len(prompts)}")
            
            try:
                result = self.call(
                    prompt=prompt,
                    system_prompt=system_prompt,
                    **kwargs
                )
                results.append(result)
            
            except Exception as e:
                logger.error(f"Batch request {i+1} failed: {e}")
                results.append({
                    "error": True,
                    "error_message": str(e),
                    "prompt_index": i
                })
        
        return results


# Singleton instance
_llm_service = None


def get_llm_service() -> LLMService:
    """
    Get or create the singleton LLM service instance
    
    Returns:
        LLMService instance
    """
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service


# Export
__all__ = [
    "LLMService",
    "get_llm_service"
]