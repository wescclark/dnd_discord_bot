import os
import asyncio
import logging
import discord
from discord.ext import commands
from dotenv import load_dotenv
from bot_config import Config

configuration = Config()

load_dotenv()

discord_oauth = os.getenv('DISCORD_TOKEN')

async def run_bot():
    bot = Bot()

    try: 
        await bot.start(discord_oauth)
    except KeyboardInterrupt:
        await bot.logout()

class Bot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix = configuration.get_property('prefix'),
            description = configuration.get_property('description'))
    
    async def on_ready(self):
        print(f'Logged in as: {self.user.name}')
        print(f'User ID is {self.user.id}')


if __name__ == '__main__':
    run_bot()