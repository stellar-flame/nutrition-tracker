import datetime
import logging
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from sqlmodel import Session
from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from app.models.schemas import MealRead, NutritionSummary, MealCreateMinimal
from fastapi.params import Query
from typing import Annotated
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Depends
from app.database.database import get_engine, get_session
from app.repositories import meal_repo
from app.models.db_models import MealItem, Meal
from datetime import date
from app.services import derive_nutrition

app = FastAPI()
log = logging.getLogger("uvicorn.error")

origins = [
    "http://nutritionapptracker.com",
    "http://localhost:5173",
    # add https://your-cloudfront-domain.com later if you use CloudFront
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def root():
    return {"message": "Hello World"}

@app.get("/db_health")
def db_health():
    try:
        with Session(get_engine()) as session:
            session.exec(text("SELECT 1"))
        return {"status": "ok"}
    except OperationalError:
        return JSONResponse(status_code=503, content={"status": "db_unavailable"})

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    log.warning("HTTP error on %s %s: %s", request.method, request.url.path, exc.detail)
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail},
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request, exc):
    log.exception("Unhandled error on %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content={"message": f"An error occurred: {str(exc)}"},
    )


@app.get("/nutrition/summary", response_model=NutritionSummary)
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


@app.get("/nutrition/meals", response_model=list[MealRead])
def get_meals(date: Annotated[str, Query(pattern=r"^\d{4}-\d{2}-\d{2}$", description="YYYY-MM-DD")], db: Session = Depends(get_session)):
    meals = meal_repo.get_meals_by_date(db, date)
    reads = [MealRead.model_validate(meal) for meal in meals] 
    return reads

@app.post("/nutrition/meals", response_model=MealRead, status_code=201)
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
