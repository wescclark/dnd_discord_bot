import argparse
import sys

from discord.ext import commands
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm.exc import NoResultFound

from westmarch.cogs.checks import DMAccessOnly, is_dm
from westmarch.db.models import Characters, Inventory, Items


class ParserException(Exception):
    pass


class ErrorCatchingArgumentParser(argparse.ArgumentParser):
    def exit(self, status=0, message=None):
        if status:
            raise ParserException(f"{message}")


class DM_Commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session = self.bot.session

    @commands.command()
    @is_dm()
    async def add_item(self, ctx, character_name: str, *input: str):
        """
        !add_item !add_item Character Item
        """
        try:
            item = (
                self.session.query(Items)
                .filter(Items.name.ilike(" ".join(input)))
                .one()
            )
        except NoResultFound:
            await ctx.send("No item found by that name.")
            return
        except SQLAlchemyError:
            await ctx.send("Someting went wrong.")
            return

        try:
            character = (
                self.session.query(Characters)
                .filter(Characters.character_name.ilike(character_name))
                .one()
            )
        except NoResultFound:
            await ctx.send("No character found by that name.")
            return
        except SQLAlchemyError:
            await ctx.send("Something went wrong!")
            return
        already_in_inventory = (
            self.session.query(Inventory)
            .filter(Inventory.character_id == character.id)
            .filter(Inventory.item_id == item.id)
            .first()
        )
        if already_in_inventory:
            already_in_inventory.quantity += 1
        else:
            character.items.append(item)
        try:
            self.session.commit()
        except SQLAlchemyError:
            await ctx.send("Something went wrong!")
            return
        else:
            await ctx.send(
                f"{character.character_name.capitalize()} received {item.name.title()}!"
            )

    @commands.command()
    @is_dm()
    async def remove_item(self, ctx, character_name: str, *input: str):
        """
        !remove_item !remove_item Character Item
        """
        try:
            item = (
                self.session.query(Items)
                .filter(Items.name.ilike(" ".join(input)))
                .one()
            )
        except NoResultFound:
            await ctx.send("No item found by that name.")
            return
        except SQLAlchemyError:
            await ctx.send("Someting went wrong.")
            return

        try:
            character = (
                self.session.query(Characters)
                .filter(Characters.character_name.ilike(character_name))
                .one()
            )
        except NoResultFound:
            await ctx.send("No character found by that name.")
            return
        except SQLAlchemyError:
            await ctx.send("Something went wrong!")
            return
        has_item = (
            self.session.query(Inventory)
            .filter(Inventory.character_id == character.id)
            .filter(Inventory.item_id == item.id)
            .first()
        )
        if has_item:
            character.items.remove(item)
            try:
                self.session.commit()
            except SQLAlchemyError:
                await ctx.send("Something went wrong!")
            else:
                await ctx.send(
                    f"Removed {item.name.title()} from"
                    + f"{character.character_name.capitalize()}'s inventory."
                )
        else:
            await ctx.send(f"{character.character_name} doesn't have that item.")

    @commands.command()
    @is_dm()
    async def create_item(self, ctx, *input: str):
        """
        !create_item See !help create_item for usage
        """
        parser = ErrorCatchingArgumentParser(prog="!create_item", add_help=False)
        parser.add_argument("name", nargs=1, metavar='"Item Name"')
        parser.add_argument("value", nargs=1, metavar="# in gp")
        parser.add_argument("--in-item-shop", dest="in_item_shop", action="store_true")
        parser.add_argument("-r", "--rarity", metavar='"Rarity"')
        parser.add_argument("-y", "--type", metavar='"Item Type"')
        parser.add_argument("-a", "--attunement", metavar='"Attunement text..."')
        parser.add_argument("-p", "--properties", metavar='"Property text..."')
        parser.add_argument("-w", "--weight", metavar='"# lbs."')
        parser.add_argument("-t", "--text", metavar='"Free text..."')

        try:
            item_info = vars(parser.parse_args(input))
        except ParserException:
            await ctx.send(f"{parser.format_help()}")
            return
        # values parsed by argparse are either None or returned inside lists. This
        # de-lists the values to make the next steps easier and avoid subscripting
        # None where there is no value.
        for k, v in item_info.items():
            if isinstance(v, list):
                item_info[k] = v[0]
        new_item = Items(
            name=item_info["name"],
            in_item_shop=item_info["in_item_shop"],
            source=ctx.author.name,
            rarity=item_info["rarity"],
            item_type=item_info["type"],
            attunement=item_info["attunement"],
            properties=item_info["properties"],
            weight=item_info["weight"],
            value=int(item_info["value"]),
            text=item_info["text"],
        )
        try:
            self.session.add(new_item)
            self.session.commit()
        except SQLAlchemyError:
            self.session.rollback()
            await ctx.send("Something went wrong!")
            await ctx.send(sys.exc_info())
        else:
            await ctx.send("New item added: ")
            await ctx.send(new_item)

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
