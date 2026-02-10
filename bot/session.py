from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from agent.state import IssueState


class SessionManager:
    """In-memory session manager mapping thread_id to IssueState."""

    def __init__(self) -> None:
        self._sessions: dict[int, IssueState] = {}
        self._lock = asyncio.Lock()

    async def get_session(self, thread_id: int) -> IssueState | None:
        """Retrieve session state for a thread. Returns None if not found."""
        async with self._lock:
            return self._sessions.get(thread_id)

    async def create_session(self, thread_id: int, state: IssueState) -> None:
        """Create a new session for a thread."""
        async with self._lock:
            self._sessions[thread_id] = state

    async def update_session(self, thread_id: int, state: IssueState) -> None:
        """Update the session state for a thread."""
        async with self._lock:
            self._sessions[thread_id] = state

    async def delete_session(self, thread_id: int) -> None:
        """Remove a session for a thread."""
        async with self._lock:
            self._sessions.pop(thread_id, None)

    async def has_session(self, thread_id: int) -> bool:
        """Check if a session exists for a thread."""
        async with self._lock:
            return thread_id in self._sessions


session_manager = SessionManager()
