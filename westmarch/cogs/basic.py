from discord.ext import commands
import dice
import discord
from westmarch.db.models import CharacterClasses, Professions


class Basic(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session = bot.session

    @commands.command()
    async def ping(self, ctx):
        """
        Ping the guild master
        """
        await ctx.send("PONG!")

    @commands.command(name="roll", help="!roll 3d6+5", aliases=["r", "Roll", "R"])
    async def roll(self, ctx, roll_string: str):
        try:
            roll_result = str(dice.roll(roll_string))
        except dice.DiceException:
            roll_result = "Invalid roll. Try again."
        await ctx.send(roll_result)

    @commands.command()
    async def list_classes(self, ctx):
        """
        List available classes
        """
        classes = [
            "* " + _.name
            for _ in self.session.query(CharacterClasses)
            .order_by(CharacterClasses.name)
            .all()
        ]
        await ctx.send("\n".join(classes))

    @commands.command()
    async def list_professions(self, ctx):
        """
        List available professions
        """
        professions = [
            "* " + _.name
            for _ in self.session.query(Professions).order_by(Professions.name).all()
        ]
        await ctx.send("\n".join(professions))
