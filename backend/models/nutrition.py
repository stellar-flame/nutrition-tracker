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