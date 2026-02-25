import asyncio
from typing import Annotated
from datetime import datetime, timezone
from sqlmodel import Session
from app.ports.job_queue import JobQueue
from app.repositories import meal_repo
from app.models.nutrition_schemas import MealRead, MealCreateMinimal
from app.models.db_models import  Meal
from app.models.nutrition_schemas import MealStatus
from fastapi import APIRouter, Depends, HTTPException, Query
from app.database.database import get_session
from app.models.nutrition_schemas import NutritionSummary
from app.api.dependencies import  get_queue
import logging

router = APIRouter(prefix="/nutrition", tags=["nutrition"])    

@router.get("/summary", response_model=NutritionSummary)
def get_nutrition_summary(date: Annotated[str, Query(pattern=r"^\d{4}-\d{2}-\d{2}$", description="YYYY-MM-DD")], db: Session = Depends(get_session)):
    meals = meal_repo.get_meals_by_date(db, date)
    mealreads = [MealRead.model_validate(meal) for meal in meals]
    meal_items = [item for meal in mealreads for item in meal.items]
    return NutritionSummary(
        date=date,
        caloriesKcal=sum(meal.caloriesKcal for meal in meal_items),
        proteinG=sum(meal.proteinG for meal in meal_items),
        carbsG=sum(meal.carbsG for meal in meal_items),
        fatG=sum(meal.fatG for meal in meal_items),
        fiberG=sum(meal.fiberG for meal in meal_items),  
        sugarG=sum(meal.sugarG for meal in meal_items),
        sodiumMg=sum(meal.sodiumMg for meal in meal_items)
    )


@router.get("/meals", response_model=list[MealRead])
def get_meals(date: Annotated[str, Query(pattern=r"^\d{4}-\d{2}-\d{2}$", description="YYYY-MM-DD")], db: Session = Depends(get_session)):
    meals = meal_repo.get_meals_by_date(db, date)
    reads = [MealRead.model_validate(meal) for meal in meals] 
    return reads

@router.post("/meals", response_model=MealRead, status_code=201)
def create_meal_endpoint(payload: MealCreateMinimal, db: Session = Depends(get_session), job: JobQueue = Depends(get_queue)):
    meal_date = payload.date 
    meal_time = payload.time
    created_at = datetime.now(timezone.utc).isoformat()
    
    meal = Meal(
        date=meal_date,
        time=meal_time,
        created_at=created_at,
        description=payload.description,
        items=[],
        status=MealStatus.PENDING
    )
    saved = meal_repo.create_meal(db, meal)
    
    prompt = {
        "meal_description": payload.description,
        "meal_id": saved.id
    }
    try:
        job.enqueue(prompt=prompt)
    except Exception as e:
        logging.error(f"Failed to enqueue job for meal_id {saved.id}: {e}")
        meal_repo.update_meal_status(db, saved.id, MealStatus.FAILED)
        raise HTTPException(status_code=503, detail="Queue operation failed")
       
    return MealRead.model_validate(saved)

