import os

from sqlmodel import create_engine, Session
from .models import SQLModel


POSTGRES_USER = os.getenv('POSTGRES_USER')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')
POSTGRES_DB = os.getenv('POSTGRES_DB')
POSTGRES_HOST = os.getenv('POSTGRES_HOST')

DATABASE_URL = f'postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}/{POSTGRES_DB}'

engine = create_engine(DATABASE_URL, echo=True, pool_pre_ping=True)


def init_db():
    SQLModel.metadata.create_all(engine)


def wait_for_db():
    while True:
        try:
            engine.connect()
            break
        except:
            pass


def get_session():
    with Session(engine) as session:
        yield session