from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


def load_engine(file_loc, echo_sql=False):
    print(file_loc)
    engine = create_engine(f"sqlite:///{file_loc}", echo=echo_sql)
    return engine


def create_session(engine):
    return sessionmaker(bind=engine)


def connect(file_loc, echo_sql=False):
    engine = load_engine(file_loc, echo_sql)
    ses = create_session(engine)
    session = ses()

    return engine, session
