from sqlmodel import SQLModel, create_engine, Session
import os

# Only try to load .env in dev/local
if os.getenv("ENV", "local") == "local":
    from dotenv import load_dotenv
    load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL, pool_pre_ping=True)

def get_session():
    with Session(engine) as session:
        yield session


