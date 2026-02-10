from __future__ import annotations

import logging

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage

from agent.prompts.ask import get_ask_prompt
from agent.prompts.system import SYSTEM_PROMPT
from agent.state import IssueState
from agent.utils import ensure_str_content, truncate_message
from config import settings

logger = logging.getLogger(__name__)

_FIELD_LABELS: list[tuple[str, str]] = [
    ("issue_title", "이슈 제목"),
    ("issue_description", "이슈 설명"),
    ("issue_type", "이슈 유형 (bug/feature/improvement/question)"),
    ("affected_domain", "영향 도메인"),
]

_BUG_FIELD_LABELS: list[tuple[str, str]] = [
    ("steps_to_reproduce", "재현 단계"),
    ("expected_behavior", "기대 동작"),
    ("actual_behavior", "실제 동작"),
]


async def ask_question(state: IssueState) -> dict:
    """Generate follow-up questions for missing issue information."""
    missing: list[str] = []
    for field, label in _FIELD_LABELS:
        if not state.get(field):
            missing.append(label)

    if state.get("issue_type") == "bug":
        for field, label in _BUG_FIELD_LABELS:
            if not state.get(field):
                missing.append(label)

    messages = state.get("messages", [])
    conversation = "\n".join(f"[{m['role']}]: {truncate_message(m['content'])}" for m in messages)
    missing_text = "\n".join(f"- {item}" for item in missing) if missing else "- 추가 세부사항"

    prompt = get_ask_prompt(conversation, missing_text)

    llm = ChatAnthropic(
        model=settings.llm_model,
        max_tokens=settings.llm_max_tokens,
        api_key=settings.anthropic_api_key,
    )

    response = await llm.ainvoke(
        [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=prompt),
        ]
    )

    content = ensure_str_content(response.content)

    return {
        "messages": [{"role": "assistant", "content": content}],
    }
