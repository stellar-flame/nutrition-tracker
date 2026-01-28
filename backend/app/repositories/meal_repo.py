from sqlmodel import Session, desc, select
from app.models.db_models import Meal, MealItem
from datetime import date

def get_meals_by_date(db: Session, day: str | date) -> list[Meal]:
    stmt = select(Meal).where(Meal.date == day).order_by(desc(Meal.time))
    return db.exec(stmt).all()

# meal_repo.py
def create_meal(db: Session, meal: Meal) -> Meal:
    db.add(meal)
    db.commit()
    db.refresh(meal)
    return meal
