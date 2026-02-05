from sqlmodel import Session, desc, select
from app.models.db_models import Meal, MealItem
from datetime import date

from app.models.schemas import MealStatus

def get_meals_by_date(db: Session, day: str | date) -> list[Meal]:
    stmt = select(Meal).where(Meal.date == day).order_by(desc(Meal.time))
    return db.exec(stmt).all()

# meal_repo.py
def create_meal(db: Session, meal: Meal) -> Meal:
    db.add(meal)
    db.commit()
    db.refresh(meal)
    return meal


def attach_meal_items(db: Session, meal_id: int, items: list[dict]) -> None:
    meal = db.get(Meal, meal_id)
    if not meal:
        raise ValueError(f"Meal with id {meal_id} not found")
    
    for item_data in items:
        item = MealItem(
            meal_id=meal_id,
            description=item_data["description"],
            caloriesKcal=item_data.get("caloriesKcal", 0.0),
            proteinG=item_data.get("proteinG", 0.0),
            carbsG=item_data.get("carbsG", 0.0),
            fatG=item_data.get("fatG", 0.0),
            fiberG=item_data.get("fiberG", 0.0),
            sugarG=item_data.get("sugarG", 0.0),
            sodiumMg=item_data.get("sodiumMg", 0.0),
        )
        db.add(item)

    meal.status = MealStatus.COMPLETED
    db.commit()