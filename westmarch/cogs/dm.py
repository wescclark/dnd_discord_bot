from discord.ext import commands
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm.exc import NoResultFound

from westmarch.cogs.checks import DMAccessOnly, is_dm
from westmarch.db.models import Characters


class DM_Commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session = self.bot.session

    @commands.command()
    @is_dm()
    async def set_gold(self, ctx, character_name: str, new_gold: int):
        """
        !set_gold <character name> <amount>
        """
        char = None
        try:
            char = (
                self.session.query(Characters)
                .filter(Characters.character_name.ilike(character_name))
                .first()
            )
        except NoResultFound:
            await ctx.send("No character found by that name.")
        except SQLAlchemyError:
            await ctx.send("Someting went wrong.")
        if char:
            char.gold = new_gold
            try:
                self.session.commit()
            except SQLAlchemyError:
                await ctx.send("Commit failed. Character gold not updated.")
                self.session.rollback()
            else:
                await ctx.send(
                    f"{char.character_name} ({char.player_name}) "
                    + f"gold set to {char.gold}."
                )

    @set_gold.error
    async def set_gold_error(self, ctx, error):
        if isinstance(error, DMAccessOnly):
            await ctx.send(error)

    @commands.command()
    @is_dm()
    async def set_xp(self, ctx, character_name: str, xp: int):
        """
        !set_xp <character name> <xp>
        """
        try:
            char = (
                self.session.query(Characters)
                .filter(Characters.character_name.ilike(character_name))
                .one()
            )
        except NoResultFound:
            await ctx.send("No character found by that name.")
            return

        char.xp = xp
        try:
            self.session.commit()
        except SQLAlchemyError:
            await ctx.send("Commit failed. Player XP not updated.")
            self.session.rollback()
        else:
            await ctx.send(
                f"{char.character_name} ({char.player_name}) XP set to {char.xp}."
            )

    @set_xp.error
    async def set_xp_error(self, ctx, error):
        if isinstance(error, DMAccessOnly):
            await ctx.send(error)
