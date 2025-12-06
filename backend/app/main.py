from fastapi import FastAPI
from app.models.nutrition import Meal, MealItem, NutritionSummary
from fastapi.params import Query
from typing import Annotated
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()


origins = [
    "http://nutritionapptracker.com",
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


@app.get("/nutrition/meals", response_model=list[Meal])
def get_meals(date: Annotated[str, Query(pattern=r"^\d{4}-\d{2}-\d{2}$", description="YYYY-MM-DD")]):
    print(f"Fetching meals for date: {date}")
    # Temp stub implementation

    return [ Meal(
        description="Apple and Peanut Butter",
        date=date,
        time="10:30",
        serving_size=1.0,
        mealItems=[
            MealItem(
                description="Apple",
                caloriesKcal=90,
                proteinG=1,
                carbsG=50,
                fatG=20,
                fiberG=5,
                sugarG=10,
                sodiumMg=600,
            ),
            MealItem(
                description="Peanut Butter",
                caloriesKcal=180,
                proteinG=7,
                carbsG=8,
                fatG=16,
                fiberG=3,
                sugarG=4,
                sodiumMg=150,
            )],
        ),
        Meal(
            description="Chicken Salad",
            date=date,
            time="13:00",
            serving_size=1.0,
            mealItems=[
                MealItem(
                    description="Grilled Chicken Breast",
                    caloriesKcal=220,
                    proteinG=40,
                    carbsG=0,
                    fatG=5,
                    fiberG=0,
                    sugarG=0,
                    sodiumMg=400,
                ),
                MealItem(
                    description="Mixed Greens",
                    caloriesKcal=50,
                    proteinG=2,
                    carbsG=10,
                    fatG=1,
                    fiberG=4,
                    sugarG=2,
                    sodiumMg=100,
                ),
            ],
        ),
    ]