import os
import asyncio
import logging
import discord
from discord.ext import commands
from dotenv import load_dotenv, find_dotenv
from westmarch.bot_config import Config
from westmarch.cogs.basic import Basic
from westmarch.cogs.db_commands import WM_Commands
from westmarch.db import db
from westmarch.db import models


configuration = Config()

load_dotenv(find_dotenv())

discord_oauth = os.getenv("DISCORD_TOKEN")
user = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")
hostname = os.getenv("DB_HOST", "localhost")
port = os.getenv("DB_PORT", 5432)
database = os.getenv("DATABASE_NAME", "west_march")
file_loc = "./test_db.db"


async def run_bot():
    """
    Sets up bot and attempts to run.
    Breaks on keyboard interrupt.
    """

    engine, ses = db.connect(file_loc)
    bot = Bot(engine=engine, session=ses)
    bot.add_cog(Basic(bot))
    bot.add_cog(WM_Commands(bot))
    print(engine.url)
    try:
        await bot.start(discord_oauth)
    except KeyboardInterrupt:
        await bot.logout()


class Bot(commands.Bot):
    def __init__(self, engine, session):
        super().__init__(
            command_prefix=configuration.get_property("prefix"),
            description=configuration.get_property("description"),
        )
        self.engine = engine
        self.session = session

    def _setup(self):
        self.load_extension("cogs.basiccog")

    async def on_ready(self):
        print(f"Logged in as: {self.user.name}")
        print(f"User ID is {self.user.id}")

    async def on_message(self, message):
        """
        Trigger on everything.
        Ignore bots.  
        Ignore self.
        """

        if message.author.bot:
            return
        await self.process_commands(message)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_bot())
