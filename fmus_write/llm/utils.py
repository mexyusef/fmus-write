"""
Utility functions for LLM response handling.
"""
import json
import logging
from typing import Any, Dict, Optional, Union

logger = logging.getLogger(__name__)

def parse_llm_json_response(response_text: str, default_value: Optional[Any] = None) -> Union[Dict[str, Any], Any]:
    """
    Parse JSON from an LLM response, handling cases where the response is wrapped in markdown code blocks.

    Args:
        response_text: The raw text response from the LLM
        default_value: Value to return if parsing fails (if None, raises the exception)

    Returns:
        Parsed JSON data as a dictionary or the default value on failure

    Raises:
        json.JSONDecodeError: If parsing fails and no default value is provided
    """
    if not response_text:
        logger.warning("Empty response received from LLM")
        if default_value is not None:
            return default_value
        raise json.JSONDecodeError("Empty response", "", 0)

    # First try direct parsing
    try:
        return json.loads(response_text)
    except json.JSONDecodeError:
        # If direct parsing fails, check for markdown code blocks
        stripped_text = response_text.strip()

        # Check if the response is wrapped in a markdown code block
        if stripped_text.startswith("```") and stripped_text.endswith("```"):
            logger.info("Detected markdown code block, extracting content")

            # Remove the first line (which might contain ```json or similar)
            lines = stripped_text.split('\n')
            if len(lines) > 2:  # We need at least opening, content, and closing
                # Remove the first line (opening ```)
                content_lines = lines[1:-1]  # Skip first and last line
                extracted_content = '\n'.join(content_lines)

                try:
                    return json.loads(extracted_content)
                except json.JSONDecodeError:
                    logger.debug(f"Failed to parse extracted content: {extracted_content[:200]}...")

        # If the markdown extraction failed, try a simpler approach
        try:
            # Find content between opening and closing braces
            start = response_text.find("{")
            if start >= 0:
                end = response_text.rfind("}")
                if end > start:
                    content = response_text[start:end+1]
                    return json.loads(content)
        except Exception:
            pass

        # If all attempts failed
        logger.warning(f"Failed to parse JSON from LLM response: {response_text[:200]}...")
        if default_value is not None:
            return default_value

        # Re-raise as a new exception with more context
        raise json.JSONDecodeError(
            "Failed to parse JSON from LLM response",
            response_text,
            0
        )
