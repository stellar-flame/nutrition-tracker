from typing import List, Optional
from sqlmodel import Field, Relationship
from app.models.schemas import MealItemBase, MealBase

class MealItem(MealItemBase, table=True):
    __tablename__ = "meal_items"
    id: Optional[int] = Field(default=None, primary_key=True)
    meal_id: int = Field(foreign_key="meals.id")
    meal: Optional["Meal"] = Relationship(back_populates="items")

class Meal(MealBase, table=True):
    __tablename__ = "meals"
    id: Optional[int] = Field(default=None, primary_key=True)
    items: List[MealItem] = Relationship(back_populates="meal")

MealItem.model_rebuild()  # for forward refs if needed
Meal.model_rebuild()
