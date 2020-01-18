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