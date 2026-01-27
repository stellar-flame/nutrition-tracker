# backend/app/services/nutrition_ai_service.py
import os
import json
from openai import OpenAI
from app.models.schemas import MealItemBase

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def derive_nutrition(description: str) -> list[MealItemBase]:
    """Parse a meal description into structured nutrition data."""
    
    response = client.chat.completions.create(
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
    
    # Parse the JSON response
    data = json.loads(response.choices[0].message.content)
    
    # Convert to typed MealItemBase objects
    return [MealItemBase.model_validate(item) for item in data["items"]]