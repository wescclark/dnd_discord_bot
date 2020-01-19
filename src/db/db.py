from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, String, Integer
import json

def load_engine(user,password,hostname,port,database):
    engine = create_engine(f'postgresql+psycopg2://{user}:{password}@{hostname}:{port}/{database}')
    return engine

def create_session(engine):
    return sessionmaker(bind=engine,autocommit=True)

def connect(user,password,db,host='localhost',port=5432):

    engine = load_engine(user,password,hostname,port,db)
    session = create_session(engine)
    meta = MetaData(bind=engine,reflect=True)

class GuildInfo(base):
    __tablename__ = 'guild_info'

    name = Column(String,primary_key=True)
    xp = Column(Integer) 