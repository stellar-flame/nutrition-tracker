import os
import httpx
from openai import OpenAI
from app.ports.nutrition_provider import NutritionProvider
import json
import logging

logger = logging.getLogger(__name__)

class DirectOpenAINutritionProvider(NutritionProvider):
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    async def run_nutrition_lookup(self, description: str, meal_id: int = None):
        try:
            data = await self.ai_lookup(description, meal_id)    
            await self.update_nutrition_info(meal_id, data["items"])
        except Exception as e:
            logger.exception(f"Error during nutrition lookup for meal_id {meal_id}: {e}")
            raise e

    async def ai_lookup(self, description: str, meal_id: int):
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            response_format={"type": "json_object"},  # Guarantees valid JSON
            messages=[
                {
                    "role": "system",
                    "content": """You are a nutrition expert. Return JSON with a "items" array.
    Each item must have: description (string), caloriesKcal (int), proteinG (float), 
    carbsG (float), fatG (float), fiberG (float), sugarG (float), sodiumMg (int)."""
                },
                {
                    "role": "user",
                    "content": f"Estimate nutrition for: {description}"
                }
            ],
            temperature=0.3,  # Lower = more consistent estimates
        )
        data = json.loads(response.choices[0].message.content)
        logger.info(f"AI nutrition lookup successful for meal_id {meal_id}")  
        return data  

    async def update_nutrition_info(self, meal_id: int, items: list[dict]):
        async with httpx.AsyncClient() as client:
            await client.post(
                os.getenv("INTERNAL_API_URL") + "/nutrition_result",
                headers={"X-Internal-Token": os.getenv("INTERNAL_TOKEN")},
                json={
                    "meal_id": meal_id,
                    "items": items
                }
            )
        logger.info(f"Nutrition info updated for meal_id {meal_id}")