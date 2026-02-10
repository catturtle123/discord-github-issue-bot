# Security Rules

## Secrets
- NEVER hardcode tokens, API keys, or secrets in source code
- All secrets go in `.env` file (which is in `.gitignore`)
- Access secrets only through `config.py`
- Never log or print secret values, even partially

## Input Validation
- Sanitize Discord user messages before passing to LLM prompts (prevent prompt injection)
- Validate GitHub API responses before using them
- Limit message length sent to LLM to prevent abuse

## GitHub
- Use minimal required permissions for GITHUB_TOKEN
- Validate that issue creation targets the configured repo only
- Never expose GitHub tokens in Discord messages or issue bodies

## Discord
- Bot should only operate in the configured channel (DISCORD_ISSUE_CHANNEL_ID)
- Ignore DMs and messages from other bots
- Don't echo back raw user input without sanitization
