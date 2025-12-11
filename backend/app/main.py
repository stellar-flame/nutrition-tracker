from fastapi import FastAPI
from sqlmodel import Session
from app.models.schemas import MealRead, NutritionSummary, MealItemRead
from fastapi.params import Query
from typing import Annotated
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Depends
from app.database.database import get_session
from app.repositories import meal_repo

app = FastAPI()


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

@app.get("/")
async def root():
    return {"message": "Hello World"}


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
    print(reads)
    return reads