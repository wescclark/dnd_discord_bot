from discord.ext import commands
import dice
import discord


class Basic(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def hello(self, ctx, member: discord.Member = None):
        """
        NI HAO
        """
        member = ctx.author
        await ctx.send(f"NI HAO {member}")

    @commands.command()
    async def ping(self, ctx):
        """
        Another test command
        """
        pinger = ctx.author
        bot_name = self.bot.user.name
        await ctx.send(f"{pinger} sent a ping to {bot_name}")

    @commands.command()
    async def engineurl(self, ctx):
        """
        Test that db is alive
        """
        pinger = ctx.author
        await ctx.send(f"{pinger}, the url for the db is {self.bot.engine.url}")

    @commands.command()
    async def listtables(self, ctx):
        """
        What tables are in the db
        """
        pinger = ctx.author
        print(self.bot.engine.table_names())
        table_names = ", ".join(self.bot.engine.table_names())
        await ctx.send(f"{pinger}, the tables in the db are {table_names}")

    @commands.command(
        name="roll", help="Roll dice, e.g. 3d6+5", aliases=["r", "Roll", "R"]
    )
    async def roll(self, ctx, roll_string: str):
        try:
            roll_result = str(dice.roll(roll_string))
        except dice.DiceException:
            roll_result = "Invalid roll. Try again."
        await ctx.send(roll_result)
