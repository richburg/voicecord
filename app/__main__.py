import asyncio
import logging
from pathlib import Path

from discord import Intents, Interaction
from discord.app_commands import (
    AppCommandError,
    BotMissingPermissions,
    MissingPermissions,
    errors,
)
from discord.ext.commands import Bot

from app.config import BOT_TOKEN
from app.database import init_db

intents = Intents.all()
bot = Bot(command_prefix="/", help_command=None, intents=intents)


@bot.tree.error
async def on_app_command_error(
    interaction: Interaction, error: AppCommandError
) -> None:
    if isinstance(error, BotMissingPermissions):
        await interaction.response.send_message("I'm missing permissions")

    elif isinstance(error, MissingPermissions):
        await interaction.response.send_message("You're missing permissions")

    elif isinstance(error, errors.CommandInvokeError):
        await interaction.response.send_message("Something went wrong")
        assert interaction.command
        logging.error(
            f"{interaction.command.name} raised an exception: {error.original}"
        )


async def find_cogs() -> list[str]:
    default = ["app.handlers"]
    found = [
        f"app.cogs.{file.stem}"
        for file in Path("app/cogs").iterdir()
        if file.suffix == ".py"
    ]
    return default + found


async def register_cogs():
    cogs = await find_cogs()
    for cog in cogs:
        try:
            await bot.load_extension(cog)
        except Exception as error:
            logging.error(f"Failed to load cog {cog}", exc_info=error)


async def main():
    async with bot:
        await init_db()
        await register_cogs()
        try:
            await bot.start(BOT_TOKEN)
        except Exception as error:
            logging.critical("Failed to start bot", exc_info=error)


if __name__ == "__main__":
    asyncio.run(main())
