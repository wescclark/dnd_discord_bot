from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
import json

Base = declarative_base()


def load_engine(file_loc, echo_sql=False):
    # engine = create_engine(f'postgresql+psycopg2://{user}:{password}@{hostname}:{port}/{database}')
    print(file_loc)
    engine = create_engine(f"sqlite:///{file_loc}", echo=echo_sql)
    return engine


def create_session(engine):
    return sessionmaker(bind=engine)


def connect(file_loc):
    engine = load_engine(file_loc)
    ses = create_session(engine)
    session = ses()

    return engine, session
