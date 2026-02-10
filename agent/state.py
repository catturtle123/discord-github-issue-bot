import operator
from typing import Annotated, Literal, TypedDict


class Message(TypedDict):
    """A single message in the conversation."""

    role: Literal["user", "assistant"]
    content: str


class IssueState(TypedDict, total=False):
    """LangGraph state for issue creation conversation.

    Fields use total=False so nodes can return only the fields they update.
    The messages field uses operator.add reducer for append semantics.
    """

    # Conversation
    messages: Annotated[list[Message], operator.add]
    thread_id: str
    user_id: str

    # Extracted issue information
    issue_title: str
    issue_description: str
    issue_type: Literal["bug", "feature", "improvement", "question"]
    affected_domain: Literal["auth", "member", "retrospect", "ai", "webhook", "config", "other"]
    labels: list[str]
    severity: Literal["critical", "major", "minor"]

    # Bug-specific fields
    steps_to_reproduce: str
    expected_behavior: str
    actual_behavior: str
    environment_info: str

    # Workflow status
    completeness_status: Literal["insufficient", "sufficient", "confirmed"]

    # Draft
    draft_title: str
    draft_body: str

    # Auto-resolve judgment
    auto_resolve: bool
    auto_resolve_reason: str
