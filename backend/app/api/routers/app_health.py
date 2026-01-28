
from sqlalchemy.exc import OperationalError
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy import text
from app.database.database import get_engine
from sqlmodel import Session

router = APIRouter(prefix="/health", tags=["health"])

@router.get("/")
async def root():
    return {"message": "Hello World"}

@router.get("/db")
def db_health():
    try:
        with Session(get_engine()) as session:
            session.exec(text("SELECT 1"))
        return {"status": "db ok"}
    except OperationalError:
        return JSONResponse(status_code=503, content={"status": "db_unavailable"})
