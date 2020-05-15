from math import floor

from discord.ext import commands
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm.exc import NoResultFound

from westmarch.db.models import Characters, Inventory, Items


class Item_shop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session = bot.session

    @commands.command()
    async def buy_item(self, ctx, *item_search: str):
        try:
            char = (
                self.session.query(Characters)
                .filter(Characters.player_id == ctx.author.id)
                .one()
            )
        except NoResultFound:
            await ctx.send("You can't but anything without a character.")
            return
        except SQLAlchemyError:
            await ctx.send("Something went wrong!")
            return

        in_stock = (
            self.session.query(Items)
            .filter(Items.in_item_shop == True)
            .filter(Items.name.ilike(" ".join(item_search)))
            .first()
        )

        if in_stock:
            has_money = char.gold >= in_stock.value
            if not has_money:
                await ctx.send("You don't have enough money.")
                return
        else:
            await ctx.send("Item not for sale.")
            return

        if in_stock and has_money:
            char.gold -= in_stock.value

            already_in_inventory = (
                self.session.query(Inventory)
                .filter(Inventory.character_id == char.id)
                .filter(Inventory.item_id == in_stock.id)
                .first()
            )
            if already_in_inventory:
                already_in_inventory.quantity += 1
            else:
                char.items.append(in_stock)
            try:
                self.session.commit()
            except SQLAlchemyError:
                await ctx.send("Something went wrong!")
                return
            else:
                await ctx.send(
                    f"{char.character_name.capitalize()} bought {in_stock.name.title()}!"
                )

    @commands.command()
    async def items_for_sale(self, ctx):
        stock = (
            self.session.query(Items)
            .filter(Items.in_item_shop == True)
            .order_by(Items.name)
            .all()
        )
        if stock:
            output = "`"
            weapons = []
            armor = []
            items = []
            for i in stock:
                if "armor" in i.item_type or i.name == "Shield":
                    armor.append(i)
                elif "weapon" in i.item_type:
                    weapons.append(i)
                else:
                    items.append(i)
            for _ in [("Items", items), ("Weapons", weapons), ("Armor", armor)]:
                output += "{:-^30}\n".format(_[0])
                for item in _[1]:
                    output += "{:.<25}{}gp\n".format(item.name, item.value)
                output += "\n"
            output += "`"
        else:
            output = "No items in stock."
        await ctx.send(output)

    @commands.command()
    async def sell_item(self, ctx, *item_name: str):
        char = Characters.find_by_player_id(self.session, ctx.author.id)
        if not char:
            await ctx.send("You must have a character.")
            return
        item, quantity = char.has_item(self.session, " ".join(item_name))
        if item:
            if quantity > 1:
                self.session.query(Inventory).filter(
                    Inventory.item_id == item.id
                ).filter(Inventory.character_id == char.id).first().quantity -= 1
            else:
                char.items.remove(item)
            sale_price = floor(0.9 * item.value)
            char.gold += sale_price

            try:
                self.session.commit()
            except SQLAlchemyError:
                await ctx.send("Something went wrong")
            else:
                await ctx.send(
                    f"{char.character_name} sold {item.name} for {sale_price}gp."
                )
        else:
            await ctx.send("No item found to sell.")
