from typing import Protocol, List

class NutritionProvider(Protocol):
    async def run_nutrition_lookup(self, description: str, meal_id: int) -> None:
        ...