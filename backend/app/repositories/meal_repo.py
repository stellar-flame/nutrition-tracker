from sqlmodel import Session, select
from app.models.db_models import Meal, MealItem
from datetime import date

def get_meals_by_date(db: Session, day: str | date) -> list[Meal]:
    stmt = select(Meal).where(Meal.date == day).options()
    return db.exec(stmt).all()