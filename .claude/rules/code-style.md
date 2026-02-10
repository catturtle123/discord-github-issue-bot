# Code Style Rules

## Python
- Python 3.12+ features are allowed (type union `X | Y`, `match` statements)
- Always use type hints on function signatures
- Use `async def` for all Discord event handlers and LangGraph nodes that call LLM
- Prefer `Annotated` types for LangGraph state fields when adding reducers
- Use f-strings for string formatting, not `.format()` or `%`
- Imports: standard lib → third party → local, separated by blank lines
- Use `from __future__ import annotations` only if needed for forward refs

## Naming
- Files and modules: `snake_case`
- Classes: `PascalCase`
- Functions and variables: `snake_case`
- Constants: `UPPER_SNAKE_CASE`
- Private functions/methods: `_prefixed`

## Structure
- Keep functions short — under 30 lines preferred
- One class per file when the class is substantial
- Prompts go in `agent/prompts/`, never inline in node logic
- Config access only through `config.py`, never direct `os.environ`
