from sqlmodel import Session, desc, select
from app.models.db_models import Meal, MealItem, User
from datetime import date

from app.models.nutrition_schemas import MealItemBase, MealStatus

def get_meals_by_date(db: Session, day: str | date, user: User) -> list[Meal]: 
    stmt = select(Meal).where(Meal.date == day)
    stmt = stmt.where(Meal.user_id == user.id)
    stmt = stmt.order_by(desc(Meal.created_at))
    return db.exec(stmt).all()

# meal_repo.py
def create_meal(db: Session, meal: Meal) -> Meal:
    db.add(meal)
    db.commit()
    db.refresh(meal)
    return meal


def attach_meal_items(db: Session, meal_id: int, items: list[MealItemBase]) -> Meal:
    meal = db.get(Meal, meal_id)
    if not meal:
        raise ValueError(f"Meal with id {meal_id} not found")

    for item_data in items:
        item = MealItem(meal_id=meal_id, **item_data.model_dump())
        db.add(item)

    meal.status = MealStatus.COMPLETE
    db.commit()
    return meal


def update_meal_status(db: Session, meal_id: int, status: MealStatus) -> Meal:
    meal = db.get(Meal, meal_id)
    if not meal:
        raise ValueError(f"Meal with id {meal_id} not found")

    meal.status = status
    db.commit()
    return meal


def delete_meal(db: Session, meal_id: int) -> Meal | None:
    meal = db.get(Meal, meal_id)
    if not meal:
        return None
    for item in db.exec(select(MealItem).where(MealItem.meal_id == meal_id)).all():
        db.delete(item)
    db.delete(meal)
    db.commit()
    return meal

