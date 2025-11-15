from fastapi import FastAPI
from models.nutrition import NutritionSummary
from fastapi.params import Query
from typing import Annotated

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/nutrition/summary", response_model=NutritionSummary)
def get_nutrition_summary(date: Annotated[str, Query(pattern=r"^\d{4}-\d{2}-\d{2}$", description="YYYY-MM-DD")]):
    print(f"Fetching nutrition summary for date: {date}")
    # Temp stub implementation
    base = sum(map(int, date.replace("-", ""))) % 200
    return NutritionSummary(
        date=date,
        caloriesKcal=2100 + base,
        proteinG=140 + base % 20,
        carbsG=240 + base % 30,
        fatG=70 + base % 10,
        fiberG=28 + base % 6,
        sugarG=80 + base % 15,
        sodiumMg=2200 + (base % 400),
    )
