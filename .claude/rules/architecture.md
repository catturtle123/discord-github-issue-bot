# Architecture Rules

## LangGraph
- State must use `TypedDict` (IssueState in `agent/state.py`)
- Each node returns only the fields it updates, not the full state
- Nodes must be stateless functions — all state flows through IssueState
- Conditional edges handle routing logic, not nodes themselves
- Never call Discord API from inside LangGraph nodes — return messages, let the bot layer send them

## Discord Bot
- Thread-per-issue: every issue conversation happens in a dedicated thread
- Session management ties thread_id → LangGraph state (checkpointer or in-memory dict)
- Bot should only respond in threads it created, ignore other messages
- Rate limit Discord messages: don't send more than 2 messages in rapid succession

## GitHub Integration
- All GitHub operations go through `github/client.py`
- Issue body must follow the template in `github/templates.py`
- Labels are applied at creation time, not as a separate API call
- auto-resolve label triggers GitHub Actions — this is the contract between bot and CI

## Separation of Concerns
- `bot/` — Discord I/O only, no business logic
- `agent/` — AI logic, prompt management, state machine
- `github/` — GitHub API wrapper, templates
- `config.py` — Single source of truth for all configuration
