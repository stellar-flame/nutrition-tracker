from fastapi import APIRouter, Depends, HTTPException, Header
from sqlmodel import Session
from app.api.dependencies import verify_internal_token
from app.database.database import get_session
from app.repositories import meal_repo
import logging

router = APIRouter(prefix="/internal", tags=["internal"])
logger = logging.getLogger(__name__)

@router.post("/nutrition_result")
def nutrition_result(
    payload: dict,
    db: Session = Depends(get_session),
    _: str = Depends(verify_internal_token),
):
    logger.info(f"Received internal nutrition result: {payload}")
   
    meal_id = payload["meal_id"]
    items = payload["items"]

    # update meal + update daily totals
    meal_repo.attach_meal_items(db, meal_id, items)
    
    logger.info(f"Updated meal {meal_id} with nutrition info.")

    return {"status": "ok"}
