import json
import logging

logger = logging.getLogger(__name__)

MAX_MESSAGE_LENGTH = 4000


def parse_json_response(text: str) -> dict | None:
    """Extract JSON from LLM response, stripping code fences if present.

    Args:
        text: Raw LLM response text, possibly wrapped in markdown code fences.

    Returns:
        Parsed dict, or None if parsing fails.
    """
    content = text
    if "```json" in content:
        content = content.split("```json", 1)[1].split("```", 1)[0]
    elif "```" in content:
        content = content.split("```", 1)[1].split("```", 1)[0]
    try:
        return json.loads(content.strip())
    except json.JSONDecodeError:
        logger.warning("Failed to parse LLM response as JSON: %s", text[:200])
        return None


def ensure_str_content(content: str | list) -> str:
    """Ensure LLM response content is a string.

    LangChain's ChatAnthropic can return str or list[ContentBlock].
    This normalizes the response to a plain string.

    Args:
        content: The response.content value from LangChain.

    Returns:
        String representation of the content.
    """
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for block in content:
            if isinstance(block, str):
                parts.append(block)
            elif isinstance(block, dict) and "text" in block:
                parts.append(block["text"])
            else:
                parts.append(str(block))
        return "".join(parts)
    return str(content)


def truncate_message(text: str, max_length: int = MAX_MESSAGE_LENGTH) -> str:
    """Truncate a message to a maximum length.

    Args:
        text: The text to truncate.
        max_length: Maximum allowed length.

    Returns:
        Truncated text.
    """
    if len(text) <= max_length:
        return text
    return text[:max_length]
