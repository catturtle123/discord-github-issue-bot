# Testing Rules

## Framework
- Use `pytest` with `pytest-asyncio` for async tests
- Test files mirror source structure: `tests/bot/`, `tests/agent/`, `tests/github/`
- Test file naming: `test_<module>.py`

## What to Test
- LangGraph nodes: test each node independently with crafted IssueState fixtures
- State transitions: verify correct routing based on check_completeness output
- GitHub client: mock API calls, verify request payloads
- Prompts: test that prompt templates render correctly with various inputs
- Discord events: mock discord.py objects, verify bot responses

## What NOT to Test
- Don't test LLM output content (non-deterministic)
- Don't test third-party library internals
- Don't write integration tests that require live API keys in CI

## Mocking
- Mock Anthropic API calls with fixed responses
- Mock Discord API with `unittest.mock` or `pytest-mock`
- Mock GitHub API responses
- Use fixtures for common IssueState configurations
