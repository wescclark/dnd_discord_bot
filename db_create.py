import argparse
from dotenv import load_dotenv, find_dotenv
import json
from sqlalchemy_utils import database_exists, create_database
import sys
from westmarch.db.db import connect, Base
from westmarch.db.models import GuildInfo, Spellbook
from westmarch.spell import Spell

load_dotenv(find_dotenv())

# user = os.getenv("DB_USER")
# password = os.getenv("DB_PASSWORD")
# hostname = os.getenv("DB_HOST", "localhost")
# port = os.getenv("DB_PORT", 5432)
# database = os.getenv("DATABASE_NAME", "west_march")
# file_loc = "test_db.db"


def db_init(env="dev", spells=None):
    engine, session = connect("westmarch-" + env + ".db")

    if database_exists(engine.url):
        print("Dropping old tables...")
        Base.metadata.drop_all(bind=engine)
        session.commit()
    else:
        print("Creating new database...")
        create_database(engine.url)

    print("Creating tables...")
    Base.metadata.create_all(bind=engine)

    print("Populating tables...")
    session.add(GuildInfo(player_name="Zaphikel", player_class="Cleric"))

    if spells:
        try:
            with open(spells, "r") as input_file:
                for spell_data in json.load(input_file)["spell"]:
                    session.add(
                        Spellbook(
                            **Spell(spell_data, from_tools=True).export_for_sqlite()
                        )
                    )
        except FileNotFoundError:
            print("File not found.")
    else:
        try:
            with open("srd-spells.json", "r") as input_file:
                for spell_data in json.load(input_file):
                    session.add(Spellbook(**Spell(spell_data).export_for_sqlite()))
        except FileNotFoundError:
            print("File not found.")

    session.commit()

    return engine, session


if __name__ == "__main__":
    # Command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--env", help="The db environment to create: dev, prod, or test", default="dev"
    )
    parser.add_argument(
        "--spells", help="A json file containing spells in 5e.tools format"
    )
    args = parser.parse_args()

    if args.env not in ["dev", "prod", "test"]:
        sys.exit("Environment not recognized. Please use dev, prod, or test.")

    response = input(
        "Are you sure you want to overwrite any existing {} database? (y/N)".format(
            args.env
        )
    )
    if response.lower() == "y":
        engine, ses = db_init(env=args.env, spells=args.spells)
    else:
        sys.exit("Database creation canceled.")
