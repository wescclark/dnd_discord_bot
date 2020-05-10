from sqlalchemy import Column, String, Integer, Boolean
import bisect
from westmarch.db.db import Base

player_level_range = [
    (0, 1),
    (300, 2),
    (900, 3),
    (2700, 4),
    (6500, 5),
    (14000, 6),
    (23000, 7),
    (34000, 8),
    (48000, 9),
    (64000, 10),
    (85000, 11),
    (100000, 12),
    (120000, 13),
    (140000, 14),
    (165000, 15),
    (195000, 16),
    (225000, 17),
    (265000, 18),
    (305000, 19),
    (355000, 20),
]


def player_level_func(context):
    return bisect.bisect_left(
        player_level_range, (context.current_parameters["current_xp"],)
    )


class CharacterClasses(Base):
    __tablename__ = "character_classes"
    name = Column(String, primary_key=True, nullable=False)


class Characters(Base):
    __tablename__ = "characters"

    player_id = Column(Integer, primary_key=True, nullable=False)
    player_name = Column(String, nullable=False)
    character_name = Column(String, nullable=False, unique=True)
    xp = Column(Integer, default=0)
    level = Column(Integer, default=1)  # , onupdate=player_level_func)
    player_class = Column(String, nullable=False)
    profession = Column(String, nullable=False)
    gold = Column(Integer, default=500)

    def __str__(self):
        output = "**{name}** - {player_class} {level} ({xp} XP)\nGold: {gold}\nProfession: {profession}\nPlayer: {player_name}".format(
            name=self.character_name,
            level=self.level,
            player_class=self.player_class,
            xp=self.xp,
            gold=self.gold,
            profession=self.profession,
            player_name=self.player_name,
        )
        return output

    def __repr__(self):
        return self.__str__()


class GuildLevel(Base):
    __tablename__ = "guild_level"
    level = Column(Integer, primary_key=True, nullable=False)
    xp_to_level = Column(Integer)
    player_min = Column(Integer)
    player_max = Column(Integer)


class Spellbook(Base):
    __tablename__ = "spells"
    id = Column(Integer, primary_key=True)
    level = Column(Integer)
    name = Column(String)
    spell_level = Column(Integer)
    school = Column(String)
    source = Column(String)
    cast_time = Column(String)
    range = Column(String)
    components = Column(String)
    duration = Column(String)
    ritual = Column(Boolean)
    description = Column(String)


class ShopList(Base):
    __tablename__ = "shop_list"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    level_req = Column(Integer)


class PotionShop(Base):
    __tablename__ = "potion_shop"
    __table_args__ = {"sqlite_autoincrement": True}
    id = Column(Integer, primary_key=True, nullable=False)
    item = Column(String)
    cost = Column(Integer)
    amount = Column(Integer)


class Professions(Base):
    __tablename__ = "professions"
    name = Column(String, primary_key=True, nullable=False)
    description = Column(String, nullable=False)


class WeaponShop(Base):
    __tablename__ = "steel_buffet"
    __table_args__ = {"sqlite_autoincrement": True}
    id = Column(Integer, primary_key=True, nullable=False)
    item = Column(String)
    cost = Column(Integer)
    amount = Column(Integer)
