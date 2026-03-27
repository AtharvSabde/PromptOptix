"""
PromptOptimizer Pro - Response Parsing Utilities
Handles parsing of LLM responses, including JSON extraction from markdown
"""

import json
import re
from typing import Any, Dict, Optional, Union
from .logger import get_logger

logger = get_logger(__name__)


class ResponseParseError(Exception):
    """Custom exception for response parsing errors"""
    pass


def extract_json_from_markdown(text: str) -> str:
    """
    Extract JSON content from markdown code fences.

    LLMs (especially Gemini) often wrap JSON in ```json ... ``` blocks.
    This function robustly extracts the content, handling:
    - Standard ```json\\n...\\n``` fences
    - Missing closing fences (truncated responses)
    - \\r\\n line endings (Windows)
    - No newline between ```json and content
    """
    text = text.strip()

    # Pattern 1: ```json ... ``` (flexible whitespace, handles \r\n)
    json_fence_pattern = r'```json\s*(.*?)\s*```'
    match = re.search(json_fence_pattern, text, re.DOTALL | re.IGNORECASE)
    if match:
        content = match.group(1).strip()
        if content:
            logger.debug("Extracted JSON from ```json fence")
            return content

    # Pattern 2: ```json without closing ``` (truncated response)
    if re.match(r'^```json', text, re.IGNORECASE):
        content = re.sub(r'^```json\s*', '', text, flags=re.IGNORECASE).strip()
        if content.endswith('```'):
            content = content[:-3].strip()
        if content.startswith('{') or content.startswith('['):
            logger.debug("Extracted JSON from unclosed ```json fence")
            return content

    # Pattern 3: ``` ... ``` (generic code fence)
    generic_fence_pattern = r'```\s*(.*?)\s*```'
    match = re.search(generic_fence_pattern, text, re.DOTALL)
    if match:
        content = match.group(1).strip()
        if content.startswith('{') or content.startswith('['):
            logger.debug("Extracted JSON from generic ``` fence")
            return content

    # Pattern 4: Look for JSON object/array anywhere in text
    json_start = -1
    for i, char in enumerate(text):
        if char in ['{', '[']:
            json_start = i
            break

    if json_start >= 0:
        potential_json = text[json_start:].strip()
        # Remove trailing ``` if present
        if potential_json.endswith('```'):
            potential_json = potential_json[:-3].strip()
        try:
            json.loads(potential_json)
            logger.debug("Extracted raw JSON from text")
            return potential_json
        except json.JSONDecodeError:
            pass

    return text.strip()


def safe_json_parse(
    text: str,
    default: Optional[Any] = None,
    extract_from_markdown: bool = True
) -> Union[Dict, list, Any]:
    """
    Safely parse JSON with multiple fallback strategies
    
    Args:
        text: JSON string to parse
        default: Default value to return on failure
        extract_from_markdown: Whether to try extracting from markdown fences
    
    Returns:
        Parsed JSON object or default value
    """
    if not text:
        logger.warning("Empty text provided to JSON parser")
        return default if default is not None else {}
    
    # Step 1: Try extracting from markdown if enabled
    if extract_from_markdown:
        text = extract_json_from_markdown(text)
    
    # Step 2: Direct parse attempt
    try:
        result = json.loads(text)
        logger.debug("Successfully parsed JSON")
        return result
    except json.JSONDecodeError as e:
        logger.debug(f"Initial JSON parse failed: {e}")
    
    # Step 3: Try cleaning common issues
    cleaned_text = text.strip()
    
    # Remove trailing commas (common LLM error)
    cleaned_text = re.sub(r',\s*([}\]])', r'\1', cleaned_text)
    
    # Remove comments (not valid JSON but LLMs sometimes add them)
    cleaned_text = re.sub(r'//.*?\n', '\n', cleaned_text)
    cleaned_text = re.sub(r'/\*.*?\*/', '', cleaned_text, flags=re.DOTALL)
    
    try:
        result = json.loads(cleaned_text)
        logger.debug("Successfully parsed JSON after cleaning")
        return result
    except json.JSONDecodeError as e:
        logger.warning(f"JSON parse failed after cleaning: {e}")
    
    # Step 4: Last resort - try to find any valid JSON object/array
    for pattern in [r'\{.*\}', r'\[.*\]']:
        match = re.search(pattern, text, re.DOTALL)
        if match:
            try:
                result = json.loads(match.group(0))
                logger.debug("Successfully extracted and parsed JSON with regex")
                return result
            except json.JSONDecodeError:
                continue
    
    # All strategies failed
    logger.error(f"All JSON parsing strategies failed. Text: {text[:200]}...")
    return default if default is not None else {}


