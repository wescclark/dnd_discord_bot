from discord.ext import commands
import discord
from db.models import * 

class WM_Commands(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
        self.session = self.bot.session

    @commands.command()
    @commands.is_owner()
    async def add_player(self, ctx, player_name: str, player_class: str):
        """
        Owner Command Only
        wm!add_player Playername Classname (defaults to 0 xp) 
        """
        new_player = GuildInfo(player_name = player_name, 
        player_class = player_class)
        self.session.add(new_player)
        self.session.commit()
        await ctx.send(f"New player added: ")
        await ctx.send(new_player)
    
    @commands.command()
    async def list_all_players(self,ctx):
        """
        Prints all player info out.
        """
        char_list = self.session.query(GuildInfo).all()
        await ctx.send([char for char in char_list])
    
    @commands.command()
    async def char_info(self,ctx,player_name: str):
        """
        wm!info PlayerName --> wm!info Zaphikel
        """
        print(player_name)
        char = self.session.query(GuildInfo).\
            filter(GuildInfo.player_name == player_name).one()
        print(char)
        
        await ctx.send(GuildInfo(player_name = char.player_name,
            current_xp = char.current_xp,
            current_level = char.current_level,
            player_class = char.player_class))

    @commands.command()
    @commands.is_owner()
    async def update_player_xp(self,ctx,player_name: str, xp: int):
        """
        Owner Command Only
        wm!update_player_xp --> wm!update_player_xp Zaphikel 1000
        """
        player = self.session.query(GuildInfo).\
            filter(GuildInfo.player_name == player_name).one()
        player.current_xp = xp
        self.session.commit()
        
        player_query = self.session.query(GuildInfo).\
            filter(GuildInfo.player_name == player_name).one()
        
        await ctx.send(f'{player_query.player_name} has a new XP value of {player_query.current_xp}')

