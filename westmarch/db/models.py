from sqlalchemy import Column, String, Integer
import bisect
from westmarch.db.db import Base

player_level_range = [
    (0,1),
    (300,2),
    (900,3),
    (2700,4),
    (6500,5),
    (14000,6),
    (23000,7),
    (34000,8),
    (48000,9),
    (64000,10),
    (85000,11),
    (100000,12),
    (120000,13),
    (140000,14),
    (165000,15),
    (195000,16),
    (225000,17),
    (265000,18),
    (305000,19),
    (355000,20)
]

def player_level_func(context): 
    return bisect.bisect_left(player_level_range,(context.current_parameters['current_xp'],))

class GuildInfo(Base):
    __tablename__ = 'guild_info'

    player_name = Column(String,primary_key=True,nullable=False)
    current_xp = Column(Integer,default=0)
    current_level = Column(Integer,default = 1, onupdate=player_level_func)
    player_class = Column(String,nullable=False)

    def __str__(self):
        player_string = f"""
        Player Name: {self.player_name}
        Current XP: {self.current_xp}
        Current Level: {self.current_level}
        Player Class: {self.player_class}
        """
        return player_string
    
    def __repr__(self):
        return self.__str__()


class GuildLevel(Base):
    __tablename__ = 'guild_level'
    level = Column(Integer,primary_key=True,nullable=False)
    xp_to_level = Column(Integer)
    player_min = Column(Integer)
    player_max = Column(Integer)

class ShopList(Base):
    __tablename__ = 'shop_list'
    id = Column(Integer,primary_key=True)
    name = Column(String)
    level_req = Column(Integer)

class PotionShop(Base):
    __tablename__ = 'potion_shop'
    __table_args__ = {'sqlite_autoincrement': True}
    id = Column(Integer,primary_key=True,nullable=False)
    item = Column(String)
    cost = Column(Integer)
    amount = Column(Integer)

class WeaponShop(Base):
    __tablename__ = 'steel_buffet'
    __table_args__ = {'sqlite_autoincrement':True}
    id = Column(Integer,primary_key=True,nullable=False)
    item = Column(String)
    cost = Column(Integer)
    amount = Column(Integer)