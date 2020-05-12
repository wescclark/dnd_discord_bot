from discord.ext import commands
import dice
import discord
from sqlalchemy import func
from sqlalchemy.orm.exc import NoResultFound
from westmarch.db.models import CharacterClasses, Items, Professions, Spellbook
from westmarch.spell import Spell


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
    async def lookup_item(self, ctx, *search_string):
        """
        !item_info <item name>
        """
        item = None
        try:
            item = (
                self.session.query(Items)
                .filter(Items.name.ilike(" ".join(search_string)))
                .one()
            )
        except NoResultFound:
            await ctx.send("No item found by that name.")
        except:
            await ctx.send("Someting went wrong.")
        else:
            await ctx.send(item)

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

    @commands.command()
    async def lookup_profession(self, ctx, profession):
        """
        !profession_info <profession>
        """

        try:
            result = (
                self.session.query(Professions)
                .filter(Professions.name.ilike(profession))
                .one()
            )
        except NoResultFound:
            await ctx.send("No such profession found.")
        except:
            await ctx.send("Something went wrong.")
        else:
            await ctx.send(result)

    @commands.command(help="!lookup_spell <spell name>", aliases=["s", "spell"])
    async def lookup_spell(self, ctx, *search_string):
        try:
            message = Spell.format_spell_text(
                self.session.query(Spellbook)
                .filter(
                    func.lower(Spellbook.name) == func.lower(" ".join(search_string))
                )
                .one()
            )
        except NoResultFound as err:
            message = "No spell found by that name."
        if len(message) > 1999:
            while len(message) > 1999:
                # Break the message on its last newline before the 2000 char limit
                clean_break = message[0:2000].rfind("\n") + 1
                await ctx.send(message[:clean_break])
                message = ">>> " + message[clean_break:]
            await ctx.send(message)
        else:
            await ctx.send(message)

    @commands.command(help="Send list of all spells by DM")
    async def list_spells(self, ctx, *search_string):
        message = "**Spell Name - Source**\n"
        for s in self.session.query(Spellbook).order_by(Spellbook.name).all():
            message += s.name + " - " + s.source + "\n"
        await ctx.send("DMing you the index now, {}!".format(ctx.author.name))
        if len(message) > 1999:
            while len(message) > 1999:
                # Break the list on its last newline before the 2000 char limit
                clean_break = message[0:2000].rfind("\n") + 1
                await ctx.author.send(message[0:clean_break])
                message = message[clean_break:]
            await ctx.author.send(message[0:2000])
        else:
            await ctx.author.send(message)
