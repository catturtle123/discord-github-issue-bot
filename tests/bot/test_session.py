"""Tests for bot.session module."""

import pytest

from agent.state import IssueState
from bot.session import SessionManager


@pytest.fixture
def manager() -> SessionManager:
    """Create a fresh SessionManager for each test."""
    return SessionManager()


@pytest.fixture
def sample_state() -> IssueState:
    """Sample IssueState for testing."""
    return {
        "messages": [{"role": "user", "content": "test message"}],
        "thread_id": "123",
        "user_id": "456",
    }


class TestSessionManager:
    """Tests for SessionManager CRUD operations."""

    @pytest.mark.asyncio
    async def test_get_session_returns_none_for_missing(self, manager: SessionManager) -> None:
        result = await manager.get_session(999)
        assert result is None

    @pytest.mark.asyncio
    async def test_create_and_get_session(
        self, manager: SessionManager, sample_state: IssueState
    ) -> None:
        await manager.create_session(100, sample_state)
        result = await manager.get_session(100)
        assert result is not None
        assert result["thread_id"] == "123"

    @pytest.mark.asyncio
    async def test_update_session(self, manager: SessionManager, sample_state: IssueState) -> None:
        await manager.create_session(100, sample_state)

        updated_state: IssueState = {
            **sample_state,
            "issue_title": "Updated title",
        }
        await manager.update_session(100, updated_state)

        result = await manager.get_session(100)
        assert result is not None
        assert result["issue_title"] == "Updated title"

    @pytest.mark.asyncio
    async def test_delete_session(self, manager: SessionManager, sample_state: IssueState) -> None:
        await manager.create_session(100, sample_state)
        await manager.delete_session(100)
        result = await manager.get_session(100)
        assert result is None

    @pytest.mark.asyncio
    async def test_delete_nonexistent_session_no_error(self, manager: SessionManager) -> None:
        await manager.delete_session(999)

    @pytest.mark.asyncio
    async def test_has_session_true(
        self, manager: SessionManager, sample_state: IssueState
    ) -> None:
        await manager.create_session(100, sample_state)
        assert await manager.has_session(100) is True

    @pytest.mark.asyncio
    async def test_has_session_false(self, manager: SessionManager) -> None:
        assert await manager.has_session(999) is False

    @pytest.mark.asyncio
    async def test_multiple_sessions(self, manager: SessionManager) -> None:
        state1: IssueState = {
            "messages": [{"role": "user", "content": "msg1"}],
            "thread_id": "t1",
            "user_id": "u1",
        }
        state2: IssueState = {
            "messages": [{"role": "user", "content": "msg2"}],
            "thread_id": "t2",
            "user_id": "u2",
        }
        await manager.create_session(1, state1)
        await manager.create_session(2, state2)

        r1 = await manager.get_session(1)
        r2 = await manager.get_session(2)
        assert r1 is not None and r1["thread_id"] == "t1"
        assert r2 is not None and r2["thread_id"] == "t2"

    @pytest.mark.asyncio
    async def test_create_overwrites_existing(
        self, manager: SessionManager, sample_state: IssueState
    ) -> None:
        await manager.create_session(100, sample_state)

        new_state: IssueState = {
            "messages": [{"role": "user", "content": "new"}],
            "thread_id": "999",
            "user_id": "789",
        }
        await manager.create_session(100, new_state)

        result = await manager.get_session(100)
        assert result is not None
        assert result["thread_id"] == "999"
