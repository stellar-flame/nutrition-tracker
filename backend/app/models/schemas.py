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
    caloriesKcal: float
    proteinG: float
    carbsG: float
    fatG: float
    fiberG: float
    sugarG: float
    sodiumMg: float


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
    caloriesKcal: float
    proteinG: float
    carbsG: float
    fatG: float
    fiberG: float
    sugarG: float
    sodiumMg: float