from __future__ import annotations

from agent.state import IssueState

_REQUIRED_FIELDS = ["issue_title", "issue_description", "issue_type", "affected_domain"]

_CONFIRMATION_KEYWORDS = frozenset(
    {
        "확인",
        "네",
        "예",
        "ㅇㅇ",
        "좋아",
        "좋습니다",
        "생성",
        "만들어",
        "등록",
        "ㅇ",
        "ok",
        "yes",
        "lgtm",
    }
)


def check_completeness(state: IssueState) -> dict:
    """Determine whether collected issue info is sufficient, needs more, or is confirmed."""
    # If a draft already exists, check if the user confirmed
    if state.get("draft_title") and state.get("draft_body"):
        messages = state.get("messages", [])
        if messages and messages[-1]["role"] == "user":
            content = messages[-1]["content"].strip().lower()
            if content in _CONFIRMATION_KEYWORDS:
                return {"completeness_status": "confirmed"}

    # Check required fields
    missing = [f for f in _REQUIRED_FIELDS if not state.get(f)]
    if missing:
        return {"completeness_status": "insufficient"}

    return {"completeness_status": "sufficient"}
