from typing import List, Optional
from sqlmodel import Field, Relationship
from app.models.nutrition_schemas import MealItemBase, MealBase, UserBase

class User(UserBase, table=True):
    __tablename__ = "users"
    id: Optional[int] = Field(default=None, primary_key=True)
    meals: List["Meal"] = Relationship(back_populates="user")
    cognito_sub: str = Field(default=None, unique=True)


class MealItem(MealItemBase, table=True):
    __tablename__ = "meal_items"
    id: Optional[int] = Field(default=None, primary_key=True)
    meal_id: int = Field(foreign_key="meals.id")
    meal: Optional["Meal"] = Relationship(back_populates="items")

class Meal(MealBase, table=True):
    __tablename__ = "meals"
    id: Optional[int] = Field(default=None, primary_key=True)
    items: List[MealItem] = Relationship(back_populates="meal")
    user_id: int = Field(foreign_key="users.id")
    user: Optional[User] = Relationship(back_populates="meals")

MealItem.model_rebuild()  # for forward refs if needed
Meal.model_rebuild()
User.model_rebuild()  # for forward refs if needed    