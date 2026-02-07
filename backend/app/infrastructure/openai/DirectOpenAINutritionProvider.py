import os
import httpx
from openai import AsyncOpenAI
from app.ports.nutrition_provider import NutritionProvider
import json
import logging

logger = logging.getLogger(__name__)

class DirectOpenAINutritionProvider(NutritionProvider):
    client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"), timeout=60.0)  # Long timeout for OpenAI calls

    async def run_nutrition_lookup(self, description: str, meal_id: int = None):
        try:
            data = await self.ai_lookup(description, meal_id)    
            await self.update_nutrition_info(meal_id, data["items"])
        except Exception as e:
            logger.exception(f"Error during nutrition lookup for meal_id {meal_id}: {e}")
            await self.mark_as_failed(meal_id, str(e))

    async def ai_lookup(self, description: str, meal_id: int):
        response = await self.client.chat.completions.create(
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
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                os.getenv("INTERNAL_API_URL") + "/nutrition_result",
                headers={"X-Internal-Token": os.getenv("INTERNAL_TOKEN")},
                json={
                    "meal_id": meal_id,
                    "items": items
                }
            )
            response.raise_for_status()
        logger.info(f"Updated nutrition info for meal_id {meal_id}")
            
        
       
    async def mark_as_failed(self, meal_id: int, error_message: str):
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    os.getenv("INTERNAL_API_URL") + "/nutrition_failed",
                    headers={"X-Internal-Token": os.getenv("INTERNAL_TOKEN")},
                    json={
                        "meal_id": meal_id,
                        "error": error_message
                    }
                )
                response.raise_for_status()
            logger.info(f"Marked meal {meal_id} as FAILED")
        except Exception as e:
            # Last resort - log but don't raise, nothing more we can do
            logger.error(f"Failed to mark meal {meal_id} as FAILED: {e}")