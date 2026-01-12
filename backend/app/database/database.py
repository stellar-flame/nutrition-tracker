import logging
from fastapi import HTTPException
from sqlalchemy.exc import OperationalError
from sqlmodel import SQLModel, create_engine, Session
import os

# Only try to load .env in dev/local
if os.getenv("ENV", "local") == "local":
    from dotenv import load_dotenv
    load_dotenv()

engine = None
log = logging.getLogger("uvicorn.error")

def get_engine():
    global engine
    if engine is None:
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            raise RuntimeError("DATABASE_URL is not set")
        engine = create_engine(database_url, pool_pre_ping=True)
    return engine

def get_session():
    with Session(get_engine()) as session:
        try:
            yield session
        except OperationalError as exc:
            log.warning("Database unavailable: %s", exc)
            raise HTTPException(status_code=503, detail="Database unavailable") from exc
