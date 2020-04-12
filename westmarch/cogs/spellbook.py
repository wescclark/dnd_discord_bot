import discord
from discord.ext import commands
from sqlalchemy import func
from sqlalchemy.orm.exc import NoResultFound
from westmarch.db.models import Spellbook
from westmarch.spell import Spell


class Spellbook_Commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session = self.bot.session

    @commands.command(
        name="spellbook", help="Look up a spell", aliases=["s", "Spellbook", "S"]
    )
    async def spell_lookup(self, ctx, *search_string):
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

    @commands.command(
        name="spell_index", help="DM you a list of all spells and sources"
    )
    async def spell_index(self, ctx, *search_string):
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
