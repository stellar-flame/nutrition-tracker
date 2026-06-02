from sqlmodel import SQLModel
from pydantic import BaseModel
from datetime import date
from typing import List
from enum import StrEnum, auto


class Gender(StrEnum):
    FEMALE = "female",
    MALE = "male",
    OTHER = "other" 

class UserBase(SQLModel):
    first_name: str
    last_name: str
    height_in: float
    weight_lb: float
    date_of_birth: date
    gender: str
    

class UserRead(UserBase):
    id: int

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
    user_id: int

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


class PendingMealStatus(StrEnum):
    PENDING_AI = "pending_ai"
    PENDING_APPROVAL = "pending_approval"
    FAILED = "failed"


class PendingMealItemEdit(BaseModel):
    description: str
    caloriesKcal: float = 0.0
    proteinG: float = 0.0
    carbsG: float = 0.0
    fatG: float = 0.0
    fiberG: float = 0.0
    sugarG: float = 0.0
    sodiumMg: float = 0.0


class PendingMealRead(BaseModel):
    meal_id: str
    user_id: int
    date: str
    time: str
    description: str
    created_at: str
    status: PendingMealStatus
    items: List[PendingMealItemEdit] = []


class MealApprovePayload(BaseModel):
    items: List[PendingMealItemEdit] | None = None