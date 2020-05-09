from discord.ext import commands
from discord.ext.commands.errors import CommandInvokeError
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import IntegrityError
import sys
import discord
from westmarch.db.models import *


class Character_Commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session = self.bot.session

    @commands.command()
    async def new_character(
        self, ctx, character_name: str, player_class: str, profession: str
    ):
        """
        !new_character <name> <class> <profession>
        """
        if self.valid_class(player_class) and self.valid_profession(profession):
            new_player = GuildInfo(
                player_name=ctx.author.name,
                character_name=str.title(character_name),
                player_class=str.capitalize(player_class),
                profession=str.capitalize(profession),
            )
            try:
                self.session.add(new_player)
                self.session.commit()
            except IntegrityError as e:
                self.session.rollback()
                if str(e.__cause__).__contains__("characters.player_name"):
                    await ctx.send(
                        "Error: You can only have one character. "
                        + "Delete yours if you'd like to make a new one."
                    )
                elif str(e.__cause__).__contains__("characters.character_name"):
                    await ctx.send("Error: Another character with that name exists.")
                else:
                    await ctx.send("Error: {}".format(e.__cause__))
            except:
                self.session.rollback()
                await ctx.send("Something went wrong!")
                await ctx.send(sys.exc_info())
            else:
                await ctx.send(f"New character added: ")
                await ctx.send(new_player)
        else:
            error_message = ""
            if not self.valid_class(player_class):
                error_message += "Invalid class entered."
            if not self.valid_profession(profession):
                if len(error_message) > 0:
                    error_message += " "
                error_message += "Invalid profession entered."
            await ctx.send(error_message)

    @commands.command()
    async def list_characters(self, ctx):
        """
        Prints all character info out.
        """
        char_list = (
            self.session.query(GuildInfo).order_by(GuildInfo.character_name).all()
        )
        for character in char_list:
            await ctx.send("\n-- " + str(character))

    @commands.command()
    async def info(self, ctx, player_name: str = ""):
        """
        !info PlayerName --> !info Zaphikel
        """
        search_name = player_name or ctx.author.name
        try:
            char = (
                self.session.query(GuildInfo)
                .filter(GuildInfo.player_name.ilike(search_name))
                .one()
            )
        except NoResultFound:
            await ctx.send("No character found for that player.")
        except:
            await ctx.send("Something went wrong!")
        else:
            await ctx.send(char)

    @commands.command()
    async def delete_character(self, ctx, char_name: str):
        """
        !delete_character CharacterName --> !delete Mako
        """
        char = (
            self.session.query(GuildInfo)
            .filter(GuildInfo.character_name == char_name)
            .one()
        )
        if char.player_name == ctx.author.name:
            self.session.delete(char)
            self.session.commit()
            await ctx.send("{} has been deleted.".format(str.title(char_name)))
        else:
            await ctx.send("You can't delete another person's character.")

    @commands.command()
    @commands.is_owner()
    async def update_player_xp(self, ctx, player_name: str, xp: int):
        """
        Owner Command Only
        wm!update_player_xp --> wm!update_player_xp Zaphikel 1000
        """
        player = (
            self.session.query(GuildInfo)
            .filter(GuildInfo.player_name == player_name)
            .one()
        )
        player.current_xp = xp
        self.session.commit()

        player_query = (
            self.session.query(GuildInfo)
            .filter(GuildInfo.player_name == player_name)
            .one()
        )

        await ctx.send(
            f"{player_query.player_name} has a new XP value of {player_query.current_xp}"
        )

    def valid_class(self, player_class):
        class_list = []
        for c in self.session.query(CharacterClasses.name).all():
            class_list.append(c.name)
        return str.title(player_class) in class_list

    def valid_profession(self, profession):
        profession_list = []
        for p in self.session.query(Professions.name).all():
            profession_list.append(p.name)
        return str.title(profession) in profession_list
