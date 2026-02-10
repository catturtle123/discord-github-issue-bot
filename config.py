from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Discord
    discord_bot_token: str = Field(description="Discord bot authentication token")
    discord_issue_channel_id: str = Field(description="Discord channel ID for issue conversations")
    discord_webhook_url: str = Field(
        default="", description="Discord webhook URL for notifications"
    )

    # Anthropic
    anthropic_api_key: str = Field(description="Anthropic API key for Claude")

    # GitHub
    github_token: str = Field(description="GitHub personal access token")
    github_owner: str = Field(description="GitHub repository owner")
    github_repo: str = Field(description="GitHub repository name")

    # LLM settings
    llm_model: str = Field(default="claude-sonnet-4-5-20250929", description="Claude model to use")
    llm_max_tokens: int = Field(default=4096, description="Maximum tokens for LLM response")

    @property
    def github_repo_full(self) -> str:
        """Full repository name in owner/repo format."""
        return f"{self.github_owner}/{self.github_repo}"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