def parse_json_response(
    response_text: str,
    required_fields: Optional[list] = None,
    default: Optional[Dict] = None
) -> Dict:
    """
    Parse JSON response and validate required fields
    
    Args:
        response_text: Response text to parse
        required_fields: List of required field names
        default: Default value if parsing fails
    
    Returns:
        Parsed and validated JSON object
    
    Raises:
        ResponseParseError: If parsing fails and no default provided
    """
    # Parse the JSON
    result = safe_json_parse(response_text, default=default)
    
    if result is None or (isinstance(result, dict) and not result):
        if default is not None:
            logger.warning("Using default value due to parse failure")
            return default
        raise ResponseParseError("Failed to parse JSON response")
    
    # Validate required fields
    if required_fields and isinstance(result, dict):
        missing_fields = [field for field in required_fields if field not in result]
        if missing_fields:
            logger.warning(f"Missing required fields: {missing_fields}")
            if default is not None:
                return default
            raise ResponseParseError(f"Missing required fields: {', '.join(missing_fields)}")
    
    return result


def extract_code_blocks(text: str, language: Optional[str] = None) -> list:
    """
    Extract all code blocks from markdown text
    
    Args:
        text: Text containing code blocks
        language: Optional language filter (e.g., 'python', 'json')
    
    Returns:
        List of code block contents
    """
    if language:
        pattern = rf'```{language}\s*\n(.*?)\n```'
    else:
        pattern = r'```(?:\w+)?\s*\n(.*?)\n```'
    
    matches = re.findall(pattern, text, re.DOTALL | re.IGNORECASE)
    
    logger.debug(f"Extracted {len(matches)} code blocks")
    return [match.strip() for match in matches]


def clean_llm_response(text: str) -> str:
    """
    Clean common artifacts from LLM responses
    
    Args:
        text: LLM response text
    
    Returns:
        Cleaned text
    """
    # Remove thinking/reasoning tags if present
    text = re.sub(r'<thinking>.*?</thinking>', '', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<reasoning>.*?</reasoning>', '', text, flags=re.DOTALL | re.IGNORECASE)
    
    # Remove XML-style tags that might wrap content
    text = re.sub(r'<response>(.*?)</response>', r'\1', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<output>(.*?)</output>', r'\1', text, flags=re.DOTALL | re.IGNORECASE)
    
    # Clean up extra whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = text.strip()
    
    return text


def parse_list_response(text: str, numbered: bool = False) -> list:
    """
    Parse a bulleted or numbered list from text
    
    Args:
        text: Text containing a list
        numbered: Whether to expect numbered lists
    
    Returns:
        List of items
    """
    items = []
    
    if numbered:
        # Match numbered lists: 1. item, 2. item, etc.
        pattern = r'^\s*\d+\.\s+(.+)$'
    else:
        # Match bulleted lists: - item, * item, • item
        pattern = r'^\s*[-*•]\s+(.+)$'
    
    for line in text.split('\n'):
        match = re.match(pattern, line)
        if match:
            items.append(match.group(1).strip())
    
    return items


def extract_key_value_pairs(text: str) -> Dict[str, str]:
    """
    Extract key-value pairs from text
    
    Looks for patterns like:
    - Key: Value
    - **Key**: Value
    - Key = Value
    
    Args:
        text: Text containing key-value pairs
    
    Returns:
        Dictionary of extracted pairs
    """
    pairs = {}
    
    # Pattern: Key: Value or **Key**: Value
    pattern = r'(?:\*\*)?([^:\n]+?)(?:\*\*)?:\s*(.+?)(?:\n|$)'
    matches = re.findall(pattern, text)
    
    for key, value in matches:
        key = key.strip().strip('*').strip()
        value = value.strip()
        if key and value:
            pairs[key] = value
    
    return pairs


def validate_json_schema(data: Dict, schema: Dict) -> bool:
    """
    Simple JSON schema validation
    
    Args:
        data: Data to validate
        schema: Schema definition (simple format)
    
    Returns:
        True if valid, False otherwise
    
    Example schema:
        {
            "required": ["field1", "field2"],
            "types": {"field1": str, "field2": int}
        }
    """
    # Check required fields
    required_fields = schema.get("required", [])
    for field in required_fields:
        if field not in data:
            logger.warning(f"Missing required field: {field}")
            return False
    
    # Check types
    type_definitions = schema.get("types", {})
    for field, expected_type in type_definitions.items():
        if field in data:
            if not isinstance(data[field], expected_type):
                logger.warning(
                    f"Type mismatch for {field}: expected {expected_type.__name__}, "
                    f"got {type(data[field]).__name__}"
                )
                return False
    
    return True


# Export all functions
__all__ = [
    "ResponseParseError",
    "extract_json_from_markdown",
    "safe_json_parse",
    "parse_json_response",
    "extract_code_blocks",
    "clean_llm_response",
    "parse_list_response",
    "extract_key_value_pairs",
    "validate_json_schema"
]