
from app.ports.nutrition_provider import NutritionProvider
from app.infrastructure.openai.DirectOpenAINutritionProvider import DirectOpenAINutritionProvider
from fastapi import Header, HTTPException
import os

def get_nutrition_provider() -> NutritionProvider:
    return DirectOpenAINutritionProvider()

def verify_internal_token(x_internal_token: str = Header(...)) -> str:
    if x_internal_token != os.environ.get("INTERNAL_TOKEN"):
        raise HTTPException(status_code=401, detail="Unauthorized")
    return x_internal_token