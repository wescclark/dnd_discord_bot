from discord.ext import commands
from discord.ext.commands.errors import CommandInvokeError
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import IntegrityError
import sys
import discord
from westmarch.db.models import *
from westmarch.cogs.checks import DMAccessOnly, is_dm


class DM_Commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session = self.bot.session

    @commands.command()
    @is_dm()
    async def set_gold(self, ctx, player: str, new_gold: int):
        """
        !set_gold <player> <amount>
        """
        char = None
        try:
            char = (
                self.session.query(Characters)
                .filter(Characters.player_name.ilike(player))
                .first()
            )
        except NoResultFound:
            await ctx.send("No character found for that player.")
        except:
            await ctx.send("Someting went wrong.")
        if char:
            char.gold = new_gold
            try:
                self.session.commit()
            except:
                await ctx.send("Commit failed. Player gold not updated.")
                self.session.rollback()
            else:
                await ctx.send(
                    f"{char.character_name} ({char.player_name}) gold set to {char.gold}."
                )

    @set_gold.error
    async def set_gold_error(self, ctx, error):
        if isinstance(error, DMAccessOnly):
            await ctx.send(error)

    @commands.command()
    @is_dm()
    async def set_xp(self, ctx, player_name: str, xp: int):
        """
        wm!update_player_xp --> wm!update_player_xp Zaphikel 1000
        """
        player = (
            self.session.query(Characters)
            .filter(Characters.player_name == player_name)
            .one()
        )
        player.current_xp = xp
        self.session.commit()

        player_query = (
            self.session.query(Characters)
            .filter(Characters.player_name == player_name)
            .one()
        )

        await ctx.send(
            f"{player_query.player_name} has a new XP value of {player_query.current_xp}"
        )

    @set_xp.error
    async def set_xp_error(self, ctx, error):
        if isinstance(error, DMAccessOnly):
            await ctx.send(error)
