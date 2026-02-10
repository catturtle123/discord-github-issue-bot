from __future__ import annotations

import logging

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage

from agent.prompts.analyze import get_analyze_prompt
from agent.prompts.system import SYSTEM_PROMPT
from agent.state import IssueState
from agent.utils import ensure_str_content, parse_json_response, truncate_message
from config import settings

logger = logging.getLogger(__name__)

_FIELD_KEYS = [
    "issue_title",
    "issue_description",
    "issue_type",
    "affected_domain",
    "severity",
    "steps_to_reproduce",
    "expected_behavior",
    "actual_behavior",
    "environment_info",
    "labels",
]


async def analyze(state: IssueState) -> dict:
    """Analyze user messages and extract issue information."""
    messages = state.get("messages", [])
    if not messages:
        return {}

    latest_message = truncate_message(messages[-1]["content"])
    context = (
        "\n".join(f"[{m['role']}]: {truncate_message(m['content'])}" for m in messages[:-1])
        if len(messages) > 1
        else "없음"
    )

    llm = ChatAnthropic(
        model=settings.llm_model,
        max_tokens=settings.llm_max_tokens,
        api_key=settings.anthropic_api_key,
    )

    prompt = get_analyze_prompt(latest_message, context)
    response = await llm.ainvoke(
        [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=prompt),
        ]
    )

    content = ensure_str_content(response.content)
    data = parse_json_response(content)
    if data is None:
        return {}

    update: dict = {}
    for key in _FIELD_KEYS:
        value = data.get(key)
        if value is not None:
            update[key] = value

    return update
