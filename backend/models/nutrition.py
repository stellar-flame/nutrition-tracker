from pydantic import BaseModel

class NutritionSummary(BaseModel):
    date: str            # YYYY-MM-DD
    caloriesKcal: int
    proteinG: int
    carbsG: int
    fatG: int
    fiberG: int
    sugarG: int
    sodiumMg: int


class MealItem(BaseModel):
    description: str
    caloriesKcal: int
    proteinG: int
    carbsG: int
    fatG: int
    fiberG: int
    sugarG: int
    sodiumMg: int


class Meal(BaseModel):
    description: str     
    mealItems: list[MealItem]
    date: str            # YYYY-MM-DD
    time: str            # HH:MM
    serving_size: float