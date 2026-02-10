"""Tests for agent.state module."""

import operator
from typing import get_type_hints

from agent.state import IssueState, Message


class TestMessage:
    """Tests for the Message TypedDict."""

    def test_message_has_role_and_content(self) -> None:
        msg: Message = {"role": "user", "content": "hello"}
        assert msg["role"] == "user"
        assert msg["content"] == "hello"

    def test_message_assistant_role(self) -> None:
        msg: Message = {"role": "assistant", "content": "response"}
        assert msg["role"] == "assistant"


class TestIssueState:
    """Tests for the IssueState TypedDict."""

    def test_issue_state_is_total_false(self) -> None:
        """Nodes can return partial state dicts."""
        state: IssueState = {"issue_title": "test"}
        assert state["issue_title"] == "test"

    def test_issue_state_has_all_expected_fields(self) -> None:
        hints = get_type_hints(IssueState, include_extras=True)
        expected_fields = {
            "messages",
            "thread_id",
            "user_id",
            "issue_title",
            "issue_description",
            "issue_type",
            "affected_domain",
            "labels",
            "severity",
            "steps_to_reproduce",
            "expected_behavior",
            "actual_behavior",
            "environment_info",
            "completeness_status",
            "draft_title",
            "draft_body",
            "auto_resolve",
            "auto_resolve_reason",
        }
        assert expected_fields.issubset(set(hints.keys()))

    def test_messages_field_has_add_reducer(self) -> None:
        """messages field should use operator.add for LangGraph append semantics."""
        hints = get_type_hints(IssueState, include_extras=True)
        messages_hint = hints["messages"]
        # Annotated types have __metadata__
        assert hasattr(messages_hint, "__metadata__")
        assert operator.add in messages_hint.__metadata__

    def test_empty_state(self) -> None:
        state: IssueState = {}
        assert state.get("messages") is None
        assert state.get("issue_title") is None

    def test_full_state(self) -> None:
        state: IssueState = {
            "messages": [{"role": "user", "content": "bug"}],
            "thread_id": "123",
            "user_id": "456",
            "issue_title": "Login fails",
            "issue_description": "Cannot login",
            "issue_type": "bug",
            "affected_domain": "auth",
            "labels": ["bug", "domain:auth"],
            "severity": "critical",
            "steps_to_reproduce": "1. Go to login",
            "expected_behavior": "Should login",
            "actual_behavior": "Error 500",
            "environment_info": "Chrome",
            "completeness_status": "sufficient",
            "draft_title": "Login fails",
            "draft_body": "## Description\n...",
            "auto_resolve": False,
            "auto_resolve_reason": "Complex auth flow",
        }
        assert state["issue_type"] == "bug"
        assert state["severity"] == "critical"
        assert len(state["labels"]) == 2
