from sqlmodel import SQLModel
from datetime import date
from typing import List, Optional


class MealBase(SQLModel):
    date: date
    time: str
    description: str
    serving_size: float

    
class MealItemBase(SQLModel):
    description: str
    caloriesKcal: int
    proteinG: float
    carbsG: float
    fatG: float
    fiberG: float
    sugarG: float
    sodiumMg: int


class MealItemRead(MealItemBase):
    id: int
    meal_id: int  

class MealRead(MealBase):
    id: int
    items: List[MealItemRead] = []

class MealCreateMinimal(SQLModel):
    description: str
    date: Optional[str] = None  # default to today if missing

class NutritionSummary(SQLModel):
    date: str            # YYYY-MM-DD
    caloriesKcal: int
    proteinG: int
    carbsG: int
    fatG: int
    fiberG: int
    sugarG: int
    sodiumMg: int