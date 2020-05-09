import argparse
from dotenv import load_dotenv, find_dotenv
import json
from sqlalchemy_utils import database_exists, create_database
import sys
from westmarch.db.db import connect, Base
from westmarch.db.models import CharacterClasses, GuildInfo, Professions, Spellbook
from westmarch.spell import Spell
from westmarch.data import character_classes, professions

load_dotenv(find_dotenv())


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
    # Populate spells table
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

    # Populate professions table
    for profession, description in professions.items():
        session.add(Professions(name=profession, description=description))
    session.commit()

    # Populate classes table
    for c in character_classes:
        session.add(CharacterClasses(name=c))
    session.commit()

    # Add test characters if building dev or test db
    if env == "dev" or env == "test":
        populate_test_characters(session).commit()

    return engine, session


def populate_test_characters(session):
    session.add(
        GuildInfo(
            player_name="Zaphikel",
            character_name="Mako",
            player_class="Warlock",
            profession="Linguist",
        )
    )
    session.add(
        GuildInfo(
            player_name="Godet",
            character_name="Verous",
            player_class="Paladin",
            profession="Physician",
        )
    )
    session.add(
        GuildInfo(
            player_name="Donknocks",
            character_name="Withers",
            player_class="Monk",
            profession="Survivalist",
        )
    )
    return session


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
