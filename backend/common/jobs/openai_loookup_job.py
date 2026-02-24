import json
import os
from openai import  AsyncOpenAI
import logging

logger = logging.getLogger(__name__)

async def ai_lookup(description: str, meal_id: int):
    client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"), timeout=60.0)  # Long timeout for OpenAI calls
    
    response = await client.chat.completions.create(
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