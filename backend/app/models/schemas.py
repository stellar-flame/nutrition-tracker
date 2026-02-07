from sqlmodel import SQLModel
from datetime import date
from typing import List
from enum import StrEnum, auto


class MealStatus(StrEnum):
    PENDING = auto()
    COMPLETE= auto()
    FAILED = auto()

class MealBase(SQLModel):
    date: date
    time: str
    created_at: str
    description: str
    serving_size: float = 1.0
    status: MealStatus = MealStatus.PENDING

class MealItemBase(SQLModel):
    description: str
    caloriesKcal: float = 0.0   
    proteinG: float = 0.0
    carbsG: float = 0.0
    fatG: float = 0.0
    fiberG: float = 0.0
    sugarG: float = 0.0
    sodiumMg: float = 0.0
    

class MealItemRead(MealItemBase):
    id: int
    meal_id: int  

class MealRead(MealBase):
    id: int
    items: List[MealItemRead] = []

class MealCreateMinimal(SQLModel):
    description: str
    date: date
    time: str

class NutritionSummary(SQLModel):
    date: str            # YYYY-MM-DD
    caloriesKcal: float
    proteinG: float
    carbsG: float
    fatG: float
    fiberG: float
    sugarG: float
    sodiumMg: float