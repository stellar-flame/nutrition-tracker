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
    serving_size: float = 1.0
    

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


class PendingMealRead(BaseModel):
    meal_id: str
    date: str
    time: str
    description: str
    created_at: str
    status: PendingMealStatus
    items: List[MealItemBase] = []


class MealApprovePayload(BaseModel):
    items: List[MealItemBase] | None = None


class MealServingUpdate(BaseModel):
    item_servings: List[float]


class NutritionResultPayload(BaseModel):
    meal_id: str
    items: List[MealItemBase]


class NutritionFailedPayload(BaseModel):
    meal_id: str
    error: str = "Unknown error"