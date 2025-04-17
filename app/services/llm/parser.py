"""Parser utilities for LLM responses."""
import json
import re
from typing import Any, Dict

from app import logger


def normalize_llm_content(content: Any) -> str:
    """
    Normalize LLM content to a string regardless of its type.
    
    Args:
        content: The content from an LLM response, which could be:
            - A string
            - A list (potentially containing dictionaries with 'text' fields)
            - A dictionary with a 'text' field
            - Other formats
            
    Returns:
        A normalized string representation of the content
    """
    # Log the content type for debugging
    content_type = type(content).__name__
    logger.debug(f"Response content type: {content_type}")
    
    if isinstance(content, str):
        return content
    elif isinstance(content, list):
        # Special handling for Amazon Nova format (list of dictionaries with 'text' field)
        logger.debug(f"Processing list content: {str(content)}")
        if content and isinstance(content[0], dict) and 'text' in content[0]:
            logger.debug("Detected Amazon Nova format, extracting text field")
            return content[0]['text']
        else:
            # For other types of lists
            logger.debug("Converting generic list to string")
            return ''.join(str(item) for item in content)
    elif isinstance(content, dict) and 'text' in content:
        # Direct dictionary with 'text' field
        logger.debug(f"Extracting text from dictionary: {content}")
        return content['text']
    else:
        # For any other type, convert to string
        logger.debug(f"Converting {content_type} content to string: {content}")
        return str(content)


def extract_json_from_text(text: str) -> str:
    """
    Extract JSON from a mixed text and JSON string.
    
    Args:
        text: Text that may contain JSON
        
    Returns:
        Extracted JSON string or original text if no JSON found
    """
    # First check if the entire text is valid JSON
    try:
        json.loads(text)
        return text
    except json.JSONDecodeError:
        pass
    
    # Try to find JSON within markdown code blocks
    json_pattern = r"```(?:json)?\s*([\s\S]*?)\s*```"
    matches = re.findall(json_pattern, text)
    
    if matches:
        # Try each match, starting from the last one
        for match in reversed(matches):
            try:
                json_str = match.strip()
                json.loads(json_str)  # Validate it's valid JSON
                return json_str
            except json.JSONDecodeError:
                continue
    
    # If no valid JSON in code blocks, look for JSON-like structure
    # First try to find the outermost balanced braces
    text = text.strip()
    start_idx = text.find('{')
    
    if start_idx >= 0:
        # Count opening and closing braces to find the matching end brace
        brace_count = 0
        for i in range(start_idx, len(text)):
            if text[i] == '{':
                brace_count += 1
            elif text[i] == '}':
                brace_count -= 1
                if brace_count == 0:
                    # Found a complete JSON object
                    json_candidate = text[start_idx:i+1]
                    try:
                        json.loads(json_candidate)
                        return json_candidate
                    except json.JSONDecodeError:
                        # Not valid JSON, continue searching
                        pass
    
    # If all else fails, use a simpler regex approach as a last resort
    json_candidate_pattern = r"\{[\s\S]*?\}"
    matches = re.findall(json_candidate_pattern, text)
    
    for match in matches:
        try:
            json.loads(match)
            return match
        except json.JSONDecodeError:
            continue
    
    # Return original if no JSON found
    return text


def parse_json_response(content: str) -> Dict[str, Any]:
    """
    Parse JSON from LLM response that may contain mixed text and JSON.
    
    Args:
        content: String content from LLM that may contain JSON
        
    Returns:
        Parsed JSON as a dictionary
    """
    try:
        # First try direct parsing
        return json.loads(content)
    except json.JSONDecodeError:
        # If direct parsing fails, try to extract JSON from text
        json_str = extract_json_from_text(content)
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from content: {e}")
            logger.error(f"Content: {content}")
            logger.error(f"Extracted JSON string: {json_str}")
            raise ValueError(f"Could not parse JSON from LLM response: {e}")
