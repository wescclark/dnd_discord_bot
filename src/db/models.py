from sqlalchemy import Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class GuildInfo(Base):
    __tablename__ = 'guild_info'

    name = Column(String,primary_key=True,nullable=False)
    current_xp = Column(Integer)
    current_level = Column(Integer)
    min_player_level = Column(Integer)
    max_player_level = Column(Integer) 

class GuildLevel(Base):
    __tablename__ = 'guild_level'
    level = Column(Int,primary_key=True,nullable=False)
    xp_to_level = Column(Int)
    player_min = Column(Int)
    player_max = Column(Int)

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
    cost = Column(Int)
    amount = Column(Int)

class WeaponShop(Base):
    __tablename__ = 'steel_buffet'
    __table_args__ = {'sqlite_autoincrement':True}
    id = Column(Integer,primary_key=True,nullable=False)
    item = Column(String)
    cost = Column(Int)
    amount = Column(Int)