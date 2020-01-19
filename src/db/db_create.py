from sqlalchemy_utils import database_exists, create_database
from db import load_engine
from dotenv import load_dotenv,find_dotenv
import os

load_dotenv(find_dotenv())

user = os.getenv('DB_USER')
password = os.getenv('DB_PASSWORD')
hostname = os.getenv('DB_HOST','localhost')
port = os.getenv('DB_PORT',5432)
database = os.getenv('DATABASE_NAME','west_march'))

def db_init():
    engine = load_engine(user,password,hostname,port,database)
    if not database_exists(engine.url):
        create_database(engine.url)

class GuildInfo(base):
    __tablename__ = 'guild_info'

    name = Column(String,primary_key=True,nullable=False)
    xp = Column(Integer)
    level = Column(Integer) 