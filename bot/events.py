from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING

import discord

from agent.state import IssueState
from bot.session import session_manager
from config import settings

if TYPE_CHECKING:
    from langgraph.graph.state import CompiledStateGraph

logger = logging.getLogger(__name__)

_graph: CompiledStateGraph | None = None


def _get_graph() -> CompiledStateGraph:
    """Lazy-load the LangGraph graph to avoid import cycles."""
    global _graph
    if _graph is None:
        from agent.graph import create_graph

        _graph = create_graph()
    return _graph


def setup_events(bot: discord.Client) -> None:
    """Register Discord event handlers on the bot."""

    @bot.event
    async def on_ready() -> None:
        logger.info("Bot is ready as %s (ID: %s)", bot.user, bot.user.id if bot.user else "?")

    @bot.event
    async def on_message(message: discord.Message) -> None:
        # Ignore messages from bots (including self)
        if message.author.bot:
            return

        # Ignore DMs
        if message.guild is None:
            return

        channel_id = str(message.channel.id)

        # --- Message in the configured issue channel (not a thread) ---
        if channel_id == settings.discord_issue_channel_id and not isinstance(
            message.channel, discord.Thread
        ):
            await _handle_new_issue(message)
            return

        # --- Message in a thread the bot owns ---
        if isinstance(message.channel, discord.Thread):
            thread = message.channel
            if thread.parent_id and str(thread.parent_id) == settings.discord_issue_channel_id:
                if await session_manager.has_session(thread.id):
                    await _handle_thread_message(message, thread)
            return

    # -----------------------------------------------------------------
    # Handlers
    # -----------------------------------------------------------------


async def _handle_new_issue(message: discord.Message) -> None:
    """Create a thread for a new issue conversation and run the agent."""
    try:
        thread = await message.create_thread(
            name=f"이슈: {message.content[:40]}",
            auto_archive_duration=1440,
        )

        initial_state: IssueState = {
            "messages": [{"role": "user", "content": message.content}],
            "thread_id": str(thread.id),
            "user_id": str(message.author.id),
        }

        await session_manager.create_session(thread.id, initial_state)
        await _run_agent_and_reply(thread, initial_state)

    except Exception:
        logger.exception("Error creating issue thread")
        try:
            await message.reply("죄송합니다, 이슈 생성 중 오류가 발생했습니다. 다시 시도해 주세요.")
        except Exception:
            logger.exception("Failed to send error reply")


async def _handle_thread_message(message: discord.Message, thread: discord.Thread) -> None:
    """Handle a follow-up message in an existing issue thread."""
    try:
        state = await session_manager.get_session(thread.id)
        if state is None:
            return

        # Append user message to state
        state["messages"] = state.get("messages", []) + [
            {"role": "user", "content": message.content}
        ]

        await _run_agent_and_reply(thread, state)

    except Exception:
        logger.exception("Error handling thread message")
        try:
            await thread.send("죄송합니다, 메시지 처리 중 오류가 발생했습니다. 다시 시도해 주세요.")
        except Exception:
            logger.exception("Failed to send error reply in thread")


async def _run_agent_and_reply(thread: discord.Thread, state: IssueState) -> None:
    """Invoke the LangGraph agent and send responses to the thread."""
    graph = _get_graph()
    msg_count_before = len(state.get("messages", []))
    result = await graph.ainvoke(state)

    # Update session with new state
    await session_manager.update_session(thread.id, result)

    # Extract only NEW messages added by this graph run
    all_messages = result.get("messages", [])
    new_messages = all_messages[msg_count_before:]
    assistant_messages = [msg for msg in new_messages if msg["role"] == "assistant"]

    # Handle confirmed status with no new messages (Phase 1: create_issue not yet implemented)
    if not assistant_messages and result.get("completeness_status") == "confirmed":
        await thread.send(
            "이슈 생성이 확인되었습니다. (이슈 생성 기능은 다음 업데이트에서 추가됩니다.)"
        )
        return

    # Send at most the last 2 assistant messages (rate-limit rule)
    for i, msg in enumerate(assistant_messages[-2:]):
        content = msg["content"]
        # Discord has a 2000 char limit
        if len(content) > 2000:
            content = content[:1997] + "..."
        await thread.send(content)
        # Small delay between multiple messages to avoid rapid-fire
        if i < len(assistant_messages[-2:]) - 1:
            await asyncio.sleep(1.0)
