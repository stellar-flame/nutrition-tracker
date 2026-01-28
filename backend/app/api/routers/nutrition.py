from typing import Annotated
import datetime
from sqlmodel import Session
from app.repositories import meal_repo
from app.models.schemas import MealRead, MealCreateMinimal
from app.models.db_models import MealItem, Meal
from app.services import derive_nutrition   
from fastapi import APIRouter, Depends, Query
from app.database.database import get_session
from app.models.schemas import NutritionSummary
from datetime import date

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
def create_meal_endpoint(payload: MealCreateMinimal, db: Session = Depends(get_session)):
    meal_date = payload.date or date.today()
    meal_time = datetime.datetime.now().strftime("%H:%M") # AI-derived nutrition (replaces hardcoded values)
    
    item_data = derive_nutrition(payload.description)
    
    print("Derived nutrition items:", item_data)  # Debugging line

    items = [MealItem(**item.model_dump()) for item in item_data]
  
    meal = Meal(
        date=meal_date,
        time=meal_time,
        description=payload.description,
        serving_size=1.0,
        items=items,
    )
    saved = meal_repo.create_meal(db, meal)
    return MealRead.model_validate(saved)
