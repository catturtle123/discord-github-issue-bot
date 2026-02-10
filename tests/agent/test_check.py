"""Tests for agent.nodes.check module."""

from agent.nodes.check import check_completeness
from agent.state import IssueState


class TestCheckCompleteness:
    """Tests for the check_completeness node."""

    def test_insufficient_when_empty_state(self) -> None:
        state: IssueState = {}
        result = check_completeness(state)
        assert result == {"completeness_status": "insufficient"}

    def test_insufficient_when_missing_title(self) -> None:
        state: IssueState = {
            "issue_description": "Something is broken",
            "issue_type": "bug",
            "affected_domain": "auth",
        }
        result = check_completeness(state)
        assert result == {"completeness_status": "insufficient"}

    def test_insufficient_when_missing_description(self) -> None:
        state: IssueState = {
            "issue_title": "Login bug",
            "issue_type": "bug",
            "affected_domain": "auth",
        }
        result = check_completeness(state)
        assert result == {"completeness_status": "insufficient"}

    def test_insufficient_when_missing_type(self) -> None:
        state: IssueState = {
            "issue_title": "Login bug",
            "issue_description": "Cannot login",
            "affected_domain": "auth",
        }
        result = check_completeness(state)
        assert result == {"completeness_status": "insufficient"}

    def test_insufficient_when_missing_domain(self) -> None:
        state: IssueState = {
            "issue_title": "Login bug",
            "issue_description": "Cannot login",
            "issue_type": "bug",
        }
        result = check_completeness(state)
        assert result == {"completeness_status": "insufficient"}

    def test_sufficient_when_all_required_present(self) -> None:
        state: IssueState = {
            "issue_title": "Login bug",
            "issue_description": "Cannot login with OAuth",
            "issue_type": "bug",
            "affected_domain": "auth",
        }
        result = check_completeness(state)
        assert result == {"completeness_status": "sufficient"}

    def test_sufficient_with_extra_fields(self) -> None:
        state: IssueState = {
            "issue_title": "Add export feature",
            "issue_description": "Support CSV export",
            "issue_type": "feature",
            "affected_domain": "retrospect",
            "severity": "minor",
            "labels": ["enhancement"],
        }
        result = check_completeness(state)
        assert result == {"completeness_status": "sufficient"}

    def test_confirmed_with_draft_and_confirmation_keyword(self) -> None:
        state: IssueState = {
            "issue_title": "Fix typo",
            "issue_description": "Typo in error message",
            "issue_type": "bug",
            "affected_domain": "config",
            "draft_title": "Fix typo in error message",
            "draft_body": "## Description\nTypo fix...",
            "messages": [
                {"role": "user", "content": "오타 수정해주세요"},
                {"role": "assistant", "content": "이슈 초안입니다..."},
                {"role": "user", "content": "확인"},
            ],
        }
        result = check_completeness(state)
        assert result == {"completeness_status": "confirmed"}

    def test_confirmed_with_ok_keyword(self) -> None:
        state: IssueState = {
            "issue_title": "Fix",
            "issue_description": "Fix it",
            "issue_type": "bug",
            "affected_domain": "auth",
            "draft_title": "Fix",
            "draft_body": "body",
            "messages": [{"role": "user", "content": "ok"}],
        }
        result = check_completeness(state)
        assert result == {"completeness_status": "confirmed"}

    def test_confirmed_with_lgtm_keyword(self) -> None:
        state: IssueState = {
            "issue_title": "Fix",
            "issue_description": "Fix it",
            "issue_type": "bug",
            "affected_domain": "auth",
            "draft_title": "Fix",
            "draft_body": "body",
            "messages": [{"role": "user", "content": "LGTM"}],
        }
        result = check_completeness(state)
        assert result == {"completeness_status": "confirmed"}

    def test_not_confirmed_without_draft(self) -> None:
        """Even with confirmation keyword, insufficient if no draft."""
        state: IssueState = {
            "messages": [{"role": "user", "content": "확인"}],
        }
        result = check_completeness(state)
        assert result == {"completeness_status": "insufficient"}

    def test_not_confirmed_when_assistant_message_last(self) -> None:
        """Only user messages trigger confirmation."""
        state: IssueState = {
            "issue_title": "Fix",
            "issue_description": "Fix it",
            "issue_type": "bug",
            "affected_domain": "auth",
            "draft_title": "Fix",
            "draft_body": "body",
            "messages": [{"role": "assistant", "content": "확인해주세요"}],
        }
        result = check_completeness(state)
        assert result == {"completeness_status": "sufficient"}

    def test_sufficient_with_draft_but_no_confirmation(self) -> None:
        """Draft exists but user asks for modification."""
        state: IssueState = {
            "issue_title": "Fix",
            "issue_description": "Fix it",
            "issue_type": "bug",
            "affected_domain": "auth",
            "draft_title": "Fix",
            "draft_body": "body",
            "messages": [{"role": "user", "content": "제목을 수정해주세요"}],
        }
        result = check_completeness(state)
        assert result == {"completeness_status": "sufficient"}

    def test_returns_only_completeness_status(self) -> None:
        """Node should return only the fields it updates."""
        state: IssueState = {
            "issue_title": "Test",
            "issue_description": "Test",
            "issue_type": "bug",
            "affected_domain": "auth",
        }
        result = check_completeness(state)
        assert set(result.keys()) == {"completeness_status"}
