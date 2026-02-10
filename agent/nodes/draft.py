from __future__ import annotations

import logging

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage

from agent.prompts.draft import get_draft_prompt
from agent.prompts.judge import get_judge_prompt
from agent.prompts.system import SYSTEM_PROMPT
from agent.state import IssueState
from agent.utils import ensure_str_content, parse_json_response
from config import settings

logger = logging.getLogger(__name__)


async def generate_draft(state: IssueState) -> dict:
    """Generate an issue draft and judge auto-resolve feasibility."""
    title = state.get("issue_title", "")
    description = state.get("issue_description", "")
    issue_type = state.get("issue_type", "")
    affected_domain = state.get("affected_domain", "")
    severity = state.get("severity", "minor")
    steps = state.get("steps_to_reproduce", "")
    expected = state.get("expected_behavior", "")
    actual = state.get("actual_behavior", "")
    env_info = state.get("environment_info", "")
    labels = state.get("labels", [])

    llm = ChatAnthropic(
        model=settings.llm_model,
        max_tokens=settings.llm_max_tokens,
        api_key=settings.anthropic_api_key,
    )

    # --- Step 1: Generate issue draft ---
    labels_text = ", ".join(labels) if labels else "없음"
    draft_prompt = get_draft_prompt(
        title=title,
        description=description,
        issue_type=issue_type,
        affected_domain=affected_domain,
        severity=severity,
        steps=steps,
        expected=expected,
        actual=actual,
        env_info=env_info,
        labels_text=labels_text,
    )

    draft_response = await llm.ainvoke(
        [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=draft_prompt),
        ]
    )

    draft_content = ensure_str_content(draft_response.content)
    draft_data = parse_json_response(draft_content)
    if draft_data is None:
        draft_data = {"draft_title": title, "draft_body": description}

    draft_title = draft_data.get("draft_title", title)
    draft_body = draft_data.get("draft_body", description)

    # --- Step 2: Judge auto-resolve ---
    judge_prompt = get_judge_prompt(draft_title, draft_body, issue_type, affected_domain)
    judge_response = await llm.ainvoke(
        [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=judge_prompt),
        ]
    )

    auto_resolve = False
    auto_resolve_reason = ""
    auto_resolve_confidence = "low"
    judge_content = ensure_str_content(judge_response.content)
    judge_data = parse_json_response(judge_content)
    if judge_data is not None:
        auto_resolve = judge_data.get("auto_resolve", False)
        auto_resolve_reason = judge_data.get("reason", "")
        auto_resolve_confidence = judge_data.get("confidence", "low")

    # Downgrade auto_resolve for low-confidence judgments
    if auto_resolve and auto_resolve_confidence == "low":
        auto_resolve = False

    # --- Build preview message ---
    confidence_labels = {"high": "높음", "medium": "보통", "low": "낮음"}
    confidence_text = confidence_labels.get(auto_resolve_confidence, "낮음")
    auto_resolve_text = "가능" if auto_resolve else "불가"
    if auto_resolve_confidence == "medium" and auto_resolve:
        auto_resolve_text = "조건부 가능"

    preview = (
        f"**이슈 초안이 작성되었습니다.**\n\n"
        f"**제목**: {draft_title}\n\n"
        f"---\n"
        f"{draft_body}\n"
        f"---\n\n"
        f"**자동 해결 판단**: {auto_resolve_text} (확신도: {confidence_text})\n"
        f"**사유**: {auto_resolve_reason}\n\n"
        f"이대로 이슈를 생성할까요? (확인/수정 요청)"
    )

    return {
        "draft_title": draft_title,
        "draft_body": draft_body,
        "auto_resolve": auto_resolve,
        "auto_resolve_reason": auto_resolve_reason,
        "messages": [{"role": "assistant", "content": preview}],
    }
