from asyncio import sleep

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from app.api.dependencies import verify_internal_token
from app.database.database import get_session
from app.models.nutrition_schemas import MealStatus
from app.repositories import meal_repo
import logging

router = APIRouter(prefix="/internal", tags=["internal"])
logger = logging.getLogger(__name__)

@router.post("/nutrition_result")
def nutrition_result(payload: dict, db: Session = Depends(get_session),_: str = Depends(verify_internal_token)):
    logger.info(f"Received internal nutrition result: {payload}")
   
    meal_id = payload["meal_id"]
    items = payload["items"]
    
    updated = meal_repo.attach_meal_items(db, meal_id, items)
    if not updated:
        raise HTTPException(status_code=404, detail="Meal not found")
    
    logger.info(f"Updated meal {meal_id} with nutrition info.")
    
    return {"status": "ok"}


@router.post("/nutrition_failed")
def mark_nutrition_failed(payload: dict, db: Session = Depends(get_session), _: str = Depends(verify_internal_token)):
    updated = meal_repo.update_meal_status(db, payload["meal_id"], MealStatus.FAILED)
    if not updated:
        raise HTTPException(status_code=404, detail="Meal not found")
   
    logger.warning(f"Meal {payload['meal_id']} marked FAILED: {payload['error']}")
    return {"status": "ok"}
