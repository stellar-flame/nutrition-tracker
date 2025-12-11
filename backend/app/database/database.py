from sqlmodel import SQLModel, create_engine, Session
import os

from dotenv import load_dotenv
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://postgres:postgres@localhost:5432/nutrition")
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

def get_session():
    with Session(engine) as session:
        yield session

# only for SQLite/tests
def create_all():
    SQLModel.metadata.create_all(engine)
