from dotenv import load_dotenv, find_dotenv
import json
import os
from sqlalchemy_utils import database_exists, create_database
import westmarch
from westmarch.db.db import load_engine, create_session, connect, Base
from westmarch.db.models import GuildInfo, GuildLevel, ShopList, WeaponShop, PotionShop, Spellbook
from westmarch.spell import Spell

load_dotenv(find_dotenv())

user = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")
hostname = os.getenv("DB_HOST", "localhost")
port = os.getenv("DB_PORT", 5432)
database = os.getenv("DATABASE_NAME", "west_march")
file_loc = "test_db.db"


def db_init():
    engine, session = connect(file_loc)

    if not database_exists(engine.url):
        print("creating db")
        create_database(engine.url)

    if not engine.dialect.has_table(engine, "guild_info"):
        print("butts")
        Base.metadata.create_all(bind=engine)

    session.add(GuildInfo(player_name="Zaphikel", player_class="Cleric"))

    with open("merged-spells.json", "r") as input_file:
        for spell_data in json.load(input_file)["spell"]:
            session.add(Spellbook(**Spell(spell_data, from_tools=True).export_for_sqlite()))
    
    session.commit()

    return engine, session


if __name__ == "__main__":
    engine, ses = db_init()
