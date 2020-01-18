import os
import asyncio
import logging
import discord
from discord.ext import commands
from dotenv import load_dotenv
from bot_config import Config
from cogs.basic import Greetings

configuration = Config()

load_dotenv()

discord_oauth = os.getenv('DISCORD_TOKEN')

async def run_bot():
    """
    Sets up bot and attempts to run.
    Breaks on keyboard interrupt.
    """
    bot = Bot()
    bot.add_cog(Greetings(bot))
    print(bot.cogs)
    try: 
        await bot.start(discord_oauth)
    except KeyboardInterrupt:
        await bot.logout()

class Bot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix = configuration.get_property('prefix'),
            description = configuration.get_property('description'))

    def _setup(self):
        self.load_extension("cogs.basiccog")
    
    async def on_ready(self):
        print(f'Logged in as: {self.user.name}')
        print(f'User ID is {self.user.id}')

    async def on_message(self,message):
        """
        Trigger on everything.
        Ignore bots.  
        Ignore self.
        """

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_bot())