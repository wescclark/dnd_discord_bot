from discord.ext import commands
import discord

class Greetings(commands.Cog):
    def __init__(self,bot):
        self.bot = bot

    @commands.command()
    async def hello(self,ctx,member: discord.Member = None):
        """
        NI HAO
        """
        member = ctx.author
        await ctx.send(f'NI HAO {member}')

    @commands.command()
    async def ping(self,ctx):
        """
        Another test command
        """
        pinger = ctx.author
        bot_name = self.bot.user.name
        await ctx.send(f"{pinger} sent a ping to {bot_name}")