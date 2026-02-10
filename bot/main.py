import logging

import discord

from bot.events import setup_events
from config import settings

logger = logging.getLogger(__name__)

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.guild_messages = True

bot = discord.Client(intents=intents)

setup_events(bot)


def run_bot() -> None:
    """Start the Discord bot."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    logger.info("Starting Discord GitHub Issue Bot...")
    bot.run(settings.discord_bot_token, log_handler=None)


if __name__ == "__main__":
    run_bot()
