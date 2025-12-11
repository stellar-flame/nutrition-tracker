# backend/seed.py
from datetime import date
from sqlmodel import Session
from app.database.database import engine
from app.models.db_models import Meal, MealItem

def main():
    today = date.today()
    # with statement ensures the session is closed after the block is executed
    with Session(engine) as session:
        meal = Meal(
            date=today,
            time="10:30",
            description="Apple and Peanut Butter",
            serving_size=1.0,
            items=[
                MealItem(
                    description="Apple",
                    caloriesKcal=90,
                    proteinG=1,
                    carbsG=25,
                    fatG=0,
                    fiberG=4,
                    sugarG=19,
                    sodiumMg=2,
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
                ),
            ],
        )
        session.add(meal)
        session.commit()

if __name__ == "__main__":
    main()
