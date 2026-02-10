# Discord GitHub Issue Bot

## Project Overview
Discord에서 대화를 통해 GitHub 이슈를 정제하고, AI가 자동 해결 가능 여부를 판단하여 라벨을 부착하면 GitHub Actions가 자동으로 코드를 수정하고 PR을 생성하는 파이프라인.

## Tech Stack
- **Language**: Python 3.12+
- **Discord**: discord.py (async, thread API)
- **AI Orchestration**: LangGraph (multi-turn state management)
- **LLM**: Claude API (Sonnet) via Anthropic SDK
- **GitHub**: PyGithub or githubkit
- **Auto-resolve**: GitHub Actions + claude-code-action
- **Session**: In-memory dict (initial) → Redis (later)

## Project Structure
```
discord-issue-bot/
├── bot/
│   ├── main.py              # Discord bot entrypoint
│   ├── events.py            # on_message, on_thread event handlers
│   └── session.py           # Per-thread session management
├── agent/
│   ├── graph.py             # LangGraph graph definition
│   ├── state.py             # IssueState definition
│   ├── nodes/
│   │   ├── analyze.py       # Extract issue info from messages
│   │   ├── check.py         # Completeness check
│   │   ├── ask.py           # Generate follow-up questions
│   │   ├── draft.py         # Draft issue + auto-resolve judgment
│   │   └── create.py        # Create GitHub issue
│   └── prompts/
│       ├── system.py        # System prompt
│       ├── analyze.py       # Analysis prompt
│       └── judge.py         # Auto-resolve judgment prompt
├── github/
│   ├── client.py            # GitHub API client
│   └── templates.py         # Issue body templates
├── .github/
│   └── workflows/
│       └── auto-resolve.yml # Auto-resolve workflow
├── config.py                # Environment variables, settings
├── requirements.txt
└── .env
```

## Architecture: LangGraph Flow
```
START → [analyze] → [check_completeness]
  ├── insufficient → [ask_question] → END (await user response)
  ├── sufficient  → [generate_draft] → END (await user confirmation)
  └── confirmed   → [create_issue] → END
```
Each node execution ends with END to wait for user response. Next message resumes from analyze with previous state.

## Key Conventions

### Language
- Code: English (variables, functions, comments)
- User-facing messages (Discord responses, issue body): Korean
- Prompts: Korean

### Code Style
- Use `async/await` throughout — the bot is fully asynchronous
- Type hints on all function signatures
- Pydantic models for structured data validation
- Use `TypedDict` for LangGraph state
- Environment variables via `python-dotenv`, access through `config.py`

### Error Handling
- Discord message handlers: catch all exceptions, reply with user-friendly error message in thread
- GitHub API calls: retry with exponential backoff (max 3 retries)
- LLM calls: handle rate limits and timeout gracefully

### LangGraph Nodes
- Each node is a pure function: `(state: IssueState) -> dict` returning only updated fields
- Nodes must not have side effects except `create.py` (GitHub API call)
- Prompts live in `agent/prompts/`, not inline in node code

### Testing
- Use `pytest` + `pytest-asyncio`
- Mock Discord API and GitHub API in tests
- Test LangGraph nodes independently with fixture states

## Environment Variables
```
DISCORD_BOT_TOKEN=
DISCORD_ISSUE_CHANNEL_ID=
ANTHROPIC_API_KEY=
GITHUB_TOKEN=
GITHUB_OWNER=
GITHUB_REPO=
DISCORD_WEBHOOK_URL=
```

## Commands
- `python -m bot.main` — Run the Discord bot
- `pytest` — Run tests
- `pytest --cov` — Run tests with coverage
- `ruff check .` — Lint
- `ruff format .` — Format
